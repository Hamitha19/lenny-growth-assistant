\# Lenny Growth Assistant



An AI-powered conversational assistant that helps users explore product management, startup growth, and product-market fit insights from Lenny's Podcast and Newsletter transcripts.



\## Features



\* \*\*Transcript-based Q\&A:\*\* Answers questions using retrieved podcast and newsletter content.

\* \*\*Retrieval-Augmented Generation (RAG):\*\* Uses vector search to find relevant transcript passages before generating answers.

\* \*\*Local AI models:\*\* Uses Ollama with Llama 3.2 for answer generation and Nomic Embed Text for embeddings.

\* \*\*Source references:\*\* Returns transcript filenames and chunk references to help users identify supporting material.

\* \*\*Conversation sessions:\*\* Supports separate chat sessions and follow-up questions.

\* \*\*Persistent storage:\*\* Uses PostgreSQL through Supabase to store chat sessions and messages.

\* \*\*Web interface:\*\* Provides a browser-based chat UI.

\* \*\*FastAPI backend:\*\* Exposes API endpoints for health checks and chat requests.
\* \*\*Configurable generation provider:\*\* Uses local Ollama by default, with optional OpenAI generation through an environment variable.
\* \*\*Artifact workflow:\*\* Generates Markdown or HTML/CSS artifacts; HTML previews run in a sandboxed iframe.



\## Technology Stack



\* Python 3.11

\* FastAPI

\* Ollama

\* Llama 3.2

\* Nomic Embed Text

\* ChromaDB

\* PostgreSQL / Supabase

\* HTML, CSS, and JavaScript

\* Pi Coding Agent CLI



\## Architecture



1\. Podcast and newsletter Markdown files are loaded from the transcript dataset.

2\. The indexing script splits the documents into chunks.

3\. Nomic Embed Text generates embeddings, which are stored in ChromaDB.

4\. A user submits a question through the web interface.

5\. The backend embeds the question and retrieves relevant transcript chunks.

6\. The local language model generates a response using the retrieved context.

7\. The API returns the answer and source references.

8\. Conversation messages are stored in PostgreSQL.



\## Project Structure



```text

lenny-growth-assistant/

â”œâ”€â”€ backend/

â”‚   â”œâ”€â”€ main.py

â”‚   â”œâ”€â”€ index\_transcripts.py

â”‚   â””â”€â”€ ...

â”œâ”€â”€ data/

â”‚   â”œâ”€â”€ transcripts/

â”‚   â””â”€â”€ vector\_db/

â”œâ”€â”€ docs/

â”œâ”€â”€ frontend/

â”‚   â””â”€â”€ index.html

â”œâ”€â”€ tests/

â”œâ”€â”€ agent\_logs/

â”œâ”€â”€ .env.example

â”œâ”€â”€ .gitignore

â””â”€â”€ README.md

```



\## Prerequisites



\* Python 3.11

\* Node.js and npm

\* Ollama

\* A PostgreSQL database, such as Supabase



\## Setup



\### 1. Clone the repository



```bash

git clone https://github.com/Hamitha19/lenny-growth-assistant.git

cd lenny-growth-assistant

```



\### 2. Create and activate a virtual environment



On Windows:



```cmd

python -m venv venv

venv\\Scripts\\activate

```



\### 3. Install dependencies



Install the project's Python dependencies by running:
pip install -r requirements.txt


\### 4. Configure environment variables



Create a `.env` file using `.env.example` as a template. Set `DATABASE_URL` for PostgreSQL/Supabase. `MODEL_PROVIDER=ollama` is the default and requires no paid API credentials. Set `CHAT_MODEL`, `EMBED_MODEL`, and `OLLAMA_BASE_URL` to override the defaults.

To opt into OpenAI for text generation, set `MODEL_PROVIDER=openai`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL`. Never put a real key in `.env.example` or commit `.env`. Embeddings and transcript retrieval still require a running Ollama server with `nomic-embed-text`, even when OpenAI generates text. Provider errors are returned to the caller; there is no automatic fallback.



\*\*Never commit `.env` or database credentials to GitHub.\*\*



\### 5. Start Ollama



Install and start Ollama, then pull the required models:



```bash

