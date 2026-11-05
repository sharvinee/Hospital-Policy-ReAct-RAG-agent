"""Build a local Chroma knowledge base from Northbridge policy Markdown files."""

# Import the Python and LangChain tools this script needs.
import json
import re
import shutil
from pathlib import Path

from langchain.embeddings import init_embeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

from src.policies_config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR
from src.settings import get_settings


# Set the policy input file, JSON output file, and section-ID pattern.
SOURCES_DIR = Path("policies")
SNAPSHOT_PATH = Path("policies/northbridge_policies.json")
CHUNK_ID_FOOTER_PATTERN = re.compile(r"\n*\*(SEC_\d{3})\*\s*$")

# Tell LangChain which Markdown headings become metadata.
SPLITTER = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "source_document"),
        ("##", "section"),
        ("###", "title"),
    ],
    strip_headers=True,
)


# Step 1: Read Markdown policies and turn them into clean Documents.
def parse_markdown_to_documents(sources_dir: Path) -> list[Document]:
    """Read policy files and return cleaned Documents sorted by section ID."""
    documents: list[Document] = []

    for path in sorted(sources_dir.glob("*.md")):  # Read every policy file.
        for chunk in SPLITTER.split_text(path.read_text(encoding="utf-8")):
            if "title" not in chunk.metadata:  # Only ### sections are policies.
                continue

            match = CHUNK_ID_FOOTER_PATTERN.search(chunk.page_content)  # Find *SEC_011*.
            if match is None:
                raise ValueError(
                    f"{path}: {chunk.metadata['title']!r} needs a footer like *SEC_011*."
                )

            metadata = dict(chunk.metadata)  # Copy the heading metadata.
            metadata["source_document"] = metadata["source_document"].removeprefix(
                "Northbridge — "  # Remove repeated organization text.
            )
            metadata["chunk_id"] = match.group(1)  # Save SEC_011 as metadata.
            content = CHUNK_ID_FOOTER_PATTERN.sub("", chunk.page_content).strip()
            documents.append(Document(page_content=content, metadata=metadata))  # Save chunk.

    return sorted(
        documents,
        key=lambda document: int(document.metadata["chunk_id"].split("_")[1]),  # SEC_2 before SEC_10.
    )


# Step 2: Add headings to the text that will be embedded for search.
def build_index_documents(docs: list[Document]) -> list[Document]:
    """Add heading context to the copies sent to the embedding model."""
    return [
        Document(
            page_content=(  # Add headings so embeddings include policy context.
                f"Source document: {doc.metadata['source_document']}\n"
                f"Section: {doc.metadata['section']}\n"
                f"Title: {doc.metadata['title']}\n\n"
                f"{doc.page_content}"
            ),
            metadata=dict(doc.metadata),  # Keep the original labels and ID.
        )
        for doc in docs
    ]


# Step 3: Save a readable JSON copy of the policy chunks.
def write_chunks_json(docs: list[Document], json_path: Path) -> None:
    """Save a readable copy of the policy chunks as JSON."""
    records = [  # Convert Documents into ordinary JSON-compatible dictionaries.
        {
            "chunk_id": doc.metadata["chunk_id"],
            "title": doc.metadata["title"],
            "section": doc.metadata["section"],
            "source_document": doc.metadata["source_document"],
            "content": doc.page_content,
        }
        for doc in docs
    ]
    json_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# Step 4: Create the local Chroma database used for semantic search.
def build_vector_store(docs: list[Document]) -> None:
    """Rebuild the Chroma collection from the current policy chunks."""
    if CHROMA_PERSIST_DIR.exists():  # Start clean so removed policies stay removed.
        shutil.rmtree(CHROMA_PERSIST_DIR)  # Remove chunks deleted from source files.

    settings = get_settings()  # Load the embedding model and OpenAI API key.
    vector_store = Chroma(  # Open a local Chroma collection.
        collection_name=CHROMA_COLLECTION_NAME,  # Name this policy database.
        embedding_function=init_embeddings(
            settings.embedding_model,  # Convert policy text into embeddings.
            api_key=settings.openai_api_key,  # Authenticate with OpenAI.
        ),
        persist_directory=str(CHROMA_PERSIST_DIR),  # Where Chroma saves its files.
        collection_metadata={"hnsw:space": "cosine"},  # Compare meaning with cosine similarity.
    )
    vector_store.add_documents(
        build_index_documents(docs),
        ids=[doc.metadata["chunk_id"] for doc in docs],
    )


# Step 5: Run all build steps in order.
def main() -> None:
    """Parse policies, save JSON, and build the searchable Chroma database."""
    documents = parse_markdown_to_documents(SOURCES_DIR)  # Markdown → Documents.
    write_chunks_json(documents, SNAPSHOT_PATH)  # Documents → readable JSON.
    build_vector_store(documents)  # Documents → searchable Chroma database.
    print(f"Built {len(documents)} chunks in {CHROMA_PERSIST_DIR}.")


# Run the build only when this file is executed directly.
if __name__ == "__main__":
    main()
