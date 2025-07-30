from typing import Dict, List, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver
import asyncio
import logging
from datetime import datetime

from .research_state import (
    ResearchState, ResearchPhase, TaskStatus, ProjectStatus,
    ResearchTask, LiteratureReview, ResearchQuestions, Methodology,
    ResearchResults, ResearchDocument, HumanFeedback
)
from ..agents.base_agent import BaseResearchAgent
from ..agents.literature_agent import LiteratureAgent
from ..agents.research_question_agent import ResearchQuestionAgent
from ..agents.methodology_agent import MethodologyAgent
from ..agents.analysis_agent import AnalysisAgent
from ..agents.writing_agent import WritingAgent

class WorkflowOrchestrator:
    """LangGraph-based workflow orchestrator for research automation"""
    
    def __init__(self):
        self.logger = logging.getLogger("workflow_orchestrator")
        self.agents: Dict[str, BaseResearchAgent] = {}
        self.memory = MemorySaver()
        self._setup_agents()
        self.workflow = self._create_workflow()
    
    def _setup_agents(self) -> None:
        """Setup all research agents"""
        try:
            self.agents = {
                "literature_review": LiteratureAgent(),
                "research_question": ResearchQuestionAgent(),
                "methodology": MethodologyAgent(),
                "analysis": AnalysisAgent(),
                "writing": WritingAgent()
            }
            self.logger.info(f"Initialized {len(self.agents)} agents")
        except Exception as e:
            self.logger.error(f"Failed to setup agents: {e}")
            raise
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create state graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes for each research phase
        workflow.add_node("literature_review", self._literature_review_node)
        workflow.add_node("research_question_formulation", self._research_question_node)
        workflow.add_node("methodology_design", self._methodology_node)
        workflow.add_node("data_collection", self._data_collection_node)
        workflow.add_node("qualitative_analysis", self._qualitative_analysis_node)
        workflow.add_node("quantitative_analysis", self._quantitative_analysis_node)
        workflow.add_node("results_integration", self._results_integration_node)
        workflow.add_node("writing", self._writing_node)
        workflow.add_node("review", self._review_node)
        workflow.add_node("human_review", self._human_review_node)
        workflow.add_node("completion", self._completion_node)
        
        # Define workflow edges
        workflow.set_entry_point("literature_review")
        
        # Literature review flow
        workflow.add_edge("literature_review", "research_question_formulation")
        
        # Research question flow
        workflow.add_conditional_edges(
            "research_question_formulation",
            self._should_require_human_review,
            {
                "human_review": "human_review",
                "continue": "methodology_design"
            }
        )
        
        # Methodology flow
        workflow.add_conditional_edges(
            "methodology_design",
            self._should_require_human_review,
            {
                "human_review": "human_review",
                "continue": "data_collection"
            }
        )
        
        # Data collection flow
        workflow.add_edge("data_collection", "qualitative_analysis")
        
        # Analysis flow
        workflow.add_edge("qualitative_analysis", "quantitative_analysis")
        workflow.add_edge("quantitative_analysis", "results_integration")
        
        # Results integration flow
        workflow.add_conditional_edges(
            "results_integration",
            self._should_require_human_review,
            {
                "human_review": "human_review",
                "continue": "writing"
            }
        )
        
        # Writing flow
        workflow.add_conditional_edges(
            "writing",
            self._should_require_human_review,
            {
                "human_review": "human_review",
                "continue": "review"
            }
        )
        
        # Review flow
        workflow.add_conditional_edges(
            "review",
            self._should_require_human_review,
            {
                "human_review": "human_review",
                "continue": "completion"
            }
        )
        
        # Human review flow
        workflow.add_conditional_edges(
            "human_review",
            self._human_review_complete,
            {
                "continue": "continue",
                "revision": "revision",
                "end": END
            }
        )
        
        # Completion
        workflow.add_edge("completion", END)
        
        # Compile workflow
        return workflow.compile(checkpointer=self.memory)
    
    async def _literature_review_node(self, state: ResearchState) -> ResearchState:
        """Literature review phase node"""
        try:
            self.logger.info("Starting literature review phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.LITERATURE_REVIEW,
                description="Conduct comprehensive literature review",
                agent_type="literature_review"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["literature_review"]
            result = await agent.execute_task(state, task)
            
            # Update state
            state.literature_review = LiteratureReview(
                summary=result.get("summary", ""),
                key_findings=result.get("key_findings", []),
                research_gaps=result.get("research_gaps", []),
                citations=result.get("citations", []),
                papers_processed=result.get("papers_processed", 0),
                search_query=result.get("search_query", "")
            )
            
            state.mark_phase_completed(ResearchPhase.LITERATURE_REVIEW)
            state.current_phase = ResearchPhase.RESEARCH_QUESTION_FORMULATION
            
            self.logger.info("Literature review phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Literature review failed: {e}")
            state.mark_phase_failed(ResearchPhase.LITERATURE_REVIEW)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _research_question_node(self, state: ResearchState) -> ResearchState:
        """Research question formulation phase node"""
        try:
            self.logger.info("Starting research question formulation phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.RESEARCH_QUESTION_FORMULATION,
                description="Formulate research questions",
                agent_type="research_question"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["research_question"]
            result = await agent.execute_task(state, task)
            
            # Update state
            state.research_questions = ResearchQuestions(
                primary_question=result.get("primary_question", ""),
                secondary_questions=result.get("secondary_questions", []),
                feasibility_analysis=result.get("feasibility_analysis", {}),
                validation_results=result.get("validation_results", {}),
                refined_questions=result.get("refined_questions", [])
            )
            
            state.mark_phase_completed(ResearchPhase.RESEARCH_QUESTION_FORMULATION)
            state.current_phase = ResearchPhase.METHODOLOGY_DESIGN
            
            self.logger.info("Research question formulation phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Research question formulation failed: {e}")
            state.mark_phase_failed(ResearchPhase.RESEARCH_QUESTION_FORMULATION)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _methodology_node(self, state: ResearchState) -> ResearchState:
        """Methodology design phase node"""
        try:
            self.logger.info("Starting methodology design phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.METHODOLOGY_DESIGN,
                description="Design research methodology",
                agent_type="methodology"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["methodology"]
            result = await agent.execute_task(state, task)
            
            # Update state
            state.methodology = Methodology(
                design_type=result.get("design_type", ""),
                data_collection_methods=result.get("data_collection_methods", []),
                analysis_methods=result.get("analysis_methods", []),
                sampling_strategy=result.get("sampling_strategy", {}),
                ethical_considerations=result.get("ethical_considerations", []),
                timeline=result.get("timeline", {}),
                validation_results=result.get("validation_results", {})
            )
            
            state.mark_phase_completed(ResearchPhase.METHODOLOGY_DESIGN)
            state.current_phase = ResearchPhase.DATA_COLLECTION
            
            self.logger.info("Methodology design phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Methodology design failed: {e}")
            state.mark_phase_failed(ResearchPhase.METHODOLOGY_DESIGN)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _data_collection_node(self, state: ResearchState) -> ResearchState:
        """Data collection phase node"""
        try:
            self.logger.info("Starting data collection phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.DATA_COLLECTION,
                description="Collect research data",
                agent_type="analysis"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["analysis"]
            result = await agent.execute_task(state, task)
            
            state.mark_phase_completed(ResearchPhase.DATA_COLLECTION)
            state.current_phase = ResearchPhase.QUALITATIVE_ANALYSIS
            
            self.logger.info("Data collection phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Data collection failed: {e}")
            state.mark_phase_failed(ResearchPhase.DATA_COLLECTION)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _qualitative_analysis_node(self, state: ResearchState) -> ResearchState:
        """Qualitative analysis phase node"""
        try:
            self.logger.info("Starting qualitative analysis phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.QUALITATIVE_ANALYSIS,
                description="Perform qualitative analysis",
                agent_type="analysis"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["analysis"]
            result = await agent.execute_task(state, task)
            
            state.mark_phase_completed(ResearchPhase.QUALITATIVE_ANALYSIS)
            state.current_phase = ResearchPhase.QUANTITATIVE_ANALYSIS
            
            self.logger.info("Qualitative analysis phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Qualitative analysis failed: {e}")
            state.mark_phase_failed(ResearchPhase.QUALITATIVE_ANALYSIS)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _quantitative_analysis_node(self, state: ResearchState) -> ResearchState:
        """Quantitative analysis phase node"""
        try:
            self.logger.info("Starting quantitative analysis phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.QUANTITATIVE_ANALYSIS,
                description="Perform quantitative analysis",
                agent_type="analysis"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["analysis"]
            result = await agent.execute_task(state, task)
            
            state.mark_phase_completed(ResearchPhase.QUANTITATIVE_ANALYSIS)
            state.current_phase = ResearchPhase.RESULTS_INTEGRATION
            
            self.logger.info("Quantitative analysis phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Quantitative analysis failed: {e}")
            state.mark_phase_failed(ResearchPhase.QUANTITATIVE_ANALYSIS)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _results_integration_node(self, state: ResearchState) -> ResearchState:
        """Results integration phase node"""
        try:
            self.logger.info("Starting results integration phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.RESULTS_INTEGRATION,
                description="Integrate research results",
                agent_type="analysis"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["analysis"]
            result = await agent.execute_task(state, task)
            
            # Update state
            state.results = ResearchResults(
                qualitative_data=result.get("qualitative_data", {}),
                quantitative_data=result.get("quantitative_data", {}),
                analysis_results=result.get("analysis_results", {}),
                visualizations=result.get("visualizations", []),
                interpretations=result.get("interpretations", {})
            )
            
            state.mark_phase_completed(ResearchPhase.RESULTS_INTEGRATION)
            state.current_phase = ResearchPhase.WRITING
            
            self.logger.info("Results integration phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Results integration failed: {e}")
            state.mark_phase_failed(ResearchPhase.RESULTS_INTEGRATION)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _writing_node(self, state: ResearchState) -> ResearchState:
        """Writing phase node"""
        try:
            self.logger.info("Starting writing phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.WRITING,
                description="Write research document",
                agent_type="writing"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["writing"]
            result = await agent.execute_task(state, task)
            
            # Update state
            state.document = ResearchDocument(
                title=result.get("title", ""),
                abstract=result.get("abstract", ""),
                sections=result.get("sections", {}),
                citations=result.get("citations", []),
                bibliography=result.get("bibliography", []),
                formatting=result.get("formatting", {})
            )
            
            state.mark_phase_completed(ResearchPhase.WRITING)
            state.current_phase = ResearchPhase.REVIEW
            
            self.logger.info("Writing phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Writing failed: {e}")
            state.mark_phase_failed(ResearchPhase.WRITING)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _review_node(self, state: ResearchState) -> ResearchState:
        """Review phase node"""
        try:
            self.logger.info("Starting review phase")
            
            # Create task
            task = ResearchTask(
                phase=ResearchPhase.REVIEW,
                description="Review research document",
                agent_type="writing"
            )
            state.add_task(task)
            
            # Execute task
            agent = self.agents["writing"]
            result = await agent.execute_task(state, task)
            
            state.mark_phase_completed(ResearchPhase.REVIEW)
            state.current_phase = ResearchPhase.COMPLETION
            
            self.logger.info("Review phase completed")
            return state
            
        except Exception as e:
            self.logger.error(f"Review failed: {e}")
            state.mark_phase_failed(ResearchPhase.REVIEW)
            state.status = ProjectStatus.FAILED
            return state
    
    async def _human_review_node(self, state: ResearchState) -> ResearchState:
        """Human review phase node"""
        try:
            self.logger.info("Starting human review phase")
            
            # Set status to waiting for human review
            state.status = ProjectStatus.WAITING_HUMAN_REVIEW
            state.pending_human_reviews.append(state.current_phase)
            
            # This node will pause the workflow until human feedback is received
            # The workflow will be resumed when human feedback is submitted via API
            
            self.logger.info("Workflow paused for human review")
            return state
            
        except Exception as e:
            self.logger.error(f"Human review failed: {e}")
            state.status = ProjectStatus.FAILED
            return state
    
    async def _completion_node(self, state: ResearchState) -> ResearchState:
        """Completion phase node"""
        try:
            self.logger.info("Starting completion phase")
            
            # Mark project as completed
            state.status = ProjectStatus.COMPLETED
            state.current_phase = ResearchPhase.COMPLETION
            
            self.logger.info("Research project completed successfully")
            return state
            
        except Exception as e:
            self.logger.error(f"Completion failed: {e}")
            state.status = ProjectStatus.FAILED
            return state
    
    def _should_require_human_review(self, state: ResearchState) -> str:
        """Determine if human review is required"""
        # Check if current phase requires human review
        if state.current_phase in state.pending_human_reviews:
            return "human_review"
        
        # Check if any tasks failed
        failed_tasks = [task for task in state.tasks if task.status == TaskStatus.FAILED]
        if failed_tasks:
            return "human_review"
        
        # Check if human review is configured for this phase
        if state.config.get("require_human_review", {}).get(state.current_phase.value, False):
            return "human_review"
        
        return "continue"
    
    def _human_review_complete(self, state: ResearchState) -> str:
        """Determine next step after human review"""
        # Check if human feedback has been resolved
        pending_feedback = [f for f in state.human_feedback_queue if not f.resolved]
        if pending_feedback:
            return "human_review"
        
        # Check if human approved the current phase
        if state.status == ProjectStatus.IN_PROGRESS:
            return "continue"
        
        # Check if human requested revision
        if state.status == ProjectStatus.PAUSED:
            return "revision"
        
        # Check if human ended the project
        if state.status == ProjectStatus.FAILED:
            return "end"
        
        return "continue"
    
    async def start_research_project(self, project_config: Dict[str, Any]) -> str:
        """Start a new research project"""
        try:
            # Create initial state
            state = ResearchState()
            state.title = project_config.get("title", "")
            state.description = project_config.get("description", "")
            state.research_domain = project_config.get("research_domain", "")
            state.config = project_config.get("config", {})
            state.status = ProjectStatus.IN_PROGRESS
            
            # Start workflow
            config = {"configurable": {"thread_id": state.project_id}}
            result = await self.workflow.ainvoke(state, config)
            
            self.logger.info(f"Research project {state.project_id} started successfully")
            return state.project_id
            
        except Exception as e:
            self.logger.error(f"Failed to start research project: {e}")
            raise
    
    async def resume_workflow(self, project_id: str, human_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Resume workflow after human feedback"""
        try:
            # Get current state
            config = {"configurable": {"thread_id": project_id}}
            current_state = await self.workflow.aget_state(config)
            
            if not current_state:
                raise ValueError(f"Project {project_id} not found")
            
            # Add human feedback
            feedback = HumanFeedback(
                task_id=human_feedback.get("task_id", ""),
                phase=current_state.current_phase,
                feedback_type=human_feedback.get("feedback_type", "approval"),
                content=human_feedback.get("content", ""),
                reviewer=human_feedback.get("reviewer", ""),
                specific_changes=human_feedback.get("specific_changes", [])
            )
            current_state.add_human_feedback(feedback)
            
            # Update state based on feedback
            if human_feedback.get("feedback_type") == "approval":
                current_state.status = ProjectStatus.IN_PROGRESS
                if current_state.current_phase in current_state.pending_human_reviews:
                    current_state.pending_human_reviews.remove(current_state.current_phase)
            
            # Resume workflow
            result = await self.workflow.ainvoke(current_state, config)
            
            self.logger.info(f"Workflow resumed for project {project_id}")
            return result.to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to resume workflow: {e}")
            raise
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get current project status"""
        try:
            config = {"configurable": {"thread_id": project_id}}
            state = await self.workflow.aget_state(config)
            
            if not state:
                return {"error": "Project not found"}
            
            return state.to_dict()
            
        except Exception as e:
            self.logger.error(f"Failed to get project status: {e}")
            raise
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get workflow information"""
        return {
            "phases": [phase.value for phase in ResearchPhase],
            "agents": {name: agent.get_agent_info() for name, agent in self.agents.items()},
            "checkpoint_memory": "enabled"
        } 