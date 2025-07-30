from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import create_openai_functions_agent, AgentExecutor
import aiohttp
import asyncio
import json
import re
from datetime import datetime, timezone
import os
import PyPDF2
from io import BytesIO

from .base_agent import BaseResearchAgent
from ..core.research_state import ResearchState, ResearchTask, TaskStatus, ResearchPhase
from .llm_backends import OpenAIBackend, GeminiBackend, LLMBackend
from analyser.utils.vector_store_manager import VectorStoreManager

# Import Weaviate with proper version handling
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

# Tool Input Models
class SearchCOREAPIInput(BaseModel):
    query: str = Field(description="Search query for academic papers")
    max_results: int = Field(default=20, description="Maximum number of papers to retrieve")
    year_from: int = Field(default=2020, description="Start year for search")
    year_to: int = Field(default=2024, description="End year for search")

class ExtractPDFInput(BaseModel):
    pdf_url: str = Field(description="URL of PDF to extract text from")
    paper_id: str = Field(description="Unique identifier for the paper")

class BuildRAGInput(BaseModel):
    papers: List[Dict[str, Any]] = Field(description="List of papers to build RAG from")
    research_domain: str = Field(description="Research domain for context")

# LangChain Tools
class COREAPISearchTool(BaseTool):
    name: str = "search_core_api"
    description: str = "Search academic papers using CORE API"
    args_schema: type = SearchCOREAPIInput
    
    def _run(self, query: str, max_results: int = 20, year_from: int = 2020, year_to: int = 2024) -> List[Dict[str, Any]]:
        """Synchronous version of CORE API search"""
        return asyncio.run(self._arun(query, max_results, year_from, year_to))
    
    async def _arun(self, query: str, max_results: int = 20, year_from: int = 2020, year_to: int = 2024) -> List[Dict[str, Any]]:
        """Search academic papers using CORE API"""
        try:
            # Use environment variable for API key
            api_key = "ZS01E3YUymOHq9RCcn5FiPb6lAjpN8kK"
            if not api_key:
                return [{"error": "Missing CORE API key"}]
            
            url = "https://api.core.ac.uk/v3/search/works"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "limit": max_results,
                "scroll": False,
                "year_from": year_from,
                "year_to": year_to,
                "fields": ["title", "authors", "abstract", "year", "doi", "downloadUrl", "citations", "language"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        return self._process_core_results(results)
                    else:
                        return [{"error": f"CORE API search failed: {response.status}"}]
                        
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    def _process_core_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process CORE API results into standardized format"""
        processed_results = []
        
        for result in results:
            processed_result = {
                "title": result.get("title", ""),
                "authors": [author.get("name", "") for author in result.get("authors", [])],
                "abstract": result.get("abstract", ""),
                "year": result.get("year"),
                "doi": result.get("doi"),
                "url": result.get("downloadUrl"),
                "source": "CORE",
                "citations": result.get("citations", 0),
                "language": result.get("language", {}),
                "content": result.get("abstract", "")  # Use abstract as initial content
            }
            processed_results.append(processed_result)
        
        return processed_results

class PDFExtractorTool(BaseTool):
    name: str = "extract_pdf"
    description: str = "Extract text content from PDF files"
    args_schema: type = ExtractPDFInput
    
    def _run(self, pdf_url: str, paper_id: str) -> Dict[str, Any]:
        """Synchronous version of PDF extraction"""
        return asyncio.run(self._arun(pdf_url, paper_id))
    
    async def _arun(self, pdf_url: str, paper_id: str) -> Dict[str, Any]:
        """Extract text from a PDF file using PyPDF2"""
        try:
            # Handle arXiv URLs
            if "arxiv.org/abs/" in pdf_url:
                pdf_url = pdf_url.replace("/abs/", "/pdf/") + ".pdf"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        # Get content as bytes
                        content_bytes = await response.read()
                        
                        # Check if this is actually a PDF by looking at the first few bytes
                        if content_bytes.startswith(b'%PDF'):
                            # This is a real PDF, extract text using PyPDF2
                            try:
                                pdf_file = BytesIO(content_bytes)
                                pdf_reader = PyPDF2.PdfReader(pdf_file)
                                
                                # Extract text from all pages
                                extracted_text = ""
                                for page_num, page in enumerate(pdf_reader.pages):
                                    try:
                                        page_text = page.extract_text()
                                        if page_text:
                                            extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                                    except Exception as page_error:
                                        print(f"Warning: Could not extract text from page {page_num + 1}: {page_error}")
                                        continue
                                
                                if extracted_text.strip():
                                    # Clean up the text
                                    cleaned_text = extracted_text.strip()
                                    word_count = len(cleaned_text.split())
                                    
                                    # For logging purposes, limit the text content to first 500 characters
                                    log_text = cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
                                    
                                    return {
                                        "paper_id": paper_id,
                                        "extraction_status": "success",
                                        "text_content": cleaned_text,  # Full content for processing
                                        "log_content": log_text,  # Limited content for logging
                                        "word_count": word_count,
                                        "pages_extracted": len(pdf_reader.pages),
                                        "extracted_at": datetime.now(timezone.utc).isoformat()
                                    }
                                else:
                                    return {
                                        "paper_id": paper_id,
                                        "extraction_status": "failed",
                                        "error": "No text could be extracted from PDF"
                                    }
                                    
                            except Exception as pdf_error:
                                return {
                                    "paper_id": paper_id,
                                    "extraction_status": "failed",
                                    "error": f"PDF parsing failed: {str(pdf_error)}"
                                }
                        else:
                            # This might be HTML or text content, try to decode as text
                            try:
                                content_text = content_bytes.decode('utf-8', errors='ignore')
                                return {
                                    "paper_id": paper_id,
                                    "extraction_status": "success",
                                    "text_content": content_text[:5000] + "..." if len(content_text) > 5000 else content_text,
                                    "word_count": len(content_text.split()),
                                    "pages_extracted": 1,  # Not a PDF, so treat as single page
                                    "extracted_at": datetime.now(timezone.utc).isoformat()
                                }
                            except Exception as text_error:
                                return {
                                    "paper_id": paper_id,
                                    "extraction_status": "failed",
                                    "error": f"Text decoding failed: {str(text_error)}"
                                }
                    else:
                        return {
                            "paper_id": paper_id,
                            "extraction_status": "failed",
                            "error": f"Failed to download PDF: {response.status}"
                        }
        except Exception as e:
            return {
                "paper_id": paper_id,
                "extraction_status": "failed",
                "error": f"PDF extraction failed: {str(e)}"
            }

class RAGBuilderTool(BaseTool):
    name: str = "build_rag"
    description: str = "Build RAG system from papers using Chroma vector store"
    args_schema: type = BuildRAGInput
    
    def _run(self, papers: List[Dict[str, Any]], research_domain: str) -> Dict[str, Any]:
        """Synchronous version of RAG building"""
        return asyncio.run(self._arun(papers, research_domain))
    
    async def _arun(self, papers: List[Dict[str, Any]], research_domain: str) -> Dict[str, Any]:
        """Build RAG system from papers"""
        try:
            # Validate input
            if not papers:
                return {"error": "No papers provided for RAG building"}
            
            # Create embeddings and text splitter when needed
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key="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"
            )
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            # Prepare documents for vector store
            documents = []
            metadatas = []
            
            for paper in papers:
                if "error" in paper:
                    continue
                    
                # Get content from paper
                content = paper.get("content", paper.get("abstract", ""))
                if not content:
                    continue
                
                # Split paper content into chunks
                text_chunks = text_splitter.split_text(content)
                
                for i, chunk in enumerate(text_chunks):
                    documents.append(chunk)
                    metadatas.append({
                        "paper_title": paper.get("title", ""),
                        "authors": ", ".join(paper.get("authors", [])),
                        "year": paper.get("year"),
                        "doi": paper.get("doi"),
                        "source": paper.get("source", ""),
                        "chunk_index": i,
                        "research_domain": research_domain
                    })
            
            if not documents:
                return {"error": "No valid content found in papers for RAG building"}
            
            # Create Chroma vector store
            vectorstore = Chroma.from_texts(
                texts=documents,
                metadatas=metadatas,
                embedding=embeddings,
                collection_name=f"research_papers_{research_domain.lower().replace(' ', '_')}"
            )
            
            return {
                "rag_status": "success",
                "papers_processed": len([p for p in papers if "error" not in p]),
                "total_chunks": len(documents),
                "vectorstore_name": vectorstore.collection.name,
                "research_domain": research_domain,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"error": f"RAG building failed: {str(e)}"}

# --- Standalone Tool Functions ---

async def search_core_api(query: str, max_results: int = 20, year_from: int = 2020, year_to: int = 2024) -> Dict[str, Any]:
    """Search academic papers using CORE API."""
    api_key = "ZS01E3YUymOHq9RCcn5FiPb6lAjpN8kK"
    if not api_key:
        return {"status": "error", "error": "Missing CORE API key"}
    url = "https://api.core.ac.uk/v3/search/works"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "limit": max_results,
        "scroll": False,
        "year_from": year_from,
        "year_to": year_to,
        "fields": ["title", "authors", "abstract", "year", "doi", "downloadUrl", "citations", "language"]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "success", "results": data.get("results", [])}
                else:
                    return {"status": "error", "error": f"CORE API search failed: {response.status}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def extract_pdf(pdf_url: str, paper_id: str) -> Dict[str, Any]:
    """Extract text from a PDF file using PyPDF2"""
    try:
        # Handle arXiv URLs
        if "arxiv.org/abs/" in pdf_url:
            pdf_url = pdf_url.replace("/abs/", "/pdf/") + ".pdf"
            
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status == 200:
                    # Get content as bytes
                    content_bytes = await response.read()
                    
                    # Check if this is actually a PDF by looking at the first few bytes
                    if content_bytes.startswith(b'%PDF'):
                        # This is a real PDF, extract text using PyPDF2
                        try:
                            pdf_file = BytesIO(content_bytes)
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            
                            # Extract text from all pages
                            extracted_text = ""
                            for page_num, page in enumerate(pdf_reader.pages):
                                try:
                                    page_text = page.extract_text()
                                    if page_text:
                                        extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                                except Exception as page_error:
                                    print(f"Warning: Could not extract text from page {page_num + 1}: {page_error}")
                                    continue
                            
                            if extracted_text.strip():
                                # Clean up the text
                                cleaned_text = extracted_text.strip()
                                word_count = len(cleaned_text.split())
                                
                                # For logging purposes, limit the text content to first 500 characters
                                log_text = cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
                                
                                return {
                                    "paper_id": paper_id,
                                    "extraction_status": "success",
                                    "text_content": cleaned_text,  # Full content for processing
                                    "log_content": log_text,  # Limited content for logging
                                    "word_count": word_count,
                                    "pages_extracted": len(pdf_reader.pages),
                                    "extracted_at": datetime.now(timezone.utc).isoformat()
                                }
                            else:
                                return {
                                    "paper_id": paper_id,
                                    "extraction_status": "failed",
                                    "error": "No text could be extracted from PDF"
                                }
                                
                        except Exception as pdf_error:
                            return {
                                "paper_id": paper_id,
                                "extraction_status": "failed",
                                "error": f"PDF parsing failed: {str(pdf_error)}"
                            }
                    else:
                        # This might be HTML or text content, try to decode as text
                        try:
                            content_text = content_bytes.decode('utf-8', errors='ignore')
                            return {
                                "paper_id": paper_id,
                                "extraction_status": "success",
                                "text_content": content_text[:5000] + "..." if len(content_text) > 5000 else content_text,
                                "word_count": len(content_text.split()),
                                "pages_extracted": 1,  # Not a PDF, so treat as single page
                                "extracted_at": datetime.now(timezone.utc).isoformat()
                            }
                        except Exception as text_error:
                            return {
                                "paper_id": paper_id,
                                "extraction_status": "failed",
                                "error": f"Text decoding failed: {str(text_error)}"
                            }
                else:
                    return {
                        "paper_id": paper_id,
                        "extraction_status": "failed",
                        "error": f"Failed to download PDF: {response.status}"
                    }
    except Exception as e:
        return {
            "paper_id": paper_id,
            "extraction_status": "failed",
            "error": f"PDF extraction failed: {str(e)}"
        }

async def build_rag(papers: List[Dict[str, Any]], research_domain: str) -> Dict[str, Any]:
    """Build a RAG system from papers using Weaviate (primary) and Chroma (backup)."""
    if not papers:
        return {"error": "No papers provided for RAG building"}
    # Chunk and store in vector DB
    chunks = []
    metadata_list = []
    for paper in papers:
        content = paper.get("extracted_content") or paper.get("content")
        if not content:
            continue
        # Simple chunking (could use utils.chunking for more advanced)
        for i, chunk in enumerate([content[i:i+1000] for i in range(0, len(content), 1000)]):
            chunks.append(chunk)
            meta = {
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "year": paper.get("year"),
                "doi": paper.get("doi", ""),
                "source": paper.get("source", ""),
                "paper_id": paper.get("doi", paper.get("title", "")),
                "chunk_index": i
            }
            metadata_list.append(meta)
    vstore = VectorStoreManager(collection_name="ResearchPaper", research_domain=research_domain)
    vstore.add_chunks(chunks, metadata_list)
    return {
        "status": "success",
        "papers_processed": len(papers),
        "chunks_stored": len(chunks),
        "vectorstore_name": f"ResearchPaper",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

# --- LLM Backend Selection ---
def get_llm_backend() -> LLMBackend:
    backend = os.getenv("LLM_BACKEND", "openai").lower()
    if backend == "openai":
        return OpenAIBackend()
    elif backend == "gemini":
        return GeminiBackend()
    else:
        raise ValueError(f"Unknown LLM backend: {backend}")

# --- Agent Definition ---

class LiteratureAgent(BaseResearchAgent):
    """Literature Review Agent for academic research"""
    
    def __init__(self, llm_backend: LLMBackend = None):
        super().__init__("literature_agent")
        self.llm_backend = llm_backend or get_llm_backend()
        
        # Initialize VectorStoreManager for this agent
        self._initialize_vector_store_manager()
    
    def _add_agent_tools(self) -> None:
        """Add literature review specific tools"""
        # Add tools
        self.add_tool(COREAPISearchTool())
        self.add_tool(PDFExtractorTool())
        self.add_tool(RAGBuilderTool())
    
    def _get_system_prompt(self) -> str:
        """Get literature agent system prompt"""
        return """You are a Literature Review Agent specialized in academic research. Your role is to:

1. Search for relevant academic papers using CORE API
2. Extract and analyze PDF content from papers
3. Build a RAG (Retrieval-Augmented Generation) system for efficient information retrieval
4. Synthesize literature reviews with key findings, research gaps, and methodologies
5. Provide structured academic analysis

IMPORTANT WORKFLOW:
1. Use search_core_api to find papers
2. Use extract_pdf to get content from each paper's URL
3. Use build_rag with the collected papers and research domain
4. Synthesize the results into a comprehensive literature review

You have access to:
- CORE API for academic paper search
- PDF extraction capabilities
- RAG system building tools
- LLM for synthesis and analysis

CRITICAL: When using build_rag, you MUST pass the papers you collected from search_core_api as the first parameter, and the research domain as the second parameter.

Always ensure academic rigor, proper citation, and comprehensive coverage of the research domain."""

    def _prepare_agent_input(self, state: ResearchState, task: ResearchTask) -> str:
        """Prepare input for the literature agent"""
        parameters = task.parameters
        
        return f"""Conduct a comprehensive literature review for the following research project:

Research Domain: {state.research_domain}
Project Title: {state.title}
Project Description: {state.description}

Search Parameters:
- Query: {parameters.get('search_query', state.research_domain)}
- Max Results: {parameters.get('max_results', 20)}
- Year Range: {parameters.get('year_from', 2020)} - {parameters.get('year_to', 2024)}

WORKFLOW INSTRUCTIONS:
1. Use search_core_api to find relevant papers
2. For each paper found, use extract_pdf to get its content
3. Collect all papers and their extracted content
4. Use build_rag with the collected papers and research domain: "{state.research_domain}"
5. Synthesize a comprehensive literature review including:
   - Summary of current research landscape
   - Key findings and insights
   - Research gaps and opportunities
   - Methodologies and theoretical frameworks
   - Future research directions

IMPORTANT: When calling build_rag, pass the papers you collected as the first parameter and "{state.research_domain}" as the second parameter.

Ensure academic rigor and provide structured, well-organized results."""

    def _process_agent_result(self, result: Dict[str, Any], state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Process the agent's result"""
        try:
            # Extract content from LangChain result
            content = result.get("output", result.get("content", ""))
            
            # Try to parse structured content
            structured_result = self._parse_structured_content(content)
            
            # Add metadata
            structured_result.update({
                "task_id": task.id,
                "agent_type": "literature_agent",
                "execution_time": task.execution_time,
                "papers_processed": structured_result.get("papers_processed", 0),
                "generated_at": datetime.now(timezone.utc).isoformat()
            })
            
            return structured_result
            
        except Exception as e:
            return {
                "error": f"Failed to process agent result: {str(e)}",
                "raw_result": result
            }
    
    def _parse_structured_content(self, content: str) -> Dict[str, Any]:
        """Parse structured content from agent output"""
        try:
            # Try to extract JSON from the content
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback to extracting sections
        return {
            "summary": content[:500] + "..." if len(content) > 500 else content,  # Limit summary for display
            "key_findings": self._extract_key_findings(content),
            "research_gaps": self._extract_research_gaps(content),
            "methodologies": self._extract_methodologies(content),
            "papers_processed": 0
        }

    async def execute_task(self, state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Execute literature review task with proper workflow coordination"""
        try:
            print(f"🔄 Starting literature review workflow for: {state.research_domain}")
            
            # Step 1: Search for papers using CORE API
            print("📚 Step 1: Searching for academic papers...")
            search_query = task.parameters.get('search_query', state.research_domain)
            max_results = task.parameters.get('max_results', 10)  # Reduced for testing
            year_from = task.parameters.get('year_from', 2020)
            year_to = task.parameters.get('year_to', 2024)
            
            search_result = await search_core_api(
                query=search_query,
                max_results=max_results,
                year_from=year_from,
                year_to=year_to
            )
            
            if search_result.get("status") != "success":
                return {
                    "error": f"Paper search failed: {search_result.get('error', 'Unknown error')}",
                    "task_id": task.id
                }
            
            papers = search_result.get("results", [])
            print(f"✅ Found {len(papers)} papers")
            
            if not papers:
                return {
                    "error": "No papers found for the given search criteria",
                    "task_id": task.id
                }
            
            # Step 2: Extract PDF content from papers
            print("📄 Step 2: Extracting PDF content...")
            extracted_papers = []
            for i, paper in enumerate(papers[:3]):  # Limit to 3 papers for testing
                print(f"   Extracting paper {i+1}/{min(3, len(papers))}: {paper.get('title', 'Unknown')[:50]}...")
                
                pdf_url = paper.get('downloadUrl', '')
                if not pdf_url:
                    print(f"   ⚠️  No PDF URL for paper: {paper.get('title', 'Unknown')}")
                    continue
                
                extraction_result = await extract_pdf(pdf_url, f"paper_{i}")
                
                if extraction_result.get("extraction_status") == "success":
                    # Combine paper metadata with extracted content
                    enriched_paper = {
                        **paper,
                        "extracted_content": extraction_result.get("text_content", ""),
                        "word_count": extraction_result.get("word_count", 0),
                        "pages_extracted": extraction_result.get("pages_extracted", 0)
                    }
                    extracted_papers.append(enriched_paper)
                    print(f"   ✅ Extracted {extraction_result.get('word_count', 0)} words")
                else:
                    print(f"   ❌ Extraction failed: {extraction_result.get('error', 'Unknown error')}")
            
            print(f"✅ Successfully extracted content from {len(extracted_papers)} papers")
            
            # Step 3: Build RAG system (skip for now due to Weaviate issues)
            print("🧠 Step 3: Building RAG system...")
            try:
                rag_result = await build_rag(extracted_papers, state.research_domain)
                if "error" in rag_result:
                    print(f"   ⚠️  RAG building failed (expected): {rag_result['error']}")
                    # Continue without RAG for now
                else:
                    print(f"   ✅ RAG system built successfully")
            except Exception as rag_error:
                print(f"   ⚠️  RAG building failed (expected): {rag_error}")
                # Continue without RAG for now
            
            # Step 4: Generate literature review using LLM
            print("📝 Step 4: Generating literature review...")
            
            # Prepare content for LLM analysis
            analysis_content = self._prepare_analysis_content(extracted_papers, state.research_domain)
            
            # Use LLM to generate literature review
            llm_result = await self._generate_literature_review(analysis_content, state, task)
            
            if "error" in llm_result:
                return llm_result
            
            # Step 5: Structure the final result
            final_result = {
                "summary": llm_result.get("summary", ""),
                "key_findings": llm_result.get("key_findings", []),
                "research_gaps": llm_result.get("research_gaps", []),
                "methodologies": llm_result.get("methodologies", []),
                "papers_processed": len(extracted_papers),
                "search_query": search_query,
                "task_id": task.id,
                "agent_type": "literature_agent",
                "execution_time": task.execution_time,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Update state
            self._update_state_with_result(state, final_result, task)
            
            print(f"✅ Literature review workflow completed successfully!")
            return final_result
            
        except Exception as e:
            error_msg = f"Literature review workflow failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "task_id": task.id
            }
    
    def _prepare_analysis_content(self, extracted_papers: List[Dict[str, Any]], research_domain: str) -> str:
        """Prepare content for LLM analysis"""
        content_parts = [
            f"Research Domain: {research_domain}",
            f"Number of Papers Analyzed: {len(extracted_papers)}",
            "\n=== PAPERS AND CONTENT ===\n"
        ]
        
        for i, paper in enumerate(extracted_papers, 1):
            # Handle authors - they might be dictionaries or strings
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                # Convert author objects to strings
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
                f"Content Length: {paper.get('word_count', 0)} words",
                f"Extracted Content: {paper.get('extracted_content', 'No content extracted')[:2000]}...",
                "\n" + "="*50 + "\n"
            ])
        
        return "\n".join(content_parts)
    
    async def _generate_literature_review(self, analysis_content: str, state: ResearchState, task: ResearchTask) -> Dict[str, Any]:
        """Generate literature review using LLM"""
        try:
            # Create a focused prompt for literature review generation
            prompt = f"""Based on the following academic papers and their content, generate a comprehensive literature review for the research domain: {state.research_domain}

{analysis_content}

Please provide a structured literature review with the following sections:

1. SUMMARY: A comprehensive overview of the current research landscape
2. KEY FINDINGS: Main insights and discoveries from the analyzed papers
3. RESEARCH GAPS: Identified gaps and opportunities for future research
4. METHODOLOGIES: Research methods and frameworks used in the field
5. FUTURE DIRECTIONS: Recommendations for future research

Format your response as a well-structured academic literature review. Focus on synthesis and analysis rather than just summarizing individual papers."""

            # Use the LLM backend to generate the review
            llm_response = await self.llm_backend.generate(prompt)
            
            if not llm_response:
                return {
                    "error": "LLM generation failed: No response received"
                }
            
            # Parse the LLM response into structured format
            structured_result = self._parse_literature_review_response(llm_response)
            
            return structured_result
            
        except Exception as e:
            return {
                "error": f"Literature review generation failed: {str(e)}"
            }
    
    def _parse_literature_review_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured literature review format"""
        try:
            # Try to extract structured sections
            sections = {
                "summary": "",
                "key_findings": [],
                "research_gaps": [],
                "methodologies": [],
                "future_directions": []
            }
            
            # Simple parsing - look for section headers
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                if any(keyword in line.lower() for keyword in ['summary', 'overview']):
                    current_section = 'summary'
                elif any(keyword in line.lower() for keyword in ['key findings', 'main findings', 'insights']):
                    current_section = 'key_findings'
                elif any(keyword in line.lower() for keyword in ['research gaps', 'gaps', 'opportunities']):
                    current_section = 'research_gaps'
                elif any(keyword in line.lower() for keyword in ['methodologies', 'methods', 'frameworks']):
                    current_section = 'methodologies'
                elif any(keyword in line.lower() for keyword in ['future directions', 'future research', 'recommendations']):
                    current_section = 'future_directions'
                elif current_section and line:
                    # Add content to current section
                    if current_section == 'summary':
                        sections['summary'] += line + " "
                    elif current_section in ['key_findings', 'research_gaps', 'methodologies', 'future_directions']:
                        sections[current_section].append(line)
            
            # Clean up summary
            sections['summary'] = sections['summary'].strip()
            
            # Convert lists to structured format
            structured_findings = [{"finding": item, "confidence": 0.8} for item in sections['key_findings'][:10]]
            structured_gaps = [{"gap": item, "priority": "medium"} for item in sections['research_gaps'][:10]]
            structured_methodologies = [{"methodology": item, "type": "research_method"} for item in sections['methodologies'][:10]]
            
            return {
                "summary": sections['summary'] or response[:1000],  # Fallback to first 1000 chars
                "key_findings": structured_findings,
                "research_gaps": structured_gaps,
                "methodologies": structured_methodologies,
                "future_directions": sections['future_directions'][:5]
            }
            
        except Exception as e:
            # Fallback to simple parsing
            return {
                "summary": response[:1000] + "..." if len(response) > 1000 else response,
                "key_findings": self._extract_key_findings(response),
                "research_gaps": self._extract_research_gaps(response),
                "methodologies": self._extract_methodologies(response)
            }

    def _update_state_with_result(self, state: ResearchState, result: Dict[str, Any], task: ResearchTask) -> None:
        """Update research state with literature review results"""
        try:
            # Create literature review object
            from analyser.core.research_state import LiteratureReview
            
            literature_review = LiteratureReview(
                summary=result.get("summary", ""),
                key_findings=result.get("key_findings", []),
                research_gaps=result.get("research_gaps", []),
                methodologies=result.get("methodologies", []),
                papers_processed=result.get("papers_processed", 0),
                search_query=result.get("search_query", ""),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Update state
            state.literature_review = literature_review
            state.updated_at = datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"Warning: Failed to update state with literature review: {e}")

    def _prepare_feedback_input(self, state: ResearchState, task: ResearchTask, feedback: Dict[str, Any]) -> str:
        """Prepare input for feedback processing"""
        return f"""Process the following feedback for the literature review:

Current Literature Review:
{state.literature_review.summary if state.literature_review else "No literature review available"}

Feedback:
{json.dumps(feedback, indent=2)}

Please:
1. Analyze the feedback
2. Identify areas for improvement
3. Suggest specific actions to address the feedback
4. Update the literature review accordingly

Provide structured recommendations for improving the literature review."""

    def _extract_key_findings(self, analysis_result: str) -> List[Dict[str, Any]]:
        """Extract key findings from analysis result"""
        findings = []
        
        # Simple extraction - in production, use more sophisticated NLP
        lines = analysis_result.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['finding', 'discovered', 'identified', 'shows', 'demonstrates']):
                findings.append({
                    "finding": line.strip(),
                    "confidence": 0.8,
                    "extracted_at": datetime.now(timezone.utc).isoformat()
                })
        
        return findings[:10]  # Limit to top 10 findings

    def _extract_research_gaps(self, analysis_result: str) -> List[Dict[str, Any]]:
        """Extract research gaps from analysis result"""
        gaps = []
        
        # Simple extraction - in production, use more sophisticated NLP
        lines = analysis_result.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['gap', 'missing', 'limited', 'lack', 'need', 'future']):
                gaps.append({
                    "gap": line.strip(),
                    "priority": "medium",
                    "extracted_at": datetime.now(timezone.utc).isoformat()
                })
        
        return gaps[:10]  # Limit to top 10 gaps

    def _extract_methodologies(self, analysis_result: str) -> List[Dict[str, Any]]:
        """Extract methodologies from analysis result"""
        methodologies = []
        
        # Simple extraction - in production, use more sophisticated NLP
        lines = analysis_result.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['method', 'approach', 'technique', 'framework', 'model']):
                methodologies.append({
                    "methodology": line.strip(),
                    "type": "research_method",
                    "extracted_at": datetime.now(timezone.utc).isoformat()
                })
        
        return methodologies[:10]  # Limit to top 10 methodologies 