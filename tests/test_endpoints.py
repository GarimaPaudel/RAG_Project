import io
import uuid
from unittest.mock import patch

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Chatbot API is running"

def test_create_collection(client):
    payload = {"collection_name": f"test_collection_{uuid.uuid4().hex[:6]}"}
    response = client.post("/create_collection", json=payload)
    assert response.status_code in [200, 201]

def test_delete_collection(client):
    collection_name = f"delete_collection_{uuid.uuid4().hex[:6]}"
    client.post("/create_collection", json={"collection_name": collection_name})
    response = client.delete(f"/delete_collection/{collection_name}")
    assert response.status_code == 200


def test_extract_documents(client):
    fake_result = {"text": "Hello World", "tables": [{"markdown": "| a | b |\n|---|---|\n| 1 | 2 |"}]}
    with patch("app.api.chat_router.extractor.extract_text", return_value=fake_result):
        files = {"files": ("test.pdf", io.BytesIO(b"dummy"), "application/pdf")}
        response = client.post("/documents/extract", files=files)
        assert response.status_code == 201
        assert response.json()["results"][0]["text"] == "Hello World"


def test_upload_documents(client):
    collection_name = f"upload_test_{uuid.uuid4().hex[:6]}"
    client.post("/create_collection", json={"collection_name": collection_name})

    payload = {"results": [{"file_name": "sample.pdf", "text": "This is a test doc", "tables": []}]}

    with patch("app.api.chat_router.vectorstore.upload_documents", return_value=True):
        response = client.post(f"/upload_documents?collection_name={collection_name}", json=payload)
        assert response.status_code == 201
        assert response.json()["detail"] == "Documents Uploaded Successfully"


def test_chat_endpoint(client):
    collection_name = f"chat_test_{uuid.uuid4().hex[:6]}"
    client.post("/create_collection", json={"collection_name": collection_name})

    payload = {"query": "What is in the document?", "session_id": str(uuid.uuid4()), "collection_name": collection_name}
    with patch("app.api.chat_router.answer_query_service.in_memory_answer_query",
               return_value={"response": "mocked answer"}):
        response = client.post("/chat", json=payload)
        assert response.status_code == 200
        assert "response" in response.json()
