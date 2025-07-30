#!/usr/bin/env python3
"""
Simple test script for Literature Review Agent structure
Tests basic imports and class structure without external dependencies
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
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

def test_agent_class_structure():
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

def test_tool_classes():
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

def test_function_signatures():
    """Test that standalone functions have correct signatures"""
    print("\n🔧 Testing function signatures...")
    
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
        print(f"❌ Function signature testing failed: {e}")
        return False

def test_research_state():
    """Test research state creation and management"""
    print("\n📊 Testing research state...")
    
    try:
        from analyser.core.research_state import ResearchState, ResearchTask, ResearchPhase
        
        # Create research state
        state = ResearchState(
            title="Test Research Project",
            description="Testing literature review functionality",
            research_domain="Web3 and Blockchain Technology"
        )
        
        # Create task
        task = ResearchTask(
            phase=ResearchPhase.LITERATURE_REVIEW,
            description="Conduct literature review on blockchain technology",
            agent_type="literature_agent",
            parameters={
                "search_query": "blockchain technology academic research",
                "max_results": 10,
                "year_from": 2020,
                "year_to": 2024
            }
        )
        
        # Add task to state
        state.add_task(task)
        
        print(f"✅ Research state created successfully")
        print(f"   Title: {state.title}")
        print(f"   Domain: {state.research_domain}")
        print(f"   Tasks: {len(state.tasks)}")
        print(f"   Current phase: {state.current_phase.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Research state testing failed: {e}")
        return False

def run_basic_tests():
    """Run basic structure tests"""
    print("🚀 Starting Basic Literature Review Agent Tests")
    print("=" * 60)
    
    # Run individual tests
    tests = [
        ("Imports", test_imports),
        ("Agent Class Structure", test_agent_class_structure),
        ("Tool Classes", test_tool_classes),
        ("Function Signatures", test_function_signatures),
        ("Research State", test_research_state)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
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
        print("\n🎉 All basic tests passed! Literature review structure is correct.")
        print("\n✅ Literature review agent is properly structured and ready for testing with API keys!")
        print("\nTo run full tests with API functionality:")
        print("1. Set OPENAI_API_KEY in your .env file")
        print("2. Optionally set CORE_API_KEY for academic paper search")
        print("3. Run: python test_literature_review.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    # Run the basic tests
    run_basic_tests() 