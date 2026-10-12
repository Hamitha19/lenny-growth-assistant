\# Design Document



\## Lenny Growth Assistant



\### 1. Design Goals



The interface should make it easy for users to ask product and growth questions, review answers, continue conversations, and generate essay drafts. The design prioritizes clarity, usability, and a straightforward local demonstration.



\### 2. Main User Workflows



\*\*Conversational assistant\*\*



1\. The user opens the web interface.

2\. The user enters a question about product management or growth.

3\. The frontend sends the question and, when available, the session ID to the FastAPI backend.

4\. The backend retrieves relevant transcript passages and generates a response.

5\. The frontend displays the answer so the user can continue the conversation.



\*\*Essay writer\*\*



1\. The user opens the Ship 30 for 30 Essay Writer section.

2\. The user requests an essay on a topic.

3\. The backend prepares a writing prompt using relevant source material.

4\. The configured local model generates the draft.

5\. The interface displays the generated essay for review.



\### 3. Interface Structure



The web interface provides:



\* A conversational area for entering questions and reading responses.

\* A session-aware interaction flow.

\* A dedicated essay-writing section and an Artifact Viewer beside chat.

\* A clear indication of generated content and the model used, where available.

\* Error feedback when a request cannot be completed.



The interface should avoid unnecessary complexity and keep the main actions easy to find.



\### 4. Backend API Design



The FastAPI backend exposes endpoints for the main application workflows.



\* `GET /` — basic application welcome response.

\* `GET /health` — application health and index status.

\* `POST /chat` — submit a conversational question with an optional session ID.

\* `POST /write` — generate a source-informed essay draft.
\* `POST /artifact` — generate Markdown or HTML/CSS for the Artifact Viewer.



Request and response payloads should be documented in the README or API documentation. The application should return appropriate error responses when model or database operations fail.



\### 5. Retrieval and Answer Quality



The assistant indexes Lenny transcript documents into chunks and stores their embeddings in a vector database. For a user question, it retrieves potentially relevant chunks and includes them in the generation prompt.



Answers should distinguish source-supported information from uncertainty. When relevant evidence is unavailable, the assistant should acknowledge the limitation rather than inventing a source or claiming certainty.



\### 6. Visual and Interaction Principles



\* Use readable typography and clear content hierarchy.

\* Separate question input from generated responses.

\* Present essays with headings and paragraphs for readability.

\* Keep loading and error states understandable.

\* Preserve conversation context when a session is continued.

\* Avoid presenting generated claims as verified facts without supporting evidence.



\### 7. Security and Content Handling



User messages and generated responses should be treated as untrusted content. If HTML artifact rendering is introduced, it should be isolated from the main application, preferably in a sandboxed iframe with restrictive permissions. Avoid directly inserting untrusted HTML into the application's DOM.



Markdown artifacts are displayed as text; HTML/CSS previews run in an iframe with `sandbox=""`. Generated HTML is not inserted into the main page DOM. Automated tests verify the sandbox configuration, but a browser smoke test remains part of the manual test plan.



\### 8. Accessibility and Limitations



Controls should have understandable labels and sufficient visual contrast. The prototype has not been established as fully accessibility-audited. Model quality, inference speed, retrieval relevance, and external database availability may affect the experience.



\### 9. Future Improvements




\* Improve source citations and source inspection.


\* Expand automated tests for retrieval, session persistence, and API failures.

\* Improve loading indicators and recovery from timeouts.



