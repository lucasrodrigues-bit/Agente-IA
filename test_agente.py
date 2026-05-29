"""Testes do agente — rodam 100% offline com o ProvedorFake (sem rede).

Cobrem comportamento real (não detalhes de implementação): os dunders que
existem, a validação da @property, o polimorfismo, a MRO da herança múltipla e
o crescimento do histórico. O ProvedorGroq (rede) não é testado de propósito —
o contrato é validado pelo ProvedorFake injetado.
"""

import pytest

from agentes import AgenteBase, AgenteLGPD, AgenteTecnologia
from dominio import Conversa, Mensagem
from provedores import ProvedorFake, ProvedorGroqAuditado, ProvedorLLM, RegistradorMixin


# --- dominio ---------------------------------------------------------------

def test_mensagem_para_dict_e_repr():
    m = Mensagem("usuario", "oi")
    assert m.para_dict() == {"role": "user", "content": "oi"}
    assert Mensagem("sistema", "x").para_dict()["role"] == "system"
    assert Mensagem("assistente", "y").para_dict()["role"] == "assistant"
    assert repr(m) == "Mensagem(papel='usuario', conteudo='oi')"


def test_mensagem_papel_invalido():
    with pytest.raises(ValueError):
        Mensagem("invalido", "x")


def test_conversa_dunders():
    c = Conversa()
    assert len(c) == 0
    c.adicionar(Mensagem("usuario", "a"))
    c.adicionar(Mensagem("assistente", "b"))
    assert len(c) == 2                                   # __len__
    assert [m.papel for m in c] == ["usuario", "assistente"]  # __iter__
    assert c.para_api() == [
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
    ]
    assert "[usuario] a" in str(c)                       # __str__


# --- provedores ------------------------------------------------------------

def test_provedor_fake_deterministico():
    p = ProvedorFake()
    msgs = [{"role": "user", "content": "pergunta X"}]
    r1 = p.gerar("especialista em LGPD", msgs, 0.7)
    r2 = p.gerar("especialista em LGPD", msgs, 0.7)
    assert r1 == r2                 # mesma entrada -> mesma saída
    assert "LGPD" in r1             # cita o nicho vindo do prompt de sistema
    assert "pergunta X" in r1       # ecoa a última fala do usuário


def test_mro_provedor_auditado():
    nomes = [c.__name__ for c in ProvedorGroqAuditado.__mro__]
    # O mixin de auditoria vem antes do provedor concreto: ele intercepta gerar().
    assert nomes.index("RegistradorMixin") < nomes.index("ProvedorGroq")
    assert ProvedorLLM in ProvedorGroqAuditado.__mro__


def test_auditoria_via_heranca_multipla():
    # Combina o mixin com o provedor offline para testar a auditoria sem rede.
    class FakeAuditado(RegistradorMixin, ProvedorFake):
        pass

    p = FakeAuditado()
    assert p.registros == []
    resposta = p.gerar("especialista em Tecnologia", [{"role": "user", "content": "oi"}], 0.5)
    # super() cooperativo: o mixin registra e delega a geração ao ProvedorFake.
    assert isinstance(resposta, str)
    assert "offline" in resposta.lower()
    assert len(p.registros) == 1


# --- agentes ---------------------------------------------------------------

def test_temperatura_validacao():
    agente = AgenteTecnologia(ProvedorFake())
    agente.temperatura = 0.0   # borda inferior: ok
    agente.temperatura = 2.0   # borda superior: ok
    for invalido in (2.01, -1.0, 3.0):
        with pytest.raises(ValueError):
            agente.temperatura = invalido


def test_polimorfismo():
    tec = AgenteTecnologia(ProvedorFake())
    lgpd = AgenteLGPD(ProvedorFake())
    assert tec.prompt_sistema() != lgpd.prompt_sistema()
    assert "LGPD" in lgpd.prompt_sistema()


def test_mro_agente():
    assert AgenteBase in AgenteTecnologia.__mro__


def test_responder_cresce_historico():
    agente = AgenteTecnologia(ProvedorFake())
    assert len(agente) == 1                 # só a mensagem de sistema
    resposta = agente.responder("o que é Python?")
    assert isinstance(resposta, str)
    assert len(agente) == 3                 # +pergunta +resposta
    mensagens = list(agente._historico)
    assert mensagens[-2].papel == "usuario"
    assert mensagens[-1].papel == "assistente"