"""
Data management route handlers for the Research Pipeline API.
Contains endpoints for document retrieval and vector database operations.
"""

import sys
import os
from datetime import datetime, timezone
from typing import List, Optional

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from api.models.requests import DataRequest
from api.models.responses import (
    DataResponse, DataStatisticsResponse
)
from api.services.data_service import DataService

router = APIRouter()

# Initialize data service
data_service = DataService()

@router.post("/retrieve", response_model=DataResponse)
async def retrieve_documents(request: DataRequest):
    """
    Retrieve documents from the vector database based on a query.
    
    This endpoint searches the vector database for relevant documents:
    - Performs semantic search using the provided query
    - Returns documents with relevance scores
    - Supports filtering by research domain
    - Limits results based on max_results parameter
    """
    try:
        if not request.query:
            raise HTTPException(
                status_code=400,
                detail="Query is required for document retrieval"
            )
        
        result = await data_service.retrieve_documents(
            query=request.query,
            research_domain=request.research_domain,
            max_results=request.max_results
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Document retrieval failed: {result.get('error', 'Unknown error')}"
            )
        
        response = DataResponse(
            success=True,
            data=result["data"],
            operation_id=result.get("operation_id"),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document retrieval failed: {str(e)}"
        )

@router.post("/store", response_model=DataResponse)
async def store_documents(request: DataRequest):
    """
    Store documents in the vector database.
    
    This endpoint stores documents for later retrieval:
    - Processes and chunks documents
    - Generates embeddings
    - Stores in vector database with metadata
    - Supports batch document storage
    """
    try:
        if not request.documents:
            raise HTTPException(
                status_code=400,
                detail="Documents are required for storage"
            )
        
        result = await data_service.store_documents(
            documents=request.documents,
            research_domain=request.research_domain,
            collection_name=request.collection_name
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Document storage failed: {result.get('error', 'Unknown error')}"
            )
        
        response = DataResponse(
            success=True,
            data=result["data"],
            operation_id=result.get("operation_id"),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document storage failed: {str(e)}"
        )

@router.get("/collections", response_model=DataResponse)
async def list_collections():
    """
    List all available vector database collections.
    
    Returns information about all collections including:
    - Collection names and descriptions
    - Document counts
    - Research domains
    - Creation dates
    """
    try:
        result = data_service.list_collections()
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list collections: {result.get('error', 'Unknown error')}"
            )
        
        response = DataResponse(
            success=True,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list collections: {str(e)}"
        )

@router.get("/collections/{collection_name}", response_model=DataResponse)
async def get_collection_info(
    collection_name: str = Path(..., description="Name of the collection")
):
    """
    Get detailed information about a specific collection.
    
    Returns collection details including:
    - Document count and metadata
    - Research domain information
    - Index statistics
    - Performance metrics
    """
    try:
        result = data_service.get_collection_info(collection_name)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Collection not found: {collection_name}"
            )
        
        response = DataResponse(
            success=True,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collection info: {str(e)}"
        )

@router.delete("/collections/{collection_name}")
async def delete_collection(
    collection_name: str = Path(..., description="Name of the collection to delete")
):
    """
    Delete a collection and all its documents.
    
    This will permanently remove the collection and all stored documents.
    Use with caution as this action cannot be undone.
    """
    try:
        result = data_service.delete_collection(collection_name)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Collection not found: {collection_name}"
            )
        
        return {
            "success": True,
            "message": f"Collection {collection_name} deleted successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete collection: {str(e)}"
        )

@router.delete("/documents")
async def delete_documents(request: DataRequest):
    """
    Delete specific documents from a collection.
    
    Removes documents by their IDs from the specified collection.
    Useful for cleaning up specific documents without deleting the entire collection.
    """
    try:
        if not request.document_ids:
            raise HTTPException(
                status_code=400,
                detail="Document IDs are required for deletion"
            )
        
        result = data_service.delete_documents(
            document_ids=request.document_ids,
            collection_name=request.collection_name
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Document deletion failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": f"Deleted {len(request.document_ids)} documents successfully",
            "data": result["data"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document deletion failed: {str(e)}"
        )

@router.get("/statistics", response_model=DataStatisticsResponse)
async def get_data_statistics(
    collection_name: Optional[str] = Query(None, description="Filter by collection name"),
    research_domain: Optional[str] = Query(None, description="Filter by research domain")
):
    """
    Get comprehensive data statistics.
    
    Returns statistics about the vector database including:
    - Total documents and collections
    - Storage usage and performance
    - Query statistics and trends
    - Research domain distribution
    """
    try:
        result = data_service.get_data_statistics(
            collection_name=collection_name,
            research_domain=research_domain
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get data statistics: {result.get('error', 'Unknown error')}"
            )
        
        response = DataStatisticsResponse(
            success=True,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get data statistics: {str(e)}"
        )

@router.get("/operations/history", response_model=DataResponse)
async def get_operation_history(
    limit: int = Query(20, ge=1, le=100, description="Number of operations to return"),
    operation_type: Optional[str] = Query(None, description="Filter by operation type")
):
    """
    Get history of data operations.
    
    Returns a history of recent data operations including:
    - Document retrievals and storage
    - Collection management operations
    - Performance metrics
    - Error logs
    """
    try:
        result = data_service.get_operation_history(
            limit=limit,
            operation_type=operation_type
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get operation history: {result.get('error', 'Unknown error')}"
            )
        
        response = DataResponse(
            success=True,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get operation history: {str(e)}"
        )

@router.post("/search/similar", response_model=DataResponse)
async def find_similar_documents(
    request: DataRequest,
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum similarity threshold")
):
    """
    Find documents similar to a given document or query.
    
    Performs similarity search to find documents that are semantically similar:
    - Uses vector similarity calculations
    - Supports both document content and query-based search
    - Configurable similarity threshold
    - Returns similarity scores
    """
    try:
        if not request.query and not request.documents:
            raise HTTPException(
                status_code=400,
                detail="Either query or document content is required for similarity search"
            )
        
        result = await data_service.find_similar_documents(
            query=request.query,
            documents=request.documents,
            research_domain=request.research_domain,
            max_results=request.max_results,
            similarity_threshold=similarity_threshold
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Similarity search failed: {result.get('error', 'Unknown error')}"
            )
        
        response = DataResponse(
            success=True,
            data=result["data"],
            operation_id=result.get("operation_id"),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Similarity search failed: {str(e)}"
        )

@router.post("/index/rebuild")
async def rebuild_index(
    collection_name: str = Query(..., description="Name of the collection to rebuild"),
    force: bool = Query(False, description="Force rebuild even if index exists")
):
    """
    Rebuild the vector index for a collection.
    
    This operation recreates the vector index for better search performance:
    - Recalculates all embeddings
    - Optimizes index structure
    - Improves search speed and accuracy
    - Can be time-consuming for large collections
    """
    try:
        result = await data_service.rebuild_index(collection_name, force)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Index rebuild failed: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": f"Index for collection {collection_name} rebuilt successfully",
            "data": result["data"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Index rebuild failed: {str(e)}"
        )

@router.get("/health", response_model=DataResponse)
async def get_data_service_health():
    """
    Get the health status of the data service.
    
    Returns health information including:
    - Vector database connectivity
    - Service status and uptime
    - Performance metrics
    - Error rates
    """
    try:
        result = data_service.get_health_status()
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Data service health check failed: {result.get('error', 'Unknown error')}"
            )
        
        response = DataResponse(
            success=True,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data service health check failed: {str(e)}"
        ) 