ollama pull llama3.2:3b

ollama pull nomic-embed-text

```



Ensure Ollama is running before starting the application.



\### 6. Index the transcripts



After obtaining the transcript dataset, place it in the expected location and run:



```cmd

python backend\\index\_transcripts.py

```



\### 7. Initialize the database



Run the database initialization script if required by your setup:



```cmd

python backend\\init\_db.py

```



\### 8. Start the backend



```cmd

uvicorn backend.main:app --reload

```



Backend: `http://127.0.0.1:8000`



API documentation: `http://127.0.0.1:8000/docs`



Health check: `http://127.0.0.1:8000/health`



\### 9. Start the frontend



Open another terminal from the project directory and run:



```cmd

python -m http.server 5500 --directory frontend

```



Open `http://localhost:5500` in your browser.



\## API



\### Health Check



`GET /health`



Checks the backend and reports the indexed chunk count.



\### Chat



`POST /chat`



Example request:



```json

{

&#x20; "message": "What are some common ways startups can find product-market fit?"

}

```



The endpoint accepts an optional session identifier for continuing an existing conversation. The response includes a generated answer, source references, model information, and a session identifier.

`POST /write` generates a source-informed essay draft targeting approximately 1,250 words. The local Ollama generation limit remains 1,800 tokens, so the final length can vary.

`POST /artifact` accepts `{ "prompt": "...", "format": "markdown" }` or `{ "prompt": "...", "format": "html" }`. HTML/CSS is untrusted and displayed only in an iframe with an empty `sandbox` attribute; scripts and other iframe permissions are not enabled. The viewer displays Markdown as text rather than inserting generated markup into the main page.

`GET /health` reports the configured provider and model name as well as the indexed chunk count. It does not expose credentials or prove that the provider is reachable.



\## Testing



Automated endpoint tests are available in `tests/test_health.py`. Manual UI test instructions are documented in `docs/TEST_PLAN.md`.

Run the automated tests with:

```cmd
python -m pytest -v
```



Recommended checks include backend health, transcript retrieval, chat responses, source references, session isolation, database persistence, and error handling.



\## Troubleshooting

\* `DATABASE_URL is missing`: create `.env` from `.env.example` and set the PostgreSQL/Supabase connection string.
\* Ollama embedding errors: start Ollama, pull `nomic-embed-text`, and verify `OLLAMA_EMBED_URL`. This remains required when `MODEL_PROVIDER=openai`.
\* Pi startup errors in local chat mode: verify Node.js and the Pi Coding Agent CLI are installed at the paths configured in `backend/main.py`.
\* OpenAI returns a configuration error: set `MODEL_PROVIDER=openai` and `OPENAI_API_KEY` in `.env`; never place the key in source or `.env.example`.
\* Missing Chroma collection: run the transcript indexing script before starting the backend.
\* The backend emits diagnostics in its server console. Retrieval currently logs passage snippets, so avoid sharing those logs publicly.



\## Limitations



\* Answer quality depends on the relevance of retrieved passages and the capabilities of the selected language model.

\* Local models may produce incomplete or inaccurate answers.

\* Source references identify retrieved transcript chunks; users should consult the original material when exact wording or attribution matters.

\* The application requires the configured local model service and database to be available.



\## Future Improvements



\* Improve retrieval quality and reranking.

\* Add automated tests for session isolation and persistence.

\* Expand end-to-end coverage for provider network failures, session persistence, and browser rendering.

\* Add Docker Compose deployment support.

\* Improve error handling, observability, and evaluation of generated answers.



\## Acknowledgements



Transcript dataset: \[Lenny's Newsletter Podcast Data](https://github.com/LennysNewsletter/lennys-newsletterpodcastdata)

**📽️Project Demo Link
**
https://www.loom.com/share/d97d8b2a18784636a62b8703cbd8dbf6

This project was developed as a conversational AI assistant for exploring product and startup growth insights.
