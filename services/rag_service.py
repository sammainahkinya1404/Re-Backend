# backend/services/rag_service.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import get_settings
from typing import List, Dict
import os

settings = get_settings()

class RAGService:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self._load_vectorstore()
    
    def _load_vectorstore(self):
        """Load FAISS index from disk"""
        if not os.path.exists(settings.FAISS_INDEX_PATH):
            raise FileNotFoundError(
                f"FAISS index not found at {settings.FAISS_INDEX_PATH}. "
                "Run 'python scripts/populate_vectordb.py' first."
            )
        
        print("[*] Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        print("[*] Loading FAISS index...")
        self.vectorstore = FAISS.load_local(
            settings.FAISS_INDEX_PATH,
            self.embeddings,
            allow_dangerous_deserialization=True  # Required for FAISS
        )
        print(f"[OK] FAISS index loaded: {self.vectorstore.index.ntotal} vectors")
    
    def retrieve_context(self, query: str, top_k: int = None) -> Dict:
        """Retrieve relevant context for a query"""
        
        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K
        
        # Retrieve documents
        docs = self.vectorstore.similarity_search_with_score(query, k=top_k)
        
        # Format results
        context_parts = []
        sources = []
        
        for doc, score in docs:
            context_parts.append(doc.page_content)
            source = doc.metadata.get("source_file", "unknown")
            if source not in sources:
                sources.append(source)
        
        return {
            "context": "\n\n---\n\n".join(context_parts),
            "sources": sources,
            "num_chunks": len(docs)
        }
    
    def retrieve_for_area(self, query: str, area: str) -> Dict:
        """Retrieve context filtered by area"""
        
        # Add area to query for better retrieval
        enhanced_query = f"{area} {query}"
        
        # Retrieve with metadata filtering (if supported)
        docs = self.vectorstore.similarity_search(enhanced_query, k=settings.RETRIEVAL_TOP_K)
        
        # Filter by area in source filename
        area_docs = [
            doc for doc in docs 
            if area.lower() in doc.metadata.get("source_file", "").lower()
        ]
        
        # If no area-specific docs, return general docs
        relevant_docs = area_docs if area_docs else docs
        
        context_parts = [doc.page_content for doc in relevant_docs]
        sources = list(set([doc.metadata.get("source_file", "unknown") for doc in relevant_docs]))
        
        return {
            "context": "\n\n---\n\n".join(context_parts),
            "sources": sources,
            "num_chunks": len(relevant_docs)
        }

# Singleton instance
rag_service = RAGService()