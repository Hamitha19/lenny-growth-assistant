\# Manual Test Plan â€” Lenny Growth Assistant



\## Test Environment



\* Backend: FastAPI

\* Frontend: HTML, CSS, JavaScript

\* Language model: Ollama with Llama 3.2

\* Embedding model: Nomic Embed Text

\* Vector database: ChromaDB

\* Relational database: PostgreSQL / Supabase



\## Test Cases



| ID    | Test                                                           | Expected Result                                                              |

| ----- | -------------------------------------------------------------- | ---------------------------------------------------------------------------- |

| TC-01 | Open the home endpoint                                         | HTTP 200 response                                                            |

| TC-02 | Open `/health`                                                 | Status is `ok` and index count is returned                                   |

| TC-03 | Ask a question about product-market fit                        | A relevant answer is returned                                                |

| TC-04 | Inspect the answer's sources                                   | Source filenames and chunk references are returned                           |

| TC-05 | Ask a follow-up question in the same session                   | The conversation continues using the session ID                              |

| TC-06 | Start a new conversation                                       | A new session is created                                                     |

| TC-07 | Ask a question not supported by retrieved passages             | The assistant acknowledges insufficient evidence rather than inventing facts |

| TC-08 | Refresh or restart the backend and inspect stored chat records | Previously saved records remain available in the database                    |

| TC-09 | Open the frontend in a browser                                 | Chat interface loads and accepts user input                                  |



\## Automated Tests



Run:



```cmd

python -m pytest tests\\test\_health.py -v

```



The home and health endpoint tests passed during development.



\## Execution Notes



Record the actual result of each manual test before submission. Do not mark a test as passed until it has been performed.
