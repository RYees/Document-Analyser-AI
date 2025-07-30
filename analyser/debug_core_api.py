#!/usr/bin/env python3
"""
Debug script to show exactly what data is sent to CORE API
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def debug_core_api_call():
    """Show exactly what data is sent to CORE API"""
    print("🔍 Debugging CORE API Call")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("CORE_API_KEY")
    if not api_key:
        print("❌ No CORE_API_KEY found in environment")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test parameters (same as in the test)
    query = "blockchain technology academic research"
    max_results = 5
    year_from = 2020
    year_to = 2024
    
    print(f"\n📤 Sending request to CORE API:")
    print(f"   URL: https://api.core.ac.uk/v3/search/works")
    print(f"   Method: POST")
    print(f"   Headers:")
    print(f"     Authorization: Bearer {api_key[:10]}...{api_key[-4:]}")
    print(f"     Content-Type: application/json")
    
    print(f"\n📋 Request Payload (JSON):")
    payload = {
        "q": query,
        "limit": max_results,
        "scroll": False,
        "year_from": year_from,
        "year_to": year_to,
        "fields": ["title", "authors", "abstract", "year", "doi", "downloadUrl", "citations", "language"]
    }
    
    print(json.dumps(payload, indent=2))
    
    print(f"\n📝 Request Details:")
    print(f"   Query: '{query}'")
    print(f"   Max Results: {max_results}")
    print(f"   Year Range: {year_from} - {year_to}")
    print(f"   Fields Requested: {payload['fields']}")
    
    # Make the actual API call
    import aiohttp
    
    url = "https://api.core.ac.uk/v3/search/works"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"\n📥 Response Status: {response.status}")
                print(f"   Response Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"\n✅ Response Data:")
                    print(json.dumps(data, indent=2))
                    
                    results = data.get("results", [])
                    print(f"\n📊 Summary:")
                    print(f"   Total Results: {len(results)}")
                    print(f"   Total Found: {data.get('totalHits', 0)}")
                    
                    if results:
                        print(f"\n📄 First Result:")
                        first_result = results[0]
                        print(f"   Title: {first_result.get('title', 'No title')}")
                        print(f"   Authors: {[author.get('name', '') for author in first_result.get('authors', [])]}")
                        print(f"   Year: {first_result.get('year', 'Unknown')}")
                        print(f"   DOI: {first_result.get('doi', 'No DOI')}")
                        # Use log_abstract if available, otherwise limit the full abstract
                        abstract = first_result.get('abstract', 'No abstract')
                        log_abstract = abstract[:200] + "..." if len(abstract) > 200 else abstract
                        print(f"   Abstract: {log_abstract}")
                    else:
                        print(f"\n⚠️  No results found for query: '{query}'")
                        print(f"   This might be due to:")
                        print(f"   - Query too specific")
                        print(f"   - No papers in the specified year range")
                        print(f"   - API key limitations")
                        
                else:
                    error_text = await response.text()
                    print(f"\n❌ API Error:")
                    print(f"   Status: {response.status}")
                    print(f"   Error: {error_text}")
                    
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_core_api_call()) 