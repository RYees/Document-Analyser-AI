# Migration Guide: New Architecture Implementation

## Overview

This guide outlines the new architecture for the Web3 Research Assistant backend, built with:
- **LangChain Agents** (replacing direct OpenAI API calls)
- **LangGraph Workflow Orchestration** (replacing custom supervisor)
- **Weaviate Vector Database** (replacing ChromaDB)
- **FastAPI Backend** (with human-in-the-loop integration)

## New Architecture Components

### 1. Core State Management (`core/research_state.py`)
- **ResearchState**: Main state object for the entire workflow
- **ResearchPhase**: Enum for different research phases
- **TaskStatus**: Enum for task status tracking
- **ProjectStatus**: Enum for project lifecycle management
- **Data Structures**: LiteratureReview, ResearchQuestions, Methodology, ResearchResults, ResearchDocument, HumanFeedback

### 2. LangChain Agents (`agents/`)
- **BaseResearchAgent**: Abstract base class for all agents
- **LiteratureReviewAgent**: Academic paper search and analysis
- **ResearchQuestionAgent**: Question formulation and validation
- **MethodologyAgent**: Research design and methodology
- **AnalysisAgent**: Data analysis and results processing
- **WritingAgent**: Document writing and formatting

### 3. LangGraph Workflow Orchestrator (`core/workflow_orchestrator.py`)
- **StateGraph**: Manages the entire research workflow
- **Conditional Edges**: Handles human-in-the-loop decision points
- **Memory Management**: Persistent state across workflow steps
- **Error Handling**: Graceful failure and recovery

### 4. FastAPI Backend (`api/main.py`)
- **Project Management**: Create, monitor, and control research projects
- **Human Feedback**: Submit and process human feedback
- **Real-time Updates**: WebSocket support for live project status
- **RESTful API**: Complete CRUD operations for research projects

## Key Features

### ✅ **Modular AI Agents**
- Each research task handled by specialized LangChain agents
- Encapsulated logic, tool usage, and LLM interactions
- Easy to extend and customize

### ✅ **Stateful Workflow Orchestration**
- LangGraph manages entire research lifecycle
- Conditional branching and cyclical processes
- Comprehensive ResearchState object

### ✅ **Human-in-the-Loop Integration**
- Explicit human review states in workflow
- API endpoints for feedback submission
- Seamless workflow pause/resume

### ✅ **Weaviate Vector Database**
- Primary vector database for RAG
- Semantic search over academic papers
- Contextual information retrieval

### ✅ **FastAPI Backend**
- Modern, async API framework
- Automatic OpenAPI documentation
- WebSocket support for real-time updates

## Installation & Setup

### 1. Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key

# Optional
CORE_API_KEY=your_core_api_key  # For academic paper search
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Weaviate
```bash
# Using Docker
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='text2vec-openai' \
  -e ENABLE_MODULES='text2vec-openai' \
  -e CLUSTER_HOSTNAME='node1' \
  semitechnologies/weaviate:1.22.4
```

### 4. Start FastAPI Server
```bash
cd web3_research_assistant
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Usage Examples

### 1. Create Research Project
```python
import requests

# Create new project
response = requests.post("http://localhost:8000/projects", json={
    "title": "Web3 Governance Analysis",
    "description": "Analysis of governance mechanisms in Web3 protocols",
    "research_domain": "blockchain_governance",
    "config": {
        "require_human_review": {
            "literature_review": True,
            "research_question_formulation": True
        }
    }
})

project_id = response.json()["project_id"]
print(f"Project created: {project_id}")
```

### 2. Monitor Project Status
```python
# Get project status
status = requests.get(f"http://localhost:8000/projects/{project_id}").json()
print(f"Current phase: {status['current_phase']}")
print(f"Status: {status['status']}")
```

### 3. Submit Human Feedback
```python
# Submit feedback when workflow is paused
feedback = requests.post(f"http://localhost:8000/projects/{project_id}/feedback", json={
    "feedback_type": "approval",
    "content": "Literature review looks comprehensive",
    "reviewer": "Dr. Smith",
    "specific_changes": []
}).json()

