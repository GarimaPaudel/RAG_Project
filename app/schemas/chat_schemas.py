from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    session_id: str
    collection_name: str

class VectorStoreSchema(BaseModel):
    collection_name: str

class Message(BaseModel):
    detail: str

class TableSchema(BaseModel):
    json: str | None = None
    csv: str | None = None
    markdown: str | None = None

class DRS(BaseModel):
    file_name: str
    text: str | None = None
    tables: list | TableSchema = None

class DocumentResponseSchema(BaseModel):
    results: list[DRS]


class UploadDocumentSchema(DocumentResponseSchema):
    pass


class UploadDocumentsResponse(BaseModel):
    detail: str
