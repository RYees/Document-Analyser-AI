from utils.vector_store_manager import VectorStoreManager
from typing import List, Dict, Any
import asyncio

class RetrieverAgent:
    """
    Queries the vector store (Weaviate) and fetches relevant documents based on a user’s research query or theme.
    """
    def __init__(self, collection_name: str = "ResearchPaper", research_domain: str = "General"):
        self.collection_name = collection_name
        self.research_domain = research_domain
        self.vstore = VectorStoreManager(collection_name=self.collection_name, research_domain=self.research_domain)

    async def run(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Main entry point for retrieval.
        Args:
            query (str): The research prompt or topic.
            top_k (int): Number of top documents to return.
        Returns:
            List[Dict]: Ranked documents with metadata.
        """
        # Use similarity_search (Weaviate logic)
        results = await asyncio.to_thread(self.vstore.similarity_search, query, top_k)
        return results 