import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import sys
import os
import subprocess
import tempfile
# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.llm_backends import get_llm_backend

class ReportGeneratorAgent:
    """
    Assembles all prior outputs into a fully structured academic paper, including citations and reference list.
    """
    def __init__(self, llm_backend=None):
        # Initialize with OpenAI backend by default
        self.llm_backend = llm_backend or get_llm_backend("openai")

    def _prepare_sections_data(self, sections: Dict[str, Any]) -> str:
        """
        Prepare all agent outputs for the report generation prompt.
        """
        sections_data = []
        
        # Literature Review section
        if "literature_review" in sections:
            lit_review = sections["literature_review"]
            sections_data.extend([
                "=== LITERATURE REVIEW OUTPUT ===",
                f"Summary: {lit_review.get('summary', 'No summary')}",
                f"Key Findings: {lit_review.get('key_findings', [])}",
                f"Research Gaps: {lit_review.get('research_gaps', [])}",
                f"Full Literature Review: {lit_review.get('full_literature_review', 'No content')}",
                "\n" + "="*50 + "\n"
            ])
        
        # Initial Coding results
        if "initial_coding" in sections:
            coding = sections["initial_coding"]
            coding_summary = coding.get("coding_summary", {})
            sections_data.extend([
                "=== INITIAL CODING OUTPUT ===",
                f"Total Units Coded: {coding_summary.get('total_units_coded', 0)}",
                f"Unique Codes: {coding_summary.get('unique_codes_generated', 0)}",
                f"Average Confidence: {coding_summary.get('average_confidence', 0):.2f}",
                f"Primary Codes: {coding_summary.get('primary_codes', [])}",
                f"Sub Codes: {coding_summary.get('sub_codes', [])}",
                "\n" + "="*50 + "\n"
            ])
        
        # Thematic Grouping results
        if "thematic_grouping" in sections:
            thematic = sections["thematic_grouping"]
            thematic_summary = thematic.get("thematic_summary", {})
            sections_data.extend([
                "=== THEMATIC GROUPING OUTPUT ===",
                f"Total Themes: {thematic_summary.get('total_themes_generated', 0)}",
                f"Codes Analyzed: {thematic_summary.get('total_codes_analyzed', 0)}",
                f"Cross-cutting Ideas: {thematic_summary.get('cross_cutting_ideas', [])}",
                "\n" + "="*50 + "\n"
            ])
        
        # Theme Refinement results
        if "theme_refinement" in sections:
            refinement = sections["theme_refinement"]
            refinement_summary = refinement.get("refinement_summary", {})
            sections_data.extend([
                "=== THEME REFINEMENT OUTPUT ===",
                f"Total Themes Refined: {refinement_summary.get('total_themes_refined', 0)}",
                f"Academic Quotes: {refinement_summary.get('total_academic_quotes', 0)}",
                f"Key Concepts: {refinement_summary.get('total_key_concepts', 0)}",
                "\n" + "="*50 + "\n"
            ])
        
        # Research domain and context
        research_domain = sections.get("research_domain", "General")
        sections_data.extend([
            "=== RESEARCH CONTEXT ===",
            f"Research Domain: {research_domain}",
            f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}",
            "\n" + "="*50 + "\n"
        ])
        
        return "\n".join(sections_data)

    def _build_report_prompt(self, sections: Dict[str, Any], supervisor_feedback=None, previous_attempts=None, attempt_number=1, max_attempts=3) -> str:
        """
        Construct a prompt for the LLM to generate the complete academic report.
        """
        from agents.agent_prompts.report_generator_prompts import ReportGeneratorPrompts
        
        return ReportGeneratorPrompts.build_report_prompt(
            sections=sections,
            supervisor_feedback=supervisor_feedback,
            previous_attempts=previous_attempts,
            attempt_number=attempt_number,
            max_attempts=max_attempts
        )

    def _extract_references_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract references from the text to build a reference list.
        """
        references = []
        import re
        
        # Look for Harvard-style citations in the text
        citation_patterns = [
            r'\(([^)]+)\)',  # (Author, Year)
            r'([A-Z][a-z]+ [A-Z][a-z]+),?\s+(\d{4})',  # Author, Year
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    author = match[0]
                    year = match[1]
                else:
                    # Handle single match case
                    parts = match.split(',')
                    if len(parts) >= 2:
                        author = parts[0].strip()
                        year = parts[1].strip()
                    else:
                        continue
                
                # Create a basic reference entry
                reference = {
                    "author": author,
                    "year": year,
                    "title": f"Work by {author} ({year})",
                    "source": "Academic source",
                    "full_citation": f"{author} ({year})"
                }
                
                # Avoid duplicates
                if not any(ref["full_citation"] == reference["full_citation"] for ref in references):
                    references.append(reference)
        
        return references

    def _save_report_locally(self, report_content: str, research_domain: str = "General") -> str:
        """
        Save the generated report to local files (both markdown and PDF).
        Returns the PDF file path as the primary file.
        """
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_domain = research_domain.replace(" ", "_").replace("/", "_")
        base_filename = f"thematic_literature_review_{safe_domain}_{timestamp}"
        
        # Save markdown file
        md_filepath = os.path.join(reports_dir, f"{base_filename}.md")
        pdf_filepath = os.path.join(reports_dir, f"{base_filename}.pdf")
        
        try:
            # Save markdown file
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"[DEBUG] Markdown report saved to: {md_filepath}")
            
            # Convert to PDF using pandoc
            try:
                self._convert_markdown_to_pdf(md_filepath, pdf_filepath)
                print(f"[DEBUG] PDF report saved to: {pdf_filepath}")
                return pdf_filepath  # Return PDF path as primary
            except Exception as pdf_error:
                print(f"[WARNING] PDF conversion failed: {pdf_error}")
                print(f"[DEBUG] Falling back to markdown file: {md_filepath}")
                return md_filepath
            
        except Exception as e:
            print(f"[ERROR] Failed to save report: {e}")
            return ""
    
    def _convert_markdown_to_pdf(self, md_filepath: str, pdf_filepath: str):
        """
        Convert markdown file to PDF using pandoc.
        """
        try:
            # Check if pandoc is available
            result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Pandoc is not installed or not available in PATH")
            
            # Try tectonic first
            print(f"[PDF] Trying Pandoc with tectonic...")
            cmd = [
                'pandoc',
                md_filepath,
                '-o', pdf_filepath,
                '--pdf-engine=tectonic',
                '--standalone',
                '--toc',
                '--number-sections'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[PDF] PDF conversion with tectonic successful: {pdf_filepath}")
                return
            else:
                print(f"[PDF] Tectonic failed: {result.stderr}")
            
            # Try weasyprint
            print(f"[PDF] Trying Pandoc with weasyprint...")
            cmd = [
                'pandoc',
                md_filepath,
                '-o', pdf_filepath,
                '--pdf-engine=weasyprint',
                '--standalone',
                '--toc'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[PDF] PDF conversion with weasyprint successful: {pdf_filepath}")
                return
            else:
                print(f"[PDF] Weasyprint failed: {result.stderr}")
            
            # Try basic
            print(f"[PDF] Trying Pandoc with default PDF engine...")
            cmd = [
                'pandoc',
                md_filepath,
                '-o', pdf_filepath,
                '--standalone'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[PDF] PDF conversion with default engine successful: {pdf_filepath}")
                return
            else:
                print(f"[PDF] Default PDF engine failed: {result.stderr}")
                raise Exception(f"PDF conversion failed: {result.stderr}")
        except Exception as e:
            print(f"[ERROR] PDF conversion error: {e}")
            raise e

    def _create_report_summary(self, report_content: str, references: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create a summary of the generated report.
        """
        # Count sections
        sections = ["Abstract", "Introduction", "Literature Review", "Methodology", "Findings", "Discussion", "Conclusion"]
        section_counts = {}
        
        for section in sections:
            if section.lower() in report_content.lower():
                section_counts[section] = True
            else:
                section_counts[section] = False
        
        # Count words
        word_count = len(report_content.split())
        
        # Count citations
        citation_count = len(references)
        
        return {
            "word_count": word_count,
            "sections_included": section_counts,
            "total_references": citation_count,
            "report_length": len(report_content),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def run(self, sections: Dict[str, Any], supervisor_feedback=None, previous_attempts=None, attempt_number=1, max_attempts=3) -> Dict[str, Any]:
        """
        Main entry point for report generation.
        Args:
            sections (Dict): Dictionary of all report sections and outputs from previous agents.
        Returns:
            Dict: Complete academic report with metadata and file path.
        """
        if not sections:
            return {"error": "No sections provided for report generation."}
        
        print(f"[DEBUG] ReportGeneratorAgent.run called with {len(sections)} sections")
        
        try:
            # Step 1: Build report generation prompt
            print(f"[DEBUG] Step 1: Building report generation prompt...")
            prompt = self._build_report_prompt(sections, supervisor_feedback, previous_attempts, attempt_number, max_attempts)
            print(f"[DEBUG] Generated prompt length: {len(prompt)} characters")
            
            if not self.llm_backend:
                return {"error": "No LLM backend provided."}
            
            print(f"[DEBUG] Using LLM backend: {self.llm_backend.get_model_info()}")
            
            # Step 2: Generate complete academic report using LLM
            print(f"[DEBUG] Step 2: Generating complete academic report...")
            print("   ⚠️  This will make an LLM API call for full report generation!")
            
            llm_response = await self.llm_backend.generate(prompt)
            print(f"[DEBUG] LLM response received, length: {len(llm_response)} characters")
            
            if not llm_response:
                return {"error": "LLM generation failed: No response received."}
            
            # Step 3: Extract references from the report
            print(f"[DEBUG] Step 3: Extracting references...")
            references = self._extract_references_from_text(llm_response)
            print(f"[DEBUG] Extracted {len(references)} references")
            
            # Step 4: Save report locally
            print(f"[DEBUG] Step 4: Saving report locally...")
            research_domain = sections.get("research_domain", "General")
            filepath = self._save_report_locally(llm_response, research_domain)
            
            # Step 5: Create report summary
            print(f"[DEBUG] Step 5: Creating report summary...")
            report_summary = self._create_report_summary(llm_response, references)
            
            # Step 6: Prepare final result
            final_result = {
                "report_content": llm_response,
                "report_summary": report_summary,
                "references": references,
                "file_path": filepath,
                "research_domain": research_domain,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            print(f"[DEBUG] Report generation completed successfully!")
            print(f"[DEBUG] Report saved to: {filepath}")
            print(f"[DEBUG] Report contains {report_summary['word_count']} words and {len(references)} references")
            
            return final_result
            
        except Exception as e:
            print(f"[ERROR] Report generation failed: {e}")
            return {"error": f"Report generation failed: {str(e)}"} 