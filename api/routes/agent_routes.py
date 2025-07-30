"""
Agent route handlers for the Research Pipeline API.
Contains endpoints for individual agent operations and management.
"""

import sys
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse

from api.models.requests import AgentRequest
from api.models.responses import (
    AgentResponse, AgentStatusResponse, AgentHealthResponse
)
from api.models.agents import (
    AgentType, AgentStatus,
    DataExtractorRequest, RetrieverRequest, LiteratureReviewRequest,
    InitialCodingRequest, ThematicGroupingRequest, ThemeRefinementRequest,
    ReportGenerationRequest, SupervisorRequest
)
from api.services.agent_service import AgentService

# Import individual agents
from api.agents.data_extractor_agent import DataExtractorAgent
from api.agents.retriever_agent import RetrieverAgent
from api.agents.literature_review_agent import LiteratureReviewAgent
from api.agents.initial_coding_agent import InitialCodingAgent
from api.agents.thematic_grouping_agent import ThematicGroupingAgent
from api.agents.theme_refiner_agent import ThemeRefinerAgent
from api.agents.report_generator_agent import ReportGeneratorAgent
from api.agents.supervisor_agent import SupervisorAgent

router = APIRouter()

# Initialize agent service
agent_service = AgentService()

# Individual Agent Routes

@router.post("/data-extractor/extract", 
            response_model=AgentResponse,
            summary="Extract content from documents",
            description="Extract structured content from academic documents using the Data Extractor Agent")
async def extract_document_content(request: DataExtractorRequest):
    """
    🗂️ **Data Extractor Agent**: Fetch and extract academic papers from external sources.
    
    **What it does:**
    - Searches academic databases (CORE API) for relevant papers
    - Downloads and extracts content from PDFs
    - Stores documents in vector database for retrieval
    
    **Use cases:**
    - Finding academic papers by search query
    - Building document collections for research
    - Populating vector store with academic content
    """
    try:
        print(f"\n🗂️ ===== DATA EXTRACTOR AGENT ENDPOINT =====")
        print(f"🗂️ Request received at: {datetime.now()}")
        print(f"🗂️ Search query: {request.query}")
        print(f"🗂️ Research domain: {request.research_domain}")
        print(f"🗂️ Max results: {request.max_results}")
        print(f"🗂️ Year range: {request.year_from}-{request.year_to}")
        
        # Initialize agent
        extractor_agent = DataExtractorAgent()
        
        # Run extraction with existing method signature
        result = await extractor_agent.run(
            query=request.query,
            max_results=request.max_results,
            year_from=request.year_from,
            year_to=request.year_to,
            research_domain=request.research_domain
        )
        
        if "error" in result:
            print(f"🗂️ ❌ Extraction failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Data extraction failed: {result['error']}"
            )
        
        print(f"🗂️ ✅ Extraction completed successfully!")
        print(f"🗂️ Papers fetched: {result.get('papers_fetched', 0)}")
        print(f"🗂️ Papers extracted: {result.get('papers_extracted', 0)}")
        
        response = AgentResponse(
            success=True,
            agent_type="data_extractor",
            data=result,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"🗂️ =======================================\n")
        return response
        
    except Exception as e:
        print(f"🗂️ ❌ Critical error: {str(e)}")
        print(f"🗂️ =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Data extraction failed: {str(e)}"
        )

@router.post("/retriever/search",
            response_model=AgentResponse,
            summary="Retrieve documents from vector store",
            description="Search and retrieve relevant documents using the Retriever Agent")
async def retrieve_documents(request: RetrieverRequest):
    """
    🔍 **Retriever Agent**: Search and retrieve relevant documents from vector store.
    
    **What it does:**
    - Semantic search through document collection
    - Retrieves most relevant documents for research query
    - Filters by research domain
    
    **Use cases:**
    - Finding relevant literature for research
    - Document discovery and exploration
    - Preparing document sets for analysis
    """
    try:
        print(f"\n🔍 ===== RETRIEVER AGENT ENDPOINT =====")
        print(f"🔍 Request received at: {datetime.now()}")
        print(f"🔍 Search query: {request.query}")
        print(f"🔍 Research domain: {request.research_domain}")
        print(f"🔍 Top K results: {request.top_k}")
        print(f"🔍 Collection: {request.collection_name}")
        
        # Initialize agent
        retriever_agent = RetrieverAgent(
            collection_name=request.collection_name,
            research_domain=request.research_domain
        )
        
        # Run retrieval
        result = await retriever_agent.run(
            query=request.query,
            top_k=request.top_k
        )
        
        if "error" in result:
            print(f"🔍 ❌ Retrieval failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Document retrieval failed: {result['error']}"
            )
        
        print(f"🔍 ✅ Retrieval completed successfully!")
        print(f"🔍 Documents found: {len(result)}")
        
        response = AgentResponse(
            success=True,
            agent_type="retriever",
            data={"documents": result},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"🔍 =======================================\n")
        return response
        
    except Exception as e:
        print(f"🔍 ❌ Critical error: {str(e)}")
        print(f"🔍 =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Document retrieval failed: {str(e)}"
        )

