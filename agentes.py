"""Agentes especialistas.

`AgenteBase` concentra **abstração** (é uma `ABC` com `prompt_sistema`
abstrato), **encapsulamento** (`_provedor` e `_historico` protegidos,
`__temperatura` privado atrás de uma `@property` que valida) e a lógica comum
de conversa. Cada especialista herda dela (**herança** + `super()`) e troca só
o prompt de sistema (**polimorfismo**).

O provedor é injetado no construtor (composição): o agente não sabe nem se
importa se está falando com o Groq, com o provedor offline ou com a versão
auditada — só conhece o contrato `ProvedorLLM`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from dominio import Conversa, Mensagem
from provedores import ProvedorLLM


class AgenteBase(ABC):
    """Base comum a todos os agentes especialistas."""

    NOME: str = ""

    def __init__(self, provedor: ProvedorLLM, temperatura: float = 0.7) -> None:
        self._provedor = provedor          # composição / injeção de dependência
        self._historico = Conversa()       # protegido
        self.temperatura = temperatura     # passa pelo setter, que valida
        # A conversa começa com a instrução de sistema do especialista.
        self._historico.adicionar(Mensagem("sistema", self.prompt_sistema()))

    @property
    def temperatura(self) -> float:
        return self.__temperatura

    @temperatura.setter
    def temperatura(self, valor: float) -> None:
        if not (0.0 <= valor <= 2.0):
            raise ValueError("temperatura deve estar entre 0.0 e 2.0")
        self.__temperatura = valor

    @property
    def nome(self) -> str:
        return type(self).NOME

    @abstractmethod
    def prompt_sistema(self) -> str:
        """Instrução de sistema que define a especialidade do agente."""

    def responder(self, pergunta: str) -> str:
        """Registra a pergunta, consulta o provedor e guarda a resposta."""
        self._historico.adicionar(Mensagem("usuario", pergunta))
        resposta = self._provedor.gerar(
            self.prompt_sistema(),
            self._historico.para_api(),
            self.temperatura,
        )
        self._historico.adicionar(Mensagem("assistente", resposta))
        return resposta

    def __str__(self) -> str:
        return f"Agente especialista em {self.nome}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(temperatura={self.temperatura})"

    def __len__(self) -> int:
        # Quantas mensagens já há no histórico (inclui a de sistema).
        return len(self._historico)


class AgenteTecnologia(AgenteBase):
    NOME = "Tecnologia"

    def prompt_sistema(self) -> str:
        return (
            "Você é um especialista sênior em tecnologia e desenvolvimento de "
            "software. Responda em português, de forma técnica e objetiva, sobre "
            "programação, arquitetura, infraestrutura e ferramentas. Se a pergunta "
            "fugir do tema de tecnologia, diga que está fora da sua especialidade."
        )


class AgenteLGPD(AgenteBase):
    NOME = "Direito Digital / LGPD"

    def prompt_sistema(self) -> str:
        return (
            "Você é um especialista em direito digital e na Lei Geral de Proteção "
            "de Dados (LGPD - Lei 13.709/2018). Responda em português, de forma "
            "clara, citando os princípios e bases legais quando fizer sentido. "
            "Inclua sempre o aviso de que as respostas são informativas e não "
            "substituem a orientação de um advogado. Se a pergunta fugir do tema, "
            "diga que está fora da sua especialidade."
        )