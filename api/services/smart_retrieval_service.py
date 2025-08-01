"""
Smart Retrieval Service - Intelligent document retrieval with quality evaluation and fallback.
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import sys
import os

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils.vector_store_manager import VectorStoreManager
from api.services.data_extraction_service import DataExtractionService

class SmartRetrievalService:
    """
    Service for intelligent document retrieval with quality evaluation and CORE API fallback.
    
    This service provides:
    1. Vector store similarity search
    2. Quality evaluation of results
    3. Smart fallback to CORE API extraction
    4. Result merging and optimization
    """
    
    def __init__(self):
        """Initialize smart retrieval service."""
        self.vector_store_manager = None
        self.extraction_service = DataExtractionService()
        self.collection_name = "ResearchPaper"
        self.research_domain = "General"
        
        # Quality thresholds
        self.quality_thresholds = {
            "min_quantity_ratio": 0.3,      # Minimum 30% of requested results
            "min_certainty_score": 0.7,     # Minimum certainty from Weaviate
            "min_relevance_score": 0.6,     # Minimum reranking score
            "min_recent_ratio": 0.2,        # Minimum 20% recent docs (last 2 years)
            "max_years_old": 2               # Define "recent" as last 2 years
        }
        
        # Retrieval history
        self.retrieval_history = []
    
    def _initialize_vector_store(self, collection_name: str = "ResearchPaper", research_domain: str = "General"):
        """Initialize vector store manager."""
        if not self.vector_store_manager or self.collection_name != collection_name or self.research_domain != research_domain:
            self.vector_store_manager = VectorStoreManager(collection_name=collection_name, research_domain=research_domain)
            self.collection_name = collection_name
            self.research_domain = research_domain
    
    def _calculate_quality_metrics(self, results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Calculate quality metrics for retrieved results.
        
        Args:
            results: List of retrieved documents
            query: Original search query
            
        Returns:
            Dict containing quality metrics
        """
        if not results:
            return {
                "quantity_score": 0.0,
                "certainty_score": 0.0,
                "recency_score": 0.0,
                "overall_score": 0.0
            }
        
        # 1. Quantity Score
        quantity_score = len(results) / max(1, len(results))  # Will be 1.0 for any results
        
        # 2. Certainty Score (from Weaviate metadata)
        certainty_scores = []
        for result in results:
            metadata = result.get("metadata", {})
            certainty = metadata.get("certainty", 0.5)  # Default to 0.5 if not available
            certainty_scores.append(certainty)
        
        avg_certainty = sum(certainty_scores) / len(certainty_scores) if certainty_scores else 0.0
        
        # 3. Recency Score
        current_year = datetime.now().year
        recent_docs = 0
        for result in results:
            year = result.get("year", 0)
            if isinstance(year, str):
                try:
                    year = int(year)
                except ValueError:
                    year = 0
            
            if year >= current_year - self.quality_thresholds["max_years_old"]:
                recent_docs += 1
        
        recency_score = recent_docs / len(results) if results else 0.0
        
        # 4. Overall Score (weighted average)
        overall_score = (
            quantity_score * 0.2 +
            avg_certainty * 0.5 +
            recency_score * 0.3
        )
        
        return {
            "quantity_score": quantity_score,
            "certainty_score": avg_certainty,
            "recency_score": recency_score,
            "overall_score": overall_score,
            "total_results": len(results),
            "recent_results": recent_docs
        }
    
    def _should_fallback_to_core_api(
        self, 
        results: List[Dict[str, Any]], 
        quality_metrics: Dict[str, Any],
        query: str, 
        max_results: int
    ) -> Dict[str, Any]:
        """
        Decide if we need to fallback to CORE API.
        
        Args:
            results: Current vector store results
            quality_metrics: Quality metrics for current results
            query: Search query
            max_results: Requested number of results
            
        Returns:
            Dict containing fallback decision and reasoning
        """
        fallback_reasons = []
        should_fallback = False
        
        # 1. Quantity Check
        if len(results) < max_results * self.quality_thresholds["min_quantity_ratio"]:
            fallback_reasons.append(f"Insufficient quantity: {len(results)} < {max_results * self.quality_thresholds['min_quantity_ratio']:.1f}")
            should_fallback = True
        
        # 2. Certainty Check
        if quality_metrics["certainty_score"] < self.quality_thresholds["min_certainty_score"]:
            fallback_reasons.append(f"Low certainty: {quality_metrics['certainty_score']:.2f} < {self.quality_thresholds['min_certainty_score']}")
            should_fallback = True
        
        # 3. Recency Check
        if quality_metrics["recency_score"] < self.quality_thresholds["min_recent_ratio"]:
            fallback_reasons.append(f"Few recent docs: {quality_metrics['recency_score']:.2f} < {self.quality_thresholds['min_recent_ratio']}")
            should_fallback = True
        
        # 4. Overall Quality Check
        if quality_metrics["overall_score"] < 0.6:  # Overall quality threshold
            fallback_reasons.append(f"Low overall quality: {quality_metrics['overall_score']:.2f} < 0.6")
            should_fallback = True
        
        return {
            "should_fallback": should_fallback,
            "reasons": fallback_reasons,
            "quality_metrics": quality_metrics
        }
    
    def _merge_and_deduplicate_results(
        self, 
        original_results: List[Dict[str, Any]], 
        new_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge and deduplicate results from vector store and CORE API.
        
        Args:
            original_results: Results from initial vector search
            new_results: Results from post-extraction vector search
            
        Returns:
            Merged and deduplicated results
        """
        # Create a dict to track unique documents by DOI or title
        seen_docs = {}
        merged_results = []
        
        # Add new results first (they're fresher)
        for result in new_results:
            doi = result.get("doi", "")
            title = result.get("title", "").lower().strip()
            
            # Create unique key based on DOI or title
            key = doi if doi else title
            
            if key and key not in seen_docs:
                seen_docs[key] = True
                result["source_priority"] = "new"
                merged_results.append(result)
        
        # Add original results if not already present
        for result in original_results:
            doi = result.get("doi", "")
            title = result.get("title", "").lower().strip()
            
            key = doi if doi else title
            
            if key and key not in seen_docs:
                seen_docs[key] = True
                result["source_priority"] = "existing"
                merged_results.append(result)
        
        print(f"[DEBUG] Merged results: {len(new_results)} new + {len(original_results)} original = {len(merged_results)} unique")
        
        return merged_results
    
    async def smart_retrieve_documents(
        self, 
        query: str, 
        research_domain: str = "General", 
        max_results: int = 20,
        enable_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Smart document retrieval with quality evaluation and fallback.
        
        Args:
            query: Search query
            research_domain: Research domain/field
            max_results: Maximum number of results to return
            enable_fallback: Whether to enable CORE API fallback
            
        Returns:
            Dict containing:
                - success: bool
                - documents: List[Dict] - Retrieved documents
                - quality_metrics: Dict - Quality evaluation
                - fallback_used: bool - Whether fallback was triggered
                - fallback_info: Dict - Fallback details (if used)
                - retrieval_id: str - For tracking
                - timestamp: str
        """
        retrieval_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        print(f"[DEBUG] ===== SMART RETRIEVAL SERVICE =====")
        print(f"[DEBUG] Retrieval ID: {retrieval_id}")
        print(f"[DEBUG] Query: '{query}'")
        print(f"[DEBUG] Research Domain: {research_domain}")
        print(f"[DEBUG] Max Results: {max_results}")
        print(f"[DEBUG] Fallback Enabled: {enable_fallback}")
        
        try:
            # Initialize vector store
            self._initialize_vector_store(self.collection_name, research_domain)
            
            # Step 1: Initial vector store search
            print(f"[DEBUG] Step 1: Initial vector store search...")
            initial_results = self.vector_store_manager.similarity_search(query, max_results, research_domain)
            print(f"[DEBUG] Initial search returned {len(initial_results)} results")
            
            # Step 2: Evaluate quality
            print(f"[DEBUG] Step 2: Evaluating result quality...")
            quality_metrics = self._calculate_quality_metrics(initial_results, query)
            print(f"[DEBUG] Quality metrics: {quality_metrics}")
            
            # Step 3: Decide on fallback
            fallback_decision = self._should_fallback_to_core_api(
                initial_results, quality_metrics, query, max_results
            )
            print(f"[DEBUG] Fallback decision: {fallback_decision}")
            
            final_results = initial_results
            fallback_info = None
            
            # Step 4: Execute fallback if needed
            if enable_fallback and fallback_decision["should_fallback"]:
                print(f"[DEBUG] Step 4: Executing CORE API fallback...")
                print(f"[DEBUG] Fallback reasons: {fallback_decision['reasons']}")
                
                # Extract new documents from CORE API
                extraction_result = await self.extraction_service.extract_and_store_documents(
                    query=query,
                    research_domain=research_domain,
                    max_results=max_results
                )
                
                if extraction_result["success"]:
                    print(f"[DEBUG] Extraction successful, re-querying vector store...")
                    
                    # Re-query vector store with higher limit to get mix of old + new
                    fresh_results = self.vector_store_manager.similarity_search(query, max_results * 2, research_domain)
                    print(f"[DEBUG] Fresh search returned {len(fresh_results)} results")
                    
                    # Merge results intelligently
                    final_results = self._merge_and_deduplicate_results(initial_results, fresh_results)
                    
                    # Limit to requested number
                    final_results = final_results[:max_results]
                    
                    fallback_info = {
                        "extraction_used": True,
                        "extraction_result": extraction_result,
                        "papers_fetched": extraction_result.get("papers_fetched", 0),
                        "chunks_stored": extraction_result.get("chunks_stored", 0),
                        "fresh_search_count": len(fresh_results),
                        "final_merged_count": len(final_results)
                    }
                else:
                    print(f"[DEBUG] Extraction failed, using original results")
                    fallback_info = {
                        "extraction_used": False,
                        "extraction_error": extraction_result.get("error", "Unknown error"),
                        "fallback_to_original": True
                    }
            else:
                print(f"[DEBUG] No fallback needed or disabled")
                fallback_info = {
                    "extraction_used": False,
                    "reason": "Quality sufficient" if not fallback_decision["should_fallback"] else "Fallback disabled"
                }
            
            # Step 5: Final quality assessment
            final_quality_metrics = self._calculate_quality_metrics(final_results, query)
            
            # Log retrieval record
            retrieval_record = {
                "retrieval_id": retrieval_id,
                "query": query,
                "research_domain": research_domain,
                "max_results": max_results,
                "initial_count": len(initial_results),
                "final_count": len(final_results),
                "fallback_used": fallback_decision["should_fallback"] and enable_fallback,
                "quality_improved": final_quality_metrics["overall_score"] > quality_metrics["overall_score"],
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "timestamp": start_time.isoformat()
            }
            self.retrieval_history.append(retrieval_record)
            
            print(f"[DEBUG] ✅ Smart retrieval completed!")
            print(f"[DEBUG] Final results: {len(final_results)} documents")
            print(f"[DEBUG] Quality score: {final_quality_metrics['overall_score']:.2f}")
            
            return {
                "success": True,
                "documents": final_results,
                "quality_metrics": final_quality_metrics,
                "fallback_used": fallback_decision["should_fallback"] and enable_fallback,
                "fallback_info": fallback_info,
                "retrieval_id": retrieval_id,
                "query": query,
                "research_domain": research_domain,
                "processing_time_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Smart retrieval failed: {e}")
            
            return {
                "success": False,
                "error": f"Smart retrieval failed: {str(e)}",
                "retrieval_id": retrieval_id,
                "query": query,
                "research_domain": research_domain,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics."""
        if not self.retrieval_history:
            return {
                "total_retrievals": 0,
                "fallback_usage_rate": 0.0,
                "average_quality_improvement": 0.0,
                "average_processing_time": 0.0
            }
        
        fallback_used = sum(1 for r in self.retrieval_history if r.get("fallback_used", False))
        quality_improved = sum(1 for r in self.retrieval_history if r.get("quality_improved", False))
        avg_time = sum(r.get("processing_time", 0) for r in self.retrieval_history) / len(self.retrieval_history)
        
        return {
            "total_retrievals": len(self.retrieval_history),
            "fallback_usage_rate": fallback_used / len(self.retrieval_history),
            "quality_improvement_rate": quality_improved / len(self.retrieval_history),
            "average_processing_time": avg_time,
            "last_retrieval": self.retrieval_history[-1]["timestamp"] if self.retrieval_history else None
        } 