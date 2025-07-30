"""
Data Service - Manages document retrieval, storage, and vector database operations.
Enhanced with smart retrieval and CORE API fallback capabilities.
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
from api.services.smart_retrieval_service import SmartRetrievalService

class DataService:
    """
    Enhanced service layer for managing data operations.
    
    Provides unified interface for:
    1. Smart document retrieval with fallback
    2. Manual data extraction from CORE API
    3. Vector store operations
    4. Analytics and monitoring
    """
    
    def __init__(self):
        """Initialize data service with enhanced capabilities."""
        # Core services
        self.extraction_service = DataExtractionService()
        self.smart_retrieval_service = SmartRetrievalService()
        
        # Legacy vector store support
        self.vector_store_manager = None
        self.collection_name = "ResearchPaper"
        self.research_domain = "General"
        
        # Track all operations
        self.operation_history = []
    
    def _initialize_vector_store(self, collection_name: str = "ResearchPaper", research_domain: str = "General"):
        """Initialize vector store manager for legacy operations."""
        if not self.vector_store_manager or self.collection_name != collection_name or self.research_domain != research_domain:
            self.vector_store_manager = VectorStoreManager(collection_name=collection_name, research_domain=research_domain)
            self.collection_name = collection_name
            self.research_domain = research_domain

    async def retrieve_documents(self, query: str, research_domain: str = "General", max_results: int = 10) -> Dict[str, Any]:
        """
        Enhanced document retrieval with smart fallback to CORE API.
        
        This method now:
        1. Tries vector store first
        2. Evaluates result quality
        3. Falls back to CORE API if needed
        4. Re-queries and merges results
        
        Args:
            query: Search query
            research_domain: Research domain/topic
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing retrieved documents and metadata
        """
        try:
            print(f"\n" + "🔍"*50)
            print(f"🔍 ENHANCED DATA SERVICE - SMART RETRIEVAL")
            print(f"🔍"*50)
            print(f"[DATA_SERVICE] 📋 Request parameters:")
            print(f"[DATA_SERVICE]   Query: '{query}'")
            print(f"[DATA_SERVICE]   Research Domain: '{research_domain}'")
            print(f"[DATA_SERVICE]   Max Results: {max_results}")
            print(f"[DATA_SERVICE]")
            print(f"[DATA_SERVICE] 🧠 SMART RETRIEVAL FLOW:")
            print(f"[DATA_SERVICE]   1️⃣ Try vector store similarity search")
            print(f"[DATA_SERVICE]   2️⃣ Calculate quality metrics (quantity, certainty, recency)")
            print(f"[DATA_SERVICE]   3️⃣ Decide if CORE API fallback needed")
            print(f"[DATA_SERVICE]   4️⃣ If needed: Fetch → Extract → Store → Re-query")
            print(f"[DATA_SERVICE]   5️⃣ Merge and optimize results")
            print(f"[DATA_SERVICE]")
            
            # Log operation
            operation_id = str(uuid.uuid4())
            self.operation_history.append({
                "operation_id": operation_id,
                "operation": "enhanced_retrieve_documents",
                "query": query,
                "research_domain": research_domain,
                "max_results": max_results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "running"
            })
            
            # Use smart retrieval service
            print(f"[DATA_SERVICE] 🎯 Delegating to SmartRetrievalService...")
            retrieval_result = await self.smart_retrieval_service.smart_retrieve_documents(
                query=query,
                research_domain=research_domain,
                max_results=max_results,
                enable_fallback=True
            )
            
            print(f"[DATA_SERVICE] 📊 SmartRetrievalService response:")
            print(f"[DATA_SERVICE]   Success: {retrieval_result.get('success', False)}")
            print(f"[DATA_SERVICE]   Documents count: {len(retrieval_result.get('documents', []))}")
            print(f"[DATA_SERVICE]   Fallback used: {retrieval_result.get('fallback_used', False)}")
            if retrieval_result.get('fallback_used'):
                fallback_info = retrieval_result.get('fallback_info', {})
                print(f"[DATA_SERVICE]   📈 Fallback details:")
                print(f"[DATA_SERVICE]     Extraction used: {fallback_info.get('extraction_used', False)}")
                if fallback_info.get('extraction_used'):
                    print(f"[DATA_SERVICE]     Papers fetched: {fallback_info.get('papers_fetched', 0)}")
                    print(f"[DATA_SERVICE]     Chunks stored: {fallback_info.get('chunks_stored', 0)}")
                    print(f"[DATA_SERVICE]     Fresh search count: {fallback_info.get('fresh_search_count', 0)}")
            
            quality_metrics = retrieval_result.get('quality_metrics', {})
            print(f"[DATA_SERVICE] 🎯 Quality metrics:")
            print(f"[DATA_SERVICE]   Overall score: {quality_metrics.get('overall_score', 0.0):.2f}")
            print(f"[DATA_SERVICE]   Certainty score: {quality_metrics.get('certainty_score', 0.0):.2f}")
            print(f"[DATA_SERVICE]   Recency score: {quality_metrics.get('recency_score', 0.0):.2f}")
            print(f"[DATA_SERVICE]   Recent results: {quality_metrics.get('recent_results', 0)}")
            
            if not retrieval_result["success"]:
                # Update operation status
                for op in self.operation_history:
                    if op["operation_id"] == operation_id:
                        op["status"] = "failed"
                        op["error"] = retrieval_result.get("error", "Unknown error")
                        break
                
                print(f"[DATA_SERVICE] ❌ Smart retrieval failed!")
                print(f"[DATA_SERVICE]   Error: {retrieval_result.get('error', 'Unknown error')}")
                print(f"🔍"*50 + "\n")
                
                return {
                    "success": False,
                    "error": retrieval_result.get("error", "Smart retrieval failed"),
                    "operation_id": operation_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            documents = retrieval_result["documents"]
            
            # Update operation status with enhanced metadata
            for op in self.operation_history:
                if op["operation_id"] == operation_id:
                    op.update({
                        "status": "completed",
                        "result_count": len(documents),
                        "fallback_used": retrieval_result.get("fallback_used", False),
                        "quality_score": retrieval_result.get("quality_metrics", {}).get("overall_score", 0.0),
                        "processing_time": retrieval_result.get("processing_time_seconds", 0.0)
                    })
                    break
            
            print(f"[DATA_SERVICE] ✅ Enhanced retrieval completed successfully!")
            print(f"[DATA_SERVICE]   Final document count: {len(documents)}")
            print(f"[DATA_SERVICE]   Fallback was used: {retrieval_result.get('fallback_used', False)}")
            print(f"[DATA_SERVICE]   Final quality score: {quality_metrics.get('overall_score', 0.0):.2f}")
            print(f"[DATA_SERVICE]   Processing time: {retrieval_result.get('processing_time_seconds', 0.0):.2f}s")
            
            # Log sample document titles for verification
            if documents:
                print(f"[DATA_SERVICE] 📚 Sample retrieved documents:")
                for i, doc in enumerate(documents[:3]):
                    title = doc.get('title', 'No title')[:50] + "..." if len(doc.get('title', '')) > 50 else doc.get('title', 'No title')
                    domain = doc.get('research_domain', 'Unknown')
                    year = doc.get('year', 'Unknown')
                    source_priority = doc.get('source_priority', 'N/A')
                    print(f"[DATA_SERVICE]     {i+1}. {title}")
                    print(f"[DATA_SERVICE]        Domain: {domain}, Year: {year}, Source: {source_priority}")
                
                if len(documents) > 3:
                    print(f"[DATA_SERVICE]     ... and {len(documents) - 3} more documents")
            
            print(f"🔍"*50 + "\n")
            
            return {
                "success": True,
                "data": {
                    "documents": documents or [],
                    "query": query,
                    "research_domain": research_domain,
                    "total_count": len(documents) if documents else 0,
                    "max_results": max_results,
                    # Enhanced metadata
                    "quality_metrics": retrieval_result.get("quality_metrics", {}),
                    "fallback_used": retrieval_result.get("fallback_used", False),
                    "fallback_info": retrieval_result.get("fallback_info", {}),
                    "retrieval_id": retrieval_result.get("retrieval_id", ""),
                    "processing_time_seconds": retrieval_result.get("processing_time_seconds", 0.0)
                },
                "operation_id": operation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"[DATA_SERVICE] ❌ ENHANCED RETRIEVAL FAILED!")
            print(f"[DATA_SERVICE]   Exception: {str(e)}")
            print(f"[DATA_SERVICE]   Exception type: {type(e).__name__}")
            import traceback
            print(f"[DATA_SERVICE]   Traceback: {traceback.format_exc()}")
            print(f"🔍"*50 + "\n")
            
            # Update operation status
            for op in self.operation_history:
                if op["operation_id"] == operation_id:
                    op["status"] = "failed"
                    op["error"] = str(e)
                    break
            
            return {
                "success": False,
                "error": f"Document retrieval failed: {str(e)}",
                "operation_id": operation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def extract_documents_from_core_api(
        self, 
        query: str, 
        research_domain: str = "General", 
        max_results: int = 20,
        year_from: int = 2020,
        year_to: int = 2024
    ) -> Dict[str, Any]:
        """
        Manual document extraction from CORE API.
        
        Use this when you specifically want to fetch fresh documents
        without the smart retrieval logic.
        
        Args:
            query: Search query for CORE API
            research_domain: Research domain/field
            max_results: Maximum number of papers to fetch
            year_from: Start year for search
            year_to: End year for search
            
        Returns:
            Dict containing extraction results
        """
        try:
            print(f"[DEBUG] ===== MANUAL CORE API EXTRACTION =====")
            print(f"[DEBUG] Query: '{query}'")
            print(f"[DEBUG] Research Domain: {research_domain}")
            
            # Log operation
            operation_id = str(uuid.uuid4())
            self.operation_history.append({
                "operation_id": operation_id,
                "operation": "manual_core_api_extraction",
                "query": query,
                "research_domain": research_domain,
                "max_results": max_results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "running"
            })
            
            # Use extraction service
            extraction_result = await self.extraction_service.extract_and_store_documents(
                query=query,
                research_domain=research_domain,
                max_results=max_results,
                year_from=year_from,
                year_to=year_to
            )
            
            # Update operation status
            for op in self.operation_history:
                if op["operation_id"] == operation_id:
                    if extraction_result["success"]:
                        op.update({
                            "status": "completed",
                            "papers_fetched": extraction_result.get("papers_fetched", 0),
                            "chunks_stored": extraction_result.get("chunks_stored", 0),
                            "processing_time": extraction_result.get("processing_time_seconds", 0.0)
                        })
                    else:
                        op.update({
                            "status": "failed",
                            "error": extraction_result.get("error", "Unknown error")
                        })
                    break
            
            return {
                "success": extraction_result["success"],
                "data": extraction_result if extraction_result["success"] else {},
                "error": extraction_result.get("error") if not extraction_result["success"] else None,
                "operation_id": operation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Manual extraction failed: {e}")
            
            # Update operation status
            for op in self.operation_history:
                if op["operation_id"] == operation_id:
                    op["status"] = "failed"
                    op["error"] = str(e)
                    break
            
            return {
                "success": False,
                "error": f"Manual extraction failed: {str(e)}",
                "operation_id": operation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def legacy_retrieve_documents(self, query: str, research_domain: str = "General", max_results: int = 10) -> Dict[str, Any]:
        """
        Legacy document retrieval (vector store only, no fallback).
        
        This is the old behavior - only searches existing vector store.
        Kept for backward compatibility.
        
        Args:
            query: Search query
            research_domain: Research domain/topic
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing retrieved documents and metadata
        """
        try:
            self._initialize_vector_store(self.collection_name, research_domain)
            
            # Log operation
            operation_id = str(uuid.uuid4())
            self.operation_history.append({
                "operation_id": operation_id,
                "operation": "legacy_retrieve_documents",
                "query": query,
                "research_domain": research_domain,
                "max_results": max_results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "running"
            })
            
            # Perform legacy retrieval using similarity search only
            documents = self.vector_store_manager.similarity_search(query, max_results)
            
            # Update operation status
            for op in self.operation_history:
                if op["operation_id"] == operation_id:
                    op["status"] = "completed"
                    op["result_count"] = len(documents) if documents else 0
                    break
            
            return {
                "success": True,
                "data": {
                    "documents": documents or [],
                    "query": query,
                    "research_domain": research_domain,
                    "total_count": len(documents) if documents else 0,
                    "max_results": max_results,
                    "method": "legacy_vector_store_only"
                },
                "operation_id": operation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Legacy document retrieval failed: {e}")
            
            # Update operation status
            for op in self.operation_history:
                if op["operation_id"] == operation_id:
                    op["status"] = "failed"
                    op["error"] = str(e)
                    break
            
            return {
                "success": False,
                "error": f"Legacy document retrieval failed: {str(e)}",
                "operation_id": operation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive service statistics.
        
        Returns:
            Dict containing service statistics from all components
        """
        # Get stats from sub-services
        extraction_stats = self.extraction_service.get_extraction_stats()
        retrieval_stats = self.smart_retrieval_service.get_retrieval_stats()
        
        # Calculate operation stats
        if self.operation_history:
            successful_ops = [op for op in self.operation_history if op.get("status") == "completed"]
            failed_ops = [op for op in self.operation_history if op.get("status") == "failed"]
            
            operation_stats = {
                "total_operations": len(self.operation_history),
                "successful_operations": len(successful_ops),
                "failed_operations": len(failed_ops),
                "success_rate": len(successful_ops) / len(self.operation_history),
                "last_operation": self.operation_history[-1]["timestamp"]
            }
        else:
            operation_stats = {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "success_rate": 0.0,
                "last_operation": None
            }
        
        return {
            "service_overview": operation_stats,
            "extraction_service": extraction_stats,
            "smart_retrieval_service": retrieval_stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_operation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent operation history.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of operation records
        """
        return self.operation_history[-limit:] if self.operation_history else [] 