@router.post("/literature-review/generate",
            response_model=AgentResponse,
            summary="Generate literature review",
            description="Generate comprehensive literature review using the Literature Review Agent")
async def generate_literature_review(request: LiteratureReviewRequest):
    """
    📚 **Literature Review Agent**: Generate comprehensive literature review from documents.
    
    **What it does:**
    - Analyzes academic documents for key themes
    - Identifies research gaps and contributions
    - Synthesizes literature into coherent review
    
    **Use cases:**
    - Creating literature review sections
    - Understanding research landscape
    - Identifying knowledge gaps
    """
    try:
        print(f"\n📚 ===== LITERATURE REVIEW AGENT ENDPOINT =====")
        print(f"📚 Request received at: {datetime.now()}")
        print(f"📚 Documents to review: {len(request.documents)}")
        print(f"📚 Research domain: {request.research_domain}")
        print(f"📚 Review type: {request.review_type}")
        
        # Initialize agent
        literature_agent = LiteratureReviewAgent()
        
        # Run literature review
        result = await literature_agent.run(
            documents=request.documents,
            research_domain=request.research_domain
        )
        
        if "error" in result:
            print(f"📚 ❌ Literature review failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Literature review failed: {result['error']}"
            )
        
        print(f"📚 ✅ Literature review completed successfully!")
        print(f"📚 Key findings: {len(result.get('key_findings', []))}")
        print(f"📚 Research gaps: {len(result.get('research_gaps', []))}")
        
        response = AgentResponse(
            success=True,
            agent_type="literature_review",
            data=result,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"📚 =======================================\n")
        return response
        
    except Exception as e:
        print(f"📚 ❌ Critical error: {str(e)}")
        print(f"📚 =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Literature review failed: {str(e)}"
        )

@router.post("/initial-coding/code",
            response_model=AgentResponse,
            summary="Perform initial coding on documents",
            description="Conduct open coding analysis using the Initial Coding Agent")
async def perform_initial_coding(request: InitialCodingRequest):
    """
    🎯 **Initial Coding Agent**: Perform open coding analysis on documents.
    
    **What it does:**
    - Segments documents into meaningful units
    - Assigns descriptive codes to text segments
    - Creates Harvard-style citations
    
    **Use cases:**
    - Qualitative data analysis
    - Thematic analysis preparation
    - Academic research coding
    """
    try:
        print(f"\n🎯 ===== INITIAL CODING AGENT ENDPOINT =====")
        print(f"🎯 Request received at: {datetime.now()}")
        print(f"🎯 Documents to code: {len(request.documents)}")
        print(f"🎯 Research domain: {request.research_domain}")
        print(f"🎯 Coding approach: {request.coding_approach}")
        
        # Initialize agent
        coding_agent = InitialCodingAgent()
        
        # Run initial coding
        result = await coding_agent.run(
            documents=request.documents,
            research_domain=request.research_domain
        )
        
        if "error" in result:
            print(f"🎯 ❌ Initial coding failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Initial coding failed: {result['error']}"
            )
        
        print(f"🎯 ✅ Initial coding completed successfully!")
        coding_summary = result.get('coding_summary', {})
        print(f"🎯 Units coded: {coding_summary.get('total_units_coded', 0)}")
        print(f"🎯 Unique codes: {coding_summary.get('unique_codes_generated', 0)}")
        
        response = AgentResponse(
            success=True,
            agent_type="initial_coding",
            data=result,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"🎯 =======================================\n")
        return response
        
    except Exception as e:
        print(f"🎯 ❌ Critical error: {str(e)}")
        print(f"🎯 =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Initial coding failed: {str(e)}"
        )

