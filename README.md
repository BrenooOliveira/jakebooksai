# JakeBooks AI

Frontend inicial em Streamlit para a futura arquitetura:

`Front -> Backend -> RAG consultando banco de dados -> Gemini com API gateway`

Neste momento o projeto entrega apenas a camada de interface. O backend ainda não foi conectado, então a app sobe como uma casca visual pronta para evoluir.

Agora o chat já consulta um RAG real em Postgres para recomendar livros com base no histórico geral de pedidos, mantendo a separação de camadas para migrar depois para o backend HTTP.

## Estrutura inicial

- `main.py`: launcher do app.
- `src/jakebooksai/app.py`: composição principal da interface Streamlit.
- `src/jakebooksai/config/`: leitura de configurações locais.
- `src/jakebooksai/state/`: estado da sessão do chat.
- `src/jakebooksai/ui/`: componentes e estilos reutilizáveis.
- `src/jakebooksai/services/`: contratos e módulo de chat (controller + gateway Gemini + RAG Postgres + fallback stub).

## Como rodar

```bash
uv sync
uv run streamlit run main.py
```

## Variáveis de ambiente

O frontend já aceita valores opcionais para personalização da UI e preparação para a integração futura:

- `JAKEBOOKS_APP_NAME`
- `JAKEBOOKS_APP_TAGLINE`
- `JAKEBOOKS_BACKEND_URL`
- `JAKEBOOKS_DEFAULT_MODEL`
- `GOOGLE_API_KEY`
- `JAKEBOOKS_GEMINI_TEMPERATURE`

Para a recuperação em banco, configure também as variáveis abaixo. Os defaults seguem o padrão do seu backend Java:

- `DB_HOST` (padrão: `localhost`)
- `DB_PORT` (padrão: `5432`)
- `DB_NAME` (padrão: `jakebooks`)
- `DB_USER` (padrão: `postgres`)
- `DB_PASSWORD` (padrão: `postgres`)

O gateway de RAG usa esses valores para consultar livros, autores, categorias e itens de pedido, e então devolve ao chat uma lista curta de recomendações com base no histórico geral de compras.

Por padrão, o frontend usa `gemini-2.5-flash-lite`, deixando a escolha de um modelo mais caro como override via `JAKEBOOKS_DEFAULT_MODEL`.

## Próxima fase

Quando o backend existir, a UI vai consumir uma camada de serviço isolada, sem precisar reestruturar a tela principal.
