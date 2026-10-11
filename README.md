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

git clone <YOUR\_PUBLIC\_GITHUB\_REPOSITORY\_URL>

cd lenny-growth-assistant

```



\### 2. Create and activate a virtual environment



On Windows:



```cmd

python -m venv venv

venv\\Scripts\\activate

```



\### 3. Install dependencies



Install the project's Python dependencies using its dependency file, if provided.



\### 4. Configure environment variables



Create a `.env` file using `.env.example` as a template. Configure the database connection and model settings as required by the application.



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



\## Testing



Automated tests and manual UI test instructions will be added under `tests/`.



Recommended checks include backend health, transcript retrieval, chat responses, source references, session isolation, database persistence, and error handling.



\## Limitations



\* Answer quality depends on the relevance of retrieved passages and the capabilities of the selected language model.

\* Local models may produce incomplete or inaccurate answers.

\* Source references identify retrieved transcript chunks; users should consult the original material when exact wording or attribution matters.

\* The application requires the configured local model service and database to be available.



\## Future Improvements



\* Improve retrieval quality and reranking.

\* Add automated tests for session isolation and persistence.

\* Add the Ship 30 for 30 writing skill and safe artifact generation.

\* Add Docker Compose deployment support.

\* Improve error handling, observability, and evaluation of generated answers.



\## Acknowledgements



Transcript dataset: \[Lenny's Newsletter Podcast Data](https://github.com/LennysNewsletter/lennys-newsletterpodcastdata)



This project was developed as a conversational AI assistant for exploring product and startup growth insights.
