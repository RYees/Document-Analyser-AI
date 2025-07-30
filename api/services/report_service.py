"""
Report Service - Manages report generation, storage, and retrieval operations.
"""

import asyncio
import uuid
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import sys

# Add the parent directory to the path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.agents.report_generator_agent import ReportGeneratorAgent

class ReportService:
    """
    Service layer for managing report operations including generation, storage, and retrieval.
    """
    
    def __init__(self):
        """Initialize report service."""
        self.report_agent = ReportGeneratorAgent()
        
        # Create reports directory if it doesn't exist
        self.reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Track reports
        self.reports_metadata = {}
        self._load_reports_metadata()
    
    def _load_reports_metadata(self):
        """Load existing reports metadata from file."""
        metadata_file = os.path.join(self.reports_dir, "reports_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.reports_metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load reports metadata: {e}")
                self.reports_metadata = {}
    
    def _save_reports_metadata(self):
        """Save reports metadata to file."""
        metadata_file = os.path.join(self.reports_dir, "reports_metadata.json")
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.reports_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save reports metadata: {e}")
    
    async def generate_report(self, sections: Dict[str, Any], pipeline_id: str = None) -> Dict[str, Any]:
        """
        Generate a complete academic report from pipeline sections.
        
        Args:
            sections: Dictionary containing all pipeline sections
            pipeline_id: Optional pipeline ID for tracking
            
        Returns:
            Dict containing report generation results
        """
        try:
            # Generate report ID
            report_id = str(uuid.uuid4())
            
            # Add pipeline ID to sections if provided
            if pipeline_id:
                sections["pipeline_id"] = pipeline_id
            
            # Generate report using agent
            result = await self.report_agent.run(sections)
            
            if not result.get("success", True) or "error" in result:
                return {
                    "success": False,
                    "error": result.get("error", "Report generation failed"),
                    "report_id": report_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Extract report data
            report_content = result.get("report_content", "")
            report_summary = result.get("report_summary", {})
            file_path = result.get("file_path", "")
            research_domain = sections.get("research_domain", "General")
            
            # Create metadata
            metadata = {
                "report_id": report_id,
                "pipeline_id": pipeline_id,
                "research_domain": research_domain,
                "file_path": file_path,
                "word_count": report_summary.get("word_count", 0),
                "total_references": report_summary.get("total_references", 0),
                "sections_included": report_summary.get("sections_included", {}),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed"
            }
            
            # Store metadata
            self.reports_metadata[report_id] = metadata
            self._save_reports_metadata()
            
            return {
                "success": True,
                "data": {
                    "report_id": report_id,
                    "pipeline_id": pipeline_id,
                    "research_domain": research_domain,
                    "file_path": file_path,
                    "word_count": report_summary.get("word_count", 0),
                    "total_references": report_summary.get("total_references", 0),
                    "sections_included": report_summary.get("sections_included", {}),
                    "report_preview": report_content[:500] + "..." if len(report_content) > 500 else report_content
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "report_id": report_id if 'report_id' in locals() else None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_reports(self, limit: int = 20, research_domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of generated reports.
        
        Args:
            limit: Maximum number of reports to return
            research_domain: Filter by research domain (optional)
            
        Returns:
            Dict containing list of reports
        """
        try:
            # Filter reports
            filtered_reports = self.reports_metadata
            if research_domain:
                filtered_reports = {
                    k: v for k, v in self.reports_metadata.items() 
                    if v.get("research_domain") == research_domain
                }
            
            # Sort by generation date (newest first)
            sorted_reports = sorted(
                filtered_reports.items(),
                key=lambda x: x[1].get("generated_at", ""),
                reverse=True
            )
            
            # Limit results
            limited_reports = sorted_reports[:limit]
            
            # Format response
            reports_list = []
            for report_id, metadata in limited_reports:
                reports_list.append({
                    "report_id": report_id,
                    "pipeline_id": metadata.get("pipeline_id"),
                    "research_domain": metadata.get("research_domain"),
                    "word_count": metadata.get("word_count", 0),
                    "total_references": metadata.get("total_references", 0),
                    "generated_at": metadata.get("generated_at"),
                    "status": metadata.get("status", "unknown")
                })
            
            return {
                "success": True,
                "data": {
                    "reports": reports_list,
                    "total_reports": len(filtered_reports),
                    "filtered_count": len(reports_list)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def list_reports(self, limit: int = 20, research_domain: Optional[str] = None, pipeline_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List reports (alias for get_reports for route compatibility).
        
        Args:
            limit: Maximum number of reports to return
            research_domain: Filter by research domain (optional)
            pipeline_id: Filter by pipeline ID (optional)
            
        Returns:
            Dict containing list of reports
        """
        try:
            # Filter reports
            filtered_reports = self.reports_metadata
            
            if research_domain:
                filtered_reports = {
                    k: v for k, v in filtered_reports.items() 
                    if v.get("research_domain") == research_domain
                }
            
            if pipeline_id:
                filtered_reports = {
                    k: v for k, v in filtered_reports.items() 
                    if v.get("pipeline_id") == pipeline_id
                }
            
            # Sort by generation date (newest first)
            sorted_reports = sorted(
                filtered_reports.items(),
                key=lambda x: x[1].get("generated_at", ""),
                reverse=True
            )
            
            # Limit results
            limited_reports = sorted_reports[:limit]
            
            # Format response
            reports_list = []
            for report_id, metadata in limited_reports:
                reports_list.append({
                    "report_id": report_id,
                    "pipeline_id": metadata.get("pipeline_id"),
                    "research_domain": metadata.get("research_domain"),
                    "word_count": metadata.get("word_count", 0),
                    "total_references": metadata.get("total_references", 0),
                    "generated_at": metadata.get("generated_at"),
                    "status": metadata.get("status", "unknown")
                })
            
            return {
                "success": True,
                "data": {
                    "reports": reports_list,
                    "total_reports": len(filtered_reports),
                    "filtered_count": len(reports_list)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_report(self, report_id: str) -> Dict[str, Any]:
        """
        Get specific report details.
        
        Args:
            report_id: ID of the report to retrieve
            
        Returns:
            Dict containing report details
        """
        try:
            if report_id not in self.reports_metadata:
                return {
                    "success": False,
                    "error": f"Report {report_id} not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            metadata = self.reports_metadata[report_id]
            file_path = metadata.get("file_path", "")
            
            # Check if file exists
            file_exists = os.path.exists(file_path) if file_path else False
            
            return {
                "success": True,
                "data": {
                    "report_id": report_id,
                    "pipeline_id": metadata.get("pipeline_id"),
                    "research_domain": metadata.get("research_domain"),
                    "file_path": file_path,
                    "file_exists": file_exists,
                    "word_count": metadata.get("word_count", 0),
                    "total_references": metadata.get("total_references", 0),
                    "sections_included": metadata.get("sections_included", {}),
                    "generated_at": metadata.get("generated_at"),
                    "status": metadata.get("status", "unknown")
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def download_report(self, report_id: str, format: str = "markdown") -> Dict[str, Any]:
        """
        Download report content in specified format.
        
        Args:
            report_id: ID of the report to download
            format: Format to download (markdown, json, text)
            
        Returns:
            Dict containing report content
        """
        try:
            if report_id not in self.reports_metadata:
                return {
                    "success": False,
                    "error": f"Report {report_id} not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            metadata = self.reports_metadata[report_id]
            file_path = metadata.get("file_path", "")
            
            if not file_path or not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Report file not found: {file_path}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Format response based on requested format
            if format.lower() == "json":
                response_data = {
                    "report_id": report_id,
                    "metadata": metadata,
                    "content": content
                }
            elif format.lower() == "text":
                # Strip markdown formatting for plain text
                import re
                content = re.sub(r'#+\s*', '', content)  # Remove headers
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove bold
                content = re.sub(r'\*(.*?)\*', r'\1', content)  # Remove italic
                response_data = {
                    "report_id": report_id,
                    "content": content
                }
            else:  # markdown
                response_data = {
                    "report_id": report_id,
                    "content": content
                }
            
            return {
                "success": True,
                "data": response_data,
                "format": format,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def delete_report(self, report_id: str) -> Dict[str, Any]:
        """
        Delete a report and its associated file.
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            Dict containing deletion results
        """
        try:
            if report_id not in self.reports_metadata:
                return {
                    "success": False,
                    "error": f"Report {report_id} not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            metadata = self.reports_metadata[report_id]
            file_path = metadata.get("file_path", "")
            
            # Delete file if it exists
            file_deleted = False
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    file_deleted = True
                except Exception as e:
                    print(f"Warning: Could not delete file {file_path}: {e}")
            
            # Remove from metadata
            del self.reports_metadata[report_id]
            self._save_reports_metadata()
            
            return {
                "success": True,
                "data": {
                    "report_id": report_id,
                    "file_deleted": file_deleted,
                    "message": "Report deleted successfully"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_report_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about generated reports.
        
        Returns:
            Dict containing report statistics
        """
        try:
            total_reports = len(self.reports_metadata)
            
            if total_reports == 0:
                return {
                    "success": True,
                    "data": {
                        "message": "No reports available for statistics",
                        "total_reports": 0
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Calculate statistics
            total_words = sum(r.get("word_count", 0) for r in self.reports_metadata.values())
            total_references = sum(r.get("total_references", 0) for r in self.reports_metadata.values())
            avg_words = total_words / total_reports if total_reports > 0 else 0
            avg_references = total_references / total_reports if total_reports > 0 else 0
            
            # Research domain distribution
            domain_counts = {}
            for report in self.reports_metadata.values():
                domain = report.get("research_domain", "Unknown")
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Recent activity
            recent_reports = [
                r for r in self.reports_metadata.values()
                if r.get("generated_at", "") > (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            ]
            
            return {
                "success": True,
                "data": {
                    "total_reports": total_reports,
                    "total_words": total_words,
                    "total_references": total_references,
                    "average_words_per_report": avg_words,
                    "average_references_per_report": avg_references,
                    "research_domain_distribution": domain_counts,
                    "reports_last_7_days": len(recent_reports),
                    "most_common_domain": max(domain_counts.items(), key=lambda x: x[1])[0] if domain_counts else "None"
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def export_reports_metadata(self) -> Dict[str, Any]:
        """
        Export all reports metadata.
        
        Returns:
            Dict containing all reports metadata
        """
        try:
            return {
                "success": True,
                "data": {
                    "reports": self.reports_metadata,
                    "total_reports": len(self.reports_metadata),
                    "export_timestamp": datetime.now(timezone.utc).isoformat()
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            } 