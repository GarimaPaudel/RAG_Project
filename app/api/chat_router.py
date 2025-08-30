import uuid
import os 
import tempfile
from fastapi import APIRouter, status, HTTPException, UploadFile, File
from app.services.answer_query.get_answers import AnswerQuery
from app.services.vectorstore import QdrantVectorStoreDB
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.utils import settings
from app.services.documents.load_document import DocumentTextExtractor
from app.schemas import (
    ChatRequest, 
    VectorStoreSchema, 
    DocumentResponseSchema,
    UploadDocumentSchema,
)
router = APIRouter()
extractor = DocumentTextExtractor()
answer_query_service = AnswerQuery()
vector_embeddings = GoogleGenerativeAIEmbeddings(
    google_api_key=settings.GOOGLE_API_KEY, model="models/text-embedding-004"
)
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
)
vectorstore = QdrantVectorStoreDB(
    qdrant_client=qdrant_client, vector_embedding=vector_embeddings
)

@router.post("/create_collection", status_code=status.HTTP_201_CREATED)
async def create_collection(request: VectorStoreSchema):
    """
    Endpoint to store embeddings in the qdrant vector database.
    """
    try:
        response = await vectorstore.create_collection(request.collection_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_collection/{collection_name}", status_code=status.HTTP_200_OK)
async def delete_collection(collection_name: str):
    """
    Endpoint to delete a collection in the qdrant vector database.
    """
    try:
        response = await vectorstore.delete_collection(collection_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post(
    "/documents/extract",
    status_code=status.HTTP_201_CREATED
)
async def extract_text(files: list[UploadFile] = File(...)) -> DocumentResponseSchema:
    """
    Extract text from the uploaded files
    """
    try:
        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in files:
                file_content = await file.read()

                temp_filename = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{file.filename}")
                with open(temp_filename, "wb") as f:
                    f.write(file_content)
                # Extract text
                text_result = extractor.extract_text(temp_filename)
                results.append(
                    {
                        "file_name": file.filename,
                        "text": text_result.get("text"),
                        "tables": text_result.get("tables")
                    }
                )
        return DocumentResponseSchema(source_type="document", results=results)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_documents", status_code=status.HTTP_201_CREATED)  
async def upload_documents(
    collection_name: str,
    request: UploadDocumentSchema
):
    """
    Upload documents to the collection of chatbot in Qdrant vectorstore.
    """
    try:
        documents = []
        for drs in request.results:
            base_doc = {
                "file_name": drs.file_name,
                "text": drs.text or ""
            }
            documents.append(base_doc)

            # Add each table as a separate "document"
            if drs.tables:
                for idx, table in enumerate(drs.tables):
                    documents.append({
                        "file_name": f"{drs.file_name}_table_{idx+1}",
                        "text": table.get("markdown") or table.get("csv") or table.get("json") or ""
                    })

        response = await vectorstore.upload_documents(
            documents=documents,
            collection_name=collection_name
        )

        if response:
            return {"detail": "Documents Uploaded Successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    result = await answer_query_service.in_memory_answer_query(
        query=request.query,
        session_id=request.session_id,
        collection_name=request.collection_name
    )
    return result

