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

from fastapi import APIRouter, HTTPException, Query, Path, Body, BackgroundTasks
from fastapi.responses import JSONResponse

from models.requests import AgentRequest
from models.responses import (
    AgentResponse, AgentStatusResponse, AgentHealthResponse
)
from models.agents import (
    AgentType, AgentStatus,
    DataExtractorRequest, RetrieverRequest, LiteratureReviewRequest,
    InitialCodingRequest, ThematicGroupingRequest, ThemeRefinementRequest,
    ReportGenerationRequest, SupervisorRequest, RetryAgentRequest
)
from services.agent_service import AgentService

# Import individual agents
from agents.data_extractor_agent import DataExtractorAgent
from agents.retriever_agent import RetrieverAgent
from agents.literature_review_agent import LiteratureReviewAgent
from agents.initial_coding_agent import InitialCodingAgent
from agents.thematic_grouping_agent import ThematicGroupingAgent
from agents.theme_refiner_agent import ThemeRefinerAgent
from agents.report_generator_agent import ReportGeneratorAgent
from agents.supervisor_agent import SupervisorAgent
from agents.enhanced_supervisor_agent import EnhancedSupervisorAgent
from services.agent_retry_service import AgentRetryService
from utils.llm_backends import get_llm_backend
import asyncio
import traceback
# NEW IMPORTS
from agents.multi_source_data_extractor_agent import MultiSourceDataExtractorAgent
from models.multi_source_models import MultiSourceExtractorRequest

router = APIRouter()

# Initialize agent service
agent_service = AgentService()

# Individual Agent Routes

@router.post("/data-extractor/extract", 
            response_model=AgentResponse,
            summary="Extract content from documents",
            description="Extract structured content from academic documents using the Data Extractor Agent")
