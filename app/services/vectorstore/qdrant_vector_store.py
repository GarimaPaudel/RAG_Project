from app.services.vectorstore.upload_document import (
    upload_document_new_collection,
    upload_document_existing_collection,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging as logger


class QdrantVectorStoreDB:
    """
    A class that handles the Qdrant vector store database operations.
    """

    def __init__(self, qdrant_client, vector_embedding):
        self.qdrant_client = qdrant_client
        self.vector_embedding = vector_embedding

    async def create_collection(self, collection_name: str):
        """
        Create a new collection in Qdrant.
        """
        try:
            await upload_document_new_collection(self.vector_embedding, collection_name)
            logger.info(f"Collection {collection_name} created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating chatbot: {e}")
            raise e

    async def delete_collection(self, bot_id: str):
        """Delete a collection in Qdrant"""
        try:
            self.qdrant_client.delete_collection(bot_id)
            logger.info(f"Collection {bot_id} deleted successfully.")
            return True

        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise e

    async def upload_documents(self, documents: list[dict], collection_name: str):
        """Upload Documents to qdrant vectorstore"""
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100, add_start_index=True
            )
            final_t = []
            for doc in documents:
                text = str(doc.get("text", ""))
                source = str(doc.get("file_name", ""))
                final_t.append(Document(page_content=text, metadata={"source": source}))
            final_docs = splitter.split_documents(final_t)
            response = await upload_document_existing_collection(
                documents_=final_docs,
                vector_embeddings=self.vector_embedding,
                collection_name_=collection_name,
            )
            if response:
                logger.info(f"Documents uploaded successfully to collection {collection_name}.")
                return response
            else:
                logger.error(f"Failed to upload documents to collection {collection_name}.")
                return False  
                #TODO: raise an exception (Custom)
        except Exception as e:
            logger.error(f"Error uploading documents: {e}")
            raise e