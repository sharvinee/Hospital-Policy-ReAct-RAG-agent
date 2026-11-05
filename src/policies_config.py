"""Define the local Chroma collection name and storage path for policy search."""

from pathlib import Path


# Configure the Chroma collection and persistence path.
CHROMA_COLLECTION_NAME = "northbridge_policies_kb"
CHROMA_PERSIST_DIR = Path(".chroma/policies_kb")
