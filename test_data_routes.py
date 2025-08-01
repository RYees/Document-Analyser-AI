#!/usr/bin/env python3
"""
Test script for data routes to verify Weaviate integration.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1/data"

async def test_data_routes():
    """Test all data routes to ensure they work with Weaviate."""
    
    print("🧪 Testing Data Routes with Weaviate Integration")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health Check
        print("\n1️⃣ Testing Health Check...")
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                result = await response.json()
                print(f"✅ Health Check: {response.status}")
                print(f"   Status: {result.get('data', {}).get('status', 'unknown')}")
                print(f"   Weaviate Connection: {result.get('data', {}).get('weaviate_connection', 'unknown')}")
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
        
        # Test 2: List Collections
        print("\n2️⃣ Testing List Collections...")
        try:
            async with session.get(f"{BASE_URL}/collections") as response:
                result = await response.json()
                print(f"✅ List Collections: {response.status}")
                collections = result.get('data', {}).get('collections', [])
                print(f"   Found {len(collections)} collections:")
                for coll in collections:
                    print(f"     - {coll.get('name', 'Unknown')}: {coll.get('document_count', 0)} documents")
        except Exception as e:
            print(f"❌ List Collections Failed: {e}")
        
        # Test 3: Get Collection Info
        print("\n3️⃣ Testing Get Collection Info...")
        try:
            async with session.get(f"{BASE_URL}/collections/ResearchPaper") as response:
                result = await response.json()
                print(f"✅ Get Collection Info: {response.status}")
                if result.get('success'):
                    data = result.get('data', {})
                    print(f"   Collection: {data.get('name', 'Unknown')}")
                    print(f"   Documents: {data.get('document_count', 0)}")
                    print(f"   Research Domain: {data.get('research_domain', 'Unknown')}")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Get Collection Info Failed: {e}")
        
        # Test 4: Data Statistics
        print("\n4️⃣ Testing Data Statistics...")
        try:
            async with session.get(f"{BASE_URL}/statistics") as response:
                result = await response.json()
                print(f"✅ Data Statistics: {response.status}")
                if result.get('success'):
                    data = result.get('data', {})
                    vector_store = data.get('vector_store', {})
                    print(f"   Total Documents: {vector_store.get('total_documents', 0)}")
                    print(f"   Collection: {vector_store.get('collection_name', 'Unknown')}")
                    domains = vector_store.get('research_domain_distribution', {})
                    if domains:
                        print(f"   Research Domains: {domains}")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Data Statistics Failed: {e}")
        
        # Test 5: Similarity Search
        print("\n5️⃣ Testing Similarity Search...")
        try:
            search_data = {
                "query": "blockchain technology",
                "research_domain": "Crypto",
                "max_results": 5
            }
            async with session.post(f"{BASE_URL}/search/similar", json=search_data) as response:
                result = await response.json()
                print(f"✅ Similarity Search: {response.status}")
                if result.get('success'):
                    data = result.get('data', {})
                    docs = data.get('similar_documents', [])
                    print(f"   Found {len(docs)} similar documents")
                    if docs:
                        print(f"   First document: {docs[0].get('title', 'No title')[:50]}...")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Similarity Search Failed: {e}")
        
        # Test 6: Operation History
        print("\n6️⃣ Testing Operation History...")
        try:
            async with session.get(f"{BASE_URL}/operations/history?limit=5") as response:
                result = await response.json()
                print(f"✅ Operation History: {response.status}")
                if result.get('success'):
                    operations = result.get('data', [])
                    print(f"   Found {len(operations)} recent operations")
                    for op in operations[:3]:  # Show first 3
                        print(f"     - {op.get('operation', 'Unknown')}: {op.get('status', 'Unknown')}")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Operation History Failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Data Routes Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_data_routes()) 