@router.post("/thematic-grouping/group",
            response_model=AgentResponse,
            summary="Group codes into themes",
            description="Group coded units into themes using the Thematic Grouping Agent")
async def group_codes_into_themes(request: ThematicGroupingRequest):
    """
    🔗 **Thematic Grouping Agent**: Group coded units into themes.
    
    **What it does:**
    - Groups similar codes into cohesive themes
    - Identifies dominant themes and sub-themes
    - Provides a hierarchical structure for theme refinement
    
    **Use cases:**
    - Preparing themes for academic analysis
    - Identifying main research questions
    - Structuring research findings
    """
    try:
        print(f"\n🔗 ===== THEMATIC GROUPING AGENT ENDPOINT =====")
        print(f"🔗 Request received at: {datetime.now()}")
        print(f"🔗 Documents to group: {len(request.coded_units)}")
        print(f"🔗 Research domain: {request.research_domain}")
        print(f"🔗 Max themes: {request.max_themes}")
        print(f"🔗 Min codes per theme: {request.min_codes_per_theme}")
        
        # Initialize agent
        grouping_agent = ThematicGroupingAgent()
        
        # Run thematic grouping
        result = await grouping_agent.run(
            coded_units=request.coded_units,
            research_domain=request.research_domain
        )
        
        if "error" in result:
            print(f"🎨 ❌ Thematic grouping failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Thematic grouping failed: {result['error']}"
            )
        
        print(f"🎨 ✅ Thematic grouping completed successfully!")
        thematic_summary = result.get("thematic_summary", {})
        print(f"🎨 Total themes generated: {thematic_summary.get('total_themes_generated', 0)}")
        
        response = AgentResponse(
            success=True,
            agent_type="thematic_grouping",
            data=result,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"🎨 =======================================\n")
        return response
        
    except Exception as e:
        print(f"🎨 ❌ Critical error: {str(e)}")
        print(f"🎨 =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Thematic grouping failed: {str(e)}"
        )

@router.post("/theme-refiner/refine",
            response_model=AgentResponse,
            summary="Refine themes with academic polish",
            description="Refine themes with academic polish using the Theme Refiner Agent")
async def refine_themes(request: ThemeRefinementRequest):
    """
    ✨ **Theme Refiner Agent**: Refine themes with academic polish.
    
    **What it does:**
    - Applies academic rigor to themes
    - Refines theme names and definitions
    - Ensures consistency and clarity
    
    **Use cases:**
    - Finalizing research themes
    - Ensuring academic quality
    - Improving theme coherence
    """
    try:
        print(f"\n✨ ===== THEME REFINER AGENT ENDPOINT =====")
        print(f"✨ Request received at: {datetime.now()}")
        print(f"✨ Themes to refine: {len(request.themes)}")
        print(f"✨ Research domain: {request.research_domain}")
        print(f"✨ Refinement level: {request.refinement_level}")
        
        # Initialize agent
        refiner_agent = ThemeRefinerAgent()
        
        # Run theme refinement
        result = await refiner_agent.run(
            themes=request.themes,
            research_domain=request.research_domain
        )
        
        if "error" in result:
            print(f"✨ ❌ Theme refinement failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Theme refinement failed: {result['error']}"
            )
        
        print(f"✨ ✅ Theme refinement completed successfully!")
        refinement_summary = result.get("refinement_summary", {})
        print(f"✨ Refined themes: {refinement_summary.get('total_themes_refined', 0)}")
        
        response = AgentResponse(
            success=True,
            agent_type="theme_refinement",
            data=result,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"✨ =======================================\n")
        return response
        
    except Exception as e:
        print(f"✨ ❌ Critical error: {str(e)}")
        print(f"✨ =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Theme refinement failed: {str(e)}"
        )

@router.post("/report-generator/generate",
            response_model=AgentResponse,
            summary="Generate final academic report",
            description="Generate final academic report using the Report Generator Agent")
