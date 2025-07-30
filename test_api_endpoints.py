#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Research Pipeline API
Tests all endpoints systematically and reports results.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# API Base URL
BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.results = []
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint and return results."""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    status = response.status
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    status = response.status
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    status = response.status
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    status = response.status
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
            
            success = status == expected_status
            result = {
                "method": method,
                "endpoint": endpoint,
                "status": status,
                "expected": expected_status,
                "success": success,
                "content": content if isinstance(content, dict) else str(content)[:200],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            result = {
                "method": method,
                "endpoint": endpoint,
                "status": "ERROR",
                "expected": expected_status,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        self.results.append(result)
        return result
    
    def print_results(self):
        """Print formatted test results."""
        print("\n" + "="*80)
        print("🧪 API ENDPOINT TESTING RESULTS")
        print("="*80)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get("success", False))
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}")
        print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\n" + "-"*80)
        print("DETAILED RESULTS:")
        print("-"*80)
        
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result.get("success", False) else "❌"
            print(f"{i:2d}. {status_icon} {result['method']} {result['endpoint']}")
            print(f"    Status: {result['status']} (Expected: {result['expected']})")
            
            if "error" in result:
                print(f"    Error: {result['error']}")
            elif "content" in result:
                if isinstance(result["content"], dict):
                    print(f"    Response: {json.dumps(result['content'], indent=2)[:200]}...")
                else:
                    print(f"    Response: {str(result['content'])[:200]}...")
            print()

async def run_comprehensive_tests():
    """Run comprehensive API endpoint tests."""
    
    async with APITester() as tester:
        print("🚀 Starting Comprehensive API Testing...")
        print(f"📍 Testing API at: {BASE_URL}")
        print(f"⏰ Started at: {datetime.now().isoformat()}")
        
        # Test 1: Health Check
        print("\n1️⃣ Testing Health Check...")
        await tester.test_endpoint("GET", "/health")
        
        # Test 2: Root Endpoint
        print("2️⃣ Testing Root Endpoint...")
        await tester.test_endpoint("GET", "/")
        
        # Test 3: OpenAPI Schema
        print("3️⃣ Testing OpenAPI Schema...")
        await tester.test_endpoint("GET", "/openapi.json")
        
        # Test 4: Pipeline Endpoints
        print("4️⃣ Testing Pipeline Endpoints...")
        
        # Test pipeline creation
        pipeline_data = {
            "query": "transparency in blockchain technology",
            "research_domain": "Blockchain",
            "max_results": 10,
            "quality_threshold": 0.7,
            "pipeline_config": {
                "enable_supervisor": True,
                "auto_retry_failed_steps": True,
                "save_intermediate_results": True
            }
        }
        await tester.test_endpoint("POST", "/api/v1/pipelines/", pipeline_data, 201)
        
        # Test pipeline listing
        await tester.test_endpoint("GET", "/api/v1/pipelines/")
        
        # Test pipeline statistics
        await tester.test_endpoint("GET", "/api/v1/pipelines/statistics/overview")
        
        # Test 5: Agent Endpoints
        print("5️⃣ Testing Agent Endpoints...")
        
        # Test agent types
        await tester.test_endpoint("GET", "/api/v1/agents/types")
        
        # Test agent status
        await tester.test_endpoint("GET", "/api/v1/agents/status")
        
        # Test agent execution
        agent_data = {
            "agent_type": "literature_review",
            "documents": [
                {
                    "title": "Sample Paper",
                    "authors": ["Author 1", "Author 2"],
                    "year": 2023,
                    "abstract": "Sample abstract for testing",
                    "extracted_content": "Sample content for literature review testing."
                }
            ],
            "research_domain": "Blockchain"
        }
        await tester.test_endpoint("POST", "/api/v1/agents/execute", agent_data)
        
        # Test 6: Quality Control Endpoints
        print("6️⃣ Testing Quality Control Endpoints...")
        
        # Test quality assessment
        quality_data = {
            "agent_output": {
                "summary": "Sample literature review summary",
                "key_findings": ["Finding 1", "Finding 2"],
                "research_gaps": ["Gap 1"]
            },
            "agent_type": "literature_review",
            "research_domain": "Blockchain"
        }
        await tester.test_endpoint("POST", "/api/v1/quality/assess", quality_data)
        
        # Test quality history
        await tester.test_endpoint("GET", "/api/v1/quality/history")
        
        # Test 7: Data Management Endpoints
        print("7️⃣ Testing Data Management Endpoints...")
        
        # Test data retrieval
        data_request = {
            "query": "blockchain transparency",
            "research_domain": "Blockchain",
            "max_results": 5
        }
        await tester.test_endpoint("POST", "/api/v1/data/retrieve", data_request)
        
        # Test data statistics
        await tester.test_endpoint("GET", "/api/v1/data/statistics")
        
        # Test 8: Report Endpoints
        print("8️⃣ Testing Report Endpoints...")
        
        # Test report generation
        report_data = {
            "sections": {
                "literature_review": {
                    "summary": "Sample literature review",
                    "key_findings": ["Finding 1", "Finding 2"]
                },
                "initial_coding": {
                    "coding_summary": {
                        "total_units_coded": 5,
                        "unique_codes_generated": 3
                    }
                },
                "thematic_grouping": {
                    "thematic_summary": {
                        "total_themes_generated": 2
                    }
                },
                "theme_refinement": {
                    "refinement_summary": {
                        "total_themes_refined": 2
                    }
                }
            },
            "research_domain": "Blockchain"
        }
        await tester.test_endpoint("POST", "/api/v1/reports/generate", report_data)
        
        # Test report listing
        await tester.test_endpoint("GET", "/api/v1/reports/")
        
        # Test 9: Error Handling
        print("9️⃣ Testing Error Handling...")
        
        # Test invalid endpoint
        await tester.test_endpoint("GET", "/api/v1/invalid/endpoint", expected_status=404)
        
        # Test invalid data
        invalid_data = {"invalid": "data"}
        await tester.test_endpoint("POST", "/api/v1/pipelines/", invalid_data, 422)
        
        print("\n✅ All tests completed!")
        
        # Print results
        tester.print_results()

if __name__ == "__main__":
    print("🧪 Research Pipeline API - Comprehensive Testing")
    print("="*50)
    
    try:
        asyncio.run(run_comprehensive_tests())
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1) 