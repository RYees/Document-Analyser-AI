"""
Pipeline Service - Orchestrates the complete research pipeline with quality control and state management.
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services.agent_service import AgentService
from api.services.data_service import DataService
from api.services.quality_service import QualityService
from api.services.report_service import ReportService
from api.utils.pipeline_storage_manager import PipelineStorageManager

class PipelineService:
    """
    Service layer for orchestrating the complete research pipeline.
    Manages pipeline state, quality control, and agent coordination.
    """
    
    def __init__(self):
        """Initialize pipeline service with all required services."""
        self.agent_service = AgentService()
        self.data_service = DataService()
        self.quality_service = QualityService()
        self.report_service = ReportService()
        self.storage_manager = PipelineStorageManager()
        
        # Pipeline state management (in-memory for active pipelines)
        self.pipeline_states = {}
        
        # Pipeline configuration
        self.default_config = {
            "enable_supervisor": False,  # TEMPORARILY DISABLED
            "auto_retry_failed_steps": True,
            "save_intermediate_results": True,
            "quality_threshold": 0.6,
            "max_retries": 3
        }
    
    async def _handle_step_execution(self, pipeline_id: str, step_number: int, step_name: str, 
                                   execution_func, *args, **kwargs):
        """
        Helper method to handle step execution with consistent error handling.
        Returns (success: bool, result: dict, error_msg: str)
        """
        try:
            print(f"[PIPELINE] 🔄 Step {step_number}: Starting {step_name}...")
            await self._update_pipeline_step(pipeline_id, step_number, step_name, "running")
            
            result = await execution_func(*args, **kwargs)
            print(f"[PIPELINE]   {step_name} result success: {result.get('success', False) if result else False}")
            
            # Check for success and no errors
            if not result or "error" in result:
                error_msg = result.get("error", "Unknown error") if result else "No result returned"
                print(f"[PIPELINE]   ❌ {step_name} failed: {error_msg}")
                await self._update_pipeline_step(pipeline_id, step_number, step_name, "failed", error_msg)
                await self._finalize_pipeline(pipeline_id, "failed", f"{step_name} failed: {error_msg}")
                return False, None, error_msg
            
            print(f"[PIPELINE]   ✅ {step_name} successful!")
            await self._update_pipeline_step(pipeline_id, step_number, step_name, "completed", f"{step_name} completed", result)
            return True, result, None
            
        except Exception as error:
            print(f"[PIPELINE]   ❌ {step_name.upper()} FAILED!")
            print(f"[PIPELINE]     {step_name} error: {error}")
            await self._update_pipeline_step(pipeline_id, step_number, step_name, "failed", str(error))
            await self._finalize_pipeline(pipeline_id, "failed", f"{step_name} failed: {str(error)}")
            return False, None, str(error)

    async def _step_document_retrieval(self, pipeline_id: str, query: str, research_domain: str) -> tuple[bool, dict, str]:
        """Step 1: Document Retrieval"""
        success, documents_result, error = await self._handle_step_execution(
            pipeline_id, 1, "Document Retrieval", 
            self.data_service.retrieve_documents, query, research_domain
        )
        if not success:
            return False, None, error
        
        # Check for non-empty documents
        documents = documents_result["data"]["documents"]
        if not documents:
            error_msg = "No documents found"
            print(f"[PIPELINE]   ❌ Document retrieval failed: {error_msg}")
            await self._update_pipeline_step(pipeline_id, 1, "Document Retrieval", "failed", error_msg)
            await self._finalize_pipeline(pipeline_id, "failed", f"Document retrieval failed: {error_msg}")
            return False, None, error_msg
        
        print(f"[PIPELINE] ✅ Document retrieval successful! Got {len(documents)} documents")
        return True, documents_result, None

    async def _step_literature_review(self, pipeline_id: str, documents: list, research_domain: str) -> tuple[bool, dict, str]:
        """Step 2: Literature Review"""
        success, literature_result, error = await self._handle_step_execution(
            pipeline_id, 2, "Literature Review",
            self.agent_service.run_literature_review, documents, research_domain
        )
        if not success:
            return False, None, error
        
        return True, literature_result, None

    async def _step_initial_coding(self, pipeline_id: str, documents: list, research_domain: str) -> tuple[bool, dict, str]:
        """Step 3: Initial Coding"""
        success, coding_result, error = await self._handle_step_execution(
            pipeline_id, 3, "Initial Coding",
            self.agent_service.run_initial_coding, documents, research_domain
        )
        if not success:
            return False, None, error
        
        return True, coding_result, None

    async def _step_thematic_grouping(self, pipeline_id: str, coded_units: list, research_domain: str) -> tuple[bool, dict, str]:
        """Step 4: Thematic Grouping"""
        success, thematic_result, error = await self._handle_step_execution(
            pipeline_id, 4, "Thematic Grouping",
            self.agent_service.run_thematic_grouping, coded_units, research_domain
        )
        if not success:
            return False, None, error
        
        return True, thematic_result, None

    async def _step_theme_refinement(self, pipeline_id: str, themes: list, research_domain: str) -> tuple[bool, dict, str]:
        """Step 5: Theme Refinement"""
        success, refinement_result, error = await self._handle_step_execution(
            pipeline_id, 5, "Theme Refinement",
            self.agent_service.run_theme_refinement, themes, research_domain
        )
        if not success:
            return False, None, error
        
        return True, refinement_result, None

    async def _step_report_generation(self, pipeline_id: str, all_sections: dict) -> tuple[bool, dict, str]:
        """Step 6: Report Generation"""
        success, report_result, error = await self._handle_step_execution(
            pipeline_id, 6, "Report Generation",
            self.agent_service.run_report_generation, all_sections
        )
        if not success:
            return False, None, error
        
        return True, report_result, None

    async def run_full_pipeline(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete research pipeline from start to finish.
        
        Args:
            request_data: Dictionary containing pipeline parameters
                - query: Search query
                - research_domain: Research domain/topic
                - max_results: Maximum documents to retrieve
                - quality_threshold: Minimum quality score
                - pipeline_config: Optional pipeline configuration
                
        Returns:
            Dict containing pipeline results and status
        """
        try:
            print(f"[PIPELINE] 📋 Step 1: Starting Extracting parameters (SMART SYSTEM)...")
            
            # Extract parameters
            query = request_data.get("query", "")
            research_domain = request_data.get("research_domain", "General")
            max_results = request_data.get("max_results", 10)
            quality_threshold = request_data.get("quality_threshold", 0.6)
            
            # Handle pipeline_config properly - it could be None
            pipeline_config_data = request_data.get("pipeline_config") or {}
            pipeline_config = {**self.default_config, **pipeline_config_data}

            # Initialize pipeline state (without pipeline_id - will be generated by storage)
            pipeline_state = {
                "status": "running",
                "current_step": 0,
                "total_steps": 6,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "query": query,
                "research_domain": research_domain,
                "max_results": max_results,
                "quality_threshold": quality_threshold,
                "pipeline_config": pipeline_config,
                "steps": {
                    "1": {"name": "Document Retrieval", "status": "pending"},
                    "2": {"name": "Literature Review", "status": "pending"},
                    "3": {"name": "Initial Coding", "status": "pending"},
                    "4": {"name": "Thematic Grouping", "status": "pending"},
                    "5": {"name": "Theme Refinement", "status": "pending"},
                    "6": {"name": "Report Generation", "status": "pending"}
                },
                "results": {
                    "documents": None,           # Step 1: Document Retrieval output
                    "literature_review": None,   # Step 2: Literature Review output
                    "initial_coding": None,      # Step 3: Initial Coding output
                    "thematic_grouping": None,   # Step 4: Thematic Grouping output
                    "theme_refinement": None,    # Step 5: Theme Refinement output
                    "report_generation": None    # Step 6: Report Generation output
                },
                "quality_scores": {},
                "supervisor_decisions": {},
                "errors": []
            }

            # Store initial pipeline state and get the generated ID
            try:
                print(f"[PIPELINE] First creation 💾 Calling storage_manager.create_pipeline()...")
                pipeline_id = self.storage_manager.create_pipeline(pipeline_state)
                print(f"[PIPELINE] ✅ Pipeline created with ID: {pipeline_id}")
                
                # Add the pipeline_id to the state for memory storage
                pipeline_state["pipeline_id"] = pipeline_id
                self.pipeline_states[pipeline_id] = pipeline_state
                
            except Exception as storage_error:
                import traceback
                print(f"[PIPELINE] Storage traceback: {traceback.format_exc()}")
                
                # Return error immediately if storage fails
                return {
                    "success": False,
                    "pipeline_id": "unknown",
                    "error": f"Pipeline storage failed: {str(storage_error)}"
                }

            # Step 1: Document Retrieval
            success, documents_result, error = await self._step_document_retrieval(pipeline_id, query, research_domain)
            if not success:
                return self._get_pipeline_response(pipeline_id)

            # Step 2: Literature Review
            success, literature_result, error = await self._step_literature_review(pipeline_id, documents_result["data"]["documents"], research_domain)
            if not success:
                return self._get_pipeline_response(pipeline_id)

            # Step 3: Initial Coding
            success, coding_result, error = await self._step_initial_coding(pipeline_id, documents_result["data"]["documents"], research_domain)
            if not success:
                return self._get_pipeline_response(pipeline_id)

            # Step 4: Thematic Grouping
            coded_units = coding_result.get("coded_units", [])
            success, thematic_result, error = await self._step_thematic_grouping(pipeline_id, coded_units, research_domain)
            if not success:
                return self._get_pipeline_response(pipeline_id)

            # Step 5: Theme Refinement
            themes = thematic_result.get("themes", [])
            success, refinement_result, error = await self._step_theme_refinement(pipeline_id, themes, research_domain)
            if not success:
                return self._get_pipeline_response(pipeline_id)

            # Step 6: Report Generation
            all_sections = {
                "research_domain": research_domain,
                "literature_review": literature_result,
                "initial_coding": coding_result,
                "thematic_grouping": thematic_result,
                "theme_refinement": refinement_result
            }
            
            success, report_result, error = await self._step_report_generation(pipeline_id, all_sections)
            if not success:
                return self._get_pipeline_response(pipeline_id)

            print(f"[PIPELINE] 🎉 Step 10: Finalizing pipeline...")
            # Finalize pipeline
            await self._finalize_pipeline(pipeline_id, "completed", "Pipeline completed successfully")
            
            print(f"[PIPELINE] ✅ PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"[PIPELINE]   Pipeline ID: {pipeline_id}")
            print(f"[PIPELINE]   Total steps completed: 6/6")
            print(f"[PIPELINE]   Documents processed: {len(documents_result['data']['documents'])}")
            print(f"🚀"*60 + "\n")
            
            return self._get_pipeline_response(pipeline_id)

        except Exception as e:
            import traceback
            print(f"[PIPELINE] Error Full traceback:")
            print(traceback.format_exc())
            
            # Try to create error response
            try:
                pipeline_id = locals().get('pipeline_id', str(uuid.uuid4()))
                return {
                    "success": False,
                    "pipeline_id": pipeline_id,
                    "error": f"Pipeline execution failed: {str(e)}"
                }
            except:
                return {
                    "success": False,
                    "pipeline_id": "unknown",
                    "error": f"Critical pipeline failure: {str(e)}"
                }
    
    async def _update_pipeline_step(self, pipeline_id: str, step_number: int, step_name: str, status: str, message: str = "", result: dict = None):
        """Update pipeline step status and persist to storage."""
        if pipeline_id in self.pipeline_states:
            pipeline_state = self.pipeline_states[pipeline_id]
            
            # Update current step
            pipeline_state["current_step"] = step_number
            
            # Create step info
            step_info = {
                "step_number": step_number,
                "step_name": step_name,
                "status": status,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Update the step in the dictionary structure (steps is now a dict with string keys)
            step_key = str(step_number)
            if step_key in pipeline_state["steps"]:
                # Update existing step
                pipeline_state["steps"][step_key].update({
                    "status": status,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                # This shouldn't happen since we pre-populate all steps, but handle it
                pipeline_state["steps"][step_key] = {
                    "name": step_name,
                    "status": status,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Save the result if provided
            if result is not None:
                # Map step number to result key
                result_keys = {
                    1: "documents",
                    2: "literature_review", 
                    3: "initial_coding",
                    4: "thematic_grouping",
                    5: "theme_refinement",
                    6: "report_generation"
                }
                result_key = result_keys.get(step_number)
                if result_key:
                    pipeline_state["results"][result_key] = result
                    print(f"[PIPELINE]     💾 Saved {result_key} result to pipeline state")
            
            print(f"[PIPELINE]     ✅ Updated step {step_number} ({step_name}): {status}")
            if message:
                print(f"[PIPELINE]       Message: {message}")
            
            # Persist to storage
            self.storage_manager.update_pipeline(pipeline_id, pipeline_state)
    
    async def _finalize_pipeline(self, pipeline_id: str, status: str, message: str = ""):
        """Finalize pipeline and persist final state."""
        if pipeline_id in self.pipeline_states:
            pipeline_state = self.pipeline_states[pipeline_id]
            pipeline_state["status"] = status
            pipeline_state["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            if message:
                pipeline_state["errors"].append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": message
                })
            
            # Persist final state
            self.storage_manager.update_pipeline(pipeline_id, pipeline_state)
    
    def _get_pipeline_response(self, pipeline_id: str) -> Dict[str, Any]:
        """Get standardized pipeline response."""
        # Try to get from memory first, then from storage
        if pipeline_id not in self.pipeline_states:
            stored_pipeline = self.storage_manager.get_pipeline(pipeline_id)
            if stored_pipeline:
                self.pipeline_states[pipeline_id] = stored_pipeline
        
        if pipeline_id not in self.pipeline_states:
            return {
                "success": False,
                "error": f"Pipeline {pipeline_id} not found",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        pipeline_state = self.pipeline_states[pipeline_id]
        
        # Handle missing keys gracefully with defaults
        current_time = datetime.now(timezone.utc).isoformat()
        
        return {
            "success": True,
            "pipeline_id": pipeline_id,
            "status": pipeline_state.get("status", "unknown"),
            "data": {
                "current_step": pipeline_state.get("current_step", 1),
                "total_steps": pipeline_state.get("total_steps", 6),
                "started_at": pipeline_state.get("started_at", pipeline_state.get("created_at", current_time)),
                "completed_at": pipeline_state.get("completed_at"),
                "query": pipeline_state.get("query", ""),
                "research_domain": pipeline_state.get("research_domain", "General"),
                "quality_scores": pipeline_state.get("quality_scores", {}),
                "supervisor_decisions": pipeline_state.get("supervisor_decisions", {}),
                "steps": pipeline_state.get("steps", {
                    "1": {"step_name": "Document Retrieval", "status": "completed", "timestamp": current_time},
                    "2": {"step_name": "Literature Review", "status": "completed", "timestamp": current_time},
                    "3": {"step_name": "Initial Coding", "status": "completed", "timestamp": current_time},
                    "4": {"step_name": "Thematic Grouping", "status": "completed", "timestamp": current_time},
                    "5": {"step_name": "Theme Refinement", "status": "completed", "timestamp": current_time},
                    "6": {"step_name": "Report Generation", "status": "completed", "timestamp": current_time}
                }),
                "error_message": pipeline_state.get("error_message")
            },
            "timestamp": current_time
        }
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get current pipeline status."""
        # Try to get from memory first, then from storage
        if pipeline_id in self.pipeline_states:
            return self._get_pipeline_response(pipeline_id)
        
        # Try to load from storage
        stored_pipeline = self.storage_manager.get_pipeline(pipeline_id)
        if stored_pipeline:
            # Load into memory
            self.pipeline_states[pipeline_id] = stored_pipeline
            return self._get_pipeline_response(pipeline_id)
        
        return {
            "success": False,
            "error": f"Pipeline {pipeline_id} not found",
            "pipeline_id": pipeline_id
        }
    
    def get_pipeline_progress(self, pipeline_id: str) -> Dict[str, Any]:
        """Get detailed pipeline progress."""
        print(f"[DEBUG] get_pipeline_progress called for: {pipeline_id}")
        
        # Try to get from memory first, then from storage
        if pipeline_id not in self.pipeline_states:
            print(f"[DEBUG] Pipeline not in memory, loading from storage...")
            stored_pipeline = self.storage_manager.get_pipeline(pipeline_id)
            if stored_pipeline:
                print(f"[DEBUG] Loaded pipeline from storage")
                self.pipeline_states[pipeline_id] = stored_pipeline
            else:
                print(f"[DEBUG] Pipeline not found in storage")
                return {
                    "success": False,
                    "error": f"Pipeline {pipeline_id} not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        pipeline_state = self.pipeline_states[pipeline_id]
        print(f"[DEBUG] Pipeline state keys: {list(pipeline_state.keys()) if pipeline_state else 'None'}")
        
        # Build steps data safely - handle missing keys
        steps_data = pipeline_state.get("steps", {})
        if not steps_data:
            # Create default steps structure if missing
            print(f"[DEBUG] No steps data found, creating default structure")
            steps_data = {
                "1": {"step_number": 1, "step_name": "Document Retrieval", "status": "completed" if pipeline_state.get("current_step", 0) > 1 else "running", "timestamp": pipeline_state.get("started_at", "")},
                "2": {"step_number": 2, "step_name": "Literature Review", "status": "completed" if pipeline_state.get("current_step", 0) > 2 else "pending", "timestamp": ""},
                "3": {"step_number": 3, "step_name": "Initial Coding", "status": "completed" if pipeline_state.get("current_step", 0) > 3 else "pending", "timestamp": ""},
                "4": {"step_number": 4, "step_name": "Thematic Grouping", "status": "completed" if pipeline_state.get("current_step", 0) > 4 else "pending", "timestamp": ""},
                "5": {"step_number": 5, "step_name": "Theme Refinement", "status": "completed" if pipeline_state.get("current_step", 0) > 5 else "pending", "timestamp": ""},
                "6": {"step_number": 6, "step_name": "Report Generation", "status": "completed" if pipeline_state.get("current_step", 0) > 6 else "pending", "timestamp": ""}
            }
        
        # Check if results exist to determine actual completion status
        results = pipeline_state.get("results", {})
        step_result_keys = {
            1: "documents",
            2: "literature_review", 
            3: "initial_coding",
            4: "thematic_grouping",
            5: "theme_refinement",
            6: "report_generation"
        }
        
        # Update step status based on actual results
        for step_num in range(1, 7):
            step_key = str(step_num)
            result_key = step_result_keys.get(step_num)
            if step_key in steps_data and result_key and result_key in results:
                steps_data[step_key]["status"] = "completed"
                print(f"[DEBUG] Step {step_num} marked as completed due to existing results")
        
        # Calculate progress percentage
        current_step = pipeline_state.get("current_step", 0)
        total_steps = pipeline_state.get("total_steps", 6)
        percentage = (current_step / total_steps) * 100 if total_steps > 0 else 0
        
        print(f"[DEBUG] Progress calculation: {current_step}/{total_steps} = {percentage}%")

        return {
            "success": True,
            "data": {
                "pipeline_id": pipeline_id,
                "status": pipeline_state.get("status", "unknown"),
                "progress": {
                    "current_step": current_step,
                    "total_steps": total_steps,
                    "percentage": percentage
                },
                "steps": steps_data,
                "quality_scores": pipeline_state.get("quality_scores", {}),
                "supervisor_decisions": pipeline_state.get("supervisor_decisions", {}),
                "started_at": pipeline_state.get("started_at", ""),
                "estimated_completion": self._estimate_completion(pipeline_state)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _estimate_completion(self, pipeline_state: Dict[str, Any]) -> str:
        """Estimate pipeline completion time."""
        if pipeline_state["status"] in ["completed", "failed", "halted"]:
            return pipeline_state.get("completed_at", "Unknown")
        
        # Simple estimation based on current step
        current_step = pipeline_state["current_step"]
        total_steps = pipeline_state["total_steps"]
        
        if current_step == 0:
            return "Unknown"
        
        # Estimate 2-3 minutes per remaining step
        remaining_steps = total_steps - current_step
        estimated_minutes = remaining_steps * 2.5
        
        estimated_time = datetime.now(timezone.utc) + timedelta(minutes=estimated_minutes)
        return estimated_time.isoformat()
    
    def get_pipeline_results(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline results."""
        # Try to get from memory first, then from storage
        if pipeline_id not in self.pipeline_states:
            stored_pipeline = self.storage_manager.get_pipeline(pipeline_id)
            if stored_pipeline:
                self.pipeline_states[pipeline_id] = stored_pipeline
            else:
                return {
                    "success": False,
                    "error": f"Pipeline {pipeline_id} not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        pipeline_state = self.pipeline_states[pipeline_id]
        
        # Allow results for completed, halted, or failed pipelines
        if pipeline_state["status"] not in ["completed", "halted", "failed"]:
            return {
                "success": False,
                "error": f"Pipeline {pipeline_id} not finished yet (status: {pipeline_state['status']})",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "success": True,
            "data": {
                "pipeline_id": pipeline_id,
                "pipeline_status": pipeline_state["status"],
                "results": pipeline_state["results"],
                "quality_scores": pipeline_state.get("quality_scores", {}),
                "supervisor_decisions": pipeline_state.get("supervisor_decisions", {}),
                "steps": pipeline_state.get("steps", []),
                "started_at": pipeline_state.get("started_at"),
                "completed_at": pipeline_state.get("completed_at"),
                "query": pipeline_state.get("query"),
                "research_domain": pipeline_state.get("research_domain")
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Delete pipeline from memory and storage."""
        # Delete from storage first
        storage_success = self.storage_manager.delete_pipeline(pipeline_id)
        
        # Delete from memory
        if pipeline_id in self.pipeline_states:
            del self.pipeline_states[pipeline_id]
        
        if storage_success:
            return {
                "success": True,
                "data": {
                    "pipeline_id": pipeline_id,
                    "message": "Pipeline deleted successfully from memory and storage"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"Pipeline {pipeline_id} not found in storage",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def list_pipelines(self, limit: int = 10, status: str = None, research_domain: str = None) -> Dict[str, Any]:
        """
        List pipelines with optional filtering.
        
        Args:
            limit: Maximum number of pipelines to return
            status: Filter by pipeline status
            research_domain: Filter by research domain
            
        Returns:
            Dict containing list of pipelines
        """
        print(f"\n" + "📋"*60)
        print(f"📋 LIST_PIPELINES - DETAILED DEBUG TRACE")
        print(f"📋"*60)
        
        try:
            print(f"[LIST_PIPELINES] 📥 Input parameters:")
            print(f"[LIST_PIPELINES]   Limit: {limit}")
            print(f"[LIST_PIPELINES]   Status filter: {status}")
            print(f"[LIST_PIPELINES]   Research domain filter: {research_domain}")
            
            print(f"[LIST_PIPELINES] 🔍 Checking in-memory cache first...")
            print(f"[LIST_PIPELINES]   In-memory pipeline count: {len(self.pipeline_states)}")
            print(f"[LIST_PIPELINES]   In-memory pipeline IDs: {list(self.pipeline_states.keys())}")
            
            # Get pipelines from storage
            print(f"[LIST_PIPELINES] 💾 Calling storage_manager.list_pipelines()...")
            stored_pipelines = self.storage_manager.list_pipelines(limit=limit, status=status, research_domain=research_domain)
            
            print(f"[LIST_PIPELINES] 📊 Storage manager results:")
            print(f"[LIST_PIPELINES]   Stored pipelines count: {len(stored_pipelines)}")
            print(f"[LIST_PIPELINES]   Stored pipeline data preview:")
            
            for i, pipeline_data in enumerate(stored_pipelines):
                print(f"[LIST_PIPELINES]     Pipeline {i+1}:")
                print(f"[LIST_PIPELINES]       ID: {pipeline_data.get('pipeline_id', 'N/A')}")
                print(f"[LIST_PIPELINES]       Status: {pipeline_data.get('status', 'N/A')}")
                print(f"[LIST_PIPELINES]       Domain: {pipeline_data.get('research_domain', 'N/A')}")
                print(f"[LIST_PIPELINES]       Query: {pipeline_data.get('query', 'N/A')[:50]}...")
                print(f"[LIST_PIPELINES]       Created: {pipeline_data.get('created_at', 'N/A')}")
            
            # Convert to API response format
            print(f"[LIST_PIPELINES] 🔄 Converting to API response format...")
            pipelines = []
            for i, pipeline_data in enumerate(stored_pipelines):
                print(f"[LIST_PIPELINES]   Processing pipeline {i+1}/{len(stored_pipelines)}...")
                
                pipeline_info = {
                    "pipeline_id": pipeline_data["pipeline_id"],
                    "status": pipeline_data["status"],
                    "query": pipeline_data["query"],
                    "research_domain": pipeline_data["research_domain"],
                    "started_at": pipeline_data["created_at"],
                    "completed_at": pipeline_data.get("completed_at"),
                    "current_step": pipeline_data["current_step"],
                    "total_steps": pipeline_data["total_steps"]
                }
                pipelines.append(pipeline_info)
                print(f"[LIST_PIPELINES]     ✅ Converted pipeline {pipeline_data['pipeline_id'][:8]}...")
            
            final_result = {
                "success": True,
                "data": {
                    "pipelines": pipelines,
                    "total_count": len(pipelines),
                    "limit": limit,
                    "filters": {
                        "status": status,
                        "research_domain": research_domain
                    }
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            print(f"[LIST_PIPELINES] 📦 Final result:")
            print(f"[LIST_PIPELINES]   Success: {final_result['success']}")
            print(f"[LIST_PIPELINES]   Total count: {final_result['data']['total_count']}")
            print(f"[LIST_PIPELINES]   Pipelines returned: {len(final_result['data']['pipelines'])}")
            print(f"[LIST_PIPELINES]   Applied filters: {final_result['data']['filters']}")
            print(f"📋"*60 + "\n")
            
            return final_result
            
        except Exception as e:
            print(f"[LIST_PIPELINES] ❌ CRITICAL ERROR!")
            print(f"[LIST_PIPELINES]   Exception: {str(e)}")
            print(f"[LIST_PIPELINES]   Exception type: {type(e).__name__}")
            import traceback
            print(f"[LIST_PIPELINES]   Full traceback:")
            print(traceback.format_exc())
            print(f"📋"*60 + "\n")
            
            return {
                "success": False,
                "error": f"Failed to list pipelines: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics from actual storage."""
        print(f"\n📊 ===== GETTING PIPELINE STATISTICS =====")
        print(f"📊 In-memory pipeline_states count: {len(self.pipeline_states)}")
        print(f"📊 In-memory states: {list(self.pipeline_states.keys())}")
        
        try:
            # Get all pipelines from storage manager instead of in-memory cache
            print(f"📊 Querying storage_manager.list_pipelines() for statistics...")
            all_pipelines = self.storage_manager.list_pipelines(limit=1000)  # Get all pipelines
            print(f"📊 Storage manager returned: {len(all_pipelines)} pipelines")
            
            if not all_pipelines:
                print(f"📊 ⚠️ No pipelines found in storage - returning zeros")
                return {
                    "success": True,
                    "data": {
                        "total_pipelines": 0,
                        "completed": 0,
                        "failed": 0,
                        "halted": 0,
                        "running": 0,
                        "success_rate": 0
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Count pipelines by status
            total_pipelines = len(all_pipelines)
            completed_pipelines = len([p for p in all_pipelines if p.get("status") == "completed"])
            failed_pipelines = len([p for p in all_pipelines if p.get("status") == "failed"])
            halted_pipelines = len([p for p in all_pipelines if p.get("status") == "halted"])
            running_pipelines = len([p for p in all_pipelines if p.get("status") == "running"])
            
            print(f"📊 Statistics computed:")
            print(f"📊   Total: {total_pipelines}")
            print(f"📊   Completed: {completed_pipelines}")
            print(f"📊   Failed: {failed_pipelines}")
            print(f"📊   Halted: {halted_pipelines}")
            print(f"📊   Running: {running_pipelines}")
            
            # Calculate success rate
            success_rate = (completed_pipelines / total_pipelines * 100) if total_pipelines > 0 else 0
            print(f"📊   Success rate: {success_rate:.1f}%")
            
            result = {
                "success": True,
                "data": {
                    "total_pipelines": total_pipelines,
                    "completed": completed_pipelines,
                    "failed": failed_pipelines,
                    "halted": halted_pipelines,
                    "running": running_pipelines,
                    "success_rate": success_rate
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            print(f"📊 ✅ Statistics endpoint completed successfully!")
            return result
            
        except Exception as e:
            print(f"📊 ❌ Statistics calculation failed: {e}")
            import traceback
            print(f"📊 Traceback: {traceback.format_exc()}")
            
            # Return error response
            return {
                "success": False,
                "error": f"Failed to calculate statistics: {str(e)}",
                "data": {
                    "total_pipelines": 0,
                    "completed": 0,
                    "failed": 0,
                    "halted": 0,
                    "running": 0,
                    "success_rate": 0
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def download_pipeline_report(self, pipeline_id: str, format: str = "pdf") -> Dict[str, Any]:
        """
        Download the generated report from a completed pipeline.
        
        Args:
            pipeline_id: The pipeline identifier
            format: The download format (pdf, markdown, text)
            
        Returns:
            Dict with success status and file information
        """
        try:
            print(f"[DOWNLOAD] 📥 Download request for pipeline {pipeline_id}, format: {format}")
            
            # Get pipeline results to check if report exists
            results = self.get_pipeline_results(pipeline_id)
            if not results["success"]:
                return {
                    "success": False,
                    "error": f"Pipeline not found: {pipeline_id}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Check if report generation step completed
            report_data = results["data"]["results"].get("report_generation")
            if not report_data or not report_data.get("data"):
                return {
                    "success": False,
                    "error": f"No report generated for pipeline: {pipeline_id}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Get the file path from the report data
            file_path = report_data["data"].get("file_path")
            if not file_path:
                return {
                    "success": False,
                    "error": f"No report file path found for pipeline: {pipeline_id}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Check if the requested format matches the available file
            # If format is PDF but we have markdown, try to find PDF version
            if format == "pdf" and file_path.endswith(".md"):
                # Try to find corresponding PDF file
                pdf_path = file_path.replace(".md", ".pdf")
                if os.path.exists(pdf_path):
                    file_path = pdf_path
                else:
                    # If PDF doesn't exist, we'll serve the markdown file
                    print(f"[DOWNLOAD] PDF file not found, serving markdown: {file_path}")
            
            # If format is markdown but we have PDF, try to find markdown version
            elif format == "markdown" and file_path.endswith(".pdf"):
                # Try to find corresponding markdown file
                md_path = file_path.replace(".pdf", ".md")
                if os.path.exists(md_path):
                    file_path = md_path
                else:
                    # If markdown doesn't exist, we'll serve the PDF file
                    print(f"[DOWNLOAD] Markdown file not found, serving PDF: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Report file not found on disk: {file_path}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Generate filename based on format
            base_name = f"pipeline_report_{pipeline_id}"
            if format == "pdf":
                filename = f"{base_name}.pdf"
            elif format == "markdown":
                filename = f"{base_name}.md"
            elif format == "text":
                filename = f"{base_name}.txt"
            else:
                filename = f"{base_name}.pdf"  # Default to PDF
            
            print(f"[DOWNLOAD] ✅ File found: {file_path}")
            print(f"[DOWNLOAD] 📄 Filename: {filename}")
            
            return {
                "success": True,
                "data": {
                    "file_path": file_path,
                    "filename": filename,
                    "format": format,
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"[DOWNLOAD] ❌ Download failed: {str(e)}")
            import traceback
            print(f"[DOWNLOAD] Traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": f"Failed to download report: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }