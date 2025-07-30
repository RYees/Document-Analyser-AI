from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import asyncio
from datetime import datetime

from ..core.workflow_orchestrator import WorkflowOrchestrator
from ..core.research_state import ResearchState, ProjectStatus, ResearchPhase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Web3 Research Assistant API",
    description="AI-powered research automation with human-in-the-loop integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow orchestrator
orchestrator = WorkflowOrchestrator()

# Pydantic models for API requests/responses
class ProjectCreateRequest(BaseModel):
    title: str
    description: str
    research_domain: str
    config: Optional[Dict[str, Any]] = {}

class ProjectResponse(BaseModel):
    project_id: str
    title: str
    description: str
    research_domain: str
    status: str
    current_phase: str
    created_at: str
    updated_at: str

class HumanFeedbackRequest(BaseModel):
    task_id: Optional[str] = None
    feedback_type: str  # approval, revision, rejection
    content: str
    reviewer: str
    specific_changes: Optional[List[Dict[str, Any]]] = []

class WorkflowInfoResponse(BaseModel):
    phases: List[str]
    agents: Dict[str, Dict[str, Any]]
    checkpoint_memory: str

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Web3 Research Assistant API"
    }

# Get workflow information
@app.get("/workflow/info", response_model=WorkflowInfoResponse)
async def get_workflow_info():
    """Get workflow information and available agents"""
    try:
        info = orchestrator.get_workflow_info()
        return WorkflowInfoResponse(**info)
    except Exception as e:
        logger.error(f"Failed to get workflow info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create new research project
@app.post("/projects", response_model=ProjectResponse)
async def create_project(request: ProjectCreateRequest, background_tasks: BackgroundTasks):
    """Create and start a new research project"""
    try:
        logger.info(f"Creating new research project: {request.title}")
        
        # Prepare project configuration
        project_config = {
            "title": request.title,
            "description": request.description,
            "research_domain": request.research_domain,
            "config": request.config or {}
        }
        
        # Start project in background
        project_id = await orchestrator.start_research_project(project_config)
        
        # Get initial project status
        project_status = await orchestrator.get_project_status(project_id)
        
        return ProjectResponse(
            project_id=project_id,
            title=request.title,
            description=request.description,
            research_domain=request.research_domain,
            status=project_status.get("status", "initialized"),
            current_phase=project_status.get("current_phase", "literature_review"),
            created_at=project_status.get("created_at", datetime.utcnow().isoformat()),
            updated_at=project_status.get("updated_at", datetime.utcnow().isoformat())
        )
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get project status
@app.get("/projects/{project_id}")
async def get_project_status(project_id: str):
    """Get current status of a research project"""
    try:
        project_status = await orchestrator.get_project_status(project_id)
        
        if "error" in project_status:
            raise HTTPException(status_code=404, detail=project_status["error"])
        
        return project_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# List all projects
@app.get("/projects")
async def list_projects():
    """List all research projects"""
    try:
        # This would typically query a database
        # For now, return a placeholder response
        return {
            "projects": [],
            "total": 0,
            "message": "Project listing not yet implemented"
        }
        
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Submit human feedback
@app.post("/projects/{project_id}/feedback")
async def submit_human_feedback(project_id: str, feedback: HumanFeedbackRequest):
    """Submit human feedback for a research project"""
    try:
        logger.info(f"Submitting human feedback for project {project_id}")
        
        # Prepare feedback data
        feedback_data = {
            "task_id": feedback.task_id,
            "feedback_type": feedback.feedback_type,
            "content": feedback.content,
            "reviewer": feedback.reviewer,
            "specific_changes": feedback.specific_changes or []
        }
        
        # Resume workflow with feedback
        updated_state = await orchestrator.resume_workflow(project_id, feedback_data)
        
        return {
            "message": "Human feedback submitted successfully",
            "project_id": project_id,
            "updated_status": updated_state.get("status"),
            "current_phase": updated_state.get("current_phase"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        logger.error(f"Project not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit human feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get pending human reviews
@app.get("/projects/{project_id}/pending-reviews")
async def get_pending_reviews(project_id: str):
    """Get pending human reviews for a project"""
    try:
        project_status = await orchestrator.get_project_status(project_id)
        
        if "error" in project_status:
            raise HTTPException(status_code=404, detail=project_status["error"])
        
        pending_reviews = project_status.get("pending_human_reviews", [])
        human_feedback_queue = project_status.get("human_feedback_queue", [])
        
        return {
            "project_id": project_id,
            "pending_reviews": pending_reviews,
            "feedback_queue": [
                feedback for feedback in human_feedback_queue 
                if not feedback.get("resolved", False)
            ],
            "requires_human_review": project_status.get("status") == "waiting_human_review"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pending reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get project tasks
@app.get("/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str):
    """Get all tasks for a research project"""
    try:
        project_status = await orchestrator.get_project_status(project_id)
        
        if "error" in project_status:
            raise HTTPException(status_code=404, detail=project_status["error"])
        
        tasks = project_status.get("tasks", [])
        
        return {
            "project_id": project_id,
            "tasks": tasks,
            "total_tasks": len(tasks),
            "completed_tasks": len([t for t in tasks if t.get("status") == "completed"]),
            "failed_tasks": len([t for t in tasks if t.get("status") == "failed"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get specific task details
@app.get("/projects/{project_id}/tasks/{task_id}")
async def get_task_details(project_id: str, task_id: str):
    """Get details of a specific task"""
    try:
        project_status = await orchestrator.get_project_status(project_id)
        
        if "error" in project_status:
            raise HTTPException(status_code=404, detail=project_status["error"])
        
        tasks = project_status.get("tasks", [])
        task = next((t for t in tasks if t.get("id") == task_id), None)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pause project
@app.post("/projects/{project_id}/pause")
async def pause_project(project_id: str):
    """Pause a research project"""
    try:
        # This would update the project status to paused
        # For now, return a placeholder response
        return {
            "message": "Project paused successfully",
            "project_id": project_id,
            "status": "paused",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to pause project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Resume project
@app.post("/projects/{project_id}/resume")
async def resume_project(project_id: str):
    """Resume a paused research project"""
    try:
        # This would resume the project workflow
        # For now, return a placeholder response
        return {
            "message": "Project resumed successfully",
            "project_id": project_id,
            "status": "in_progress",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to resume project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cancel project
@app.post("/projects/{project_id}/cancel")
async def cancel_project(project_id: str):
    """Cancel a research project"""
    try:
        # This would cancel the project and clean up resources
        # For now, return a placeholder response
        return {
            "message": "Project cancelled successfully",
            "project_id": project_id,
            "status": "cancelled",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get project results
@app.get("/projects/{project_id}/results")
async def get_project_results(project_id: str):
    """Get research results for a completed project"""
    try:
        project_status = await orchestrator.get_project_status(project_id)
        
        if "error" in project_status:
            raise HTTPException(status_code=404, detail=project_status["error"])
        
        if project_status.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Project not yet completed")
        
        return {
            "project_id": project_id,
            "literature_review": project_status.get("literature_review"),
            "research_questions": project_status.get("research_questions"),
            "methodology": project_status.get("methodology"),
            "results": project_status.get("results"),
            "document": project_status.get("document"),
            "completed_at": project_status.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates (placeholder)
@app.websocket("/ws/projects/{project_id}")
async def websocket_endpoint(websocket, project_id: str):
    """WebSocket endpoint for real-time project updates"""
    try:
        await websocket.accept()
        
        # Send initial project status
        project_status = await orchestrator.get_project_status(project_id)
        await websocket.send_text(str(project_status))
        
        # Keep connection alive and send updates
        while True:
            await asyncio.sleep(5)  # Check for updates every 5 seconds
            
            # Get updated status
            updated_status = await orchestrator.get_project_status(project_id)
            await websocket.send_text(str(updated_status))
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 