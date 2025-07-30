import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
import sys
import os
# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.llm_backends import get_llm_backend

@dataclass
class QualityAssessment:
    """Represents a quality assessment result"""
    status: str  # APPROVE, REVISE, HALT
    feedback: List[str]
    action: str
    confidence: float
    issues_found: List[str]
    quality_score: float

class SupervisorAgent:
    """
    Quality Control Supervisor Agent that reviews each agent's output and decides whether to proceed.
    """
    def __init__(self, llm_backend=None):
        # Initialize with OpenAI backend by default
        self.llm_backend = llm_backend or get_llm_backend("openai")

    def _get_quality_criteria(self, agent_type: str) -> Dict[str, Any]:
        """
        Get quality criteria for a specific agent type.
        """
        criteria = {
            "literature_review": {
                "summary_length_min": 200,
                "key_findings_min": 3,
                "research_gaps_min": 2,
                "required_elements": ["summary", "key_findings", "research_gaps", "full_literature_review"],
                "tone_check": "academic but accessible",
                "citation_format": "Harvard-style"
            },
            "initial_coding": {
                "unique_codes_min": 5,
                "average_confidence_min": 0.7,
                "required_elements": ["coding_summary", "coded_units"],
                "code_relevance": "aligned with research domain",
                "code_definitions": "clear and specific"
            },
            "thematic_grouping": {
                "theme_count_min": 2,
                "theme_count_max": 5,
                "required_elements": ["thematic_summary", "themes"],
                "code_distribution": "relatively even across themes",
                "theme_distinctness": "no redundant themes",
                "cross_cutting_ideas": "identified"
            },
            "theme_refinement": {
                "academic_quotes_min_per_theme": 2,
                "required_elements": ["refinement_summary", "refined_themes"],
                "definitions": "precise and clear",
                "scope_boundaries": "well-defined",
                "theoretical_frameworks": "identified"
            },
            "report_generation": {
                "word_count_min": 800,
                "required_sections": ["Abstract", "Introduction", "Literature Review", "Methodology", "Findings", "Discussion", "Conclusion"],
                "citation_format": "Harvard-style throughout",
                "logical_flow": "coherent narrative"
            }
        }
        
        return criteria.get(agent_type, {})

    def _build_supervisor_prompt(self, agent_output: Dict[str, Any], agent_type: str, research_domain: str) -> str:
        """
        Build the supervisor prompt for quality assessment.
        """
        criteria = self._get_quality_criteria(agent_type)
        
        # Format agent output for review
        output_summary = self._format_output_for_review(agent_output, agent_type)
        
        prompt = f"""You are a Quality Control Supervisor Agent for an automated academic research pipeline.

**Your Role:** Review each agent's output and decide whether it meets quality standards to proceed to the next step.

**Quality Assessment Framework:**
For each agent output, evaluate:
1. COMPLETENESS: Does it contain all required elements?
2. RELEVANCE: Is it aligned with the research domain?
3. QUALITY: Does it meet academic standards?
4. CONSISTENCY: Are there internal contradictions?

**Decision Options:**
- APPROVE: Output meets all quality standards, proceed to next agent
- REVISE: Output has issues but can be fixed, provide specific feedback
- HALT: Output has critical issues, stop pipeline

**Current Agent Output to Review:**
{output_summary}

**Agent Type:** {agent_type}
**Research Domain:** {research_domain}
**Expected Elements:** {criteria.get('required_elements', [])}

**Quality Criteria for {agent_type}:**
{self._format_criteria_for_prompt(criteria)}

**Your Response Format:**
Status: [APPROVE/REVISE/HALT]
Feedback: [List specific issues found, if any]
Action: [What should be done next]
Confidence: [0.0-1.0 score for your assessment]
Quality Score: [0.0-1.0 overall quality score]

**Your Assessment:**
"""
        return prompt

    def _format_output_for_review(self, agent_output: Dict[str, Any], agent_type: str) -> str:
        """
        Format agent output for supervisor review.
        """
        if "error" in agent_output:
            return f"ERROR: {agent_output['error']}"
        
        # Extract key metrics based on agent type
        if agent_type == "literature_review":
            summary = agent_output.get("summary", "")
            key_findings = agent_output.get("key_findings", [])
            research_gaps = agent_output.get("research_gaps", [])
            full_review = agent_output.get("full_literature_review", "")
            
            return f"""
Summary Length: {len(summary)} characters
Key Findings Count: {len(key_findings)}
Research Gaps Count: {len(research_gaps)}
Full Review Length: {len(full_review)} characters
Summary Preview: {summary[:200]}...
Key Findings: {key_findings}
Research Gaps: {research_gaps}
"""
        
        elif agent_type == "initial_coding":
            coding_summary = agent_output.get("coding_summary", {})
            coded_units = agent_output.get("coded_units", [])
            
            return f"""
Total Units Coded: {coding_summary.get('total_units_coded', 0)}
Unique Codes: {coding_summary.get('unique_codes_generated', 0)}
Average Confidence: {coding_summary.get('average_confidence', 0):.2f}
Primary Codes: {coding_summary.get('primary_codes', [])}
Sub Codes: {coding_summary.get('sub_codes', [])}
Coded Units Count: {len(coded_units)}
"""
        
        elif agent_type == "thematic_grouping":
            thematic_summary = agent_output.get("thematic_summary", {})
            themes = agent_output.get("themes", [])
            
            return f"""
Total Themes: {thematic_summary.get('total_themes_generated', 0)}
Codes Analyzed: {thematic_summary.get('total_codes_analyzed', 0)}
Cross-cutting Ideas: {thematic_summary.get('cross_cutting_ideas', [])}
Theme Names: {[theme.get('theme_name', '') for theme in themes]}
"""
        
        elif agent_type == "theme_refinement":
            refinement_summary = agent_output.get("refinement_summary", {})
            refined_themes = agent_output.get("refined_themes", [])
            
            return f"""
Total Themes Refined: {refinement_summary.get('total_themes_refined', 0)}
Academic Quotes: {refinement_summary.get('total_academic_quotes', 0)}
Key Concepts: {refinement_summary.get('total_key_concepts', 0)}
Refined Theme Names: {[theme.get('refined_name', '') for theme in refined_themes]}
"""
        
        elif agent_type == "report_generation":
            report_summary = agent_output.get("report_summary", {})
            report_content = agent_output.get("report_content", "")
            
            return f"""
Word Count: {report_summary.get('word_count', 0)}
Sections Included: {report_summary.get('sections_included', {})}
Total References: {report_summary.get('total_references', 0)}
Report Length: {len(report_content)} characters
"""
        
        else:
            return f"Agent output: {str(agent_output)[:500]}..."

    def _format_criteria_for_prompt(self, criteria: Dict[str, Any]) -> str:
        """
        Format quality criteria for the prompt.
        """
        criteria_text = []
        for key, value in criteria.items():
            if isinstance(value, list):
                criteria_text.append(f"- {key}: {', '.join(value)}")
            else:
                criteria_text.append(f"- {key}: {value}")
        
        return "\n".join(criteria_text)

    def _parse_supervisor_response(self, response: str) -> QualityAssessment:
        """
        Parse the supervisor's response into structured format.
        """
        status = "HALT"  # Default to halt if parsing fails
        feedback = []
        action = "Stop pipeline due to parsing error"
        confidence = 0.0
        quality_score = 0.0
        issues_found = []
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse status
            if line.startswith('Status:'):
                status_part = line.split(':', 1)[1].strip()
                if status_part in ['APPROVE', 'REVISE', 'HALT']:
                    status = status_part
            
            # Parse feedback
            elif line.startswith('Feedback:'):
                feedback_part = line.split(':', 1)[1].strip()
                if feedback_part and feedback_part != '[List specific issues found, if any]':
                    feedback.append(feedback_part)
            
            # Parse action
            elif line.startswith('Action:'):
                action_part = line.split(':', 1)[1].strip()
                if action_part and action_part != '[What should be done next]':
                    action = action_part
            
            # Parse confidence
            elif line.startswith('Confidence:'):
                try:
                    conf_part = line.split(':', 1)[1].strip()
                    confidence = float(conf_part)
                except:
                    confidence = 0.0
            
            # Parse quality score
            elif line.startswith('Quality Score:'):
                try:
                    score_part = line.split(':', 1)[1].strip()
                    quality_score = float(score_part)
                except:
                    quality_score = 0.0
        
        # Extract issues from feedback
        issues_found = feedback.copy()
        
        return QualityAssessment(
            status=status,
            feedback=feedback,
            action=action,
            confidence=confidence,
            issues_found=issues_found,
            quality_score=quality_score
        )

    async def check_quality(self, agent_output: Dict[str, Any], agent_type: str, research_domain: str = "General") -> QualityAssessment:
        """
        Check the quality of an agent's output.
        Args:
            agent_output: The output from the agent to check
            agent_type: Type of agent (literature_review, initial_coding, etc.)
            research_domain: The research domain being studied
        Returns:
            QualityAssessment: The quality assessment result
        """
        print(f"[DEBUG] SupervisorAgent.check_quality called for {agent_type}")
        print(f"[DEBUG] Research domain: {research_domain}")
        
        try:
            # Check for errors first
            if "error" in agent_output:
                print(f"[DEBUG] Agent output contains error: {agent_output['error']}")
                return QualityAssessment(
                    status="HALT",
                    feedback=[f"Agent failed with error: {agent_output['error']}"],
                    action="Stop pipeline due to agent error",
                    confidence=1.0,
                    issues_found=[f"Agent error: {agent_output['error']}"],
                    quality_score=0.0
                )
            
            # Build supervisor prompt
            prompt = self._build_supervisor_prompt(agent_output, agent_type, research_domain)
            print(f"[DEBUG] Generated supervisor prompt length: {len(prompt)} characters")
            
            if not self.llm_backend:
                return QualityAssessment(
                    status="HALT",
                    feedback=["No LLM backend provided for supervisor"],
                    action="Stop pipeline due to missing LLM backend",
                    confidence=1.0,
                    issues_found=["Missing LLM backend"],
                    quality_score=0.0
                )
            
            print(f"[DEBUG] Using LLM backend: {self.llm_backend.get_model_info()}")
            
            # Get supervisor assessment
            llm_response = await self.llm_backend.generate(prompt)
            print(f"[DEBUG] Supervisor LLM response received, length: {len(llm_response)} characters")
            
            if not llm_response:
                return QualityAssessment(
                    status="HALT",
                    feedback=["Supervisor LLM generation failed"],
                    action="Stop pipeline due to supervisor failure",
                    confidence=1.0,
                    issues_found=["Supervisor LLM failure"],
                    quality_score=0.0
                )
            
            # Parse supervisor response
            assessment = self._parse_supervisor_response(llm_response)
            
            print(f"[DEBUG] Supervisor assessment: {assessment.status} (confidence: {assessment.confidence:.2f})")
            if assessment.feedback:
                print(f"[DEBUG] Feedback: {assessment.feedback}")
            
            return assessment
            
        except Exception as e:
            print(f"[ERROR] Supervisor quality check failed: {e}")
            return QualityAssessment(
                status="HALT",
                feedback=[f"Supervisor check failed: {str(e)}"],
                action="Stop pipeline due to supervisor error",
                confidence=1.0,
                issues_found=[f"Supervisor error: {str(e)}"],
                quality_score=0.0
            )

    async def run(self, pipeline_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for supervisor agent.
        Args:
            pipeline_state: Current state of the pipeline with all agent outputs
        Returns:
            Dict: Overall pipeline assessment and recommendations
        """
        print(f"[DEBUG] SupervisorAgent.run called with pipeline state")
        
        # This method can be used for overall pipeline assessment
        # For now, we'll use check_quality for individual agent checks
        
        return {
            "status": "supervisor_ready",
            "message": "Supervisor agent ready for quality checks",
            "timestamp": datetime.now(timezone.utc).isoformat()
        } 