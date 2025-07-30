#!/usr/bin/env python3
"""
Test to verify the unit ID parsing fix in InitialCodingAgent.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.agents.initial_coding_agent import InitialCodingAgent, MeaningUnit

def test_unit_id_parsing():
    """Test the unit ID parsing logic."""
    
    print("🧪 Testing Unit ID Parsing...")
    
    # Create test meaning units
    meaning_units = [
        MeaningUnit(
            content="Test content 1",
            source_paper="Test Paper 1",
            source_authors=["Test Author"],
            source_year=2024,
            unit_id="unit_0000"
        ),
        MeaningUnit(
            content="Test content 2", 
            source_paper="Test Paper 2",
            source_authors=["Test Author"],
            source_year=2024,
            unit_id="unit_0001"
        )
    ]
    
    # Create agent instance
    agent = InitialCodingAgent()
    
    # Test the problematic format from the logs
    test_response = """### Unit 1
**Unit ID:** unit_0000
**Primary Code:** Test Code
**Definition:** This is a test code definition

### Unit 2  
**Unit ID:** unit_0001
**Primary Code:** Another Code
**Definition:** Another test definition"""
    
    print(f"📝 Testing response format:")
    print(f"Response: {test_response}")
    
    try:
        # Test the parsing
        coded_units = agent._parse_coding_response(test_response, meaning_units)
        print(f"✅ Parsed {len(coded_units)} coded units")
        
        for unit in coded_units:
            print(f"   Unit ID: {unit.meaning_unit.unit_id}")
            print(f"   Codes: {len(unit.codes)}")
            
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Unit ID parsing test completed!")

if __name__ == "__main__":
    test_unit_id_parsing() 