async def generate_report(request: ReportGenerationRequest):
    """
    📄 **Report Generator Agent**: Generate final academic report.
    
    **What it does:**
    - Synthesizes research findings into a coherent academic report
    - Includes introduction, methodology, findings, discussion, and conclusion
    - Adapts to different report formats (academic, executive, technical)
    
    **Use cases:**
    - Finalizing research output
    - Creating deliverables for academic publications
    - Generating reports for stakeholders
    """
    try:
        print(f"\n📄 ===== REPORT GENERATOR AGENT ENDPOINT =====")
        print(f"📄 Request received at: {datetime.now()}")
        print(f"📄 Sections to generate: {len(request.sections)}")
        print(f"📄 Research domain: {request.research_domain}")
        print(f"📄 Report format: {request.report_format}")
        
        # Initialize agent
        report_agent = ReportGeneratorAgent()
        
        # Run report generation
        result = await report_agent.run(
            sections=request.sections
        )
        
        if "error" in result:
            print(f"📄 ❌ Report generation failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Report generation failed: {result['error']}"
            )
        
        print(f"📄 ✅ Report generation completed successfully!")
        report_summary = result.get("report_summary", {})
        print(f"📄 Word count: {report_summary.get('word_count', 0)}")
        print(f"📄 File path: {result.get('file_path', 'N/A')}")
        
        response = AgentResponse(
            success=True,
            agent_type="report_generation",
            data=result,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"📄 =======================================\n")
        return response
        
    except Exception as e:
        print(f"📄 ❌ Critical error: {str(e)}")
        print(f"📄 =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )

@router.post("/supervisor/check-quality",
            response_model=AgentResponse,
            summary="Check quality of agent output",
            description="Check quality of agent output using the Supervisor Agent")
async def check_agent_quality(request: SupervisorRequest):
    """
    🔍 **Supervisor Agent**: Check quality of agent output.
    
    **What it does:**
    - Evaluates agent output for quality and consistency
    - Provides feedback and recommendations
    - Ensures adherence to research standards
    
    **Use cases:**
    - Quality control for research outputs
    - Validating agent performance
    - Ensuring research integrity
    """
    try:
        print(f"\n🔍 ===== SUPERVISOR AGENT ENDPOINT =====")
        print(f"🔍 Request received at: {datetime.now()}")
        print(f"🔍 Agent type to supervise: {request.agent_type}")
        print(f"🔍 Research domain: {request.research_domain}")
        
        # Initialize agent
        supervisor_agent = SupervisorAgent()
        
        # Run quality check
        result = await supervisor_agent.check_quality(
            agent_output=request.agent_output,
            agent_type=request.agent_type,
            research_domain=request.research_domain
        )
        
        if not result:
            print(f"🔍 ❌ Quality check failed: No result returned")
            raise HTTPException(
                status_code=400,
                detail=f"Quality check failed: No result returned"
            )
        
        print(f"🔍 ✅ Quality check completed successfully!")
        print(f"🔍 Status: {result.status}")
        print(f"🔍 Quality score: {result.quality_score}")
        print(f"🔍 Confidence: {result.confidence}")
        
        response = AgentResponse(
            success=True,
            agent_type="supervisor",
            data={
                "status": result.status,
                "feedback": result.feedback,
                "action": result.action,
                "confidence": result.confidence,
                "issues_found": result.issues_found,
                "quality_score": result.quality_score
            },
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"🔍 =======================================\n")
        return response
        
    except Exception as e:
        print(f"🔍 ❌ Critical error: {str(e)}")
        print(f"🔍 =======================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Quality check failed: {str(e)}"
        )

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """
    Execute a specific agent with provided input data.
    
    This endpoint allows you to run individual agents:
    - **literature_review**: Generate literature review from documents
    - **initial_coding**: Perform open coding on documents
    - **thematic_grouping**: Group codes into themes
    - **theme_refinement**: Refine themes with academic polish
    - **report_generation**: Generate final academic report
    
    Each agent requires specific input data as defined in the request model.
    """
    try:
        # Convert request to service format
        request_data = {
            "agent_type": request.agent_type.value,
            "documents": request.documents,
            "coded_units": request.coded_units,
            "themes": request.themes,
            "sections": request.sections,
            "research_domain": request.research_domain
        }
        
        # Execute agent based on type
        if request.agent_type == AgentType.LITERATURE_REVIEW:
            result = await agent_service.run_literature_review(
                request.documents, request.research_domain
            )
        elif request.agent_type == AgentType.INITIAL_CODING:
            result = await agent_service.run_initial_coding(
                request.documents, request.research_domain
            )
        elif request.agent_type == AgentType.THEMATIC_GROUPING:
            result = await agent_service.run_thematic_grouping(
                request.coded_units, request.research_domain
            )
        elif request.agent_type == AgentType.THEME_REFINEMENT:
            result = await agent_service.run_theme_refinement(
                request.themes, request.research_domain
            )
        elif request.agent_type == AgentType.REPORT_GENERATION:
            result = await agent_service.run_report_generation(
                request.sections, request.research_domain
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported agent type: {request.agent_type}"
            )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Agent execution failed: {result.get('error', 'Unknown error')}"
            )
        
        response = AgentResponse(
            success=True,
            agent_type=request.agent_type.value,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )

