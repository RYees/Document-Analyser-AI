"""
Literature Review Agent Prompts

Prompt templates for the Literature Review Agent.
"""

from typing import List, Dict, Any
from api.agents.agent_prompts.base_prompts import BaseAgentPrompts

class LiteratureReviewPrompts:
    """
    Prompt templates for the Literature Review Agent.
    """
    
    @staticmethod
    def build_literature_review_prompt(documents: List[Dict[str, Any]], research_domain: str = "General", 
                                     supervisor_feedback=None, previous_attempts=None, attempt_number=1, max_attempts=3) -> str:
        """
        Build the literature review prompt with optional supervisor feedback integration.
        """
        # Format document content
        content_parts = BaseAgentPrompts.format_document_content(documents, research_domain)
        
        # Build supervisor feedback section if provided
        supervisor_section = BaseAgentPrompts.get_supervisor_feedback_section(
            supervisor_feedback, previous_attempts, attempt_number, max_attempts
        )
        
        prompt = f"""You are the Literature Reviewer Agent. Your task is to synthesize and evaluate the key academic publications retrieved by the Data Retrieval Agent to produce a formal **Literature Review** section.

You must compare how different scholars conceptualize transparency across blockchain, Web3, and AI; highlight key debates; identify knowledge gaps; and justify the need for a thematic analysis.

{BaseAgentPrompts.get_academic_tone_guidelines()}

---

**Objectives:**

1. Contextual Framing: Situate the topic of transparency within academic debates in the selected domains.
2. Comparative Synthesis: Compare how authors approach the issue — including areas of agreement, disagreement, and evolution.
3. Identify Gaps: Point out any theoretical, empirical, or methodological gaps that justify a deeper thematic analysis.
4. Citations: Include Harvard-style in-text citations.
5. Deliverable: Output a self-contained Literature Review section to be used in the final report.

---

{BaseAgentPrompts.get_harvard_citation_guidelines()}

{supervisor_section}

**Based on the following academic papers and their content, generate a comprehensive literature review:**

{content_parts}

Please provide a structured literature review that addresses the objectives above, using the specified tone and citation format."""
        
        return prompt 