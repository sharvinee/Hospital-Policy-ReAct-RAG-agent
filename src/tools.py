"""Provide one LangChain tool for searching persisted Northbridge policies."""

from langchain.embeddings import init_embeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from src.policies_config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR
from src.settings import get_settings

settings = get_settings()

class RelevantChunks(BaseModel):
    """Identify chunks relevant to search query."""
    chunk_ids: list[str]

relevance_model = init_chat_model(
    settings.light_chat_model,
    api_key = settings.openai_api_key
    ).with_structured_output(RelevantChunks)

def filter_relevant_chunks(query: str, documents: list[Document]) -> list[Document]:
    """Keep policy chunks relevant to search query."""
    if not documents:
        return []

    candidates = "\n\n".join(
        f"ID: {doc.metadata["chunk_id"]}\n{doc.page_content}"
        for doc in documents
    )

    result = relevance_model.invoke(
        f"""Select the policy chunks relevant to the search query.
        Keep chunks that discuss the topic even if they don't specify the requested
        detail. Return the relevant IDs, or an empty list if none are relevant.

        Query: {query}

        Chunks:
        {candidates}
        """
    )

    return [
        doc for doc in documents
        if doc.metadata["chunk_id"] in
        result.chunk_ids
    ]

def retrieve_chunks(query: str) -> list[Document]:
    """Return the policy chunks most relevant to a question."""
    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=init_embeddings(
            settings.embedding_model,
            api_key=settings.openai_api_key,
        ),
        persist_directory=str(CHROMA_PERSIST_DIR),
    )
    results = vector_store.similarity_search_with_relevance_scores(
        query,
        k=settings.retrieval_top_k,
        score_threshold=settings.retrieval_score_threshold,
    )
    return [document for document, _score in results]

@tool
def search_kb(query: str) -> str:
    """Search Northbridge policies to answer a question about hospital policy."""
    documents = retrieve_chunks(query)
    documents = filter_relevant_chunks(query, documents)
    return "\n\n".join(
        (
            f"Citation ID: {document.metadata['chunk_id']}\n"
            f"Source: {document.metadata['source_document']}\n"
            f"Section: {document.metadata['section']}\n"
            f"Title: {document.metadata['title']}\n"
            f"Content: {document.page_content}"
        )
        for document in documents
    )
