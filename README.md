# Agente-IA 🤖👨‍💻

## 📌 Sobre o projeto
 
Este é um trabalho em grupo da disciplina de Laboratório de Programação. A turma
ficou responsável por criar **agentes de IA**, e cada integrante desenvolve um
agente especializado em uma ou mais áreas de conhecimento.
 
Eu fiquei responsável pelo agente especialista em **Tecnologia** e em **Direito
Digital / LGPD**. O usuário escolhe o nicho, conversa pelo terminal, e o agente
responde sempre dentro do contexto daquela especialidade.

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

  ## 🧠 Conceitos de POO aplicados

| **Abstração** |
| **Herança**  |
| **Polimorfismo** |
| **Encapsulamento** |
| **`@property`** com validação |
| **Herança múltipla + MRO** |
| **Dunder methods** |

  ## 📁 Estrutura do projeto
 
agente_ia/
├── dominio.py        # Mensagem + Conversa  (todos os dunder methods)
├── provedores.py     # ProvedorLLM (ABC) + ProvedorGroq + ProvedorFake
├── agentes.py        # AgenteBase (ABC) + mixins + AgenteTecnologia + AgenteLGPD
├── main.py           # CLI: menu de nicho + loop de conversa
├── test_agente.py    # testes pytest
├── .env.example      # GROQ_API_KEY=
├── requirements.txt
└── README.md

## 🧰 Desenvolvimento assistido por IA
 
O projeto foi desenvolvido com apoio do **Claude Code**, seguindo a filosofia do
trabalho: a IA acelera, mas **não decide sozinha**. O fluxo foi:
 
1. Desenhar a arquitetura e os contratos das classes **antes** de codar.
2. Gerar a implementação a partir dessa especificação.
3. **Revisar e validar** cada arquivo, entendendo o porquê de cada decisão.
4. Testar, identificar e corrigir bugs.


