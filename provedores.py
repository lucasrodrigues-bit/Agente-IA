"""Provedores de modelo de linguagem.

Esta é a espinha dorsal de POO do projeto:

- `ProvedorLLM` é a **abstração** (classe abstrata com um método abstrato).
- `ProvedorGroq` e `ProvedorFake` são duas implementações concretas
  (**herança** + **polimorfismo**): o agente fala com qualquer uma sem saber
  qual é, porque ambas respeitam o mesmo contrato `gerar(...)`.
- `RegistradorMixin` + `ProvedorGroqAuditado` introduzem **herança múltipla**
  de forma honesta: registrar (auditar) cada acesso ao modelo é uma
  necessidade real do domínio de LGPD, não um enfeite para "demonstrar MRO".

O SDK do Groq é importado de forma preguiçosa (só quando `ProvedorGroq` é
realmente usado), para que os testes e o modo offline rodem sem a dependência
instalada.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import datetime


class ErroDoProvedor(Exception):
    """Erro amigável quando não dá para obter a resposta do provedor online.

    Cobre os casos que o usuário pode enfrentar no dia a dia: chave inválida,
    limite de requisições (429) e falha de conexão. A CLI captura este erro e
    mostra a mensagem em vez de quebrar com um traceback.
    """


class ProvedorLLM(ABC):
    """Contrato que todo provedor de modelo precisa cumprir."""

    @abstractmethod
    def gerar(self, prompt_sistema: str, mensagens: list[dict], temperatura: float) -> str:
        """Recebe o prompt de sistema + histórico (formato da API) e devolve a
        resposta do assistente como texto."""


class ProvedorFake(ProvedorLLM):
    """Provedor offline e determinístico — não usa rede.

    Serve para rodar os testes e para a demonstração sem internet. A resposta
    é função pura da entrada (mesma entrada → mesma saída), por isso é segura
    para asserts em testes. Demonstra polimorfismo: mesma interface do
    `ProvedorGroq`, comportamento diferente.
    """

    def gerar(self, prompt_sistema: str, mensagens: list[dict], temperatura: float) -> str:
        # Identifica o nicho a partir do prompt de sistema, sem aleatoriedade.
        nicho = "LGPD" if "lgpd" in prompt_sistema.lower() else "Tecnologia"

        # Pega a última fala do usuário (se houver) para ecoar.
        ultima_pergunta = ""
        for mensagem in reversed(mensagens):
            if mensagem.get("role") == "user":
                ultima_pergunta = mensagem.get("content", "")
                break

        return (
            f"[Modo offline | especialista em {nicho}] "
            f"Você perguntou: '{ultima_pergunta}'. "
            "Esta é uma resposta simulada (sem internet)."
        )


class ProvedorGroq(ProvedorLLM):
    """Provedor online e gratuito, usando o SDK do Groq (modelos Llama).

    A chave de API fica em `__api_key` (privado, **encapsulamento** real via
    name mangling) e o cliente em `__cliente`. O modelo fica em `_modelo`
    (protegido) e é exposto só para leitura via `@property modelo`.
    """

    def __init__(self, modelo: str = "llama-3.3-70b-versatile", api_key: str | None = None) -> None:
        try:
            from groq import Groq
        except ImportError as erro:  # pragma: no cover - depende do ambiente
            raise ErroDoProvedor(
                "O pacote 'groq' não está instalado. Rode: pip install groq"
            ) from erro

        chave = api_key if api_key is not None else os.environ.get("GROQ_API_KEY")
        if not chave:
            raise ErroDoProvedor(
                "GROQ_API_KEY não encontrada. Configure o .env ou use o modo offline."
            )

        self.__api_key = chave
        self.__cliente = Groq(api_key=self.__api_key)
        self._modelo = modelo

    @property
    def modelo(self) -> str:
        """Modelo em uso (somente leitura)."""
        return self._modelo

    def gerar(self, prompt_sistema: str, mensagens: list[dict], temperatura: float) -> str:
        import groq

        messages = [{"role": "system", "content": prompt_sistema}] + mensagens
        try:
            resposta = self.__cliente.chat.completions.create(
                model=self._modelo,
                messages=messages,
                temperature=temperatura,
            )
        except groq.AuthenticationError as erro:
            raise ErroDoProvedor(
                "Chave da API do Groq inválida ou expirada. Confira a GROQ_API_KEY no .env."
            ) from erro
        except groq.RateLimitError as erro:
            raise ErroDoProvedor(
                "Limite de requisições do Groq atingido (429). Aguarde um pouco e tente de novo."
            ) from erro
        except groq.APIConnectionError as erro:
            raise ErroDoProvedor(
                "Não foi possível conectar ao Groq. Verifique sua internet."
            ) from erro
        except groq.APIError as erro:
            # Rede para qualquer outro erro vindo da API (modelo inválido, etc.).
            raise ErroDoProvedor(f"Erro do Groq: {erro}") from erro
        return resposta.choices[0].message.content


class RegistradorMixin:
    """Mixin que audita cada acesso ao modelo (trilha para LGPD).

    Registra apenas **metadados** da chamada (quando, quantas mensagens, qual
    temperatura) — nunca o conteúdo, justamente para respeitar a privacidade
    dos dados tratados. É um mixin de verdade: agrega um comportamento
    ortogonal (auditoria) a qualquer `ProvedorLLM`.

    Coopera na cadeia de herança via `super()`: por isso funciona combinado
    com qualquer provedor, e é o que faz o MRO importar de fato.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._registros: list[str] = []
        # Encadeia para o próximo da MRO (o provedor concreto).
        super().__init__(*args, **kwargs)

    def gerar(self, prompt_sistema: str, mensagens: list[dict], temperatura: float) -> str:
        carimbo = datetime.now().isoformat(timespec="seconds")
        self._registros.append(
            f"{carimbo} | acesso ao modelo | {len(mensagens)} mensagens | temp={temperatura}"
        )
        # Delega a geração de fato para o provedor abaixo na MRO.
        return super().gerar(prompt_sistema, mensagens, temperatura)

    @property
    def registros(self) -> list[str]:
        """Trilha de auditoria acumulada (somente leitura)."""
        return list(self._registros)


class ProvedorGroqAuditado(RegistradorMixin, ProvedorGroq):
    """Groq com trilha de auditoria — herança múltipla + MRO.

    MRO: ProvedorGroqAuditado -> RegistradorMixin -> ProvedorGroq -> ProvedorLLM
    -> ABC -> object. Ao chamar `gerar`, o `RegistradorMixin` registra e então
    `super().gerar(...)` cai no `ProvedorGroq`, que fala com a API.
    """