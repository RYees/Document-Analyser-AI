#!/usr/bin/env python3
"""
End-to-End Test script for Theme Refiner Agent
Tests the pipeline: Retrieval → Initial Coding → Thematic Grouping → Theme Refinement
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path to import the agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retriever_agent import RetrieverAgent
from initial_coding_agent import InitialCodingAgent
from thematic_grouping_agent import ThematicGroupingAgent
from theme_refiner_agent import ThemeRefinerAgent

async def test_full_pipeline():
    """Test the complete pipeline: Retrieval → Initial Coding → Thematic Grouping → Theme Refinement"""
    
    print("🚀 ===== Testing Full Pipeline: Retrieval → Initial Coding → Thematic Grouping → Theme Refinement =====")
    print(f"📅 Test started at: {datetime.now()}")
    
    research_domain = "Blockchain and Web3 Governance"
    search_query = "blockchain governance transparency mechanisms"
    
    try:
        # Step 1: Retrieve existing documents from vector store
        print(f"\n🔍 Step 1: Retrieving existing documents...")
        print(f"   Query: '{search_query}'")
        print(f"   Domain: {research_domain}")
        
        retriever = RetrieverAgent(collection_name="ResearchPaper", research_domain=research_domain)
        documents = await retriever.run(search_query, top_k=5)
        
        if not documents or len(documents) == 0:
            print("   ❌ No documents found in vector store")
            print("   💡 Run data extraction first to populate the vector store")
            return False
        
        print(f"   ✅ Retrieved {len(documents)} existing documents from vector store")
        
        # Step 2: Initial Coding
        print(f"\n🎯 Step 2: Initial Coding...")
        print("   ⚠️  This will make an LLM API call - ensure you have valid API keys!")
        
        initial_coder = InitialCodingAgent()
        coding_result = await initial_coder.run(documents, research_domain)
        
        if "error" in coding_result:
            print(f"   ❌ Initial coding failed: {coding_result['error']}")
            return False
        
        print("   ✅ Initial coding completed successfully!")
        
        # Display coding results
        summary = coding_result.get("coding_summary", {})
        print(f"   📊 Coding Summary:")
        print(f"      Total units coded: {summary.get('total_units_coded', 0)}")
        print(f"      Unique codes generated: {summary.get('unique_codes_generated', 0)}")
        print(f"      Average confidence: {summary.get('average_confidence', 0):.2f}")
        
        # Step 3: Thematic Grouping
        print(f"\n🎨 Step 3: Thematic Grouping...")
        print("   ⚠️  This will make another LLM API call for thematic analysis!")
        
        thematic_grouper = ThematicGroupingAgent()
        coded_units = coding_result.get("coded_units", [])
        
        if not coded_units:
            print("   ❌ No coded units available for thematic grouping")
            return False
        
        thematic_result = await thematic_grouper.run(coded_units, research_domain)
        
        if "error" in thematic_result:
            print(f"   ❌ Thematic grouping failed: {thematic_result['error']}")
            return False
        
        print("   ✅ Thematic grouping completed successfully!")
        
        # Display thematic results
        thematic_summary = thematic_result.get("thematic_summary", {})
        print(f"   📊 Thematic Analysis Summary:")
        print(f"      Total themes generated: {thematic_summary.get('total_themes_generated', 0)}")
        print(f"      Total codes analyzed: {thematic_summary.get('total_codes_analyzed', 0)}")
        print(f"      Average codes per theme: {thematic_summary.get('average_codes_per_theme', 0):.1f}")
        
        # Step 4: Theme Refinement
        print(f"\n✨ Step 4: Theme Refinement...")
        print("   ⚠️  This will make another LLM API call for theme refinement!")
        
        theme_refiner = ThemeRefinerAgent()
        themes = thematic_result.get("themes", [])
       
        if not themes:
            print("   ❌ No themes available for refinement")
            return False
        
        refinement_result = await theme_refiner.run(themes, research_domain)
        print("Theme Refiner Agent: themes =================================")
        print(refinement_result)
        
        if "error" in refinement_result:
            print(f"   ❌ Theme refinement failed: {refinement_result['error']}")
            return False
        
        print("   ✅ Theme refinement completed successfully!")
        
        # Display refinement results
        refinement_summary = refinement_result.get("refinement_summary", {})
        print(f"\n📊 Theme Refinement Summary:")
        print(f"   Total themes refined: {refinement_summary.get('total_themes_refined', 0)}")
        print(f"   Total academic quotes: {refinement_summary.get('total_academic_quotes', 0)}")
        print(f"   Total key concepts: {refinement_summary.get('total_key_concepts', 0)}")
        print(f"   Average quotes per theme: {refinement_summary.get('average_quotes_per_theme', 0):.1f}")
        print(f"   Themes with framework: {refinement_summary.get('themes_with_framework', 0)}")
        print(f"   Themes with implications: {refinement_summary.get('themes_with_implications', 0)}")
        
        # Show refined themes
        refined_themes = refinement_result.get("refined_themes", [])
        if refined_themes:
            print(f"\n✨ Refined Themes:")
            for i, theme in enumerate(refined_themes, 1):
                print(f"   Theme {i}: {theme['refined_name']}")
                print(f"      Original: {theme['original_name']}")
                print(f"      Definition: {theme['precise_definition'][:100]}...")
                print(f"      Scope: {theme['scope_boundaries'][:100]}...")
                print(f"      Quotes: {len(theme['academic_quotes'])} academic quotes")
                print(f"      Concepts: {len(theme['key_concepts'])} key concepts")
                if theme['theoretical_framework']:
                    print(f"      Framework: {theme['theoretical_framework'][:100]}...")
                if theme['research_implications']:
                    print(f"      Implications: {theme['research_implications'][:100]}...")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_theme_refinement_only():
    """Test just the theme refinement with sample themes"""
    
    print("\n✨ ===== Testing Theme Refinement Only =====")
    
    # Sample themes from previous Thematic Grouping Agent run
    sample_themes = [
        {
            "theme_name": "Transparency and Security Applications of Blockchain",
            "description": "This theme explores how blockchain technology is leveraged to enhance transparency and security across different sectors.",
            "codes": [
                {"name": "Transparency in genomic", "definition": "Transparency in blockchain governance", "confidence": 0.8, "category": "primary"},
                {"name": "Blockchain for transparency", "definition": "Blockchain for transparency and security", "confidence": 0.8, "category": "primary"},
                {"name": "Enhancing transparency in environmental agreements", "definition": "Enhancing transparency through blockchain", "confidence": 0.8, "category": "primary"}
            ],
            "justification": "These codes are grouped together because they all focus on the application of blockchain technology to enhance transparency and security in various domains.",
            "cross_cutting_ideas": ["Blockchain as a cross-sectoral innovator"],
            "academic_reasoning": "The grouping reflects the broader application of blockchain principles across different sectors."
        },
        {
            "theme_name": "Blockchain-Enhanced Governance Models",
            "description": "This theme focuses on governance frameworks and models enhanced by blockchain technology.",
            "codes": [
                {"name": "Governance models in blockchain", "definition": "Governance models in blockchain", "confidence": 0.8, "category": "primary"},
                {"name": "Blockchain in carbon market governance", "definition": "Blockchain in carbon market governance", "confidence": 0.8, "category": "primary"}
            ],
            "justification": "These codes are grouped together because they focus on governance structures and models that are enhanced or enabled by blockchain technology.",
            "cross_cutting_ideas": ["Governance innovation through blockchain"],
            "academic_reasoning": "The grouping emphasizes the role of blockchain in redefining governance approaches."
        }
    ]
    
    research_domain = "Blockchain and Web3 Governance"
    
    try:
        theme_refiner = ThemeRefinerAgent()
        result = await theme_refiner.run(sample_themes, research_domain)
        
        if "error" in result:
            print(f"❌ Theme refinement failed: {result['error']}")
            return False
        
        print(f"✅ Theme refinement completed successfully!")
        print(f"📊 Refined {result.get('refinement_summary', {}).get('total_themes_refined', 0)} themes")
        
        # Show the refined themes
        refined_themes = result.get("refined_themes", [])
        if refined_themes:
            print(f"\n✨ FULL REFINED THEMES:")
            for i, theme in enumerate(refined_themes, 1):
                print(f"\n{'='*80}")
                print(f"THEME {i}: {theme['refined_name']}")
                print(f"{'='*80}")
                print(f"Original Name: {theme['original_name']}")
                print(f"\n📖 PRECISE DEFINITION:")
                print(f"{theme['precise_definition']}")
                print(f"\n🎯 SCOPE BOUNDARIES:")
                print(f"{theme['scope_boundaries']}")
                print(f"\n📚 ACADEMIC QUOTES ({len(theme['academic_quotes'])} quotes):")
                for j, quote_data in enumerate(theme['academic_quotes'], 1):
                    print(f"   Quote {j}: \"{quote_data.get('quote', 'No quote')}\"")
                    print(f"   Citation: {quote_data.get('citation', 'No citation')}")
                print(f"\n🔑 KEY CONCEPTS ({len(theme['key_concepts'])} concepts):")
                for concept in theme['key_concepts']:
                    print(f"   • {concept}")
                if theme['theoretical_framework']:
                    print(f"\n🏗️  THEORETICAL FRAMEWORK:")
                    print(f"{theme['theoretical_framework']}")
                if theme['research_implications']:
                    print(f"\n🔬 RESEARCH IMPLICATIONS:")
                    print(f"{theme['research_implications']}")
                print(f"\n{'='*80}")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme refinement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function with multiple test options."""
    print("🚀 Starting Theme Refiner Agent End-to-End Tests")
    print("=" * 60)
    
    # Test options
    test_mode = "refinement_only"  # Options: "full", "refinement_only"
    
    if test_mode == "full":
        success = await test_full_pipeline()
    elif test_mode == "refinement_only":
        success = await test_theme_refinement_only()
    else:
        print("❌ Invalid test mode")
        return
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("⚠️  Some tests failed - check the output above for details")
    
    print(f"📅 Test completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main()) 