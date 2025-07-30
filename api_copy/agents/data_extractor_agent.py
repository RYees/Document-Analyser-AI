import os
import aiohttp
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timezone
from io import BytesIO
import PyPDF2
import sys
import os
# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.vector_store_manager import VectorStoreManager

class DataExtractorAgent:
    """
    Fetches raw academic texts from external sources (e.g., CORE API, Arxiv, Semantic Scholar),
    extracts relevant metadata, and stores documents in a vector database for retrieval.
    """
    def __init__(self):
        # Initialize any API clients, vector store managers, etc.
        pass

    async def fetch_papers(self, query: str, max_results: int = 20, year_from: int = 2020, year_to: int = 2024) -> List[Dict[str, Any]]:
        """
        Fetch academic papers and metadata from CORE API.
        """
        api_key = os.getenv("CORE_API_KEY")
        print(f"[DEBUG] CORE_API_KEY found: {bool(api_key)}")

        if not api_key:
            raise ValueError("Missing CORE API key in environment variables.")
        
        print(f"[DEBUG] Fetching papers with query: '{query}', max_results: {max_results}")
        
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
        
        print(f"[DEBUG] CORE API payload: {payload}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"[DEBUG] CORE API response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    print(f"[DEBUG] CORE API returned {len(results)} papers")
                    
                    # Log first few papers for debugging
                    for i, paper in enumerate(results[:3]):
                        print(f"[DEBUG] Paper {i+1}:")
                        print(f"  Title: {paper.get('title', 'No title')[:50]}...")
                        print(f"  Authors: {paper.get('authors', [])}")
                        print(f"  DOI: {paper.get('doi', 'No DOI')}")
                        print(f"  Download URL: {paper.get('downloadUrl', 'No URL')}")
                        print(f"  Abstract length: {len(paper.get('abstract', ''))}")
                    
                    return results
                else:
                    try:
                        error_body = await response.text()
                    except Exception:
                        error_body = "<could not read response body>"
                    print(f"[ERROR] CORE API search failed: {response.status}, body: {error_body}")
                    raise RuntimeError(f"CORE API search failed: {response.status}")

    async def extract_pdf_content(self, pdf_url: str, paper_id: str) -> Dict[str, Any]:
        """
        Extract text content from a PDF file given its URL.
        """
        print(f"[DEBUG] Extracting PDF content for paper_id: {paper_id}")
        print(f"[DEBUG] PDF URL: {pdf_url}")
        
        # Handle arXiv URLs
        if "arxiv.org/abs/" in pdf_url:
            pdf_url = pdf_url.replace("/abs/", "/pdf/") + ".pdf"
            print(f"[DEBUG] Converted arXiv URL to: {pdf_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                print(f"[DEBUG] PDF download response status: {response.status}")
                
                if response.status == 200:
                    content_bytes = await response.read()
                    print(f"[DEBUG] Downloaded {len(content_bytes)} bytes")
                    
                    if content_bytes.startswith(b'%PDF'):
                        print(f"[DEBUG] Content is a valid PDF")
                        try:
                            pdf_file = BytesIO(content_bytes)
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            print(f"[DEBUG] PDF has {len(pdf_reader.pages)} pages")
                            
                            extracted_text = ""
                            for page_num, page in enumerate(pdf_reader.pages):
                                try:
                                    page_text = page.extract_text()
                                    if page_text:
                                        extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                                        print(f"[DEBUG] Extracted {len(page_text)} characters from page {page_num + 1}")
                                except Exception as e:
                                    print(f"[WARNING] Could not extract text from page {page_num + 1}: {e}")
                                    continue
                            
                            if extracted_text.strip():
                                cleaned_text = extracted_text.strip()
                                word_count = len(cleaned_text.split())
                                print(f"[DEBUG] Successfully extracted {word_count} words from PDF")
                                
                                return {
                                    "paper_id": paper_id,
                                    "extraction_status": "success",
                                    "text_content": cleaned_text,
                                    "word_count": word_count,
                                    "pages_extracted": len(pdf_reader.pages),
                                    "extracted_at": datetime.now(timezone.utc).isoformat()
                                }
                            else:
                                print(f"[ERROR] No text could be extracted from PDF")
                                return {
                                    "paper_id": paper_id,
                                    "extraction_status": "failed",
                                    "error": "No text could be extracted from PDF"
                                }
                        except Exception as pdf_error:
                            print(f"[ERROR] PDF parsing failed: {pdf_error}")
                            return {
                                "paper_id": paper_id,
                                "extraction_status": "failed",
                                "error": f"PDF parsing failed: {str(pdf_error)}"
                            }
                    else:
                        print(f"[DEBUG] Content is not a PDF, trying to decode as text")
                        try:
                            content_text = content_bytes.decode('utf-8', errors='ignore')
                            word_count = len(content_text.split())
                            print(f"[DEBUG] Successfully decoded {word_count} words as text")
                            
                            return {
                                "paper_id": paper_id,
                                "extraction_status": "success",
                                "text_content": content_text[:5000] + "..." if len(content_text) > 5000 else content_text,
                                "word_count": word_count,
                                "pages_extracted": 1,
                                "extracted_at": datetime.now(timezone.utc).isoformat()
                            }
                        except Exception as text_error:
                            print(f"[ERROR] Text decoding failed: {text_error}")
                            return {
                                "paper_id": paper_id,
                                "extraction_status": "failed",
                                "error": f"Text decoding failed: {str(text_error)}"
                            }
                else:
                    print(f"[ERROR] Failed to download PDF: {response.status}")
                    return {
                        "paper_id": paper_id,
                        "extraction_status": "failed",
                        "error": f"Failed to download PDF: {response.status}"
                    }

    async def store_in_vector_db(self, papers: List[Dict[str, Any]], research_domain: str) -> Dict[str, Any]:
        """
        Store papers and their content in a Weaviate vector database for retrieval.
        """
        print(f"[DEBUG] store_in_vector_db called with {len(papers)} papers")
        print(f"[DEBUG] Research domain: {research_domain}")
        
        vstore = VectorStoreManager(collection_name="ResearchPaper", research_domain=research_domain)
        chunks = []
        metadata_list = []
        
        for i, paper in enumerate(papers):
            print(f"[DEBUG] Processing paper {i+1}/{len(papers)}")
            print(f"[DEBUG] Paper title: {paper.get('title', 'No title')[:50]}...")
            
            content = paper.get("extracted_content") or paper.get("content")
            if not content:
                print(f"[WARNING] No content found for paper {i+1}")
                continue
            
            print(f"[DEBUG] Paper content length: {len(content)} characters")
            
            # Simple chunking (could use utils.chunking for more advanced)
            paper_chunks = [content[j:j+1000] for j in range(0, len(content), 1000)]
            print(f"[DEBUG] Created {len(paper_chunks)} chunks for paper {i+1}")
            
            for j, chunk in enumerate(paper_chunks):
                chunks.append(chunk)
                
                # Handle authors - convert list to string if needed
                authors = paper.get("authors", [])
                if isinstance(authors, list):
                    authors_str = ", ".join([str(author) for author in authors])
                else:
                    authors_str = str(authors)
                
                meta = {
                    "title": paper.get("title", ""),
                    "authors": authors_str,  # Convert to string
                    "year": paper.get("year"),
                    "doi": paper.get("doi", ""),
                    "source": paper.get("source", ""),
                    "paper_id": paper.get("doi", paper.get("title", "")),
                    "chunk_index": j
                }
                metadata_list.append(meta)
                
                if j < 2:  # Log first few chunks
                    print(f"[DEBUG] Chunk {j+1}: {len(chunk)} chars, metadata: {meta}")
        
        print(f"[DEBUG] Total chunks to store: {len(chunks)}")
        print(f"[DEBUG] Total metadata entries: {len(metadata_list)}")
        
        if chunks:
            print(f"[DEBUG] Calling vstore.add_chunks...")
            result = vstore.add_chunks(chunks, metadata_list)
            print(f"[DEBUG] vstore.add_chunks returned: {result}")
            return {
                "status": "success",
                "papers_processed": len(papers),
                "chunks_stored": len(chunks),
                "vectorstore_name": "ResearchPaper"
            }
        else:
            print(f"[ERROR] No chunks to store!")
            return {
                "status": "error",
                "error": "No content chunks to store"
            }

    async def run(self, query: str, max_results: int = 20, year_from: int = 2020, year_to: int = 2024, research_domain: str = "General") -> Dict[str, Any]:
        """
        Main entry point for data extraction pipeline.
        1. Fetch papers
        2. Extract PDF content
        3. Store in vector DB
        Returns a summary of the ingestion process.
        """
        print(f"[DEBUG] ===== Starting DataExtractorAgent.run =====")
        print(f"[DEBUG] Query: {query}")
        print(f"[DEBUG] Max results: {max_results}")
        print(f"[DEBUG] Research domain: {research_domain}")
        
        # Step 1: Fetch papers
        print(f"[DEBUG] Step 1: Fetching papers...")
        papers = await self.fetch_papers(query, max_results, year_from, year_to)
        print(f"[DEBUG] Fetched {len(papers)} papers")
        
        # Step 2: Extract PDF content
        print(f"[DEBUG] Step 2: Extracting PDF content...")
        extracted_papers = []
        for i, paper in enumerate(papers):
            print(f"[DEBUG] Processing paper {i+1}/{len(papers)}")
            pdf_url = paper.get('downloadUrl', '')
            if not pdf_url:
                print(f"[WARNING] No PDF URL for paper {i+1}")
                continue
            
            extraction_result = await self.extract_pdf_content(pdf_url, f"paper_{i}")
            print(f"[DEBUG] Extraction result for paper {i+1}: {extraction_result.get('extraction_status')}")
            
            if extraction_result.get("extraction_status") == "success":
                enriched_paper = {**paper, "extracted_content": extraction_result.get("text_content", "")}
                extracted_papers.append(enriched_paper)
                print(f"[DEBUG] Successfully enriched paper {i+1}")
            else:
                print(f"[ERROR] Failed to extract paper {i+1}: {extraction_result.get('error')}")
        
        print(f"[DEBUG] Successfully extracted content from {len(extracted_papers)} papers")
        
        # Step 3: Store in vector DB
        print(f"[DEBUG] Step 3: Storing in vector database...")
        store_result = await self.store_in_vector_db(extracted_papers, research_domain)
        print(f"[DEBUG] Store result: {store_result}")
        
        final_result = {
            "papers_fetched": len(papers),
            "papers_extracted": len(extracted_papers),
            "vector_store_result": store_result
        }
        
        print(f"[DEBUG] ===== DataExtractorAgent.run completed =====")
        print(f"[DEBUG] Final result: {final_result}")
        
        return final_result 