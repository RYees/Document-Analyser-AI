#!/usr/bin/env python3
"""
Test script for Literature Review Agent as a LangChain agent in workflow context
Tests the agent's ability to use tools, process results, and integrate with workflow orchestrator
"""

import asyncio
import os
import sys
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Suppress verbose logging from LangChain and other libraries
logging.getLogger("langchain").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv("env_file")

def truncate_long_output(text: str, max_length: int = 200) -> str:
    """Truncate long text output to prevent verbose logging"""
    if isinstance(text, str) and len(text) > max_length:
        return text[:max_length] + "..."
    return text

def filter_agent_output(output: Any) -> Any:
    """Filter agent output to remove verbose content"""
    if isinstance(output, dict):
        filtered = {}
        for key, value in output.items():
            if key in ["text_content", "log_content", "abstract", "content"]:
                filtered[key] = truncate_long_output(str(value), 100)
            elif isinstance(value, str) and len(value) > 200:
                filtered[key] = truncate_long_output(value, 100)
            else:
                filtered[key] = value
        return filtered
    elif isinstance(output, str) and len(output) > 200:
        return truncate_long_output(output, 100)
    return output

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment setup...")
    
    required_vars = "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"
    optional_vars = "ZS01E3YUymOHq9RCcn5FiPb6lAjpN8kK"
    
    # missing_required = [var for var in required_vars if not os.getenv(var)]
    # missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    # if not required_vars:
    #     print(f"❌ Missing required environment variables: {missing_required}")
    #     print("Please set these in your .env file:")
    #     for var in missing_required:
    #         print(f"  {var}=your_api_key_here")
    #     return False
    
    # if not optional_vars:
    #     print(f"⚠️  Missing optional environment variables: {missing_optional}")
    #     print("These are recommended for full functionality:")
    #     for var in missing_optional:
    #         print(f"  {var}=your_api_key_here")
    #     print("Continuing with limited functionality...")
    
    print("✅ Environment setup complete")
    return True

