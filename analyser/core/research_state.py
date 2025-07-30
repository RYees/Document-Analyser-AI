from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

class ResearchPhase(Enum):
    LITERATURE_REVIEW = "literature_review"
    RESEARCH_QUESTION_FORMULATION = "research_question_formulation"
    METHODOLOGY_DESIGN = "methodology_design"
    DATA_COLLECTION = "data_collection"
    QUALITATIVE_ANALYSIS = "qualitative_analysis"
    QUANTITATIVE_ANALYSIS = "quantitative_analysis"
    RESULTS_INTEGRATION = "results_integration"
    WRITING = "writing"
    REVIEW = "review"
    COMPLETION = "completion"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_HUMAN_FEEDBACK = "waiting_human_feedback"
    REVISION_REQUIRED = "revision_required"

class ProjectStatus(Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    WAITING_HUMAN_REVIEW = "waiting_human_review"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class ResearchTask:
    """Represents a research task in the workflow"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phase: ResearchPhase = ResearchPhase.LITERATURE_REVIEW
    status: TaskStatus = TaskStatus.PENDING
    description: str = ""
    agent_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    human_feedback: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time: Optional[float] = None

@dataclass
class LiteratureReview:
    """Literature review data structure"""
    summary: str = ""
    key_findings: List[Dict[str, Any]] = field(default_factory=list)
    research_gaps: List[Dict[str, Any]] = field(default_factory=list)
    methodologies: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    papers_processed: int = 0
    search_query: str = ""
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ResearchQuestions:
    """Research questions data structure"""
    primary_question: str = ""
    secondary_questions: List[str] = field(default_factory=list)
    feasibility_analysis: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    refined_questions: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Methodology:
    """Research methodology data structure"""
    design_type: str = ""  # qualitative, quantitative, mixed
    data_collection_methods: List[str] = field(default_factory=list)
    analysis_methods: List[str] = field(default_factory=list)
    sampling_strategy: Dict[str, Any] = field(default_factory=dict)
    ethical_considerations: List[str] = field(default_factory=list)
    timeline: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ResearchResults:
    """Research results data structure"""
    qualitative_data: Dict[str, Any] = field(default_factory=dict)
    quantitative_data: Dict[str, Any] = field(default_factory=dict)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    interpretations: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ResearchDocument:
    """Research document data structure"""
    title: str = ""
    abstract: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    bibliography: List[Dict[str, Any]] = field(default_factory=list)
    formatting: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class HumanFeedback:
    """Human feedback data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    phase: ResearchPhase = ResearchPhase.LITERATURE_REVIEW
    feedback_type: str = ""  # approval, revision, rejection
    content: str = ""
    specific_changes: List[Dict[str, Any]] = field(default_factory=list)
    reviewer: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False

@dataclass
class ResearchState:
    """Main state object for the research workflow"""
    
    # Project Information
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    research_domain: str = ""
    status: ProjectStatus = ProjectStatus.INITIALIZED
    
    # Workflow State
    current_phase: ResearchPhase = ResearchPhase.LITERATURE_REVIEW
    completed_phases: List[ResearchPhase] = field(default_factory=list)
    failed_phases: List[ResearchPhase] = field(default_factory=list)
    
    # Tasks
    tasks: List[ResearchTask] = field(default_factory=list)
    current_task: Optional[ResearchTask] = None
    
    # Research Data
    literature_review: Optional[LiteratureReview] = None
    research_questions: Optional[ResearchQuestions] = None
    methodology: Optional[Methodology] = None
    results: Optional[ResearchResults] = None
    document: Optional[ResearchDocument] = None
    
    # Human Interaction
    human_feedback_queue: List[HumanFeedback] = field(default_factory=list)
    pending_human_reviews: List[ResearchPhase] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_execution_time: float = 0.0
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    def add_task(self, task: ResearchTask) -> None:
        """Add a task to the workflow"""
        self.tasks.append(task)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task"""
        for task in self.tasks:
            if task.id == task_id:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                task.updated_at = datetime.now(timezone.utc)
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False
    
    def get_task(self, task_id: str) -> Optional[ResearchTask]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_tasks_by_phase(self, phase: ResearchPhase) -> List[ResearchTask]:
        """Get all tasks for a specific phase"""
        return [task for task in self.tasks if task.phase == phase]
    
    def add_human_feedback(self, feedback: HumanFeedback) -> None:
        """Add human feedback"""
        self.human_feedback_queue.append(feedback)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_pending_feedback(self, task_id: str) -> List[HumanFeedback]:
        """Get pending feedback for a task"""
        return [f for f in self.human_feedback_queue if f.task_id == task_id and not f.resolved]
    
    def mark_phase_completed(self, phase: ResearchPhase) -> None:
        """Mark a phase as completed"""
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_phase_failed(self, phase: ResearchPhase) -> None:
        """Mark a phase as failed"""
        if phase not in self.failed_phases:
            self.failed_phases.append(phase)
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "research_domain": self.research_domain,
            "status": self.status.value,
            "current_phase": self.current_phase.value,
            "completed_phases": [phase.value for phase in self.completed_phases],
            "failed_phases": [phase.value for phase in self.failed_phases],
            "tasks": [
                {
                    "id": task.id,
                    "phase": task.phase.value,
                    "status": task.status.value,
                    "description": task.description,
                    "agent_type": task.agent_type,
                    "parameters": task.parameters,
                    "result": task.result,
                    "error": task.error,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "execution_time": task.execution_time
                }
                for task in self.tasks
            ],
            "current_task": {
                "id": self.current_task.id,
                "phase": self.current_task.phase.value,
                "status": self.current_task.status.value
            } if self.current_task else None,
            "literature_review": self.literature_review.__dict__ if self.literature_review else None,
            "research_questions": self.research_questions.__dict__ if self.research_questions else None,
            "methodology": self.methodology.__dict__ if self.methodology else None,
            "results": self.results.__dict__ if self.results else None,
            "document": self.document.__dict__ if self.document else None,
            "human_feedback_queue": [
                {
                    "id": feedback.id,
                    "task_id": feedback.task_id,
                    "phase": feedback.phase.value,
                    "feedback_type": feedback.feedback_type,
                    "content": feedback.content,
                    "reviewer": feedback.reviewer,
                    "timestamp": feedback.timestamp.isoformat(),
                    "resolved": feedback.resolved
                }
                for feedback in self.human_feedback_queue
            ],
            "pending_human_reviews": [phase.value for phase in self.pending_human_reviews],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total_execution_time": self.total_execution_time,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchState':
        """Create state from dictionary"""
        state = cls()
        state.project_id = data.get("project_id", str(uuid.uuid4()))
        state.title = data.get("title", "")
        state.description = data.get("description", "")
        state.research_domain = data.get("research_domain", "")
        state.status = ProjectStatus(data.get("status", "initialized"))
        state.current_phase = ResearchPhase(data.get("current_phase", "literature_review"))
        
        # Restore phases
        state.completed_phases = [ResearchPhase(phase) for phase in data.get("completed_phases", [])]
        state.failed_phases = [ResearchPhase(phase) for phase in data.get("failed_phases", [])]
        
        # Restore tasks
        for task_data in data.get("tasks", []):
            task = ResearchTask()
            task.id = task_data["id"]
            task.phase = ResearchPhase(task_data["phase"])
            task.status = TaskStatus(task_data["status"])
            task.description = task_data["description"]
            task.agent_type = task_data["agent_type"]
            task.parameters = task_data["parameters"]
            task.result = task_data["result"]
            task.error = task_data["error"]
            task.created_at = datetime.fromisoformat(task_data["created_at"])
            task.updated_at = datetime.fromisoformat(task_data["updated_at"])
            task.execution_time = task_data.get("execution_time")
            state.tasks.append(task)
        
        # Restore timestamps
        state.created_at = datetime.fromisoformat(data.get("created_at", datetime.now(timezone.utc).isoformat()))
        state.updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now(timezone.utc).isoformat()))
        state.total_execution_time = data.get("total_execution_time", 0.0)
        state.config = data.get("config", {})
        
        return state 