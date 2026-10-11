\# Architecture Document



\## Lenny Growth Assistant



\### 1. Overview



Lenny Growth Assistant is a web application that combines a frontend, a FastAPI backend, a local language model, a vector database, and PostgreSQL persistence. It supports conversational questions about product and growth topics and a separate essay-generation workflow.



\### 2. High-Level Architecture



The main components are:



1\. \*\*Frontend:\*\* HTML, CSS, and JavaScript provide the user interface for chat and essay generation.

2\. \*\*FastAPI backend:\*\* Validates incoming requests, coordinates retrieval and generation, manages session workflows, and returns responses.

3\. \*\*Pi Coding Agent integration:\*\* The chat workflow invokes the configured Pi command-line agent, which uses the available local model.

4\. \*\*Ollama:\*\* Runs the local `llama3.2:3b` generation model and `nomic-embed-text` embedding model.

5\. \*\*Chroma vector database:\*\* Stores embedded transcript chunks and supports similarity-based retrieval.

6\. \*\*PostgreSQL via Supabase:\*\* Persists chat sessions and messages.

7\. \*\*Transcript dataset:\*\* Supplies the Lenny podcast and newsletter content used to build the searchable knowledge base.



\### 3. Request and Data Flow



\*\*Chat workflow\*\*



1\. The frontend sends a question and optional session ID to `POST /chat`.

2\. FastAPI processes the request and retrieves relevant transcript chunks from Chroma.

3\. The backend prepares a prompt containing the question and retrieved context.

4\. The chat agent generates a response using the configured local model.

5\. The backend returns the response and associated session information.

6\. Conversation data is persisted in PostgreSQL according to the application's database workflow.



\*\*Essay workflow\*\*



1\. The frontend sends an essay-generation request to `POST /write`.

2\. The backend retrieves or prepares relevant source context.

3\. It constructs a structured essay-writing prompt.

4\. The backend calls Ollama's local generation API.

5\. The generated essay is returned to the frontend.



\*\*Indexing workflow\*\*



1\. Transcript Markdown files are read from the dataset.

2\. Documents are split into manageable chunks.

3\. The embedding model converts chunks into vectors.

4\. Chunks and their vectors are stored in the Chroma collection `lenny\_sources`.



The current index contains approximately 4,995 chunks prepared from 60 transcript files.



\### 4. Technology Choices



| Component           | Technology            | Purpose                         |

| ------------------- | --------------------- | ------------------------------- |

| Frontend            | HTML, CSS, JavaScript | User interaction                |

| API                 | FastAPI               | Request handling                |

| Chat agent          | Pi Coding Agent       | Chat generation workflow        |

| Local inference     | Ollama                | Local language-model inference  |

| Generation model    | `llama3.2:3b`         | Responses and essays            |

| Embedding model     | `nomic-embed-text`    | Transcript embeddings           |

| Vector store        | Chroma                | Semantic retrieval              |

| Relational database | PostgreSQL / Supabase | Session and message persistence |

| Tests               | pytest                | Automated checks                |



\### 5. Configuration and Startup



The application uses environment variables for configuration, including the database connection and agent settings. Local model dependencies must be installed and running before the corresponding workflows can operate.



The README should document prerequisites, setup, model downloads, environment variables, indexing, backend startup, frontend startup, and test execution. Secrets must remain in `.env` and must not be committed to version control.



\### 6. Reliability and Error Handling



Potential failure points include:



\* Ollama not running or a required model missing.

\* Agent process errors or timeouts.

\* Empty or irrelevant retrieval results.

\* Database connection failures.

\* Invalid requests or malformed responses.



The application should report meaningful errors, use sensible timeouts, and log enough information to troubleshoot failures without exposing credentials. Health checks and automated tests provide basic verification, but do not guarantee every dependency is healthy.



\### 7. Security Considerations



\* Do not commit `.env` or credentials.

\* Avoid logging secrets or complete sensitive connection strings.

\* Validate request data and handle errors safely.

\* Treat retrieved documents and model output as untrusted content.

\* Isolate any future generated HTML preview from the main application.



\### 8. Trade-offs and Limitations



Local inference reduces dependence on paid APIs but can be slower and may generate lower-quality answers than larger hosted models. Retrieval quality depends on the dataset, chunking, embeddings, and query relevance. The current test suite is limited and requires expansion.



A cloud-provider selector and automatic fallback should be considered unimplemented unless they are present in the code and verified through testing. Similarly, a dedicated isolated Artifact Viewer should not be considered complete until implemented and tested.



\### 9. Future Improvements



\* Add and test cloud/local model-provider selection and fallback.

\* Improve retrieval evaluation and source attribution.

\* Expand tests for API errors, retrieval, persistence, and session isolation.

\* Add structured observability for model, retrieval, and database operations.

\* Provide an isolated Artifact Viewer for generated HTML/CSS.

\* Simplify fresh-clone setup and consider Docker Compose for reproducible startup.





