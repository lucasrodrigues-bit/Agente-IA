"""Domínio da conversa: as classes de valor que o agente manipula.

Aqui moram os *dunder methods* que fazem sentido de verdade para o problema:
- `Mensagem` representa uma fala (papel + conteúdo) e sabe se converter para o
  formato que a API de modelos espera.
- `Conversa` é uma coleção de mensagens; por isso ela se comporta como uma
  coleção (itera, tem tamanho) sem que o resto do código precise mexer na lista
  interna.
"""

from __future__ import annotations

from datetime import datetime


# Mapeia os papéis em português para os nomes que a API (Groq/OpenAI) espera.
_PAPEIS_API = {
    "sistema": "system",
    "usuario": "user",
    "assistente": "assistant",
}


class Mensagem:
    """Uma única fala da conversa.

    É um objeto de valor: guarda quem falou (`papel`), o que foi dito
    (`conteudo`) e quando (`criada_em`). O `criada_em` é injetável no
    construtor para que os testes não dependam do relógio do sistema.
    """

    def __init__(self, papel: str, conteudo: str, criada_em: datetime | None = None) -> None:
        if papel not in _PAPEIS_API:
            raise ValueError(
                f"papel inválido: {papel!r} (use um de {list(_PAPEIS_API)})"
            )
        self.papel = papel
        self.conteudo = conteudo
        self.criada_em = criada_em if criada_em is not None else datetime.now()

    def __repr__(self) -> str:
        return f"Mensagem(papel={self.papel!r}, conteudo={self.conteudo!r})"

    def __str__(self) -> str:
        return f"[{self.papel}] {self.conteudo}"

    def para_dict(self) -> dict:
        """Converte para o formato da API: {"role": ..., "content": ...}."""
        return {"role": _PAPEIS_API[self.papel], "content": self.conteudo}


class Conversa:
    """Coleção de `Mensagem`.

    Comporta-se como uma coleção (é iterável e tem tamanho), porque é
    exatamente isso que o agente faz com ela: percorre o histórico e mede
    quantas mensagens já foram trocadas. A lista interna (`_mensagens`) é
    protegida — ninguém de fora mexe nela diretamente.
    """

    def __init__(self, mensagens: list[Mensagem] | None = None) -> None:
        self._mensagens: list[Mensagem] = list(mensagens) if mensagens else []

    def adicionar(self, mensagem: Mensagem) -> None:
        self._mensagens.append(mensagem)

    def __len__(self) -> int:
        return len(self._mensagens)

    def __iter__(self):
        return iter(self._mensagens)

    def __repr__(self) -> str:
        return f"Conversa({len(self)} mensagens)"

    def __str__(self) -> str:
        # Transcrição: uma mensagem por linha, reaproveitando o __str__ da Mensagem.
        return "\n".join(str(m) for m in self._mensagens)

    def para_api(self) -> list[dict]:
        """Histórico no formato que o provedor envia ao modelo."""
        return [m.para_dict() for m in self._mensagens]