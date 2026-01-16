# backend/scripts/populate_vectordb.py
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import get_settings

settings = get_settings()

def load_and_chunk_documents():
    """Load markdown files and chunk by headers"""

    # Path to knowledge base (backend/knowledge_base)
    kb_path = Path(__file__).parent.parent / "knowledge_base"

    print(f"[*] Loading documents from: {kb_path}")

    # Load all markdown files
    loader = DirectoryLoader(
        str(kb_path),
        glob="**/*.md",
        loader_cls=TextLoader,
        show_progress=True
    )
    documents = loader.load()

    print(f"[OK] Loaded {len(documents)} documents")

    # Split by markdown headers (## sections)
    headers_to_split_on = [
        ("#", "Header1"),
        ("##", "Header2"),
        ("###", "Header3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    all_chunks = []
    for doc in documents:
        chunks = markdown_splitter.split_text(doc.page_content)

        # Add source metadata
        source_file = os.path.basename(doc.metadata.get("source", "unknown"))
        for chunk in chunks:
            chunk.metadata["source_file"] = source_file
            chunk.metadata["source_path"] = doc.metadata.get("source", "")

        all_chunks.extend(chunks)

    print(f"[OK] Created {len(all_chunks)} chunks")

    return all_chunks

def create_faiss_index():
    """Create FAISS vector store from documents"""

    # Load and chunk documents
    chunks = load_and_chunk_documents()

    # Initialize embeddings
    print("[*] Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # Create FAISS index
    print("[*] Creating FAISS index...")
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    # Save to disk
    os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
    vectorstore.save_local(settings.FAISS_INDEX_PATH)

    print(f"[OK] FAISS index saved to: {settings.FAISS_INDEX_PATH}")
    print(f"[OK] Total vectors: {vectorstore.index.ntotal}")

    return vectorstore

if __name__ == "__main__":
    print("[*] Populating vector database...")
    vectorstore = create_faiss_index()
    print("[OK] Done!")
