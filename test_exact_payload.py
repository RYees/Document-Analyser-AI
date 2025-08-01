#!/usr/bin/env python3
"""
Test script to test the exact payload provided by the user.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1/data"

async def test_exact_payload():
    """Test the exact payload provided by the user."""
    
    print("🧪 Testing Exact User Payload")
    print("=" * 60)
    
    # The exact payload provided by the user
    payload = {
        "collection_name": "ResearchPaper",
        "document_ids": [
            "doc1",
            "doc2"
        ],
        "documents": [
            {
                "authors": "Author Name",
                "content": "Document content...",
                "title": "Sample Document",
                "year": 2024
            }
        ],
        "max_results": 10,
        "query": "crypto",
        "research_domain": "web3"
    }
    
    print(f"📤 Sending payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    async with aiohttp.ClientSession() as session:
        try:
            print("🚀 Making request to /api/v1/data/retrieve...")
            async with session.post(f"{BASE_URL}/retrieve", json=payload) as response:
                result = await response.json()
                print(f"✅ Status: {response.status}")
                print(f"⏱️  Response time: {response.headers.get('X-Process-Time', 'Unknown')}")
                
                if result.get('success'):
                    docs = result.get('data', {}).get('documents', [])
                    print(f"📄 Found {len(docs)} documents")
                    
                    if docs:
                        print(f"📋 First document:")
                        print(f"   Title: {docs[0].get('title', 'No title')}")
                        print(f"   Domain: {docs[0].get('research_domain', 'Unknown')}")
                        print(f"   Year: {docs[0].get('year', 'Unknown')}")
                    else:
                        print("📭 No documents found")
                        
                    # Show quality metrics if available
                    quality_metrics = result.get('data', {}).get('quality_metrics', {})
                    if quality_metrics:
                        print(f"📊 Quality metrics:")
                        print(f"   Overall score: {quality_metrics.get('overall_score', 0.0):.2f}")
                        print(f"   Certainty score: {quality_metrics.get('certainty_score', 0.0):.2f}")
                        print(f"   Recency score: {quality_metrics.get('recency_score', 0.0):.2f}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_exact_payload()) 