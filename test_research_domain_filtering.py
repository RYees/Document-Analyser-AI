#!/usr/bin/env python3
"""
Test script to verify research domain filtering in the retrieve endpoint.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1/data"

async def test_research_domain_filtering():
    """Test that research domain filtering works correctly."""
    
    print("🧪 Testing Research Domain Filtering")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Search for "beyonce" with "Content" domain
        print("\n1️⃣ Testing 'beyonce' + 'Content' domain...")
        try:
            search_data = {
                "query": "beyonce",
                "research_domain": "Content",
                "max_results": 5
            }
            async with session.post(f"{BASE_URL}/retrieve", json=search_data) as response:
                result = await response.json()
                print(f"✅ Status: {response.status}")
                if result.get('success'):
                    docs = result.get('data', {}).get('documents', [])
                    print(f"   Found {len(docs)} documents")
                    if docs:
                        print(f"   First document domain: {docs[0].get('research_domain', 'Unknown')}")
                        print(f"   First document title: {docs[0].get('title', 'No title')[:50]}...")
                    else:
                        print("   No documents found (expected if no Content domain docs)")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        # Test 2: Search for "beyonce" with "General" domain
        print("\n2️⃣ Testing 'beyonce' + 'General' domain...")
        try:
            search_data = {
                "query": "beyonce",
                "research_domain": "General",
                "max_results": 5
            }
            async with session.post(f"{BASE_URL}/retrieve", json=search_data) as response:
                result = await response.json()
                print(f"✅ Status: {response.status}")
                if result.get('success'):
                    docs = result.get('data', {}).get('documents', [])
                    print(f"   Found {len(docs)} documents")
                    if docs:
                        print(f"   First document domain: {docs[0].get('research_domain', 'Unknown')}")
                        print(f"   First document title: {docs[0].get('title', 'No title')[:50]}...")
                    else:
                        print("   No documents found")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        # Test 3: Search for "blockchain" with "Crypto" domain
        print("\n3️⃣ Testing 'blockchain' + 'Crypto' domain...")
        try:
            search_data = {
                "query": "blockchain",
                "research_domain": "Crypto",
                "max_results": 5
            }
            async with session.post(f"{BASE_URL}/retrieve", json=search_data) as response:
                result = await response.json()
                print(f"✅ Status: {response.status}")
                if result.get('success'):
                    docs = result.get('data', {}).get('documents', [])
                    print(f"   Found {len(docs)} documents")
                    if docs:
                        print(f"   First document domain: {docs[0].get('research_domain', 'Unknown')}")
                        print(f"   First document title: {docs[0].get('title', 'No title')[:50]}...")
                    else:
                        print("   No documents found")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        # Test 4: Search for "blockchain" with "Content" domain (should return fewer results)
        print("\n4️⃣ Testing 'blockchain' + 'Content' domain (should filter)...")
        try:
            search_data = {
                "query": "blockchain",
                "research_domain": "Content",
                "max_results": 5
            }
            async with session.post(f"{BASE_URL}/retrieve", json=search_data) as response:
                result = await response.json()
                print(f"✅ Status: {response.status}")
                if result.get('success'):
                    docs = result.get('data', {}).get('documents', [])
                    print(f"   Found {len(docs)} documents")
                    if docs:
                        print(f"   First document domain: {docs[0].get('research_domain', 'Unknown')}")
                        print(f"   First document title: {docs[0].get('title', 'No title')[:50]}...")
                    else:
                        print("   No documents found (expected if no Content domain docs)")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Research Domain Filtering Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_research_domain_filtering()) 