from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.vectorstore import answer_query_from_existing_collection
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.utils.config import settings


GROQ_API_KEY = settings.GROQ_API_KEY
GOOGLE_API_KEY = settings.GOOGLE_API_KEY


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


class AnswerQuery:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=GOOGLE_API_KEY, model="models/text-embedding-004"
        )
        self.model = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=100,
            streaming=True,
            timeout=None,
            max_retries=2,
        )
        self.sessions = {}

    def get_by_session_id(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryHistory()
        return self.sessions[session_id]

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if (session_id) not in self.sessions:
            self.sessions[(session_id)] = InMemoryHistory()
        return self.sessions[(session_id)]

    async def in_memory_answer_query(
        self, query: str, session_id: str, collection_name: str):
        """ "
        Chat with bot using In Memory Implementation.
        """

        # Vector store first!
        vector_store = await answer_query_from_existing_collection(
            collection_name_=collection_name,
            vector_embed=self.embeddings,
        )

        # Retriever
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4, "fetch_k": 8, "lambda_mult": 0.5},
        )

        # Get documents
        compressed_docs = retriever.get_relevant_documents(query)

        # Build context from docs
        context_chunks = [doc.page_content for doc in compressed_docs]
        context = "\n\n".join(context_chunks)

        # Prompt
        prompt = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=[
        MessagesPlaceholder(variable_name="history"),
        ("system", "You are chatbot, a smart assistant who always responds using only the provided context. "
                   "Do not mention or refer to the context explicitly. Limit your answers to a maximum of two sentences."),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ]
)

        chain = prompt | self.model

        with_message_history = RunnableWithMessageHistory(
            chain,
            get_session_history=self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        # Run the memory-wrapped chain with both context & question
        response_stream = with_message_history.astream(
            {
                "question": query,
                "context": context,
                "history": self.get_session_history(session_id),
            },
            config={"configurable": {"session_id": session_id}},
        )
        # Collect the streamed response into a string
        response_text = ""
        async for chunk in response_stream:
            response_text += str(chunk.content) if hasattr(chunk, "content") else str(chunk)
        return {"response": response_text}