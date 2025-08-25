from langchain_qdrant import QdrantVectorStore, RetrievalMode
from app.utils import settings


async def upload_document_new_collection(vector_embeddings, collection_name_):
    QdrantVectorStore.from_documents(
        documents=[],
        embedding=vector_embeddings,
        url=settings.QDRANT_URL,
        prefer_grpc=True,
        collection_name=collection_name_,
        retrieval_mode=RetrievalMode.DENSE,
        force_recreate=True,
        timeout=30000,
    )


async def upload_document_existing_collection(
    documents_, vector_embeddings, collection_name_
):
    QdrantVectorStore.from_documents(
        documents=documents_,
        embedding=vector_embeddings,
        url=settings.QDRANT_URL,
        prefer_grpc=True,
        collection_name=collection_name_,
        retrieval_mode=RetrievalMode.DENSE,
        timeout=30000,
    )


async def answer_query_from_existing_collection(vector_embed, collection_name_):
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=vector_embed,
        collection_name=collection_name_,
        url=settings.QDRANT_URL,
        retrieval_mode=RetrievalMode.DENSE,
    )
    return vector_store