@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """
    Get the status of all agents.
    
    Returns status information for all available agents including:
    - Current status (ready, running, error)
    - Last usage timestamp
    - Performance metrics
    - Error messages if any
    """
    try:
        result = agent_service.get_agent_status()
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get agent status: {result.get('error', 'Unknown error')}"
            )
        
        response = AgentStatusResponse(
            success=True,
            agents=result["agents"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )

@router.get("/{agent_type}/health", response_model=AgentHealthResponse)
async def get_agent_health(
    agent_type: AgentType = Path(..., description="Type of agent to check")
):
    """
    Get detailed health information for a specific agent.
    
    Returns comprehensive health metrics including:
    - Agent status and uptime
    - Memory and CPU usage
    - Error count and success rate
    - Performance metrics
    """
    try:
        result = agent_service.get_agent_health(agent_type.value)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Agent not found: {agent_type.value}"
            )
        
        response = AgentHealthResponse(
            success=True,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent health: {str(e)}"
        )

@router.get("/{agent_type}/performance", response_model=AgentResponse)
async def get_agent_performance(
    agent_type: AgentType = Path(..., description="Type of agent"),
    limit: int = Query(10, ge=1, le=100, description="Number of recent operations to include")
):
    """
    Get performance metrics for a specific agent.
    
    Returns performance statistics including:
    - Total operations and success rate
    - Average processing time
    - Quality scores
    - Recent operation history
    """
    try:
        result = agent_service.get_agent_performance(agent_type.value, limit)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Agent not found: {agent_type.value}"
            )
        
        response = AgentResponse(
            success=True,
            agent_type=agent_type.value,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent performance: {str(e)}"
        )

@router.post("/{agent_type}/restart", response_model=AgentResponse)
async def restart_agent(
    agent_type: AgentType = Path(..., description="Type of agent to restart")
):
    """
    Restart a specific agent.
    
    This is useful when an agent is in an error state or needs to be reset.
    The agent will be reinitialized and marked as ready.
    """
    try:
        result = agent_service.restart_agent(agent_type.value)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to restart agent: {result.get('error', 'Unknown error')}"
            )
        
        response = AgentResponse(
            success=True,
            agent_type=agent_type.value,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart agent: {str(e)}"
        )

@router.get("/types", response_model=List[str])
async def get_available_agent_types():
    """
    Get a list of all available agent types.
    
    Returns the list of agent types that can be executed:
    - literature_review
    - initial_coding
    - thematic_grouping
    - theme_refinement
    - report_generation
    - supervisor
    """
    try:
        agent_types = [agent_type.value for agent_type in AgentType]
        return agent_types
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent types: {str(e)}"
        )

@router.get("/{agent_type}/capabilities", response_model=AgentResponse)
async def get_agent_capabilities(
    agent_type: AgentType = Path(..., description="Type of agent")
):
    """
    Get capabilities and requirements for a specific agent.
    
    Returns information about:
    - Required input data format
    - Expected output format
    - Processing capabilities
    - Configuration options
    """
    try:
        result = agent_service.get_agent_capabilities(agent_type.value)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Agent not found: {agent_type.value}"
            )
        
        response = AgentResponse(
            success=True,
            agent_type=agent_type.value,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent capabilities: {str(e)}"
        )

@router.post("/{agent_type}/test", response_model=AgentResponse)
async def test_agent(
    agent_type: AgentType = Path(..., description="Type of agent to test"),
    test_data: Optional[dict] = None
):
    """
    Test a specific agent with sample data.
    
    This endpoint allows you to test an agent with minimal sample data
    to verify it's working correctly without running a full operation.
    """
    try:
        result = agent_service.test_agent(agent_type.value, test_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Agent test failed: {result.get('error', 'Unknown error')}"
            )
        
        response = AgentResponse(
            success=True,
            agent_type=agent_type.value,
            data=result["data"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent test failed: {str(e)}"
        ) 