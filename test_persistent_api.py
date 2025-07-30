#!/usr/bin/env python3
"""
Test script for API endpoints with persistent storage.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_pipeline_endpoints():
    """Test pipeline endpoints with persistent storage."""
    
    print("🧪 Testing API Endpoints with Persistent Storage...")
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Create a pipeline
        print("\n1️⃣ Creating pipeline...")
        create_data = {
            "query": "blockchain transparency governance",
            "research_domain": "Blockchain",
            "max_results": 5,
            "quality_threshold": 0.6
        }
        
        async with session.post(f"{BASE_URL}/pipelines", json=create_data) as response:
            if response.status == 200:
                result = await response.json()
                pipeline_id = result.get("pipeline_id")
                print(f"✅ Pipeline created: {pipeline_id}")
                print(f"   Status: {result.get('status')}")
                print(f"   Current step: {result.get('current_step')}/{result.get('total_steps')}")
            else:
                print(f"❌ Failed to create pipeline: {response.status}")
                return
        
        # Test 2: Check pipeline status
        print(f"\n2️⃣ Checking pipeline status...")
        async with session.get(f"{BASE_URL}/pipelines/{pipeline_id}/status") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Pipeline status: {result.get('status')}")
                print(f"   Current step: {result.get('current_step')}/{result.get('total_steps')}")
            else:
                print(f"❌ Failed to get status: {response.status}")
        
        # Test 3: Check pipeline progress
        print(f"\n3️⃣ Checking pipeline progress...")
        async with session.get(f"{BASE_URL}/pipelines/{pipeline_id}/progress") as response:
            if response.status == 200:
                result = await response.json()
                if result.get("success"):
                    progress = result["data"]["progress"]
                    print(f"✅ Progress: {progress['percentage']:.1f}%")
                    print(f"   Step {progress['current_step']}/{progress['total_steps']}")
                else:
                    print(f"❌ Progress check failed: {result.get('error')}")
            else:
                print(f"❌ Failed to get progress: {response.status}")
        
        # Test 4: List pipelines
        print(f"\n4️⃣ Listing pipelines...")
        async with session.get(f"{BASE_URL}/pipelines") as response:
            if response.status == 200:
                result = await response.json()
                if result.get("success"):
                    pipelines = result["data"]["pipelines"]
                    print(f"✅ Found {len(pipelines)} pipelines")
                    for pipeline in pipelines:
                        print(f"   - {pipeline['pipeline_id'][:8]}... ({pipeline['status']})")
                else:
                    print(f"❌ List failed: {result.get('error')}")
            else:
                print(f"❌ Failed to list pipelines: {response.status}")
        
        # Test 5: Wait a bit and check if pipeline is still accessible
        print(f"\n5️⃣ Testing persistence (waiting 5 seconds)...")
        await asyncio.sleep(5)
        
        async with session.get(f"{BASE_URL}/pipelines/{pipeline_id}/status") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Pipeline still accessible after wait")
                print(f"   Status: {result.get('status')}")
            else:
                print(f"❌ Pipeline not accessible after wait: {response.status}")
        
        # Test 6: Try to get results (might not be ready yet)
        print(f"\n6️⃣ Checking for results...")
        async with session.get(f"{BASE_URL}/pipelines/{pipeline_id}/results") as response:
            if response.status == 200:
                result = await response.json()
                if result.get("success"):
                    print(f"✅ Results available!")
                    print(f"   Pipeline status: {result['data']['pipeline_status']}")
                else:
                    print(f"ℹ️  Results not ready yet: {result.get('error')}")
            else:
                print(f"❌ Failed to get results: {response.status}")
        
        print(f"\n🎉 API testing completed!")
        print(f"Pipeline ID for further testing: {pipeline_id}")

async def test_agent_endpoints():
    """Test individual agent endpoints."""
    
    print("\n🧪 Testing Individual Agent Endpoints...")
    
    async with aiohttp.ClientSession() as session:
        
        # Test Data Retrieval Agent
        print("\n1️⃣ Testing Data Retrieval Agent...")
        data_request = {
            "query": "blockchain transparency",
            "research_domain": "Blockchain",
            "max_results": 3
        }
        
        async with session.post(f"{BASE_URL}/agents/data-retrieval", json=data_request) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("success"):
                    documents = result["data"]["documents"]
                    print(f"✅ Retrieved {len(documents)} documents")
                    return documents
                else:
                    print(f"❌ Data retrieval failed: {result.get('error')}")
                    return []
            else:
                print(f"❌ Data retrieval request failed: {response.status}")
                return []
        
        # Test Literature Review Agent
        print("\n2️⃣ Testing Literature Review Agent...")
        if documents:
            literature_request = {
                "documents": documents,
                "research_domain": "Blockchain"
            }
            
            async with session.post(f"{BASE_URL}/agents/literature-review", json=literature_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        print(f"✅ Literature review completed")
                        print(f"   Summary length: {len(result['data'].get('summary', ''))}")
                    else:
                        print(f"❌ Literature review failed: {result.get('error')}")
                else:
                    print(f"❌ Literature review request failed: {response.status}")

async def main():
    """Run all tests."""
    print("🚀 Starting API Tests with Persistent Storage...")
    
    try:
        # Test pipeline endpoints
        await test_pipeline_endpoints()
        
        # Test individual agent endpoints
        await test_agent_endpoints()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 