print(f"Feedback submitted: {feedback['message']}")
```

### 4. Get Project Results
```python
# Get final results
results = requests.get(f"http://localhost:8000/projects/{project_id}/results").json()
print(f"Literature review: {results['literature_review']['summary'][:100]}...")
print(f"Research questions: {results['research_questions']['primary_question']}")
```

## Workflow Phases

### 1. Literature Review
- Search academic papers using CORE API and arXiv
- Analyze papers for key findings and research gaps
- Generate comprehensive literature review
- Store papers in Weaviate for future reference

### 2. Research Question Formulation
- Formulate primary and secondary research questions
- Validate questions for clarity and feasibility
- Analyze methodological requirements
- Refine questions based on validation

### 3. Methodology Design
- Design research methodology based on questions
- Define data collection and analysis methods
- Consider ethical considerations and timeline
- Validate methodology for feasibility

### 4. Data Collection & Analysis
- Collect research data according to methodology
- Perform qualitative and quantitative analysis
- Generate visualizations and interpretations
- Integrate results from different analyses

### 5. Writing & Review
- Write comprehensive research document
- Include all sections with proper citations
- Review document for quality and completeness
- Format according to academic standards

## Human-in-the-Loop Integration

### Automatic Pause Points
The workflow automatically pauses for human review at:
- Literature review completion
- Research question formulation
- Methodology design
- Results integration
- Document writing

### Feedback Types
- **Approval**: Continue to next phase
- **Revision**: Modify current phase output
- **Rejection**: Restart current phase

### API Endpoints
- `POST /projects/{id}/feedback`: Submit human feedback
- `GET /projects/{id}/pending-reviews`: Check pending reviews
- `GET /projects/{id}/tasks`: View all tasks and status

## Development & Extension

### Adding New Agents
1. Create new agent class inheriting from `BaseResearchAgent`
2. Implement required abstract methods
3. Add agent to `WorkflowOrchestrator._setup_agents()`
4. Add corresponding workflow node

### Adding New Tools
1. Create tool class inheriting from `BaseTool`
2. Implement `_arun()` method
3. Add tool to agent's `_add_agent_tools()` method

### Customizing Workflow
1. Modify `WorkflowOrchestrator._create_workflow()`
2. Add new nodes and edges as needed
3. Update conditional logic in routing functions

## Monitoring & Debugging

### Logging
- All agents use structured logging
- Workflow orchestrator logs all state transitions
- FastAPI logs all API requests

### State Inspection
- Use `GET /projects/{id}` to inspect current state
- Check `tasks` array for detailed task information
- Monitor `human_feedback_queue` for pending feedback

### Error Handling
- Failed tasks are marked with error details
- Workflow can be resumed after fixing issues
- Human intervention available at any point

## Performance Considerations

### Vector Database
- Weaviate handles large-scale document storage
- Efficient semantic search capabilities
- Automatic indexing and optimization

### Async Processing
- All agents use async/await patterns
- FastAPI provides high-performance async API
- Background task processing for long-running operations

### Memory Management
- LangGraph checkpoint memory for state persistence
- Efficient state serialization/deserialization
- Automatic cleanup of completed projects

## Security & Best Practices

### API Security
- Input validation using Pydantic models
- Rate limiting and authentication (to be implemented)
- CORS configuration for frontend integration

### Data Privacy
- Secure storage of research data
- API key management
- Audit logging for all operations

### Error Handling
- Graceful degradation on failures
- Comprehensive error messages
- Automatic retry mechanisms

## Future Enhancements

### Planned Features
- Database persistence for project metadata
- Advanced analytics and reporting
- Integration with more academic databases
- Collaborative research features
- Export to various document formats

### Scalability
- Horizontal scaling with multiple instances
- Load balancing for high-traffic scenarios
- Caching layer for improved performance
- Microservices architecture evolution 