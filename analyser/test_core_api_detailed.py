#!/usr/bin/env python3
"""
Detailed test script to show exactly what data is sent to CORE API and what it returns
"""

import asyncio
import os
import json
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_core_api_detailed():
    """Test CORE API with detailed logging of request and response"""
    print("🔍 DETAILED CORE API TEST")
    print("=" * 80)
    
    # Get API key
    api_key = "ZS01E3YUymOHq9RCcn5FiPb6lAjpN8kK"
    # os.getenv("CORE_API_KEY")
    if not api_key:
        print("❌ No CORE_API_KEY found in environment")
        print("Please set CORE_API_KEY in your .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test parameters
    query = "blockchain technology academic research"
    max_results = 3
    year_from = 2020
    year_to = 2024
    
    print(f"\n📋 TEST PARAMETERS:")
    print(f"   Query: '{query}'")
    print(f"   Max Results: {max_results}")
    print(f"   Year Range: {year_from} - {year_to}")
    
    # Prepare the request
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
    
    print(f"\n📤 REQUEST DETAILS:")
    print(f"   URL: {url}")
    print(f"   Method: POST")
    print(f"   Headers:")
    for key, value in headers.items():
        if key == "Authorization":
            print(f"     {key}: Bearer {api_key[:10]}...{api_key[-4:]}")
        else:
            print(f"     {key}: {value}")
    
    print(f"\n📦 REQUEST PAYLOAD (JSON):")
    print(json.dumps(payload, indent=2))
    
    print(f"\n🚀 SENDING REQUEST...")
    start_time = datetime.now()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print(f"\n📥 RESPONSE RECEIVED:")
                print(f"   Status Code: {response.status}")
                print(f"   Response Time: {duration:.2f} seconds")
                print(f"   Response Headers:")
                for key, value in response.headers.items():
                    print(f"     {key}: {value}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"\n✅ SUCCESSFUL RESPONSE:")
                    print(f"   Response Size: {len(str(data))} characters")
                    
                    # Show the full response structure
                    print(f"\n📄 FULL RESPONSE STRUCTURE:")
                    print(json.dumps(data, indent=2))
                    
                    # Extract and display results
                    results = data.get("results", [])
                    total_hits = data.get("totalHits", 0)
                    search_id = data.get("searchId", "N/A")
                    
                    print(f"\n📊 RESPONSE SUMMARY:")
                    print(f"   Total Hits: {total_hits}")
                    print(f"   Results Returned: {len(results)}")
                    print(f"   Search ID: {search_id}")
                    
                    if results:
                        print(f"\n📚 PAPERS FOUND:")
                        for i, paper in enumerate(results, 1):
                            print(f"\n   {i}. PAPER DETAILS:")
                            print(f"      Title: {paper.get('title', 'No title')}")
                            print(f"      Authors: {[author.get('name', '') for author in paper.get('authors', [])]}")
                            print(f"      Year: {paper.get('yearPublished', 'Unknown')}")
                            print(f"      DOI: {paper.get('doi', 'No DOI')}")
                            print(f"      Language: {paper.get('language', {}).get('name', 'Unknown')}")
                            print(f"      Citations: {paper.get('citationCount', 0)}")
                            print(f"      Download URL: {paper.get('downloadUrl', 'No download URL')}")
                            # Use log_abstract if available, otherwise limit the full abstract
                            abstract = paper.get('abstract', 'No abstract')
                            log_abstract = abstract[:200] + "..." if len(abstract) > 200 else abstract
                            print(f"      Abstract: {log_abstract}")
                            
                            # Show identifiers
                            identifiers = paper.get('identifiers', [])
                            if identifiers:
                                print(f"      Identifiers:")
                                for ident in identifiers:
                                    print(f"        {ident.get('type', 'Unknown')}: {ident.get('identifier', 'N/A')}")
                    
                    else:
                        print(f"\n⚠️  NO PAPERS FOUND")
                        print(f"   This might be due to:")
                        print(f"   - Query too specific")
                        print(f"   - No papers in the specified year range")
                        print(f"   - API key limitations")
                        
                else:
                    error_text = await response.text()
                    print(f"\n❌ API ERROR:")
                    print(f"   Status Code: {response.status}")
                    print(f"   Error Response: {error_text}")
                    
                    if response.status == 401:
                        print(f"   This is likely an authentication error - check your API key")
                    elif response.status == 429:
                        print(f"   This is a rate limit error - try again later")
                    elif response.status == 400:
                        print(f"   This is a bad request error - check your payload")
                        
    except Exception as e:
        print(f"\n❌ REQUEST FAILED:")
        print(f"   Error: {str(e)}")
        print(f"   Error Type: {type(e).__name__}")

async def test_literature_agent_core_api():
    """Test the literature agent's CORE API integration"""
    print(f"\n\n🤖 TESTING LITERATURE AGENT CORE API INTEGRATION")
    print("=" * 80)
    
    try:
        from analyser.agents.literature_agent import search_core_api
        
        print("✅ Successfully imported search_core_api function")
        
        # Test the function
        query = "blockchain technology academic research"
        max_results = 2
        year_from = 2020
        year_to = 2024
        
        print(f"\n📋 CALLING search_core_api:")
        print(f"   Query: '{query}'")
        print(f"   Max Results: {max_results}")
        print(f"   Year Range: {year_from} - {year_to}")
        
        result = await search_core_api(query, max_results, year_from, year_to)
        
        print(f"\n📥 FUNCTION RESULT:")
        print(json.dumps(result, indent=2))
        
        if result.get("status") == "success":
            papers = result.get("results", [])
            print(f"\n✅ SUCCESS: Found {len(papers)} papers")
            
            for i, paper in enumerate(papers, 1):
                print(f"\n   {i}. PAPER:")
                print(f"      Title: {paper.get('title', 'No title')}")
                print(f"      Authors: {[author.get('name', '') for author in paper.get('authors', [])]}")
                print(f"      Year: {paper.get('yearPublished', 'Unknown')}")
                print(f"      DOI: {paper.get('doi', 'No DOI')}")
        else:
            print(f"\n❌ FUNCTION FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ LITERATURE AGENT TEST FAILED: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 STARTING DETAILED CORE API TESTS")
    print("=" * 80)
    
    # Test 1: Direct API call
    await test_core_api_detailed()
    
    # Test 2: Literature agent integration
    await test_literature_agent_core_api()
    
    print(f"\n\n🏁 TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 