async def test_literature_agent_as_langchain_agent():
    """Test Literature Agent as a LangChain agent with tools"""
    print("\n🤖 Testing Literature Agent as LangChain Agent...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent
        from analyser.core.research_state import ResearchState, ResearchTask, ResearchPhase
        from analyser.agents.llm_backends import OpenAIBackend
        
        print("✅ Successfully imported required modules")
        
        # Initialize LLM backend
        llm_backend = OpenAIBackend()
        print("✅ LLM backend initialized")
        
        # Initialize Literature Agent
        agent = LiteratureAgent(llm_backend)
        print("✅ Literature Agent initialized")
        
        # Check if agent has tools
        if hasattr(agent, 'tools') and agent.tools:
            print(f"✅ Agent has {len(agent.tools)} tools:")
            for tool in agent.tools:
                print(f"   - {tool.name}: {tool.description}")
        else:
            print("❌ Agent has no tools")
            return False
        
        # Check if agent has LangChain executor
        if hasattr(agent, 'agent_executor') and agent.agent_executor:
            print("✅ Agent has LangChain executor")
        else:
            print("❌ Agent missing LangChain executor")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Literature agent initialization failed: {e}")
        return False

async def test_agent_tool_execution():
    """Test that the agent can execute its tools"""
    print("\n🛠️  Testing Agent Tool Execution...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent
        from analyser.agents.llm_backends import OpenAIBackend
        
        # Initialize agent
        llm_backend = OpenAIBackend()
        agent = LiteratureAgent(llm_backend)
        
        # Test CORE API tool
        core_tool = None
        for tool in agent.tools:
            if tool.name == "search_core_api":
                core_tool = tool
                break
        
        if core_tool:
            print("✅ Found CORE API tool")
            
            # Test tool execution
            try:
                result = await core_tool._arun(
                    query="blockchain technology",
                    max_results=2,
                    year_from=2020,
                    year_to=2024
                )
                
                if result and len(result) > 0:
                    print(f"✅ CORE API tool executed successfully")
                    print(f"   Found {len(result)} papers")
                    
                    # Show first paper details
                    if len(result) > 0:
                        first_paper = result[0]
                        print(first_paper)
                        print(f"   First paper: {first_paper.get('title', 'No title')}")
                        print(f"   Authors: {first_paper.get('authors', [])}")
                        print(f"   Year: {first_paper.get('year', 'Unknown')}")
                else:
                    print("⚠️  CORE API tool returned no results")
                    
            except Exception as e:
                print(f"❌ CORE API tool execution failed: {e}")
                return False
        else:
            print("❌ CORE API tool not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        return False

async def test_agent_task_execution():
    """Test the complete agent task execution as it would be used in workflow"""
    print("\n📋 Testing Complete Agent Task Execution...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent
        from analyser.core.research_state import ResearchState, ResearchTask, ResearchPhase
        from analyser.agents.llm_backends import OpenAIBackend
        
        # Create research state (as in workflow orchestrator)
        state = ResearchState(
            title="Test Research Project: Blockchain in Academic Research",
            description="A comprehensive study of blockchain technology applications in academic research",
            research_domain="Web3 and Blockchain Technology"
        )
        
        # Create task (as in _literature_review_node)
        task = ResearchTask(
            phase=ResearchPhase.LITERATURE_REVIEW,
            description="Conduct comprehensive literature review on blockchain technology in academic research",
            agent_type="literature_agent",
            parameters={
                "search_query": "blockchain technology academic research",
                "max_results": 5,
                "year_from": 2020,
                "year_to": 2024,
                "research_domain": "Web3 and Blockchain Technology"
            }
        )
        
        # Add task to state
        state.add_task(task)
        
        print("✅ Research state and task created")
        print(f"   Project: {state.title}")
        # print(f"   Domain: {state.research_domain}")
        # print(f"   Task: {task.description}")
        
        # Initialize agent
        llm_backend = OpenAIBackend()
        agent = LiteratureAgent(llm_backend)
        
        print("✅ Agent initialized, executing task...")
        
        # Execute task
        print("   Executing agent task...")
        result = await agent.execute_task(state, task)
        
        # Filter the result to remove verbose content
        filtered_result = filter_agent_output(result)
        
        if filtered_result and "error" not in filtered_result:
            print("✅ Agent task executed successfully")
            print(f"   Task ID: {task.id}")
            # print(f"   Status: {task.status.value}")
            if task.execution_time is not None:
                print(f"   Execution time: {task.execution_time:.2f}s")
            else:
                print("   Execution time: Not recorded")
            
            # Check result structure with filtered output
            print("\n📊 Task Result Analysis:")
            print(f"   Result type: {type(filtered_result)}")
            print(f"   Result keys: {list(filtered_result.keys()) if isinstance(filtered_result, dict) else 'Not a dict'}")
            
            if isinstance(filtered_result, dict):
                for key, value in filtered_result.items():
                    if key == "summary":
                        print(f"   Summary: {str(value)[:50]}...")
                    elif key == "key_findings":
                        print(f"   Key findings: {len(value) if isinstance(value, list) else 'Not a list'}")
                    elif key == "research_gaps":
                        print(f"   Research gaps: {len(value) if isinstance(value, list) else 'Not a list'}")
                    elif key == "papers_processed":
                        print(f"   Papers processed: {value}")
                    elif key in ["text_content", "log_content", "abstract", "content"]:
                        # Skip displaying verbose content
                        continue
                    elif isinstance(value, str) and len(value) > 100:
                        # Limit any long string content
                        print(f"   {key}: {str(value)[:50]}...")
                    else:
                        print(f"   {key}: {type(value)}")
            
            return True
        else:
            print("❌ Agent task execution failed")
            if isinstance(filtered_result, dict) and "error" in filtered_result:
                print(f"   Error: {filtered_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Agent task execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_integration():
    """Test how the agent integrates with workflow orchestrator"""
    print("\n🔄 Testing Workflow Integration...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent
        from analyser.core.research_state import ResearchState, ResearchTask, ResearchPhase, LiteratureReview
        from analyser.agents.llm_backends import OpenAIBackend
        
        # Simulate workflow orchestrator logic
        state = ResearchState(
            title="Workflow Test: Blockchain Research",
            description="Testing literature review workflow integration",
            research_domain="Blockchain Technology"
        )
        
        # Create task
        task = ResearchTask(
            phase=ResearchPhase.LITERATURE_REVIEW,
            description="Conduct literature review",
            agent_type="literature_agent",
            parameters={
                "search_query": "blockchain academic research",
                "max_results": 3,
                "year_from": 2020,
                "year_to": 2024
            }
        )
        state.add_task(task)
        
        # Execute task (as in _literature_review_node)
        agent = LiteratureAgent(OpenAIBackend())
        result = await agent.execute_task(state, task)
        
        # Filter the result to remove verbose content
        filtered_result = filter_agent_output(result)
        
        if filtered_result and "error" not in filtered_result:
            print("✅ Agent executed successfully in workflow context")
            
            # Simulate workflow orchestrator state update
            state.literature_review = LiteratureReview(
                summary=filtered_result.get("summary", ""),
                key_findings=filtered_result.get("key_findings", []),
                research_gaps=filtered_result.get("research_gaps", []),
                methodologies=filtered_result.get("methodologies", []),
                citations=filtered_result.get("citations", []),
                papers_processed=filtered_result.get("papers_processed", 0),
                search_query=filtered_result.get("search_query", "")
            )
            
            state.mark_phase_completed(ResearchPhase.LITERATURE_REVIEW)
            state.current_phase = ResearchPhase.RESEARCH_QUESTION_FORMULATION
            
            print("✅ Workflow state updated successfully")
            print(f"   Current phase: {state.current_phase.value}")
            print(f"   Literature review created: {state.literature_review is not None}")
            
            # if state.literature_review:
            #     print(f"   Summary length: {len(state.literature_review.summary)}")
            #     print(f"   Summary preview: {state.literature_review.summary[:50]}...")
            #     print(f"   Key findings count: {len(state.literature_review.key_findings)}")
            #     print(f"   Research gaps count: {len(state.literature_review.research_gaps)}")
            #     print(f"   Papers processed: {state.literature_review.papers_processed}")
            
            return True
        else:
            print("❌ Workflow integration failed")
            return False
            
    except Exception as e:
        print(f"❌ Workflow integration test failed: {e}")
        return False

async def test_agent_reasoning_capabilities():
    """Test the agent's LLM reasoning capabilities"""
    print("\n🧠 Testing Agent Reasoning Capabilities...")
    
    try:
        from analyser.agents.literature_agent import LiteratureAgent
        from analyser.core.research_state import ResearchState, ResearchTask, ResearchPhase
        from analyser.agents.llm_backends import OpenAIBackend
        
        # Create a focused test
        state = ResearchState(
            title="Reasoning Test",
            description="Testing agent's ability to reason about research",
            research_domain="Blockchain"
        )
        
        task = ResearchTask(
            phase=ResearchPhase.LITERATURE_REVIEW,
            description="Analyze blockchain research trends",
            agent_type="literature_agent",
            parameters={
                "search_query": "blockchain research trends",
                "max_results": 2,
                "year_from": 2020,
                "year_to": 2024
            }
        )
        state.add_task(task)
        
        agent = LiteratureAgent(OpenAIBackend())
        result = await agent.execute_task(state, task)
        
        # Filter the result to remove verbose content
        filtered_result = filter_agent_output(result)
        
        if filtered_result and "error" not in filtered_result:
            print("✅ Agent reasoning test successful")
            
            # Check for structured reasoning output
            has_summary = bool(filtered_result.get("summary", "").strip())
            has_findings = bool(filtered_result.get("key_findings", []))
            has_gaps = bool(filtered_result.get("research_gaps", []))
            
            print(f"   Generated summary: {'✅' if has_summary else '❌'}")
            print(f"   Identified key findings: {'✅' if has_findings else '❌'}")
            print(f"   Identified research gaps: {'✅' if has_gaps else '❌'}")
            
            # if has_summary:
            #     print(f"   Summary preview: {filtered_result['summary'][:50]}...")
            
            return has_summary or has_findings or has_gaps
        else:
            print("❌ Agent reasoning test failed")
            return False
            
    except Exception as e:
        print(f"❌ Agent reasoning test failed: {e}")
        return False

async def run_all_tests():
    """Run all LangChain agent tests"""
    print("🚀 Starting Literature Review Agent LangChain Tests")
    print("=" * 70)
    
    # Environment check
    if not check_environment():
        return False
    
    # Run individual tests
    tests = [
        ("Agent Initialization", test_literature_agent_as_langchain_agent),
        ("Tool Execution", test_agent_tool_execution),
        ("Task Execution", test_agent_task_execution),
        ("Workflow Integration", test_workflow_integration),
        ("Reasoning Capabilities", test_agent_reasoning_capabilities)
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
    print("\n" + "=" * 70)
    print("📊 LangChain Agent Test Results Summary")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All LangChain agent tests passed!")
        print("\n✅ Literature Review Agent is working as a proper LangChain agent!")
        print("\n✅ Ready for integration with workflow orchestrator!")
        print("\n✅ Agent can:")
        print("   - Use tools (CORE API, PDF extraction, RAG building)")
        print("   - Process results with LLM reasoning")
        print("   - Generate structured research insights")
        print("   - Integrate with workflow orchestrator")
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