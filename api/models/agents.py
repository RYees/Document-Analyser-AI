"""
Agent-specific models for the Research Pipeline API.
Contains Pydantic models for agent status, health, and output structures.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    """Enumeration of available agent types."""
    LITERATURE_REVIEW = "literature_review"
    INITIAL_CODING = "initial_coding"
    THEMATIC_GROUPING = "thematic_grouping"
    THEME_REFINEMENT = "theme_refinement"
    REPORT_GENERATION = "report_generation"
    SUPERVISOR = "supervisor"

class AgentStatus(str, Enum):
    """Enumeration of agent status values."""
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    BUSY = "busy"
    OFFLINE = "offline"

class AgentHealth(BaseModel):
    """Model for agent health information."""
    agent_type: AgentType = Field(..., description="Type of agent")
    status: AgentStatus = Field(..., description="Current status")
    last_used: Optional[str] = Field(default=None, description="Last usage timestamp")
    healthy: bool = Field(..., description="Whether the agent is healthy")
    uptime_seconds: Optional[float] = Field(default=None, description="Agent uptime in seconds")
    memory_usage_mb: Optional[float] = Field(default=None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(default=None, description="CPU usage percentage")
    error_count: int = Field(default=0, description="Number of recent errors")
    success_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Success rate percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "literature_review",
                "status": "ready",
                "last_used": "2024-01-15T10:30:00Z",
                "healthy": True,
                "uptime_seconds": 3600.0,
                "memory_usage_mb": 128.5,
                "cpu_usage_percent": 5.2,
                "error_count": 0,
                "success_rate": 95.5
            }
        }

class AgentStatusInfo(BaseModel):
    """Model for agent status information."""
    status: AgentStatus = Field(..., description="Current status")
    last_used: Optional[str] = Field(default=None, description="Last usage timestamp")
    error_message: Optional[str] = Field(default=None, description="Last error message")
    performance_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Performance metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ready",
                "last_used": "2024-01-15T10:30:00Z",
                "error_message": None,
                "performance_metrics": {
                    "average_response_time": 2.5,
                    "total_operations": 150,
                    "successful_operations": 145
                }
            }
        }

class AgentOutput(BaseModel):
    """Base model for agent output."""
    agent_type: AgentType = Field(..., description="Type of agent that produced the output")
    timestamp: str = Field(..., description="Output generation timestamp")
    processing_time_seconds: Optional[float] = Field(default=None, description="Processing time")
    input_size: Optional[int] = Field(default=None, description="Input size (documents, units, etc.)")
    output_size: Optional[int] = Field(default=None, description="Output size (words, codes, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "literature_review",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time_seconds": 45.2,
                "input_size": 15,
                "output_size": 2500
            }
        }

class LiteratureReviewOutput(AgentOutput):
    """Model for literature review agent output."""
    agent_type: AgentType = Field(default=AgentType.LITERATURE_REVIEW, description="Agent type")
    summary: str = Field(..., description="Literature review summary")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    research_gaps: List[str] = Field(default_factory=list, description="Research gaps identified")
    methodologies: List[str] = Field(default_factory=list, description="Methodologies found")
    future_directions: List[str] = Field(default_factory=list, description="Future research directions")
    full_literature_review: str = Field(..., description="Complete literature review text")
    documents_analyzed: int = Field(..., description="Number of documents analyzed")
    research_domain: str = Field(..., description="Research domain")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "literature_review",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time_seconds": 45.2,
                "input_size": 15,
                "output_size": 2500,
                "summary": "Comprehensive review of transparency in blockchain technology",
                "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
                "research_gaps": ["Gap 1", "Gap 2"],
                "methodologies": ["Qualitative analysis", "Systematic review"],
                "future_directions": ["Direction 1", "Direction 2"],
                "full_literature_review": "Complete literature review text...",
                "documents_analyzed": 15,
                "research_domain": "Blockchain"
            }
        }

class Code(BaseModel):
    """Model for individual code in initial coding."""
    name: str = Field(..., description="Code name")
    definition: str = Field(..., description="Code definition")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    category: str = Field(..., description="Code category (primary/sub)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Transparency Mechanisms",
                "definition": "Various mechanisms for ensuring transparency in blockchain systems",
                "confidence": 0.85,
                "category": "primary"
            }
        }

class CodedUnit(BaseModel):
    """Model for coded unit in initial coding."""
    unit_id: str = Field(..., description="Unique unit identifier")
    content: str = Field(..., description="Unit content")
    source: str = Field(..., description="Source paper")
    authors: List[str] = Field(default_factory=list, description="Paper authors")
    year: int = Field(..., description="Publication year")
    codes: List[Code] = Field(default_factory=list, description="Assigned codes")
    harvard_citation: str = Field(..., description="Harvard-style citation")
    insights: List[str] = Field(default_factory=list, description="Key insights")
    
    class Config:
        json_schema_extra = {
            "example": {
                "unit_id": "unit_0001",
                "content": "This paper discusses transparency mechanisms in blockchain...",
                "source": "Sample Paper Title",
                "authors": ["Author 1", "Author 2"],
                "year": 2023,
                "codes": [
                    {
                        "name": "Transparency Mechanisms",
                        "definition": "Various mechanisms for ensuring transparency",
                        "confidence": 0.85,
                        "category": "primary"
                    }
                ],
                "harvard_citation": "(Author 1, 2023)",
                "insights": ["Insight 1", "Insight 2"]
            }
        }

class InitialCodingOutput(AgentOutput):
    """Model for initial coding agent output."""
    agent_type: AgentType = Field(default=AgentType.INITIAL_CODING, description="Agent type")
    coding_summary: Dict[str, Any] = Field(..., description="Coding summary statistics")
    coded_units: List[CodedUnit] = Field(default_factory=list, description="Coded units")
    documents_analyzed: int = Field(..., description="Number of documents analyzed")
    research_domain: str = Field(..., description="Research domain")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "initial_coding",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time_seconds": 60.5,
                "input_size": 15,
                "output_size": 50,
                "coding_summary": {
                    "total_units_coded": 25,
                    "unique_codes_generated": 12,
                    "average_confidence": 0.82,
                    "primary_codes": ["Code 1", "Code 2"],
                    "sub_codes": ["Sub-code 1", "Sub-code 2"]
                },
                "coded_units": [
                    {
                        "unit_id": "unit_0001",
                        "content": "Sample content",
                        "source": "Sample Paper",
                        "authors": ["Author 1"],
                        "year": 2023,
                        "codes": [],
                        "harvard_citation": "(Author 1, 2023)",
                        "insights": []
                    }
                ],
                "documents_analyzed": 15,
                "research_domain": "Blockchain"
            }
        }

class Theme(BaseModel):
    """Model for theme in thematic grouping."""
    theme_name: str = Field(..., description="Theme name")
    description: str = Field(..., description="Theme description")
    codes: List[Code] = Field(default_factory=list, description="Codes in this theme")
    justification: str = Field(..., description="Justification for theme grouping")
    illustrative_quotes: List[str] = Field(default_factory=list, description="Illustrative quotes")
    cross_cutting_ideas: List[str] = Field(default_factory=list, description="Cross-cutting ideas")
    academic_reasoning: str = Field(..., description="Academic reasoning")
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme_name": "Transparency Mechanisms",
                "description": "Various mechanisms for ensuring transparency in blockchain systems",
                "codes": [
                    {
                        "name": "Transparency Mechanisms",
                        "definition": "Various mechanisms for ensuring transparency",
                        "confidence": 0.85,
                        "category": "primary"
                    }
                ],
                "justification": "These codes relate to transparency mechanisms...",
                "illustrative_quotes": ["Quote 1", "Quote 2"],
                "cross_cutting_ideas": ["Idea 1", "Idea 2"],
                "academic_reasoning": "Academic reasoning for this theme..."
            }
        }

class ThematicGroupingOutput(AgentOutput):
    """Model for thematic grouping agent output."""
    agent_type: AgentType = Field(default=AgentType.THEMATIC_GROUPING, description="Agent type")
    thematic_summary: Dict[str, Any] = Field(..., description="Thematic analysis summary")
    themes: List[Theme] = Field(default_factory=list, description="Generated themes")
    coded_units_analyzed: int = Field(..., description="Number of coded units analyzed")
    research_domain: str = Field(..., description="Research domain")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "thematic_grouping",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time_seconds": 30.2,
                "input_size": 25,
                "output_size": 5,
                "thematic_summary": {
                    "total_themes_generated": 3,
                    "total_codes_analyzed": 12,
                    "unique_codes_clustered": 12,
                    "cross_cutting_ideas": ["Idea 1", "Idea 2"],
                    "average_codes_per_theme": 4.0
                },
                "themes": [
                    {
                        "theme_name": "Transparency Mechanisms",
                        "description": "Various mechanisms for ensuring transparency",
                        "codes": [],
                        "justification": "Justification text",
                        "illustrative_quotes": [],
                        "cross_cutting_ideas": [],
                        "academic_reasoning": "Academic reasoning"
                    }
                ],
                "coded_units_analyzed": 25,
                "research_domain": "Blockchain"
            }
        }

class RefinedTheme(BaseModel):
    """Model for refined theme in theme refinement."""
    original_name: str = Field(..., description="Original theme name")
    refined_name: str = Field(..., description="Refined theme name")
    precise_definition: str = Field(..., description="Precise definition")
    scope_boundaries: str = Field(..., description="Scope boundaries")
    academic_quotes: List[Dict[str, str]] = Field(default_factory=list, description="Academic quotes with citations")
    key_concepts: List[str] = Field(default_factory=list, description="Key concepts")
    theoretical_framework: str = Field(..., description="Theoretical framework")
    research_implications: str = Field(..., description="Research implications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_name": "Transparency Mechanisms",
                "refined_name": "Blockchain Transparency Mechanisms",
                "precise_definition": "Precise definition of the theme",
                "scope_boundaries": "Scope boundaries description",
                "academic_quotes": [
                    {
                        "quote": "Sample quote",
                        "citation": "(Author, 2023)"
                    }
                ],
                "key_concepts": ["Concept 1", "Concept 2"],
                "theoretical_framework": "Theoretical framework description",
                "research_implications": "Research implications description"
            }
        }

class ThemeRefinementOutput(AgentOutput):
    """Model for theme refinement agent output."""
    agent_type: AgentType = Field(default=AgentType.THEME_REFINEMENT, description="Agent type")
    refinement_summary: Dict[str, Any] = Field(..., description="Refinement summary statistics")
    refined_themes: List[RefinedTheme] = Field(default_factory=list, description="Refined themes")
    themes_refined: int = Field(..., description="Number of themes refined")
    research_domain: str = Field(..., description="Research domain")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "theme_refinement",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time_seconds": 25.8,
                "input_size": 3,
                "output_size": 3,
                "refinement_summary": {
                    "total_themes_refined": 3,
                    "total_academic_quotes": 6,
                    "total_key_concepts": 15,
                    "average_quotes_per_theme": 2.0,
                    "average_concepts_per_theme": 5.0
                },
                "refined_themes": [
                    {
                        "original_name": "Transparency Mechanisms",
                        "refined_name": "Blockchain Transparency Mechanisms",
                        "precise_definition": "Definition",
                        "scope_boundaries": "Boundaries",
                        "academic_quotes": [],
                        "key_concepts": [],
                        "theoretical_framework": "Framework",
                        "research_implications": "Implications"
                    }
                ],
                "themes_refined": 3,
                "research_domain": "Blockchain"
            }
        }

class ReportGenerationOutput(AgentOutput):
    """Model for report generation agent output."""
    agent_type: AgentType = Field(default=AgentType.REPORT_GENERATION, description="Agent type")
    report_content: str = Field(..., description="Generated report content")
    report_summary: Dict[str, Any] = Field(..., description="Report summary statistics")
    references: List[Dict[str, str]] = Field(default_factory=list, description="References list")
    file_path: str = Field(..., description="File path where report is saved")
    research_domain: str = Field(..., description="Research domain")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "report_generation",
                "timestamp": "2024-01-15T10:30:00Z",
                "processing_time_seconds": 120.5,
                "input_size": 6,
                "output_size": 1500,
                "report_content": "# Thematic Literature Review\n\nComplete report content...",
                "report_summary": {
                    "word_count": 1500,
                    "sections_included": {
                        "Abstract": True,
                        "Introduction": True,
                        "Literature Review": True,
                        "Methodology": True,
                        "Findings": True,
                        "Discussion": True,
                        "Conclusion": True
                    },
                    "total_references": 25
                },
                "references": [
                    {
                        "author": "Author 1",
                        "year": "2023",
                        "title": "Sample Paper",
                        "full_citation": "Author 1 (2023)"
                    }
                ],
                "file_path": "/reports/report_123.md",
                "research_domain": "Blockchain"
            }
        }

class AgentPerformanceMetrics(BaseModel):
    """Model for agent performance metrics."""
    agent_type: AgentType = Field(..., description="Agent type")
    total_operations: int = Field(..., ge=0, description="Total operations performed")
    successful_operations: int = Field(..., ge=0, description="Successful operations")
    failed_operations: int = Field(..., ge=0, description="Failed operations")
    success_rate: float = Field(..., ge=0.0, le=100.0, description="Success rate percentage")
    average_processing_time: Optional[float] = Field(default=None, description="Average processing time")
    average_quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Average quality score")
    last_operation: Optional[str] = Field(default=None, description="Last operation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "literature_review",
                "total_operations": 50,
                "successful_operations": 48,
                "failed_operations": 2,
                "success_rate": 96.0,
                "average_processing_time": 45.2,
                "average_quality_score": 0.82,
                "last_operation": "2024-01-15T10:30:00Z"
            }
        }

# ===== INDIVIDUAL AGENT REQUEST MODELS =====

class DataExtractorRequest(BaseModel):
    """Request model for Data Extractor Agent."""
    query: str
    research_domain: str = "General"
    max_results: int = 20
    year_from: int = 2020
    year_to: int = 2025
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "blockchain governance transparency mechanisms",
                "research_domain": "Blockchain Governance",
                "max_results": 15,
                "year_from": 2020,
                "year_to": 2025
            }
        }

class RetrieverRequest(BaseModel):
    """Request model for Retriever Agent."""
    query: str
    research_domain: str = "General" 
    top_k: int = 10
    collection_name: str = "ResearchPaper"
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "blockchain governance transparency mechanisms",
                "research_domain": "Blockchain",
                "top_k": 5,
                "collection_name": "ResearchPaper"
            }
        }

class LiteratureReviewRequest(BaseModel):
    """Request model for Literature Review Agent."""
    documents: List[Dict[str, Any]]
    research_domain: str = "General"
    review_type: str = "thematic"  # thematic, systematic, narrative
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "title": "Blockchain Governance Study",
                        "extracted_content": "Content extracted from document...",
                        "authors": ["Author Name"],
                        "year": 2024
                    }
                ],
                "research_domain": "Blockchain Governance",
                "review_type": "thematic"
            }
        }

class InitialCodingRequest(BaseModel):
    """Request model for Initial Coding Agent."""
    documents: List[Dict[str, Any]]
    research_domain: str = "General"
    coding_approach: str = "open"  # open, axial, selective
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "title": "Research Document",
                        "extracted_content": "Text content for coding analysis...",
                        "authors": ["Researcher"],
                        "year": 2024
                    }
                ],
                "research_domain": "Qualitative Research",
                "coding_approach": "open"
            }
        }

class ThematicGroupingRequest(BaseModel):
    """Request model for Thematic Grouping Agent."""
    coded_units: List[Dict[str, Any]]
    research_domain: str = "General"
    max_themes: int = 8
    min_codes_per_theme: int = 2
    
    class Config:
        json_schema_extra = {
            "example": {
                "coded_units": [
                    {
                        "unit_id": "unit_0001",
                        "content": "Text segment about governance...",
                        "codes": [
                            {
                                "name": "transparency",
                                "definition": "Openness in decision making",
                                "confidence": 0.9
                            }
                        ]
                    }
                ],
                "research_domain": "Governance Research",
                "max_themes": 5,
                "min_codes_per_theme": 3
            }
        }

class ThemeRefinementRequest(BaseModel):
    """Request model for Theme Refinement Agent."""
    themes: List[Dict[str, Any]]
    research_domain: str = "General"
    refinement_level: str = "academic"  # academic, detailed, concise
    
    class Config:
        json_schema_extra = {
            "example": {
                "themes": [
                    {
                        "theme_name": "Governance Transparency",
                        "description": "Theme about transparency in governance",
                        "codes": [
                            {
                                "name": "transparency",
                                "definition": "Openness in processes"
                            }
                        ]
                    }
                ],
                "research_domain": "Governance",
                "refinement_level": "academic"
            }
        }

class ReportGenerationRequest(BaseModel):
    """Request model for Report Generation Agent."""
    sections: Dict[str, Any]
    research_domain: str = "General"
    report_format: str = "academic"  # academic, executive, technical
    
    class Config:
        json_schema_extra = {
            "example": {
                "sections": {
                    "literature_review": {"summary": "Literature findings..."},
                    "initial_coding": {"coded_units": []},
                    "thematic_grouping": {"themes": []},
                    "theme_refinement": {"refined_themes": []}
                },
                "research_domain": "Research Topic",
                "report_format": "academic"
            }
        }

class SupervisorRequest(BaseModel):
    """Request model for Supervisor Agent."""
    agent_output: Dict[str, Any] = Field(..., description="Output produced by the agent that needs evaluation")
    agent_type: str = Field(..., description="Type of agent (e.g., literature_review, data_extractor, etc.)")
    original_agent_input: Dict[str, Any] = Field(..., description="Original input that was sent to the agent (required for retry)")
    agent_input: Optional[Dict[str, Any]] = Field(default=None, description="Optional modified input for retry (if not provided, uses original_agent_input)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_output": {
                    "summary": "Transparency in blockchain technology is important for trust.",
                    "key_findings": ["Blockchain provides transparency"],
                    "research_gaps": ["Need more research on privacy"],
                    "full_literature_review": "A brief overview of blockchain transparency...",
                    "documents_analyzed": 3,
                    "research_domain": "Technology"
                },
                "agent_type": "literature_review",
                "original_agent_input": {
                    "documents": [
                        {
                            "title": "Blockchain Transparency in Financial Services",
                            "authors": ["Smith, J.", "Johnson, A."],
                            "abstract": "This paper explores transparency in blockchain...",
                            "extracted_content": "Blockchain technology provides unprecedented transparency...",
                            "year": 2023,
                            "source": "Journal of Financial Technology"
                        }
                    ]
                }
            }
        }


class RetryAgentRequest(BaseModel):
    """Request model for Agent Retry with Enhanced Context."""
    agent_type: str = Field(..., description="Type of agent to retry (e.g., literature_review, data_extractor, etc.)")
    original_agent_input: Dict[str, Any] = Field(..., description="Original input that was sent to the agent")
    enhanced_context: str = Field(..., description="Enhanced context from supervisor feedback and user input")
    user_context: Optional[str] = Field(default=None, description="Additional context provided by the user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "literature_review",
                "original_agent_input": {
                    "documents": [
                        {
                            "title": "Blockchain Transparency Study",
                            "authors": ["Smith, J."],
                            "extracted_content": "Content for analysis..."
                        }
                    ],
                    "research_domain": "Blockchain Technology"
                },
                "enhanced_context": "Focus on transparency mechanisms in blockchain protocol layers. Include detailed analysis of consensus mechanisms and their transparency implications. Provide specific examples and case studies.",
                "user_context": "I need more detailed analysis of the technical aspects of blockchain transparency."
            }
        } 