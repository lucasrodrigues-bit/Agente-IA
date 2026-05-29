# Agente-IA 🤖👨‍💻

## 📌 Sobre o projeto
 
Este é um trabalho em grupo da disciplina de Laboratório de Programação. A turma
ficou responsável por criar **agentes de IA**, e cada integrante desenvolve um
agente especializado em uma ou mais áreas de conhecimento.
 
Eu fiquei responsável pelo agente especialista em **Tecnologia** e em **Direito
Digital / LGPD**. É um **único agente** que responde aos dois assuntos na mesma
conversa pelo terminal — sem o usuário precisar escolher o nicho.

## 🎯 Objetivo
 
O foco do projeto é duplo:
 
1. **Aplicar na prática os conceitos de POO** que estamos vendo nas aulas —
   não de forma decorativa, mas onde cada pilar resolve um problema real do
   código.
2. **Usar IA da melhor maneira e com boas práticas** durante o desenvolvimento:
   validando tudo que é gerado, entendendo cada decisão de arquitetura e
   corrigindo bugs — em vez de aceitar código cego.

   ## 🛠️ Stack e tecnologias
 
- **Python 3.10+** — linguagem do projeto.
- **Groq (SDK `groq`)** — provedor do modelo de linguagem, no plano gratuito.
- **Modelo do agente:** **Llama 3.3 70B** (`llama-3.3-70b-versatile`) via Groq.
- **`python-dotenv`** — carregamento da chave de API a partir do `.env`.
- **`pytest`** — testes automatizados (rodam offline, sem consumir a API).
- **Claude Code (Anthropic)** — IA usada como apoio no desenvolvimento, sempre
  com revisão e validação humana do que é gerado.

# 🎼 Orquestração com o BMAD Method
 
O coração do processo de desenvolvimento deste projeto é o **BMAD Method**
(*Breakthrough Method of Agile AI-Driven Development*) — um framework que troca o
prompting solto por um **fluxo orquestrado**, como uma orquestra em vez de uma
jam improvisada.
 
Em vez de um único assistente de código, a BMAD simula um **time de
desenvolvimento** com agentes especializados, e um **orquestrador** que coordena
todos eles:
 
| Agente da BMAD | Papel no projeto |
|---|---|
| 🔍 **Analista** | Clareia o escopo: que agente de IA construir e por quê. |
| 📋 **Product Manager** | Organiza os requisitos (nichos, conceitos de POO exigidos). |
| 🏛️ **Arquiteto** | Define a modelagem das classes e os contratos — gera a especificação. |
| 💻 **Dev** | Implementa cada módulo a partir da especificação. |
| ✅ **QA** | Revisa o código gerado, roda os testes e aponta correções. |
 
**O que o orquestrador garante:**
 
- **Handoffs claros** — cada etapa entrega um artefato pronto para a próxima
  (ex.: o arquiteto produz a especificação que o dev implementa).
- **Memória de contexto** — as decisões tomadas no planejamento continuam
  valendo na implementação, mantendo a integridade da arquitetura do começo ao
  fim.
- **Disciplina antes do código** — nada é codado sem planejamento, o que evita o
  "vibe coding" e mantém o projeto sob controle.
A BMAD roda **integrada ao Claude Code**, que executa a parte de implementação
dentro desse fluxo orquestrado.
 


  ## 🧠 Conceitos de POO aplicados

Cada pilar aparece porque resolve um problema real do código — não de forma
decorativa. A tabela abaixo mostra **onde** cada conceito está, para facilitar a
correção:

| Conceito | Onde aparece (arquivo · classe / método) |
|---|---|
| **Abstração** | `provedores.py` · `ProvedorLLM(ABC)` e `agentes.py` · `AgenteBase(ABC)`, com `@abstractmethod` |
| **Herança + `super()`** | `agentes.py` · `AgenteTecnologia`, `AgenteLGPD` e `AgenteGeral` estendem `AgenteBase` |
| **Polimorfismo** | `prompt_sistema()` com 3 implementações; e `ProvedorGroq` vs `ProvedorFake` |
| **Composição** | `agentes.py` · `AgenteGeral` reúne os especialistas reaproveitando o `prompt_sistema()` deles |
| **Encapsulamento** | `provedores.py` · `__api_key` (privado); `agentes.py` · `_historico` e `__temperatura` |
| **`@property` com validação** | `agentes.py` · `AgenteBase.temperatura` (faixa 0.0–2.0, levanta `ValueError`) |
| **Herança múltipla + MRO** | `provedores.py` · `ProvedorGroqAuditado(RegistradorMixin, ProvedorGroq)` (auditoria LGPD) |
| **Dunder methods** | `dominio.py` · `Mensagem` e `Conversa` (`__len__`, `__iter__`, `__str__`, `__repr__`, ...) |

  ## 📁 Estrutura do projeto
 
.
├── dominio.py        # Mensagem + Conversa  (dunder methods)
├── provedores.py     # ProvedorLLM (ABC) + ProvedorGroq + ProvedorFake + ProvedorGroqAuditado (MRO)
├── agentes.py        # AgenteBase (ABC) + AgenteTecnologia + AgenteLGPD + AgenteGeral
├── main.py           # CLI: agente único (Tecnologia + LGPD) + loop de conversa
├── test_agente.py    # testes pytest (rodam offline, sem rede)
├── requirements.txt
├── .gitignore
└── README.md

## ▶️ Como rodar

```bash
pip install -r requirements.txt
# crie um arquivo .env na raiz com a sua chave gratuita do Groq:
#   GROQ_API_KEY=gsk_sua_chave_aqui
python main.py
```

Sem a `GROQ_API_KEY`, o agente roda em **modo offline** (provedor falso,
determinístico) — útil para a demonstração sem internet e para os testes.
Rodar os testes: `pytest -q`.

## 🧰 Desenvolvimento assistido por IA
 
O projeto foi desenvolvido com apoio do **Claude Code**, seguindo a filosofia do
trabalho: a IA acelera, mas **não decide sozinha**. O fluxo foi:
 
1. Desenhar a arquitetura e os contratos das classes **antes** de codar.
2. Gerar a implementação a partir dessa especificação.
3. **Revisar e validar** cada arquivo, entendendo o porquê de cada decisão.
4. Testar, identificar e corrigir bugs.


