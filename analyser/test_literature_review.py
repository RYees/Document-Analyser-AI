#!/usr/bin/env python3
"""
Test script for Literature Review Agent
Tests CORE API integration, PDF extraction, and RAG functionality
"""

import asyncio
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment setup...")
    
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["CORE_API_KEY"]
    
    missing_required = [var for var in required_vars if not os.getenv(var)]
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        print("Please set these in your .env file:")
        for var in missing_required:
            print(f"  {var}=your_api_key_here")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {missing_optional}")
        print("These are recommended for full functionality:")
        for var in missing_optional:
            print(f"  {var}=your_api_key_here")
        print("Continuing with limited functionality...")
    
    print("✅ Environment setup complete")
    return True

async def test_imports():
    """Test that all required modules can be imported"""
    print("\n🔍 Testing imports...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent, search_core_api, extract_pdf, build_rag
        print("✅ Literature agent imports successful")
    except Exception as e:
        print(f"❌ Literature agent imports failed: {e}")
        return False
    
    try:
        from analyser.core.research_state import ResearchState, ResearchTask, ResearchPhase, TaskStatus
        print("✅ Research state imports successful")
    except Exception as e:
        print(f"❌ Research state imports failed: {e}")
        return False
    
    try:
        from analyser.agents.llm_backends import OpenAIBackend, LLMBackend
        print("✅ LLM backends imports successful")
    except Exception as e:
        print(f"❌ LLM backends imports failed: {e}")
        return False
    
    try:
        from analyser.agents.base_agent import BaseResearchAgent
        print("✅ Base agent imports successful")
    except Exception as e:
        print(f"❌ Base agent imports failed: {e}")
        return False
    
    return True

async def test_standalone_functions():
    """Test standalone functions without external dependencies"""
    print("\n🔧 Testing standalone functions...")
    
    try:
        from analyser.agents.literature_agent import search_core_api, extract_pdf, build_rag
        
        # Test search_core_api function structure
        import inspect
        sig = inspect.signature(search_core_api)
        params = list(sig.parameters.keys())
        expected_params = ['query', 'max_results', 'year_from', 'year_to']
        
        if all(param in params for param in expected_params):
            print("✅ search_core_api function signature correct")
        else:
            print(f"❌ search_core_api function signature incorrect. Expected: {expected_params}, Got: {params}")
            return False
        
        # Test extract_pdf function structure
        sig = inspect.signature(extract_pdf)
        params = list(sig.parameters.keys())
        expected_params = ['pdf_url', 'paper_id']
        
        if all(param in params for param in expected_params):
            print("✅ extract_pdf function signature correct")
        else:
            print(f"❌ extract_pdf function signature incorrect. Expected: {expected_params}, Got: {params}")
            return False
        
        # Test build_rag function structure
        sig = inspect.signature(build_rag)
        params = list(sig.parameters.keys())
        expected_params = ['papers', 'research_domain']
        
        if all(param in params for param in expected_params):
            print("✅ build_rag function signature correct")
        else:
            print(f"❌ build_rag function signature incorrect. Expected: {expected_params}, Got: {params}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone function testing failed: {e}")
        return False

async def test_agent_class_structure():
    """Test that the LiteratureAgent class has the required methods"""
    print("\n🤖 Testing agent class structure...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent
        
        # Check if class exists
        if not hasattr(LiteratureAgent, '__init__'):
            print("❌ LiteratureAgent missing __init__ method")
            return False
        
        # Check for required methods
        required_methods = [
            'execute_task',
            '_prepare_agent_input',
            '_process_agent_result',
            '_update_state_with_result',
            '_prepare_feedback_input'
        ]
        
        for method in required_methods:
            if not hasattr(LiteratureAgent, method):
                print(f"❌ LiteratureAgent missing {method} method")
                return False
        
        print("✅ LiteratureAgent class structure correct")
        return True
        
    except Exception as e:
        print(f"❌ Agent class structure testing failed: {e}")
        return False

async def test_tool_classes():
    """Test that tool classes are properly defined"""
    print("\n🛠️  Testing tool classes...")
    
    try:
        from analyser.agents.literature_agent import COREAPISearchTool, PDFExtractorTool, RAGBuilderTool
        
        # Test COREAPISearchTool
        if hasattr(COREAPISearchTool, '__pydantic_fields__') and 'name' in COREAPISearchTool.__pydantic_fields__:
            name_field = COREAPISearchTool.__pydantic_fields__['name']
            if name_field.default == 'search_core_api':
                print("✅ COREAPISearchTool properly defined")
            else:
                print(f"❌ COREAPISearchTool name incorrect. Expected: search_core_api, Got: {name_field.default}")
                return False
        else:
            print("❌ COREAPISearchTool not properly defined")
            return False
        
        # Test PDFExtractorTool
        if hasattr(PDFExtractorTool, '__pydantic_fields__') and 'name' in PDFExtractorTool.__pydantic_fields__:
            name_field = PDFExtractorTool.__pydantic_fields__['name']
            if name_field.default == 'extract_pdf':
                print("✅ PDFExtractorTool properly defined")
            else:
                print(f"❌ PDFExtractorTool name incorrect. Expected: extract_pdf, Got: {name_field.default}")
                return False
        else:
            print("❌ PDFExtractorTool not properly defined")
            return False
        
        # Test RAGBuilderTool
        if hasattr(RAGBuilderTool, '__pydantic_fields__') and 'name' in RAGBuilderTool.__pydantic_fields__:
            name_field = RAGBuilderTool.__pydantic_fields__['name']
            if name_field.default == 'build_rag':
                print("✅ RAGBuilderTool properly defined")
            else:
                print(f"❌ RAGBuilderTool name incorrect. Expected: build_rag, Got: {name_field.default}")
                return False
        else:
            print("❌ RAGBuilderTool not properly defined")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tool classes testing failed: {e}")
        return False

async def test_core_api_search():
    """Test CORE API search functionality (if API key available)"""
    print("\n🔍 Testing CORE API search...")
    
    if not os.getenv("CORE_API_KEY"):
        print("⚠️  CORE_API_KEY not set, skipping CORE API test")
        return True
    
    try:
        from analyser.agents.literature_agent import search_core_api
        
        # Test search
        query = "blockchain technology academic research"
        result = await search_core_api(query, max_results=5, year_from=2020, year_to=2024)
        
        if result.get("status") == "error":
            print(f"❌ CORE API search failed: {result.get('error')}")
            return False
        
        papers = result.get("papers", [])
        print(f"✅ Found {len(papers)} papers")
        
        # Display first few papers
        for i, paper in enumerate(papers[:3]):
            print(f"  {i+1}. {paper.get('title', 'No title')}")
            print(f"     Authors: {', '.join(paper.get('authors', []))}")
            print(f"     Year: {paper.get('year', 'Unknown')}")
            print(f"     DOI: {paper.get('doi', 'No DOI')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ CORE API test failed: {e}")
        return False

async def test_pdf_extraction():
    """Test PDF extraction functionality"""
    print("\n📄 Testing PDF extraction...")
    
    try:
        from analyser.agents.literature_agent import extract_pdf
        
        # Test with a sample PDF URL (you might want to use a real academic PDF)
        pdf_url = "https://arxiv.org/pdf/2008.03961.pdf"  # Example arXiv paper
        paper_id = "test_paper_001"
        
        result = await extract_pdf(pdf_url, paper_id)
        
        if result.get("extraction_status") == "success":
            print("✅ PDF extraction successful")
            print(f"   Word count: {result.get('word_count', 0)}")
            return True
        else:
            print(f"❌ PDF extraction failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ PDF extraction test failed: {e}")
        return False

async def test_rag_building():
    """Test RAG system building"""
    print("\n🧠 Testing RAG system building...")
    
    try:
        from analyser.agents.literature_agent import build_rag
        
        # Create sample papers data
        sample_papers = [
            {
                "title": "Blockchain Technology: A Comprehensive Review",
                "authors": ["John Doe", "Jane Smith"],
                "abstract": "This paper provides a comprehensive review of blockchain technology...",
                "year": 2023,
                "doi": "10.1234/test.2023.001",
                "content": "Blockchain technology has emerged as a revolutionary innovation...",
                "source": "CORE"
            },
            {
                "title": "Web3 Applications in Academic Research",
                "authors": ["Alice Johnson", "Bob Brown"],
                "abstract": "This study explores the applications of Web3 in academic research...",
                "year": 2023,
                "doi": "10.1234/test.2023.002",
                "content": "Web3 technologies are transforming how academic research is conducted...",
                "source": "CORE"
            }
        ]
        
        result = await build_rag(sample_papers, "Web3 Research")
        
        if "error" not in result:
            print("✅ RAG system built successfully")
            print(f"   Papers processed: {result.get('papers_processed', 0)}")
            print(f"   Total chunks: {result.get('total_chunks', 0)}")
            return True
        else:
            print(f"❌ RAG building failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ RAG building test failed: {e}")
        return False

async def test_literature_agent_task():
    """Test the complete literature agent task execution"""
    print("\n🤖 Testing Literature Agent task execution...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent
        from analyser.core.research_state import ResearchState, ResearchTask, ResearchPhase
        from analyser.agents.llm_backends import OpenAIBackend
        
        # Create a test task
        task = ResearchTask(
            phase=ResearchPhase.LITERATURE_REVIEW,
            description="Conduct literature review on blockchain technology",
            agent_type="literature_agent",
            parameters={
                "search_query": "blockchain technology academic research",
                "max_results": 10,
                "year_from": 2020,
                "year_to": 2024,
                "research_domain": "Web3 and Blockchain Technology"
            }
        )
        
        # Initialize research state
        state = ResearchState(
            title="Test Research Project",
            description="Testing literature review functionality",
            research_domain="Web3 and Blockchain Technology"
        )
        
        # Add task to state
        state.add_task(task)
        
        # Initialize agent
        llm_backend = OpenAIBackend()
        agent = LiteratureAgent(llm_backend)
        
        # Execute task
        result = await agent.execute_task(state, task)
        
        if result and "error" not in result:
            print("✅ Literature agent task completed successfully")
            print(f"   Task ID: {task.id}")
            print(f"   Status: {task.status.value}")
            print(f"   Execution time: {task.execution_time:.2f}s")
            
            # Check if literature review was created
            if state.literature_review:
                print(f"   Papers processed: {state.literature_review.papers_processed}")
                print(f"   Key findings: {len(state.literature_review.key_findings)}")
                print(f"   Research gaps: {len(state.literature_review.research_gaps)}")
            
            return True
        else:
            print("❌ Literature agent task failed")
            if "error" in result:
                print(f"   Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Literature agent test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Literature Review Agent Tests")
    print("=" * 60)
    
    # Environment check
    if not check_environment():
        return False
    
    # Run individual tests
    tests = [
        ("Imports", test_imports),
        ("Standalone Functions", test_standalone_functions),
        ("Agent Class Structure", test_agent_class_structure),
        ("Tool Classes", test_tool_classes),
        ("CORE API Search", test_core_api_search),
        ("PDF Extraction", test_pdf_extraction),
        ("RAG Building", test_rag_building),
        ("Literature Agent Task", test_literature_agent_task)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Literature review functionality is working correctly.")
        print("\n✅ Literature review automation is ready for use!")
        print("\nNext steps:")
        print("1. Test with real research projects")
        print("2. Integrate with the workflow orchestrator")
        print("3. Add human-in-the-loop feedback mechanisms")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == len(results)

async def main():
    """Main test function"""
    success = await run_all_tests()
    return success

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 