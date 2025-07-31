#!/usr/bin/env python3
"""
Test script for the new retry system.
"""

import asyncio
import json
import sys
import os

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.services.agent_retry_service import AgentRetryService

async def test_retry_service():
    """Test the retry service functionality."""
    
    print("🧪 Testing Agent Retry Service")
    print("=" * 50)
    
    # Initialize retry service
    retry_service = AgentRetryService()
    
    # Test data for literature review retry
    test_data = {
        "agent_type": "literature_review",
        "original_input": {
            "documents": [
                {
                    "title": "Blockchain Transparency Study",
                    "authors": ["Smith, J."],
                    "extracted_content": "Blockchain technology provides transparency through its immutable ledger system...",
                    "year": 2024
                }
            ],
            "research_domain": "Blockchain Technology"
        },
        "enhanced_context": "Focus on transparency mechanisms in blockchain protocol layers. Include detailed analysis of consensus mechanisms and their transparency implications. Provide specific examples and case studies.",
        "user_context": "I need more detailed analysis of the technical aspects of blockchain transparency."
    }
    
    print(f"📋 Test Parameters:")
    print(f"   Agent Type: {test_data['agent_type']}")
    print(f"   Enhanced Context: {test_data['enhanced_context'][:100]}...")
    print(f"   User Context: {test_data['user_context']}")
    print(f"   Documents: {len(test_data['original_input']['documents'])}")
    
    try:
        # Test the retry service
        result = await retry_service.retry_agent(
            agent_type=test_data["agent_type"],
            original_input=test_data["original_input"],
            enhanced_context=test_data["enhanced_context"],
            user_context=test_data["user_context"]
        )
        
        print(f"\n✅ Retry Service Test Successful!")
        print(f"📊 Result Type: {type(result)}")
        if isinstance(result, dict):
            print(f"📊 Result Keys: {list(result.keys())}")
            print(f"📊 Success: {result.get('success', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Retry Service Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_retry_service())
    sys.exit(0 if success else 1) 