# LLM com Python e LangChain

Projeto de estudo para aprender a usar a biblioteca **LangChain** e construir
pequenas ferramentas em cima de uma **LLM**, usando o **Claude** (da
Anthropic) e servindo tudo como uma **API REST** (FastAPI).

## O que é uma LLM?

**LLM** significa *Large Language Model* (Modelo de Linguagem Grande). É um
tipo de modelo de inteligência artificial treinado com uma quantidade enorme
de texto (livros, artigos, código, conversas, etc.), e que aprende, a partir
desse treinamento, a prever qual é a próxima palavra (ou "pedaço de palavra",
chamado *token*) mais provável dado um texto de entrada.

Na prática, é essa capacidade de "prever o próximo token" repetida várias
vezes que permite que a LLM:

- Responda perguntas em linguagem natural;
- Resuma, traduza ou reescreva textos;
- Gere código;
- Converse mantendo o contexto de uma conversa;
- Extraia informação de documentos (técnica usada neste projeto, veja RAG
  abaixo).

Exemplos de LLMs conhecidas: **GPT** (OpenAI, usado no ChatGPT), **Claude**
(Anthropic, usado neste projeto) e **Gemini** (Google).

Um conceito usado neste projeto é o de **RAG** (*Retrieval-Augmented
Generation*, ou "geração aumentada por recuperação"): em vez de a LLM
responder só com o que ela "decorou" durante o treinamento, o sistema busca
antes trechos relevantes em documentos próprios (no nosso caso, PDFs de
seguro de cartão de crédito) e entrega esses trechos como contexto para a
LLM, para que ela responda com base neles.

## Sobre este projeto

Os exemplos usam o **Claude** (da Anthropic) através do Claude Agent SDK. Na
prática isso significa que, se a máquina já tem o Claude Code instalado e
autenticado, não é preciso pagar nem configurar nenhuma chave de API para
rodar o projeto.

O projeto é servido como uma **API REST** (FastAPI), com quatro recursos —
um por caso de uso (ver "Endpoints da API" abaixo).

## Como rodar

Para começar, crie o ambiente virtual do Python com o comando:

```
python3 -m venv venv
```

em seguida, entre no ambiente virtual:

```
source ./venv/bin/activate
```

por fim, instale as dependências usando o pip:

```
pip install -r requirements.txt
```

## Modelo: Claude Agent SDK (sem chave de API)

Este projeto usa `claude_agent_sdk` para chamar o Claude Code local, em vez
de uma chave de API. Basta ter o Claude Code (`claude`) instalado e
autenticado (`claude login`) na máquina.

Configure no `.env`:

```
CLAUDE_MODEL=claude-sonnet-5
CLAUDE_EFFORT=medium
INSURANCE_PDF_PATHS=documentos/GTB_standard_Nov23.pdf,documentos/GTB_gold_Nov23.pdf,documentos/GTB_platinum_Nov23.pdf
```

`INSURANCE_PDF_PATHS` é opcional — usa por padrão os três PDFs de exemplo
acima.

## Rodando a API

Na raiz do repositório (para que os caminhos do `.env` e dos
`documentos/*.pdf` sejam resolvidos corretamente):

```
uvicorn app.api.main:app --reload --port 8000 --workers 1
```

Documentação interativa (Swagger UI): `http://127.0.0.1:8000/docs`.

`--workers 1` é importante: as sessões de chat ficam guardadas em memória no
processo em execução, então mais de um worker (ou um restart) faz com que
sessões criadas em um worker não apareçam em outro, ou sejam perdidas.

## Endpoints da API (prefixo `/api/v1`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/trip-suggestions` | Sugere uma cidade, restaurantes e atividades culturais para um interesse informado |
| POST | `/chat-sessions` | Cria uma nova sessão de chat de viagem (retorna `session_id`) |
| POST | `/chat-sessions/{id}/messages` | Envia uma mensagem para a sessão de chat, retorna a resposta da IA |
| GET | `/chat-sessions/{id}/messages` | Retorna o histórico da conversa de uma sessão |
| POST | `/travel-advice` | Roteia a pergunta para um consultor de praia ou de montanha e retorna a resposta |
| POST | `/insurance-queries` | RAG: responde uma pergunta com base nos PDFs de seguro de cartão de crédito |
| GET | `/health` | Health check |

## Arquitetura do código

O código fica organizado em camadas dentro de `app/`, inspiradas em Clean
Architecture / DDD — cada camada só conhece a de baixo, nunca o contrário:

- `app/domain/` — os conceitos de negócio, sem depender de LangChain nem de
  IA nenhuma: o que é um `Destination`, uma `Route`, etc. (`travel.py`).
- `app/application/` — os casos de uso, um arquivo por recurso
  (`trip_suggestion.py`, `travel_chat.py`, `travel_advisor.py`,
  `insurance_query.py`), cada um montando os prompts e a cadeia daquele
  fluxo.
- `app/infrastructure/` — os detalhes técnicos que poderiam ser trocados sem
  mexer no resto: o adaptador do Claude Agent SDK (`claude_chat_model.py`) e
  a busca vetorial em PDFs (`vector_store.py`).
- `app/config.py` — leitura das variáveis de ambiente (`.env`).
- `app/api/` — a interface REST: app FastAPI, rotas, schemas de
  request/response e a montagem das dependências. É a única camada que
  conhece HTTP; ela só conecta os casos de uso acima e nunca contém regra de
  negócio.

Essa separação segue boas práticas de Clean Code: cada arquivo tem uma
responsabilidade só, sem duplicar a leitura do `.env` ou a criação do
modelo, e trocar de fornecedor de IA ou de banco vetorial no futuro exigiria
mexer só na camada de infraestrutura.