async def extract_document_content(request: DataExtractorRequest):
    print(f"🔍 [BACKEND DEBUG] Data extractor request received:")
    print(f"🔍 [BACKEND DEBUG] query: {request.query}")
    print(f"🔍 [BACKEND DEBUG] max_results: {request.max_results} (type: {type(request.max_results)})")
    print(f"🔍 [BACKEND DEBUG] year_from: {request.year_from} (type: {type(request.year_from)})")
    print(f"🔍 [BACKEND DEBUG] year_to: {request.year_to} (type: {type(request.year_to)})")
    print(f"🔍 [BACKEND DEBUG] research_domain: {request.research_domain}")
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
        print(f"🔍 Research domain: {request.agent_output.get('research_domain', 'Not specified')}")
        print(f"🔍 [SUPERVISOR DEBUG] Original agent input received:")
        print(f"🔍 [SUPERVISOR DEBUG] Type: {type(request.original_agent_input)}")
        print(f"🔍 [SUPERVISOR DEBUG] Value: {request.original_agent_input}")
        if request.original_agent_input:
            if isinstance(request.original_agent_input, dict):
                print(f"🔍 [SUPERVISOR DEBUG] Keys: {list(request.original_agent_input.keys())}")
                # Check if it's a nested structure
                if 'original_agent_input' in request.original_agent_input:
                    nested_input = request.original_agent_input['original_agent_input']
                    print(f"🔍 [SUPERVISOR DEBUG] Found nested original_agent_input: {nested_input}")
                    print(f"🔍 [SUPERVISOR DEBUG] max_results: {nested_input.get('max_results')}")
                    print(f"🔍 [SUPERVISOR DEBUG] year_from: {nested_input.get('year_from')}")
                    print(f"🔍 [SUPERVISOR DEBUG] year_to: {nested_input.get('year_to')}")
                else:
                    print(f"🔍 [SUPERVISOR DEBUG] max_results: {request.original_agent_input.get('max_results')}")
                    print(f"🔍 [SUPERVISOR DEBUG] year_from: {request.original_agent_input.get('year_from')}")
                    print(f"🔍 [SUPERVISOR DEBUG] year_to: {request.original_agent_input.get('year_to')}")
            else:
                print(f"🔍 [SUPERVISOR DEBUG] WARNING: original_agent_input is not a dictionary!")
        else:
            print(f"🔍 [SUPERVISOR DEBUG] WARNING: original_agent_input is None or empty!")
        
        # Initialize enhanced supervisor agent
        from agents.enhanced_supervisor_agent import EnhancedSupervisorAgent
        supervisor_agent = EnhancedSupervisorAgent()
        
        # Run enhanced evaluation and retry
        result = await supervisor_agent.evaluate_quality(
            agent_output=request.agent_output,
            agent_type=request.agent_type,
            agent_input=request.agent_input if hasattr(request, 'agent_input') else {},
            original_agent_input=request.original_agent_input
        )
        
        print(f"🔍 ✅ Enhanced supervisor evaluation completed!")
        print(f"🔍 Final status: {result.final_status}")
        print(f"🔍 Retry attempts: {result.retry_attempts}")
        print(f"🔍 Initial assessment: {result.initial_assessment.status}")
        print(f"🔍 Retry output type: {type(result.retry_output)}")
        print(f"🔍 Final assessment type: {type(result.final_assessment)}")
        
        response = AgentResponse(
            success=True,
            agent_type="supervisor",
            data={
                "initial_assessment": result.initial_assessment.__dict__,
                "final_status": result.final_status,
                "final_message": result.final_message,
                "retry_attempts": result.retry_attempts,
                "retry_output": result.retry_output,
                "final_assessment": result.final_assessment.__dict__ if result.final_assessment else None
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


@router.post("/retry-agent",
            response_model=AgentResponse,
            summary="Retry agent with enhanced context",
            description="Retry an agent with enhanced context from supervisor feedback and user input")
async def retry_agent_with_context(request: RetryAgentRequest):
    """
    🔄 **Agent Retry with Enhanced Context**: Retry an agent with improved context.
    
    **What it does:**
    - Takes supervisor feedback and user context
    - Retries the specified agent with enhanced instructions
    - Returns improved agent output
    
    **Use cases:**
    - Improving agent output based on supervisor assessment
    - Human-in-the-loop refinement of agent results
    - Iterative improvement of research outputs
    """
    try:
        print(f"\n🔄 ===== AGENT RETRY ENDPOINT =====")
        print(f"🔄 Request received at: {datetime.now()}")
        print(f"🔄 Agent type: {request.agent_type}")
        print(f"🔄 Enhanced context: {request.enhanced_context[:100]}...")
        print(f"🔄 User context: {request.user_context[:100] if request.user_context else 'None'}...")
        print(f"🔄 [RETRY DEBUG] Original agent input received:")
        print(f"🔄 [RETRY DEBUG] {request.original_agent_input}")
        if request.original_agent_input:
            print(f"🔄 [RETRY DEBUG] max_results: {request.original_agent_input.get('max_results')}")
            print(f"🔄 [RETRY DEBUG] year_from: {request.original_agent_input.get('year_from')}")
            print(f"🔄 [RETRY DEBUG] year_to: {request.original_agent_input.get('year_to')}")
        
        # Initialize retry service
        retry_service = AgentRetryService()
        
        # Retry the agent with enhanced context
        result = await retry_service.retry_agent(
            agent_type=request.agent_type,
            original_input=request.original_agent_input,
            enhanced_context=request.enhanced_context,
            user_context=request.user_context
        )
        
        print(f"[DEBUG] Retry result type: {type(result)}")
        print(f"[DEBUG] Retry result: {result}")
        
        # Check if result is a string (error message) or dict with error
        if isinstance(result, str):
            print(f"🔄 ❌ Agent retry failed: {result}")
            raise HTTPException(
                status_code=400,
                detail=f"Agent retry failed: {result}"
            )
        elif isinstance(result, dict) and "error" in result:
            print(f"🔄 ❌ Agent retry failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Agent retry failed: {result['error']}"
            )
        
        print(f"🔄 ✅ Agent retry completed successfully!")
        print(f"🔄 Agent type: {request.agent_type}")
        print(f"🔄 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        response = AgentResponse(
            success=True,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_type=request.agent_type,
            data=result
        )
        
        print(f"🔄 =======================================")
        
        return response
        
    except Exception as e:
        print(f"🔄 ❌ Agent retry failed: {str(e)}")
        print(f"🔄 Error details: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent retry failed: {str(e)}"
        )


@router.post(
    "/multi-source-extractor/extract",
    response_model=AgentResponse,
    summary="Extract from multiple sources (OpenAlex, Europe PMC, arXiv, CORE)",
    description="Runs the multi-source extractor with optional enrichment (Crossref, Unpaywall, Semantic Scholar)."
)
async def multi_source_extract(request: MultiSourceExtractorRequest):
    try:
        print(f"\n🌐 ===== MULTI-SOURCE EXTRACTOR ENDPOINT =====")
        print(f"🌐 Request received at: {datetime.now()}")
        print(f"🌐 Query: {request.query}")
        print(f"🌐 Research domain: {request.research_domain}")
        print(f"🌐 Mode: {request.mode} | Enrich: {request.enrich}")
        yrs_from = getattr(request.years, 'from_year', None) if request.years else None
        yrs_to = getattr(request.years, 'to_year', None) if request.years else None
        print(f"🌐 Limit: {request.limit} | Years: {yrs_from}-{yrs_to}")
        print(f"🌐 Requested sources: {request.sources}")
        print(f"🌐 Store: {request.store} | Collection: {request.collection_name}")

        agent = MultiSourceDataExtractorAgent(collection_name=request.collection_name, research_domain=request.research_domain)

        # Map simplified request to agent parameters
        selected_sources = request.sources if request.mode == "manual" and request.sources else [
            "openalex", "europe_pmc", "arxiv", "core"
        ]
        if request.enrich == "none":
            enrich_with = []
        elif request.enrich == "deep":
            enrich_with = ["crossref", "unpaywall", "sem_scholar"]
        else:
            enrich_with = ["crossref", "unpaywall"]
        max_results = request.limit
        per_source_limit = max(2, (max_results + len(selected_sources) - 1) // max(1, len(selected_sources)))
        year_from = request.years.from_year if request.years else None
        year_to = request.years.to_year if request.years else None

        # Server-side decisions for fallbacks
        auto_fallback = True  # always enable backend auto fallback
        enable_playwright_env = os.getenv("ENABLE_PLAYWRIGHT", "").lower() in ("1", "true", "yes")
        use_playwright_fallback = bool(request.store) and enable_playwright_env
        full_text = None  # let the agent auto-decide (PDF when available, else abstract)

        print(f"🌐 Backend choices -> auto_fallback: {auto_fallback}, use_playwright_fallback: {use_playwright_fallback}, full_text: {full_text}")

        result = await agent.run(
            query=request.query,
            research_domain=request.research_domain,
            max_results=max_results,
            year_from=year_from,
            year_to=year_to,
            language=None,
            sources=selected_sources,
            enrich_with=enrich_with,
            per_source_limit=per_source_limit,
            oa_only=True,
            auto_fallback=auto_fallback,
            store=request.store,
            full_text=full_text,
            use_playwright_fallback=use_playwright_fallback,
        )

        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=f"Multi-source extraction failed: {result.get('error', 'Unknown error')}")

        # Ensure collection_name is returned when storing
        response_data = result.get("data", {}) or {}
        if request.store and not response_data.get("collection_name"):
            response_data["collection_name"] = request.collection_name

        response = AgentResponse(
            success=True,
            agent_type="multi_source_extractor",
            data=response_data,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        print(f"🌐 ✅ Multi-source extraction completed. docs={len(response.data.get('documents', []) )}")
        print(f"🌐 =======================================\n")
        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"🌐 ❌ Critical error: {e}")
        print(f"🌐 =======================================\n")
        raise HTTPException(status_code=500, detail=f"Multi-source extraction failed: {str(e)}")

