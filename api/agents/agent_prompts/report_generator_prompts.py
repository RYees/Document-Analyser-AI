"""
Report Generator Agent Prompts

Prompt templates for the Report Generator Agent.
"""

from typing import List, Dict, Any
from api.agents.agent_prompts.base_prompts import BaseAgentPrompts

class ReportGeneratorPrompts:
    """
    Prompt templates for the Report Generator Agent.
    """
    
    @staticmethod
    def build_report_prompt(sections: Dict[str, Any], supervisor_feedback=None, previous_attempts=None, attempt_number=1, max_attempts=3) -> str:
        """
        Build the report generation prompt with optional supervisor feedback integration.
        """
        # Prepare sections data
        sections_data = ReportGeneratorPrompts._prepare_sections_data(sections)
        research_domain = sections.get("research_domain", "General")
        
        # Build supervisor feedback section if provided
        supervisor_section = BaseAgentPrompts.get_supervisor_feedback_section(
            supervisor_feedback, previous_attempts, attempt_number, max_attempts
        )
        
        prompt = f"""As the Report Generation Agent, your task is to compile a polished, academic-style **Thematic Literature Review** report. Use the outputs from all other agents to create a well-structured research paper that includes Harvard-style in-text citations and a properly formatted reference list.

Your output must integrate a standalone **Literature Review section**, situated after the Introduction and before the Methodology. This section should summarize and critique key academic sources, providing the theoretical and conceptual context for the thematic analysis.

Maintain an academic yet conversational tone. {BaseAgentPrompts.get_common_transitional_phrases()}
{BaseAgentPrompts.get_academic_tone_guidelines()}

---

**Required Report Structure:**

1. **Abstract** *(optional but encouraged)*  
2. **Introduction**: Set the stage for why transparency in blockchain, Web3, and AI is significant.  
3. **Literature Review**: Summarize and synthesize academic perspectives, highlight debates and gaps.  
4. **Methodology**: Describe the thematic analysis process used to derive themes. Avoid referring to agents by name.  
5. **Findings**: Present clearly defined and titled themes with subheadings, definitions, scope, and citations.  
6. **Discussion**: Unpack tensions, synthesize implications, and reflect on cross-thematic relationships.  
7. **Conclusion**: Summarize main contributions and outline possible future research directions.  
8. **Reference List**: Generate a complete, properly formatted Harvard-style bibliography.

---

**Objectives:**

1. **Structured Composition**: Follow academic conventions and include the new Literature Review section.
2. **Theme Integration**: Coherently integrate refined thematic findings into the broader narrative.
3. **Literature Contextualization**: Connect themes back to the scholarly literature reviewed earlier.
4. **Methodological Transparency**: Clearly explain the thematic analysis steps without naming individual agents.
5. **Harvard Referencing**: Use consistent Harvard-style in-text citations and generate a reference list.
6. **Clarity & Coherence**: Ensure all sections flow logically and read like a single, cohesive academic paper.
7. **Data Storage**: The report will be automatically saved to a local file for future reference.

---

**Research Domain:** {research_domain}

{supervisor_section}

**Based on the following agent outputs, generate a complete academic report:**

{sections_data}

Please provide a complete, structured academic report following the required format and objectives above."""
        
        return prompt
    
    @staticmethod
    def _prepare_sections_data(sections: Dict[str, Any]) -> str:
        """
        Prepare sections data for report generation prompt.
        """
        sections_data = []
        
        # Literature Review section
        if "literature_review" in sections:
            lit_review = sections["literature_review"]
            if lit_review and "data" in lit_review:
                data = lit_review["data"]
                sections_data.append(f"""**Literature Review Data:**
Summary: {data.get('summary', 'No summary available')}
Key Findings: {len(data.get('key_findings', []))} findings
Research Gaps: {len(data.get('research_gaps', []))} gaps identified
Full Review Length: {len(data.get('full_literature_review', ''))} characters
""")
        
        # Initial Coding section
        if "initial_coding" in sections:
            coding = sections["initial_coding"]
            if coding and "data" in coding:
                data = coding["data"]
                coding_summary = data.get("coding_summary", {})
                sections_data.append(f"""**Initial Coding Data:**
Total Units Coded: {coding_summary.get('total_units_coded', 0)}
Unique Codes: {coding_summary.get('unique_codes_generated', 0)}
Average Confidence: {coding_summary.get('average_confidence', 0):.2f}
Primary Codes: {coding_summary.get('primary_codes', [])}
Sub Codes: {coding_summary.get('sub_codes', [])}
""")
        
        # Thematic Grouping section
        if "thematic_grouping" in sections:
            thematic = sections["thematic_grouping"]
            if thematic and "data" in thematic:
                data = thematic["data"]
                thematic_summary = data.get("thematic_summary", {})
                sections_data.append(f"""**Thematic Grouping Data:**
Total Themes: {thematic_summary.get('total_themes_generated', 0)}
Total Codes Analyzed: {thematic_summary.get('total_codes_analyzed', 0)}
Average Codes per Theme: {thematic_summary.get('average_codes_per_theme', 0):.1f}
Themes: {[theme.get('theme_name', 'Unknown') for theme in data.get('themes', [])]}
""")
        
        # Theme Refinement section
        if "theme_refinement" in sections:
            refinement = sections["theme_refinement"]
            if refinement and "data" in refinement:
                data = refinement["data"]
                refinement_summary = data.get("refinement_summary", {})
                sections_data.append(f"""**Theme Refinement Data:**
Total Themes Refined: {refinement_summary.get('total_themes_refined', 0)}
Total Academic Quotes: {refinement_summary.get('total_academic_quotes', 0)}
Average Quotes per Theme: {refinement_summary.get('average_quotes_per_theme', 0):.1f}
Themes with Framework: {refinement_summary.get('themes_with_framework', 0)}
""")
        
        return "\n".join(sections_data) 