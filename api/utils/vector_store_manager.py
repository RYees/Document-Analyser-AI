import logging
from typing import List, Dict, Any, Optional
from .weaviate_client import get_weaviate_manager

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manages vector storage and retrieval using Weaviate only.
    """
    def __init__(self, collection_name: str = "ResearchPaper", research_domain: str = "General"):
        self.collection_name = collection_name
        self.research_domain = research_domain
        self.weaviate = get_weaviate_manager()

        # Ensure the collection exists with a vectorizer
        if self.weaviate.is_available():
            existing_collections = self.weaviate.list_collections()
            if self.collection_name not in existing_collections:
                print(f"[DEBUG] Creating collection {self.collection_name} with text2vec-openai vectorizer...")
                schema = {
                    "class": self.collection_name,
                    "description": "Academic research papers",
                    "vectorizer": "text2vec-openai",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "model": "ada",
                            "type": "text"
                        }
                    },
                    "properties": [
                        {"name": "content", "dataType": ["text"]},
                        {"name": "research_domain", "dataType": ["text"]},
                        {"name": "title", "dataType": ["text"]},
                        {"name": "authors", "dataType": ["text"]},
                        {"name": "year", "dataType": ["int"]},
                        {"name": "doi", "dataType": ["text"]},
                        {"name": "source", "dataType": ["text"]},
                        {"name": "paper_id", "dataType": ["text"]},
                        {"name": "chunk_index", "dataType": ["int"]},
                    ]
                }
                self.weaviate.create_collection(self.collection_name, schema)
            # Debug print the schema after creation or if it exists
            try:
                schema = self.weaviate.get_class_schema(self.collection_name)
                print(f"[DEBUG] Current schema for {self.collection_name}: {schema}")
            except Exception as e:
                print(f"[ERROR] Could not fetch schema for {self.collection_name}: {e}")
        else:
            print(f"[ERROR] Weaviate is not available! Cannot initialize VectorStoreManager")
            raise RuntimeError("Weaviate is not available")

    def add_chunks(self, chunks: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Add chunks to Weaviate only.
        metadata_list: List of dicts with metadata for each chunk (optional).
        """
        print(f"[DEBUG] VectorStoreManager.add_chunks called with {len(chunks)} chunks")
        print(f"[DEBUG] Weaviate available: {self.weaviate.is_available()}")
        
        if not self.weaviate.is_available():
            error_msg = "Weaviate is not available. Cannot store chunks."
            print(f"[ERROR] {error_msg}")
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            print(f"[DEBUG] Preparing {len(chunks)} documents for Weaviate insertion")
            docs = []
            for i, chunk in enumerate(chunks):
                meta = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
                
                # Ensure all metadata values are strings or numbers
                cleaned_meta = {}
                for key, value in meta.items():
                    if key == 'year' and value is None:
                        # Skip year if it's None, or set to 0 as fallback
                        cleaned_meta[key] = 0
                    elif key == 'chunk_index' and value is None:
                        # Skip chunk_index if it's None, or set to 0 as fallback
                        cleaned_meta[key] = 0
                    elif isinstance(value, (str, int, float, bool)):
                        cleaned_meta[key] = value
                    else:
                        cleaned_meta[key] = str(value)
                
                doc = {
                    "properties": {
                        "content": chunk,
                        "research_domain": self.research_domain,
                        **cleaned_meta
                    }
                }
                docs.append(doc)
                
                if i < 3:  # Show first 3 docs for debugging
                    print(f"[DEBUG] Doc {i}: content_length={len(chunk)}, metadata={cleaned_meta}")
            
            print(f"[DEBUG] Calling weaviate.insert_documents with {len(docs)} documents")
            print(f"[DEBUG] Collection name: {self.collection_name}")
            
            # Log the first document structure
            if docs:
                print(f"[DEBUG] First document structure: {docs[0]}")
            
            insert_result = self.weaviate.insert_documents(self.collection_name, docs)
            print(f"[DEBUG] Weaviate insert_documents returned: {insert_result}")
            
            # Verify insertion by checking collection count
            try:
                count_result = self.weaviate.client.collections.get(self.collection_name).aggregate.over_all(total_count=True)
                total_count = count_result.total_count
                print(f"[DEBUG] Collection count after insertion: {total_count}")
                
                if total_count > 0:
                    print(f"[DEBUG] ✅ Successfully inserted documents. Collection now has {total_count} documents")
                else:
                    print(f"[DEBUG] ⚠️ Insertion may have failed - collection still has 0 documents")
                    
            except Exception as count_error:
                print(f"[ERROR] Could not verify insertion count: {count_error}")
            
            logger.info(f"✅ Added {len(chunks)} chunks to Weaviate")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add chunks to Weaviate: {e}")
            print(f"[ERROR] Exception type: {type(e)}")
            import traceback
            print(f"[ERROR] Full traceback: {traceback.format_exc()}")
            logger.error(f"❌ Failed to add chunks to Weaviate: {e}")
            raise RuntimeError(f"Failed to add chunks to Weaviate: {e}")

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar chunks using Weaviate only.
        Returns a list of document dictionaries with metadata.
        """
        if not self.weaviate.is_available():
            error_msg = "Weaviate is not available. Cannot perform similarity search."
            print(f"[ERROR] {error_msg}")
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        try:
            print(f"[DEBUG] Performing similarity search with query: '{query}', top_k: {top_k}")
            raw_results = self.weaviate.search_documents(self.collection_name, query, limit=top_k)
            print(f"[DEBUG] Search returned {len(raw_results)} results")
            
            # Transform results to expected format
            transformed_results = []
            for result in raw_results:
                properties = result.get("properties", {})
                transformed_result = {
                    "title": properties.get("title", "Unknown"),
                    "authors": properties.get("authors", "Unknown"),
                    "year": properties.get("year", "Unknown"),
                    "content": properties.get("content", ""),
                    "doi": properties.get("doi", ""),
                    "source": properties.get("source", ""),
                    "paper_id": properties.get("paper_id", ""),
                    "chunk_index": properties.get("chunk_index", 0),
                    "research_domain": properties.get("research_domain", ""),
                    "uuid": result.get("uuid", ""),
                    "metadata": result.get("metadata", {})
                }
                transformed_results.append(transformed_result)
            
            if transformed_results:
                logger.info(f"✅ Retrieved {len(transformed_results)} chunks from Weaviate")
                return transformed_results
            else:
                print(f"[DEBUG] No results found for query: '{query}'")
                return []
                
        except Exception as e:
            print(f"[ERROR] Weaviate similarity search failed: {e}")
            logger.error(f"❌ Weaviate similarity search failed: {e}")
            raise RuntimeError(f"Weaviate similarity search failed: {e}") 