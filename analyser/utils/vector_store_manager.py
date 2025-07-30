import logging
from typing import List, Dict, Any, Optional
from analyser.utils.weaviate_client import get_weaviate_manager
import analyser.utils.chroma as chroma_utils

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manages vector storage and retrieval using Weaviate as primary and Chroma as backup.
    """
    def __init__(self, collection_name: str = "ResearchPaper", research_domain: str = "General"):
        self.collection_name = collection_name
        self.research_domain = research_domain
        self.weaviate = get_weaviate_manager()
        self.chroma_collection = None
        self.embedding_function = chroma_utils.embedding()

    def add_chunks(self, chunks: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Add chunks to Weaviate (primary) and fallback to Chroma if needed.
        metadata_list: List of dicts with metadata for each chunk (optional).
        """
        # Try Weaviate first
        if self.weaviate.is_available():
            try:
                docs = []
                for i, chunk in enumerate(chunks):
                    meta = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
                    doc = {
                        "properties": {
                            "content": chunk,
                            "research_domain": self.research_domain,
                            **meta
                        }
                    }
                    docs.append(doc)
                self.weaviate.insert_documents(self.collection_name, docs)
                logger.info(f"✅ Added {len(chunks)} chunks to Weaviate")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to add chunks to Weaviate: {e}")
        # Fallback to Chroma
        try:
            token_split_texts = chroma_utils.sentence_transfomer_textsplitter(chunks)
            self.chroma_collection = chroma_utils.connect_with_chromadb(self.embedding_function, token_split_texts)
            logger.info(f"✅ Added {len(token_split_texts)} chunks to Chroma (backup)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add chunks to Chroma: {e}")
            return False

    def similarity_search(self, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve similar chunks using Weaviate (primary) or Chroma (backup).
        Returns a list of chunk contents.
        """
        # Try Weaviate first
        if self.weaviate.is_available():
            try:
                results = self.weaviate.search_documents(self.collection_name, query, limit=top_k)
                if results:
                    logger.info(f"✅ Retrieved {len(results)} chunks from Weaviate")
                    return [r["properties"]["content"] for r in results if "content" in r["properties"]]
            except Exception as e:
                logger.error(f"❌ Weaviate similarity search failed: {e}")
        # Fallback to Chroma
        try:
            if not self.chroma_collection:
                logger.warning("Chroma collection not initialized; cannot search.")
                return []
            retrieved = chroma_utils.vectordb_answer_question(query, self.chroma_collection)
            logger.info(f"✅ Retrieved {len(retrieved)} chunks from Chroma (backup)")
            return retrieved
        except Exception as e:
            logger.error(f"❌ Chroma similarity search failed: {e}")
            return [] 