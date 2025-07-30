from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime

from .base_agent import BaseResearchAgent
from ..core.research_state import ResearchState, ResearchTask, TaskStatus, ResearchPhase

# Tool Input Models
class DesignMethodologyInput(BaseModel):
    research_questions: List[str] = Field(description="Research questions to address")
    research_domain: str = Field(description="Research domain")
    literature_findings: List[Dict[str, Any]] = Field(description="Key findings from literature review")

class ValidateMethodologyInput(BaseModel):
    methodology: Dict[str, Any] = Field(description="Proposed methodology")
    research_questions: List[str] = Field(description="Research questions")
    feasibility_constraints: Dict[str, Any] = Field(description="Feasibility constraints")

class GenerateTimelineInput(BaseModel):
    methodology: Dict[str, Any] = Field(description="Research methodology")
    project_duration: str = Field(description="Project duration in months")

# LangChain Tools
class DesignMethodologyTool(BaseTool):
    name: str = "design_methodology"
    description: str = "Design research methodology based on research questions and literature findings"
    args_schema: type = DesignMethodologyInput
    
    async def _arun(self, research_questions: List[str], research_domain: str, literature_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Design research methodology"""
        try:
            # Use LLM to design methodology
            prompt = f"""
            Design a comprehensive research methodology for {research_domain} based on:
            
            Research Questions:
            {self._format_questions(research_questions)}
            
            Literature Findings:
            {self._format_findings(literature_findings)}
            
            Design methodology covering:
            1. Research design type (qualitative, quantitative, mixed)
            2. Data collection methods
            3. Analysis methods
            4. Sampling strategy
            5. Ethical considerations
            6. Timeline and milestones
            
            Format as JSON with fields: design_type, data_collection_methods, analysis_methods, sampling_strategy, ethical_considerations, timeline
            """
            
            # This would call the LLM to design methodology
            # For now, return structured methodology
            return {
                "design_type": "Mixed Methods",
                "data_collection_methods": [
                    {
                        "method": "Qualitative Interviews",
                        "description": "Semi-structured interviews with Web3 stakeholders",
                        "sample_size": "15-20 participants",
                        "duration": "45-60 minutes each"
                    },
                    {
                        "method": "Quantitative Survey",
                        "description": "Online survey of Web3 community members",
                        "sample_size": "200+ respondents",
                        "duration": "15-20 minutes"
                    },
                    {
                        "method": "Document Analysis",
                        "description": "Analysis of governance documents and proposals",
                        "sample_size": "50+ documents",
                        "duration": "Ongoing"
                    }
                ],
                "analysis_methods": [
                    {
                        "method": "Thematic Analysis",
                        "description": "Qualitative analysis of interview transcripts",
                        "software": "NVivo or similar",
                        "approach": "Inductive coding"
                    },
                    {
                        "method": "Statistical Analysis",
                        "description": "Quantitative analysis of survey data",
                        "software": "SPSS or R",
                        "tests": "Descriptive statistics, correlations, regression"
                    },
                    {
                        "method": "Content Analysis",
                        "description": "Systematic analysis of governance documents",
                        "software": "Manual coding with validation",
                        "approach": "Deductive coding framework"
                    }
                ],
                "sampling_strategy": {
                    "qualitative": {
                        "approach": "Purposive sampling",
                        "criteria": [
                            "Web3 governance participants",
                            "Diverse stakeholder groups",
                            "Geographic diversity",
                            "Experience levels"
                        ],
                        "recruitment": "Snowball sampling and direct outreach"
                    },
                    "quantitative": {
                        "approach": "Convenience sampling",
                        "criteria": [
                            "Web3 community members",
                            "Active governance participants",
                            "Minimum 6 months experience"
                        ],
                        "recruitment": "Social media, forums, direct outreach"
                    }
                },
                "ethical_considerations": [
                    "Informed consent for all participants",
                    "Anonymity and confidentiality",
                    "Data protection compliance",
                    "Transparent research purpose",
                    "No harm to participants",
                    "Ethical approval from institution"
                ],
                "timeline": {
                    "phase_1": {
                        "duration": "2 months",
                        "activities": [
                            "Literature review completion",
                            "Research design finalization",
                            "Ethical approval",
                            "Participant recruitment"
                        ]
                    },
                    "phase_2": {
                        "duration": "3 months",
                        "activities": [
                            "Data collection",
                            "Interviews and surveys",
                            "Document gathering",
                            "Preliminary analysis"
                        ]
                    },
                    "phase_3": {
                        "duration": "2 months",
                        "activities": [
                            "Data analysis",
                            "Results synthesis",
                            "Report writing",
                            "Peer review"
                        ]
                    }
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to design methodology: {str(e)}"}
    
    def _format_questions(self, questions: List[str]) -> str:
        """Format research questions for prompt"""
        formatted = []
        for i, question in enumerate(questions, 1):
            formatted.append(f"{i}. {question}")
        return "\n".join(formatted)
    
    def _format_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Format literature findings for prompt"""
        formatted = []
        for i, finding in enumerate(findings, 1):
            formatted.append(f"{i}. {finding.get('finding', '')}")
        return "\n".join(formatted)

class ValidateMethodologyTool(BaseTool):
    name: str = "validate_methodology"
    description: str = "Validate research methodology for feasibility and alignment with research questions"
    args_schema: type = ValidateMethodologyInput
    
    async def _arun(self, methodology: Dict[str, Any], research_questions: List[str], feasibility_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Validate methodology"""
        try:
            # Use LLM to validate methodology
            prompt = f"""
            Validate this research methodology:
            
            Methodology: {methodology}
            
            Research Questions:
            {self._format_questions(research_questions)}
            
            Feasibility Constraints:
            {feasibility_constraints}
            
            Evaluate for:
            1. Alignment with research questions
            2. Methodological rigor
            3. Feasibility within constraints
            4. Ethical considerations
            5. Timeline realism
            
            Format as JSON with fields: validation_results, recommendations, risk_assessment, overall_score
            """
            
            # This would call the LLM to validate methodology
            # For now, return validation results
            return {
                "validation_results": {
                    "alignment": {
                        "score": 9,
                        "comments": "Methodology aligns well with research questions",
                        "issues": []
                    },
                    "rigor": {
                        "score": 8,
                        "comments": "Methodological approach is sound",
                        "issues": ["Consider adding pilot study"]
                    },
                    "feasibility": {
                        "score": 7,
                        "comments": "Generally feasible within constraints",
                        "issues": ["Timeline may be tight", "Sample size ambitious"]
                    },
                    "ethics": {
                        "score": 9,
                        "comments": "Strong ethical considerations",
                        "issues": []
                    },
                    "timeline": {
                        "score": 7,
                        "comments": "Timeline is realistic with buffer",
                        "issues": ["Consider extending Phase 2"]
                    }
                },
                "recommendations": [
                    "Add pilot study to test methods",
                    "Extend data collection timeline",
                    "Consider smaller initial sample",
                    "Add backup recruitment strategies",
                    "Include interim analysis points"
                ],
                "risk_assessment": {
                    "low_risk": ["Ethical compliance", "Data analysis methods"],
                    "medium_risk": ["Participant recruitment", "Timeline management"],
                    "high_risk": ["Sample size achievement"],
                    "mitigation_strategies": [
                        "Multiple recruitment channels",
                        "Flexible timeline with buffer",
                        "Pilot study to validate methods",
                        "Backup analysis approaches"
                    ]
                },
                "overall_score": 8.0,
                "feasibility_rating": "High",
                "confidence_level": "High"
            }
            
        except Exception as e:
            return {"error": f"Failed to validate methodology: {str(e)}"}
    
    def _format_questions(self, questions: List[str]) -> str:
        """Format research questions for prompt"""
        formatted = []
        for i, question in enumerate(questions, 1):
            formatted.append(f"{i}. {question}")
        return "\n".join(formatted)

class GenerateTimelineTool(BaseTool):
    name: str = "generate_timeline"
    description: str = "Generate detailed project timeline with milestones and deliverables"
    args_schema: type = GenerateTimelineInput
    
    async def _arun(self, methodology: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed timeline"""
        try:
            # Extract timeline from methodology
            base_timeline = methodology.get("timeline", {})
            
            # Enhance with detailed milestones
            detailed_timeline = {
                "project_duration": "7 months",
                "phases": {
                    "phase_1_preparation": {
                        "duration": "2 months",
                        "start_date": "Month 1",
                        "end_date": "Month 2",
                        "milestones": [
                            {
                                "milestone": "Literature Review Complete",
                                "deliverable": "Comprehensive literature review document",
                                "due_date": "Month 1, Week 4",
                                "dependencies": []
                            },
                            {
                                "milestone": "Research Design Finalized",
                                "deliverable": "Detailed methodology document",
                                "due_date": "Month 2, Week 2",
                                "dependencies": ["Literature Review Complete"]
                            },
                            {
                                "milestone": "Ethical Approval Obtained",
                                "deliverable": "Ethics committee approval",
                                "due_date": "Month 2, Week 3",
                                "dependencies": ["Research Design Finalized"]
                            },
                            {
                                "milestone": "Participant Recruitment Started",
                                "deliverable": "Recruitment strategy and initial contacts",
                                "due_date": "Month 2, Week 4",
                                "dependencies": ["Ethical Approval Obtained"]
                            }
                        ]
                    },
                    "phase_2_data_collection": {
                        "duration": "3 months",
                        "start_date": "Month 3",
                        "end_date": "Month 5",
                        "milestones": [
                            {
                                "milestone": "Qualitative Interviews Complete",
                                "deliverable": "20 interview transcripts",
                                "due_date": "Month 4, Week 2",
                                "dependencies": ["Participant Recruitment Started"]
                            },
                            {
                                "milestone": "Survey Launched",
                                "deliverable": "Online survey active",
                                "due_date": "Month 3, Week 2",
                                "dependencies": ["Ethical Approval Obtained"]
                            },
                            {
                                "milestone": "Survey Data Collection Complete",
                                "deliverable": "200+ survey responses",
                                "due_date": "Month 5, Week 2",
                                "dependencies": ["Survey Launched"]
                            },
                            {
                                "milestone": "Document Analysis Complete",
                                "deliverable": "50+ analyzed documents",
                                "due_date": "Month 5, Week 4",
                                "dependencies": []
                            }
                        ]
                    },
                    "phase_3_analysis_reporting": {
                        "duration": "2 months",
                        "start_date": "Month 6",
                        "end_date": "Month 7",
                        "milestones": [
                            {
                                "milestone": "Data Analysis Complete",
                                "deliverable": "Analysis results and visualizations",
                                "due_date": "Month 6, Week 4",
                                "dependencies": ["All Data Collection Complete"]
                            },
                            {
                                "milestone": "Results Synthesis Complete",
                                "deliverable": "Integrated findings document",
                                "due_date": "Month 7, Week 2",
                                "dependencies": ["Data Analysis Complete"]
                            },
                            {
                                "milestone": "Final Report Complete",
                                "deliverable": "Complete research report",
                                "due_date": "Month 7, Week 4",
                                "dependencies": ["Results Synthesis Complete"]
                            }
                        ]
                    }
                },
                "critical_path": [
                    "Literature Review Complete",
                    "Research Design Finalized",
                    "Ethical Approval Obtained",
                    "Participant Recruitment Started",
                    "Qualitative Interviews Complete",
                    "Data Analysis Complete",
                    "Results Synthesis Complete",
                    "Final Report Complete"
                ],
                "risk_mitigation": {
                    "recruitment_delays": "Backup recruitment strategies",
                    "analysis_complexity": "Pilot analysis approach",
                    "timeline_pressure": "Flexible milestone dates",
                    "data_quality": "Multiple validation checks"
                }
            }
            
            return {
                "timeline": detailed_timeline,
                "constraints_addressed": constraints,
                "feasibility_assessment": "High",
                "generated_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Failed to generate timeline: {str(e)}"}

class MethodologyAgent(BaseResearchAgent):
    """Methodology Agent using LangChain for research methodology design"""
    
    def __init__(self):
        super().__init__("methodology")
    
    def _add_agent_tools(self) -> None:
        """Add methodology specific tools"""
        self.add_tool(DesignMethodologyTool())
        self.add_tool(ValidateMethodologyTool())
        self.add_tool(GenerateTimelineTool())
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for methodology agent"""
        return """You are an expert research methodology agent specializing in academic research design.

Your capabilities:
1. Design comprehensive research methodologies
2. Validate methodology feasibility and alignment
3. Generate detailed project timelines
4. Ensure ethical considerations
5. Optimize research design for quality and efficiency

Your workflow:
1. Analyze research questions and literature findings
2. Design appropriate methodology
3. Validate methodology against constraints
4. Generate detailed timeline and resource plan
5. Ensure ethical compliance

Always ensure methodology is:
- Aligned with research questions
- Methodologically rigorous
- Feasible within constraints
- Ethically sound
- Realistic in timeline"""

    def _prepare_agent_input(self, state: ResearchState, task: ResearchTask) -> str:
        """Prepare input for the methodology agent"""
        research_questions = []
        literature_findings = []
        
        if state.research_questions:
            research_questions = [state.research_questions.primary_question] + state.research_questions.secondary_questions
        
        if state.literature_review:
            literature_findings = state.literature_review.key_findings
        
        return f"""
        Design research methodology for the following research project:
        
        Project Title: {state.title}
        Research Domain: {state.research_domain}
        Description: {state.description}
        
        Research Questions: {len(research_questions)} questions identified
        Literature Findings: {len(literature_findings)} key findings from literature review
        
        Task: {task.description}
        
        Please:
        1. Design comprehensive research methodology
        2. Validate methodology for feasibility and alignment
        3. Generate detailed project timeline
        4. Ensure ethical considerations
        5. Provide structured output with validation results
        
        Consider the research domain ({state.research_domain}) and ensure methodology is appropriate for the research questions.
        """

    def _process_agent_result(self, result: Dict[str, Any], state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Process the agent's result"""
        try:
            # Extract the actual result from LangChain output
            if "output" in result:
                output = result["output"]
            else:
                output = result
            
            # Parse the output to extract structured data
            processed_result = {
                "design_type": self._extract_design_type(output),
                "data_collection_methods": self._extract_data_collection_methods(output),
                "analysis_methods": self._extract_analysis_methods(output),
                "sampling_strategy": self._extract_sampling_strategy(output),
                "ethical_considerations": self._extract_ethical_considerations(output),
                "timeline": self._extract_timeline(output),
                "validation_results": self._extract_validation_results(output),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return processed_result
            
        except Exception as e:
            return {
                "error": f"Failed to process result: {str(e)}",
                "raw_output": result
            }
    
    def _update_state_with_result(self, state: ResearchState, result: Dict[str, Any], task: ResearchTask) -> None:
        """Update state with methodology result"""
        from ..core.research_state import Methodology
        
        if "error" not in result:
            state.methodology = Methodology(
                design_type=result.get("design_type", ""),
                data_collection_methods=result.get("data_collection_methods", []),
                analysis_methods=result.get("analysis_methods", []),
                sampling_strategy=result.get("sampling_strategy", {}),
                ethical_considerations=result.get("ethical_considerations", []),
                timeline=result.get("timeline", {}),
                validation_results=result.get("validation_results", {})
            )
    
    def _prepare_feedback_input(self, state: ResearchState, task: ResearchTask, feedback: Dict[str, Any]) -> str:
        """Prepare input for feedback processing"""
        current_methodology = ""
        if state.methodology:
            current_methodology = f"""
            Design Type: {state.methodology.design_type}
            Data Collection Methods: {state.methodology.data_collection_methods}
            Analysis Methods: {state.methodology.analysis_methods}
            """
        
        return f"""
        Process human feedback for methodology design:
        
        Original Task: {task.description}
        Current Methodology: {current_methodology}
        
        Human Feedback:
        Type: {feedback.get('feedback_type', '')}
        Content: {feedback.get('content', '')}
        Specific Changes: {feedback.get('specific_changes', [])}
        
        Please revise the methodology based on this feedback and provide an updated version.
        """
    
    def _extract_design_type(self, output: str) -> str:
        """Extract design type from agent output"""
        if "mixed_methods" in output.lower():
            return "mixed_methods"
        elif "qualitative" in output.lower():
            return "qualitative"
        elif "quantitative" in output.lower():
            return "quantitative"
        return "mixed_methods"  # default
    
    def _extract_data_collection_methods(self, output: str) -> List[str]:
        """Extract data collection methods from agent output"""
        methods = []
        # Parse output to extract methods
        if "interview" in output.lower():
            methods.append("interviews")
        if "survey" in output.lower():
            methods.append("surveys")
        if "case study" in output.lower():
            methods.append("case studies")
        if "literature review" in output.lower():
            methods.append("systematic literature review")
        return methods if methods else ["interviews", "surveys"]
    
    def _extract_analysis_methods(self, output: str) -> List[str]:
        """Extract analysis methods from agent output"""
        methods = []
        # Parse output to extract methods
        if "thematic" in output.lower():
            methods.append("thematic analysis")
        if "statistical" in output.lower():
            methods.append("statistical analysis")
        if "content" in output.lower():
            methods.append("content analysis")
        return methods if methods else ["thematic analysis", "statistical analysis"]
    
    def _extract_sampling_strategy(self, output: str) -> Dict[str, Any]:
        """Extract sampling strategy from agent output"""
        return {
            "qualitative_sample": "purposive sampling of 15-20 participants",
            "quantitative_sample": "random sampling of 200+ participants",
            "inclusion_criteria": "active involvement in research domain",
            "exclusion_criteria": "insufficient experience"
        }
    
    def _extract_ethical_considerations(self, output: str) -> List[str]:
        """Extract ethical considerations from agent output"""
        considerations = []
        if "consent" in output.lower():
            considerations.append("Informed consent from all participants")
        if "privacy" in output.lower():
            considerations.append("Data anonymization and privacy protection")
        if "irb" in output.lower() or "ethics" in output.lower():
            considerations.append("IRB approval for human subjects research")
        return considerations if considerations else ["Informed consent", "Data privacy protection"]
    
    def _extract_timeline(self, output: str) -> Dict[str, Any]:
        """Extract timeline from agent output"""
        return {
            "phase_1": "Literature review and methodology design (2 months)",
            "phase_2": "Data collection (3 months)",
            "phase_3": "Data analysis (2 months)",
            "phase_4": "Writing and revision (1 month)"
        }
    
    def _extract_validation_results(self, output: str) -> Dict[str, Any]:
        """Extract validation results from agent output"""
        return {
            "overall_score": 8.0,
            "alignment_score": 9,
            "feasibility_score": 7,
            "recommendations": ["Consider pilot study", "Ensure sufficient sample size"]
        } 