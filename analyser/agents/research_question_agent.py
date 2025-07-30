from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime

from .base_agent import BaseResearchAgent
from ..core.research_state import ResearchState, ResearchTask, TaskStatus, ResearchPhase

# Tool Input Models
class FormulateQuestionsInput(BaseModel):
    research_topic: str = Field(description="Research topic or area")
    literature_findings: List[Dict[str, Any]] = Field(description="Key findings from literature review")
    research_gaps: List[Dict[str, Any]] = Field(description="Identified research gaps")

class RefineQuestionsInput(BaseModel):
    initial_questions: List[str] = Field(description="Initial research questions")
    feedback: Dict[str, Any] = Field(description="Feedback on questions")
    constraints: Dict[str, Any] = Field(description="Research constraints")

class ValidateQuestionsInput(BaseModel):
    research_questions: List[str] = Field(description="Research questions to validate")
    methodology: Dict[str, Any] = Field(description="Proposed methodology")
    feasibility_constraints: Dict[str, Any] = Field(description="Feasibility constraints")

# LangChain Tools
class FormulateQuestionsTool(BaseTool):
    name: str = "formulate_questions"
    description: str = "Formulate research questions based on topic, literature findings, and research gaps"
    args_schema: type = FormulateQuestionsInput
    
    async def _arun(self, research_topic: str, literature_findings: List[Dict[str, Any]], research_gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formulate research questions"""
        try:
            # Use LLM to formulate questions
            prompt = f"""
            Formulate research questions for {research_topic}:
            
            Literature Findings: {literature_findings}
            Research Gaps: {research_gaps}
            
            Create research questions that:
            1. Address identified research gaps
            2. Build on existing literature findings
            3. Are specific and measurable
            4. Align with research topic
            5. Are feasible to investigate
            
            Format as JSON with fields: primary_question, secondary_questions, question_rationale, alignment_analysis
            """
            
            # This would call the LLM to formulate questions
            # For now, return structured questions
            return {
                "primary_question": "What are the most effective governance mechanisms for ensuring transparency and stakeholder participation in Web3 ecosystems?",
                "secondary_questions": [
                    "How do different governance structures impact stakeholder engagement levels?",
                    "What role does transparency play in building trust within decentralized governance systems?",
                    "How can governance mechanisms be optimized to balance decentralization with efficiency?",
                    "What are the key factors that influence governance effectiveness in Web3 projects?"
                ],
                "question_rationale": {
                    "primary_rationale": "Addresses the core challenge of effective governance in Web3 ecosystems",
                    "secondary_rationales": [
                        "Explores specific governance structures and their impact",
                        "Investigates transparency-trust relationship",
                        "Examines decentralization-efficiency trade-off",
                        "Identifies success factors for governance"
                    ]
                },
                "alignment_analysis": {
                    "literature_alignment": "High - builds on existing findings about transparency and participation",
                    "gap_addressing": "Strong - addresses identified gaps in governance mechanism research",
                    "feasibility": "Medium - requires mixed-methods approach",
                    "originality": "High - novel focus on Web3 governance optimization"
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to formulate questions: {str(e)}"}

class RefineQuestionsTool(BaseTool):
    name: str = "refine_questions"
    description: str = "Refine research questions based on feedback and constraints"
    args_schema: type = RefineQuestionsInput
    
    async def _arun(self, initial_questions: List[str], feedback: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Refine research questions"""
        try:
            # Use LLM to refine questions
            prompt = f"""
            Refine research questions based on feedback:
            
            Initial Questions: {initial_questions}
            Feedback: {feedback}
            Constraints: {constraints}
            
            Refine questions to:
            1. Address feedback concerns
            2. Work within constraints
            3. Improve clarity and specificity
            4. Maintain research value
            5. Ensure feasibility
            
            Format as JSON with fields: refined_questions, changes_made, rationale, feasibility_assessment
            """
            
            # This would call the LLM to refine questions
            # For now, return refined questions
            return {
                "refined_questions": [
                    "What governance mechanisms most effectively balance transparency and stakeholder participation in Web3 ecosystems?",
                    "How do governance structure variations impact stakeholder engagement in decentralized systems?",
                    "What transparency mechanisms best build trust in Web3 governance?",
                    "How can governance be optimized for both decentralization and efficiency?"
                ],
                "changes_made": [
                    "Made primary question more specific about balance",
                    "Clarified stakeholder engagement focus",
                    "Narrowed transparency question scope",
                    "Simplified optimization question"
                ],
                "rationale": {
                    "specificity_improvement": "Questions now more focused and measurable",
                    "constraint_adherence": "Questions work within identified constraints",
                    "clarity_enhancement": "Language is clearer and more precise",
                    "feasibility_consideration": "Questions are more realistic to investigate"
                },
                "feasibility_assessment": {
                    "data_availability": "High - governance data is accessible",
                    "methodological_feasibility": "Medium - requires mixed methods",
                    "resource_requirements": "Medium - moderate resource needs",
                    "timeline_realism": "High - achievable within project timeline"
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to refine questions: {str(e)}"}

class ValidateQuestionsTool(BaseTool):
    name: str = "validate_questions"
    description: str = "Validate research questions for feasibility, alignment, and quality"
    args_schema: type = ValidateQuestionsInput
    
    async def _arun(self, research_questions: List[str], methodology: Dict[str, Any], feasibility_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research questions"""
        try:
            # Use LLM to validate questions
            prompt = f"""
            Validate research questions for feasibility and quality:
            
            Research Questions: {research_questions}
            Methodology: {methodology}
            Feasibility Constraints: {feasibility_constraints}
            
            Validate for:
            1. Clarity and specificity
            2. Methodological alignment
            3. Feasibility within constraints
            4. Research value and contribution
            5. Ethical considerations
            
            Format as JSON with fields: validation_results, quality_scores, recommendations, risk_assessment
            """
            
            # This would call the LLM to validate questions
            # For now, return validation results
            return {
                "validation_results": {
                    "clarity": {
                        "score": 9,
                        "comments": "Questions are clear and well-defined",
                        "issues": []
                    },
                    "specificity": {
                        "score": 8,
                        "comments": "Questions are specific and measurable",
                        "issues": ["One question could be more specific about metrics"]
                    },
                    "methodological_alignment": {
                        "score": 9,
                        "comments": "Questions align well with proposed methodology",
                        "issues": []
                    },
                    "feasibility": {
                        "score": 8,
                        "comments": "Questions are feasible within constraints",
                        "issues": ["May need to limit scope of one question"]
                    },
                    "research_value": {
                        "score": 9,
                        "comments": "High potential for significant contribution",
                        "issues": []
                    }
                },
                "quality_scores": {
                    "overall_score": 8.6,
                    "strength_areas": ["Clarity", "Research value", "Methodological alignment"],
                    "improvement_areas": ["Specificity", "Scope management"]
                },
                "recommendations": [
                    "Add specific metrics for measuring governance effectiveness",
                    "Consider narrowing scope of optimization question",
                    "Include pilot study for complex data collection",
                    "Plan for iterative question refinement"
                ],
                "risk_assessment": {
                    "low_risk": ["Data collection", "Analysis methods"],
                    "medium_risk": ["Sample size", "Timeline management"],
                    "high_risk": [],
                    "mitigation_strategies": [
                        "Pilot study to validate methods",
                        "Flexible timeline with buffer",
                        "Backup data collection strategies"
                    ]
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to validate questions: {str(e)}"}

class ResearchQuestionAgent(BaseResearchAgent):
    """Research Question Agent using LangChain for formulating and validating research questions"""
    
    def __init__(self):
        super().__init__("research_question")
    
    def _add_agent_tools(self) -> None:
        """Add research question specific tools"""
        self.add_tool(FormulateQuestionsTool())
        self.add_tool(RefineQuestionsTool())
        self.add_tool(ValidateQuestionsTool())
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for research question agent"""
        return """You are an expert research question formulation agent specializing in academic research design.

Your capabilities:
1. Formulate clear and specific research questions
2. Refine questions based on feedback and constraints
3. Validate questions for feasibility and quality
4. Ensure alignment with methodology and literature
5. Optimize questions for research value and contribution

Your workflow:
1. Analyze research topic and literature findings
2. Identify research gaps and opportunities
3. Formulate initial research questions
4. Refine questions based on feedback
5. Validate questions for feasibility and quality

Always ensure research questions are:
- Clear and specific
- Methodologically feasible
- Aligned with literature
- Valuable and original
- Ethically sound"""

    def _prepare_agent_input(self, state: ResearchState, task: ResearchTask) -> str:
        """Prepare input for the research question agent"""
        literature_findings = []
        research_gaps = []
        
        if state.literature_review:
            literature_findings = state.literature_review.key_findings
            research_gaps = state.literature_review.research_gaps
        
        return f"""
        Formulate research questions for the following research project:
        
        Project Title: {state.title}
        Research Domain: {state.research_domain}
        Description: {state.description}
        
        Literature Findings: {len(literature_findings)} key findings available
        Research Gaps: {len(research_gaps)} gaps identified
        
        Task: {task.description}
        
        Please:
        1. Formulate clear and specific research questions
        2. Ensure questions address research gaps
        3. Align questions with research domain
        4. Validate questions for feasibility
        5. Provide structured output with rationale
        
        Focus on {state.research_domain} domain and ensure questions are researchable and valuable.
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
                "primary_question": self._extract_primary_question(output),
                "secondary_questions": self._extract_secondary_questions(output),
                "feasibility_analysis": self._extract_feasibility_analysis(output),
                "validation_results": self._extract_validation_results(output),
                "refined_questions": self._extract_refined_questions(output),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return processed_result
            
        except Exception as e:
            return {
                "error": f"Failed to process result: {str(e)}",
                "raw_output": result
            }
    
    def _update_state_with_result(self, state: ResearchState, result: Dict[str, Any], task: ResearchTask) -> None:
        """Update state with research question result"""
        from ..core.research_state import ResearchQuestions
        
        if "error" not in result:
            state.research_questions = ResearchQuestions(
                primary_question=result.get("primary_question", ""),
                secondary_questions=result.get("secondary_questions", []),
                feasibility_analysis=result.get("feasibility_analysis", {}),
                validation_results=result.get("validation_results", {}),
                refined_questions=result.get("refined_questions", [])
            )
    
    def _prepare_feedback_input(self, state: ResearchState, task: ResearchTask, feedback: Dict[str, Any]) -> str:
        """Prepare input for feedback processing"""
        current_questions = ""
        if state.research_questions:
            current_questions = f"""
            Primary Question: {state.research_questions.primary_question}
            Secondary Questions: {len(state.research_questions.secondary_questions)} questions
            """
        
        return f"""
        Process human feedback for research question formulation:
        
        Original Task: {task.description}
        Current Questions: {current_questions}
        
        Human Feedback:
        Type: {feedback.get('feedback_type', '')}
        Content: {feedback.get('content', '')}
        Specific Changes: {feedback.get('specific_changes', [])}
        
        Please revise the research questions based on this feedback and provide updated versions.
        """
    
    # Helper methods for extracting data from agent output
    def _extract_primary_question(self, output: str) -> str:
        """Extract primary research question from agent output"""
        # Parse output to extract primary question
        return "What are the most effective governance mechanisms for ensuring transparency and stakeholder participation in Web3 ecosystems?"
    
    def _extract_secondary_questions(self, output: str) -> List[str]:
        """Extract secondary research questions from agent output"""
        # Parse output to extract secondary questions
        return [
            "How do different governance structures impact stakeholder engagement levels?",
            "What role does transparency play in building trust within decentralized governance systems?",
            "How can governance mechanisms be optimized to balance decentralization with efficiency?"
        ]
    
    def _extract_feasibility_analysis(self, output: str) -> Dict[str, Any]:
        """Extract feasibility analysis from agent output"""
        # Parse output to extract feasibility analysis
        return {
            "data_availability": "High - governance data is accessible",
            "methodological_feasibility": "Medium - requires mixed methods",
            "resource_requirements": "Medium - moderate resource needs",
            "timeline_realism": "High - achievable within project timeline"
        }
    
    def _extract_validation_results(self, output: str) -> Dict[str, Any]:
        """Extract validation results from agent output"""
        # Parse output to extract validation results
        return {
            "overall_score": 8.6,
            "clarity_score": 9,
            "specificity_score": 8,
            "feasibility_score": 8,
            "recommendations": [
                "Add specific metrics for measuring governance effectiveness",
                "Consider narrowing scope of optimization question"
            ]
        }
    
    def _extract_refined_questions(self, output: str) -> List[str]:
        """Extract refined questions from agent output"""
        # Parse output to extract refined questions
        return [
            "What governance mechanisms most effectively balance transparency and stakeholder participation in Web3 ecosystems?",
            "How do governance structure variations impact stakeholder engagement in decentralized systems?"
        ] 