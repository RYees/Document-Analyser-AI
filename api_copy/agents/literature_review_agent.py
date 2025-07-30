import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timezone
import sys
import os
# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.llm_backends import get_llm_backend

class LiteratureReviewAgent:
    """
    Generates a standalone academic-style literature review using the documents retrieved.
    Synthesizes summary, key findings, research gaps, methodologies, etc. using an LLM backend.
    """
    def __init__(self, llm_backend=None):
        # Initialize with OpenAI backend by default
        self.llm_backend = llm_backend or get_llm_backend("openai")

    def _build_prompt(self, documents: List[Dict[str, Any]], research_domain: str = "General") -> str:
        """
        Construct a prompt for the LLM to generate a literature review.
        """
        content_parts = [
            f"Research Domain: {research_domain}",
            f"Number of Papers Analyzed: {len(documents)}",
            "\n=== PAPERS AND CONTENT ===\n"
        ]
        for i, paper in enumerate(documents, 1):
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                author_names = []
                for author in authors:
                    if isinstance(author, dict):
                        author_names.append(author.get('name', str(author)))
                    else:
                        author_names.append(str(author))
                authors_str = ', '.join(author_names)
            else:
                authors_str = str(authors)
            content_parts.extend([
                f"Paper {i}:",
                f"Title: {paper.get('title', 'Unknown')}",
                f"Authors: {authors_str}",
                f"Year: {paper.get('year', 'Unknown')}",
                f"Abstract: {paper.get('abstract', 'No abstract available')}",
                f"Content Length: {len(paper.get('extracted_content', ''))} chars",
                f"Extracted Content: {paper.get('extracted_content', 'No content extracted')[:2000]}...",
                "\n" + "="*50 + "\n"
            ])
        
        prompt = f"""You are the Literature Reviewer Agent. Your task is to synthesize and evaluate the key academic publications retrieved by the Data Retrieval Agent to produce a formal **Literature Review** section.

You must compare how different scholars conceptualize transparency across blockchain, Web3, and AI; highlight key debates; identify knowledge gaps; and justify the need for a thematic analysis.

The tone should be academic but casual and spartan. Down to earth. Avoid Jargon. Generously use expressions like: "More often than not", "It can be argued that", "In effect", "Ideally", "We can infer", etc. 

---

**Objectives:**

1. Contextual Framing: Situate the topic of transparency within academic debates in the selected domains.
2. Comparative Synthesis: Compare how authors approach the issue — including areas of agreement, disagreement, and evolution.
3. Identify Gaps: Point out any theoretical, empirical, or methodological gaps that justify a deeper thematic analysis.
4. Citations: Include Harvard-style in-text citations.
5. Deliverable: Output a self-contained Literature Review section to be used in the final report.

---

**Use the following format for Harvard-style citations:**

**In-text citation examples:**
- Narrative: According to Mason (2020), transparency is central to building trust in blockchain ecosystems.
- Parenthetical: Transparency is often linked to user empowerment in decentralized systems (O'Reilly, 2019).

**Reference List format (used at the end of the paper):**
- Mason, J. (2020). *The Role of Trust in Blockchain Technology*. Journal of Digital Innovation, 12(3), pp.45–58.
- O'Reilly, T. (2019). *The Open Future: Transparency in a Decentralized Internet*. Web3 Journal, 7(1), pp.12–29.

Ensure that all in-text citations match entries that would be added to the reference list.

---

**Based on the following academic papers and their content, generate a comprehensive literature review:**

{chr(10).join(content_parts)}

Please provide a structured literature review that addresses the objectives above, using the specified tone and citation format."""
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into structured literature review format.
        """
        sections = {
            "summary": "",
            "key_findings": [],
            "research_gaps": [],
            "methodologies": [],
            "future_directions": [],
            "full_literature_review": response  # Store the complete response
        }
        
        # Try to extract structured sections from the academic literature review
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for section headers in academic literature review format
            if any(keyword in line.lower() for keyword in ['introduction', 'background', 'context']):
                current_section = 'summary'
            elif any(keyword in line.lower() for keyword in ['key findings', 'main findings', 'insights', 'synthesis']):
                current_section = 'key_findings'
            elif any(keyword in line.lower() for keyword in ['research gaps', 'gaps', 'limitations', 'opportunities']):
                current_section = 'research_gaps'
            elif any(keyword in line.lower() for keyword in ['methodologies', 'methods', 'frameworks', 'approaches']):
                current_section = 'methodologies'
            elif any(keyword in line.lower() for keyword in ['future directions', 'future research', 'recommendations', 'conclusion']):
                current_section = 'future_directions'
            elif current_section and line:
                # Add content to current section
                if current_section == 'summary':
                    sections['summary'] += line + " "
                elif current_section in ['key_findings', 'research_gaps', 'methodologies', 'future_directions']:
                    sections[current_section].append(line)
        
        # Clean up summary
        sections['summary'] = sections['summary'].strip()
        
        # If no structured sections found, use the full response as summary
        if not sections['summary'] and response:
            sections['summary'] = response[:1000] + "..." if len(response) > 1000 else response
        
        # Extract key findings from the full text if not found in sections
        if not sections['key_findings']:
            sections['key_findings'] = self._extract_key_points(response, 'findings')
        
        # Extract research gaps from the full text if not found in sections
        if not sections['research_gaps']:
            sections['research_gaps'] = self._extract_key_points(response, 'gaps')
        
        return sections
    
    def _extract_key_points(self, text: str, point_type: str) -> List[str]:
        """
        Extract key points from the full text using simple heuristics.
        """
        points = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for sentences that might contain key points
            if point_type == 'findings':
                if any(keyword in line.lower() for keyword in ['find', 'discover', 'show', 'demonstrate', 'reveal', 'indicate']):
                    points.append(line)
            elif point_type == 'gaps':
                if any(keyword in line.lower() for keyword in ['gap', 'missing', 'lack', 'need', 'future', 'limitation']):
                    points.append(line)
        
        return points[:5]  # Limit to top 5 points

    async def run(self, documents: List[Dict[str, Any]], research_domain: str = "General") -> Dict[str, Any]:
        """
        Main entry point for literature review generation.
        Args:
            documents (List[Dict]): List of academic documents (with extracted content).
            research_domain (str): The research domain/topic.
        Returns:
            Dict: Structured literature review (summary, key findings, gaps, etc.)
        """
        if not documents:
            return {"error": "No documents provided for literature review."}
        
        print(f"[DEBUG] LiteratureReviewAgent.run called with {len(documents)} documents")
        print(f"[DEBUG] Research domain: {research_domain}")
        
        prompt = self._build_prompt(documents, research_domain)
        print(f"[DEBUG] Generated prompt length: {len(prompt)} characters")
        
        if not self.llm_backend:
            return {"error": "No LLM backend provided."}
        
        print(f"[DEBUG] Using LLM backend: {self.llm_backend.get_model_info()}")
        
        try:
            llm_response = await self.llm_backend.generate(prompt)
            print(f"[DEBUG] LLM response received, length: {len(llm_response)} characters")
            
            if not llm_response:
                return {"error": "LLM generation failed: No response received."}
            
            structured_result = self._parse_response(llm_response)
            structured_result["generated_at"] = datetime.now(timezone.utc).isoformat()
            structured_result["documents_analyzed"] = len(documents)
            structured_result["research_domain"] = research_domain
            
            print(f"[DEBUG] Structured result created with sections: {list(structured_result.keys())}")
            return structured_result
            
        except Exception as e:
            print(f"[ERROR] Literature review generation failed: {e}")
            return {"error": f"Literature review generation failed: {str(e)}"} 