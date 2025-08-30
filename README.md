# SDS Chatbot

## Overview

The project implements Retrieval-Augmented Generation (RAG) chatbot built with FastAPI, Qdrant vector store, Groq for llm access and Google Gemini embeddings. It supports document upload, text extraction, vector storage, and conversational querying.

---

## Quick Start (Docker Compose)

1. **Clone the repository**
   ```sh
   git clone https://github.com/GarimaPaudel/RAG_Project.git
   cd RAG_Project
   ```

2. **Configure environment variables**
   - Create the `.env` file with the sample given: `.env.sample`.

3. **Build and start the containers**
   ```sh
   docker compose up --build
   ```

4. **Access the API**
   - The API will be available at [http://localhost:3000](http://localhost:3000).
   - Qdrant will be available at [http://localhost:6333](http://localhost:6333).

---

## API Endpoints

- `POST /create_collection` — Create a new Qdrant collection.
- `DELETE /delete_collection/{collection_name}` — Delete a Qdrant collection.
- `POST /documents/extract` — Extract texts and tables from uploaded documents.
- `POST /upload_documents` — Upload extracted documents to Qdrant.
- `POST /chat` — Query the chatbot.

---

## Running Tests

1. **Inside the backend container:**
   ```sh
   docker exec -it <container_id> bash
   pytest tests/
   ```

2. **Test files**
   - All test scripts are in the `tests/` directory.
---

