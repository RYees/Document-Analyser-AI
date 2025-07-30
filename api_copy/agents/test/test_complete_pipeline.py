#!/usr/bin/env python3
"""
Complete Pipeline Test: Retrieval → Literature Review → Initial Coding → Thematic Grouping → Theme Refinement → Report Generation
Uses actual retrieved documents instead of sample data.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the path to import the agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retriever_agent import RetrieverAgent
from literature_review_agent import LiteratureReviewAgent
from initial_coding_agent import InitialCodingAgent
from thematic_grouping_agent import ThematicGroupingAgent
from theme_refiner_agent import ThemeRefinerAgent
from report_generator_agent import ReportGeneratorAgent
from supervisor_agent import SupervisorAgent

async def test_complete_pipeline():
    """Test the complete pipeline with actual retrieved documents"""
    
    print("🚀 ===== Testing Complete Pipeline with Real Documents =====")
    print(f"📅 Test started at: {datetime.now()}")
    
    research_domain = "Blockchain and Web3 Governance"
    search_query = "blockchain governance transparency mechanisms"
    
    # Store all agent outputs for final report generation
    all_sections: Dict[str, Any] = {
        "research_domain": research_domain
    }
    
    # Initialize Supervisor Agent for quality control
    supervisor = SupervisorAgent()
    print(f"🔍 Supervisor Agent initialized for quality control")
    
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
        
        # Step 2: Literature Review
        print(f"\n📚 Step 2: Literature Review...")
        print("   🔄 [2/6] Starting Literature Review Agent")
        print("   ⚠️  This will make an LLM API call!")
        
        literature_reviewer = LiteratureReviewAgent()
        literature_result = await literature_reviewer.run(documents, research_domain)
        
        if "error" in literature_result:
            print(f"   ❌ Literature review failed: {literature_result['error']}")
            return False
        
        all_sections["literature_review"] = literature_result
        print("   ✅ Literature review completed successfully!")
        
        # Supervisor Quality Check: Literature Review
        print(f"\n🔍 Supervisor Quality Check: Literature Review...")
        print("   ⚠️  This will make a supervisor LLM API call!")
        
        lit_quality = await supervisor.check_quality(
            agent_output=literature_result,
            agent_type="literature_review",
            research_domain=research_domain
        )
        
        print(f"   📊 Quality Assessment: {lit_quality.status} (confidence: {lit_quality.confidence:.2f})")
        print(f"   🎯 Quality Score: {lit_quality.quality_score:.2f}")
        
        if lit_quality.status == "HALT":
            print(f"   ❌ SUPERVISOR HALTED PIPELINE!")
            print(f"   🛑 Action: {lit_quality.action}")
            if lit_quality.feedback:
                print(f"   📝 Feedback: {lit_quality.feedback}")
            print(f"   🚫 Next agent (Initial Coding) will NOT proceed")
            return False
        elif lit_quality.status == "REVISE":
            print(f"   ⚠️  SUPERVISOR SUGGESTS REVISION")
            print(f"   🔄 Action: {lit_quality.action}")
            if lit_quality.feedback:
                print(f"   📝 Feedback: {lit_quality.feedback}")
            print(f"   ⏭️  Continuing to next agent (Initial Coding) with warnings")
        else:
            print(f"   ✅ SUPERVISOR APPROVED - PROCEEDING TO NEXT AGENT")
            print(f"   🎯 Quality Score: {lit_quality.quality_score:.2f}")
            print(f"   ➡️  Next agent (Initial Coding) will proceed")
        
        # Display literature review summary
        lit_summary = literature_result.get("summary", "")
        print(f"   📊 Literature Review Summary: {lit_summary[:100]}...")
        
        # Step 3: Initial Coding
        print(f"\n🎯 Step 3: Initial Coding...")
        print("   🔄 [3/6] Starting Initial Coding Agent")
        print("   ⚠️  This will make another LLM API call!")
        
        initial_coder = InitialCodingAgent()
        coding_result = await initial_coder.run(documents, research_domain)
        
        if "error" in coding_result:
            print(f"   ❌ Initial coding failed: {coding_result['error']}")
            return False
        
        all_sections["initial_coding"] = coding_result
        print("   ✅ Initial coding completed successfully!")
        
        # Supervisor Quality Check: Initial Coding
        print(f"\n🔍 Supervisor Quality Check: Initial Coding...")
        print("   ⚠️  This will make a supervisor LLM API call!")
        
        coding_quality = await supervisor.check_quality(
            agent_output=coding_result,
            agent_type="initial_coding",
            research_domain=research_domain
        )
        
        print(f"   📊 Quality Assessment: {coding_quality.status} (confidence: {coding_quality.confidence:.2f})")
        print(f"   🎯 Quality Score: {coding_quality.quality_score:.2f}")
        
        if coding_quality.status == "HALT":
            print(f"   ❌ SUPERVISOR HALTED PIPELINE!")
            print(f"   🛑 Action: {coding_quality.action}")
            if coding_quality.feedback:
                print(f"   📝 Feedback: {coding_quality.feedback}")
            print(f"   🚫 Next agent (Thematic Grouping) will NOT proceed")
            return False
        elif coding_quality.status == "REVISE":
            print(f"   ⚠️  SUPERVISOR SUGGESTS REVISION")
            print(f"   🔄 Action: {coding_quality.action}")
            if coding_quality.feedback:
                print(f"   📝 Feedback: {coding_quality.feedback}")
            print(f"   ⏭️  Continuing to next agent (Thematic Grouping) with warnings")
        else:
            print(f"   ✅ SUPERVISOR APPROVED - PROCEEDING TO NEXT AGENT")
            print(f"   🎯 Quality Score: {coding_quality.quality_score:.2f}")
            print(f"   ➡️  Next agent (Thematic Grouping) will proceed")
        
        # Display coding results
        coding_summary = coding_result.get("coding_summary", {})
        print(f"   📊 Coding Summary:")
        print(f"      Total units coded: {coding_summary.get('total_units_coded', 0)}")
        print(f"      Unique codes generated: {coding_summary.get('unique_codes_generated', 0)}")
        print(f"      Average confidence: {coding_summary.get('average_confidence', 0):.2f}")
        
        # Step 4: Thematic Grouping
        print(f"\n🎨 Step 4: Thematic Grouping...")
        print("   🔄 [4/6] Starting Thematic Grouping Agent")
        print("   ⚠️  This will make another LLM API call!")
        
        thematic_grouper = ThematicGroupingAgent()
        coded_units = coding_result.get("coded_units", [])
        
        if not coded_units:
            print("   ❌ No coded units available for thematic grouping")
            return False
        
        thematic_result = await thematic_grouper.run(coded_units, research_domain)
        
        if "error" in thematic_result:
            print(f"   ❌ Thematic grouping failed: {thematic_result['error']}")
            return False
        
        all_sections["thematic_grouping"] = thematic_result
        print("   ✅ Thematic grouping completed successfully!")
        
        # Supervisor Quality Check: Thematic Grouping
        print(f"\n🔍 Supervisor Quality Check: Thematic Grouping...")
        print("   ⚠️  This will make a supervisor LLM API call!")
        
        thematic_quality = await supervisor.check_quality(
            agent_output=thematic_result,
            agent_type="thematic_grouping",
            research_domain=research_domain
        )
        
        print(f"   📊 Quality Assessment: {thematic_quality.status} (confidence: {thematic_quality.confidence:.2f})")
        print(f"   🎯 Quality Score: {thematic_quality.quality_score:.2f}")
        
        if thematic_quality.status == "HALT":
            print(f"   ❌ SUPERVISOR HALTED PIPELINE!")
            print(f"   🛑 Action: {thematic_quality.action}")
            if thematic_quality.feedback:
                print(f"   📝 Feedback: {thematic_quality.feedback}")
            print(f"   🚫 Next agent (Theme Refinement) will NOT proceed")
            return False
        elif thematic_quality.status == "REVISE":
            print(f"   ⚠️  SUPERVISOR SUGGESTS REVISION")
            print(f"   🔄 Action: {thematic_quality.action}")
            if thematic_quality.feedback:
                print(f"   📝 Feedback: {thematic_quality.feedback}")
            print(f"   ⏭️  Continuing to next agent (Theme Refinement) with warnings")
        else:
            print(f"   ✅ SUPERVISOR APPROVED - PROCEEDING TO NEXT AGENT")
            print(f"   🎯 Quality Score: {thematic_quality.quality_score:.2f}")
            print(f"   ➡️  Next agent (Theme Refinement) will proceed")
        
        # Display thematic results
        thematic_summary = thematic_result.get("thematic_summary", {})
        print(f"   📊 Thematic Analysis Summary:")
        print(f"      Total themes generated: {thematic_summary.get('total_themes_generated', 0)}")
        print(f"      Total codes analyzed: {thematic_summary.get('total_codes_analyzed', 0)}")
        print(f"      Average codes per theme: {thematic_summary.get('average_codes_per_theme', 0):.1f}")
        
        # Step 5: Theme Refinement
        print(f"\n✨ Step 5: Theme Refinement...")
        print("   🔄 [5/6] Starting Theme Refinement Agent")
        print("   ⚠️  This will make another LLM API call!")
        
        theme_refiner = ThemeRefinerAgent()
        themes = thematic_result.get("themes", [])
        
        if not themes:
            print("   ❌ No themes available for refinement")
            return False
        
        refinement_result = await theme_refiner.run(themes, research_domain)
        
        if "error" in refinement_result:
            print(f"   ❌ Theme refinement failed: {refinement_result['error']}")
            return False
        
        all_sections["theme_refinement"] = refinement_result
        print("   ✅ Theme refinement completed successfully!")
        
        # Supervisor Quality Check: Theme Refinement
        print(f"\n🔍 Supervisor Quality Check: Theme Refinement...")
        print("   ⚠️  This will make a supervisor LLM API call!")
        
        refinement_quality = await supervisor.check_quality(
            agent_output=refinement_result,
            agent_type="theme_refinement",
            research_domain=research_domain
        )
        
        print(f"   📊 Quality Assessment: {refinement_quality.status} (confidence: {refinement_quality.confidence:.2f})")
        print(f"   🎯 Quality Score: {refinement_quality.quality_score:.2f}")
        
        if refinement_quality.status == "HALT":
            print(f"   ❌ SUPERVISOR HALTED PIPELINE!")
            print(f"   🛑 Action: {refinement_quality.action}")
            if refinement_quality.feedback:
                print(f"   📝 Feedback: {refinement_quality.feedback}")
            print(f"   🚫 Next agent (Report Generation) will NOT proceed")
            return False
        elif refinement_quality.status == "REVISE":
            print(f"   ⚠️  SUPERVISOR SUGGESTS REVISION")
            print(f"   🔄 Action: {refinement_quality.action}")
            if refinement_quality.feedback:
                print(f"   📝 Feedback: {refinement_quality.feedback}")
            print(f"   ⏭️  Continuing to next agent (Report Generation) with warnings")
        else:
            print(f"   ✅ SUPERVISOR APPROVED - PROCEEDING TO NEXT AGENT")
            print(f"   🎯 Quality Score: {refinement_quality.quality_score:.2f}")
            print(f"   ➡️  Next agent (Report Generation) will proceed")
        
        # Display refinement results
        refinement_summary = refinement_result.get("refinement_summary", {})
        print(f"   📊 Theme Refinement Summary:")
        print(f"      Total themes refined: {refinement_summary.get('total_themes_refined', 0)}")
        print(f"      Academic quotes: {refinement_summary.get('total_academic_quotes', 0)}")
        print(f"      Key concepts: {refinement_summary.get('total_key_concepts', 0)}")
        
        # Step 6: Report Generation
        print(f"\n📄 Step 6: Report Generation...")
        print("   🔄 [6/6] Starting Report Generation Agent")
        print("   ⚠️  This will make the final LLM API call for complete report!")
        
        report_generator = ReportGeneratorAgent()
        report_result = await report_generator.run(all_sections)
        
        if "error" in report_result:
            print(f"   ❌ Report generation failed: {report_result['error']}")
            return False
        
        print("   ✅ Report generation completed successfully!")
        
        # Supervisor Quality Check: Report Generation
        print(f"\n🔍 Supervisor Quality Check: Report Generation...")
        print("   ⚠️  This will make a supervisor LLM API call!")
        
        report_quality = await supervisor.check_quality(
            agent_output=report_result,
            agent_type="report_generation",
            research_domain=research_domain
        )
        
        print(f"   📊 Quality Assessment: {report_quality.status} (confidence: {report_quality.confidence:.2f})")
        print(f"   🎯 Quality Score: {report_quality.quality_score:.2f}")
        
        if report_quality.status == "HALT":
            print(f"   ❌ SUPERVISOR HALTED PIPELINE!")
            print(f"   🛑 Action: {report_quality.action}")
            if report_quality.feedback:
                print(f"   📝 Feedback: {report_quality.feedback}")
            print(f"   🚫 Final report will NOT be saved")
            return False
        elif report_quality.status == "REVISE":
            print(f"   ⚠️  SUPERVISOR SUGGESTS REVISION")
            print(f"   🔄 Action: {report_quality.action}")
            if report_quality.feedback:
                print(f"   📝 Feedback: {report_quality.feedback}")
            print(f"   ⏭️  Final report will be saved with warnings")
        else:
            print(f"   ✅ SUPERVISOR APPROVED - FINAL REPORT READY")
            print(f"   🎯 Quality Score: {report_quality.quality_score:.2f}")
            print(f"   💾 Final report will be saved")
        
        # Display final report summary
        report_summary = report_result.get("report_summary", {})
        print(f"\n📊 Final Report Summary:")
        print(f"   Word Count: {report_summary.get('word_count', 0)}")
        print(f"   Total References: {report_summary.get('total_references', 0)}")
        print(f"   Report Length: {report_summary.get('report_length', 0)} characters")
        
        # Display sections included
        sections_included = report_summary.get("sections_included", {})
        print(f"\n📋 Report Sections:")
        for section, included in sections_included.items():
            status = "✅" if included else "❌"
            print(f"   {status} {section}")
        
        # Display file path
        file_path = report_result.get("file_path", "")
        if file_path:
            print(f"\n💾 Complete Academic Paper saved to:")
            print(f"   {file_path}")
        
        # Show preview of the generated report
        report_content = report_result.get("report_content", "")
        if report_content:
            print(f"\n📖 Generated Report Preview (first 300 characters):")
            print(f"{'='*60}")
            print(report_content[:300] + "..." if len(report_content) > 300 else report_content)
            print(f"{'='*60}")
        
        # Final Supervisor Summary
        print(f"\n🎯 ===== SUPERVISOR QUALITY CONTROL SUMMARY =====")
        print(f"All agents passed quality control checks!")
        print(f"Pipeline completed successfully with supervisor oversight.")
        print(f"Quality scores:")
        print(f"  📚 Literature Review: {lit_quality.quality_score:.2f}")
        print(f"  🎯 Initial Coding: {coding_quality.quality_score:.2f}")
        print(f"  🎨 Thematic Grouping: {thematic_quality.quality_score:.2f}")
        print(f"  ✨ Theme Refinement: {refinement_quality.quality_score:.2f}")
        print(f"  📄 Report Generation: {report_quality.quality_score:.2f}")
        
        avg_quality = (lit_quality.quality_score + coding_quality.quality_score + 
                      thematic_quality.quality_score + refinement_quality.quality_score + 
                      report_quality.quality_score) / 5
        print(f"  📊 Average Quality Score: {avg_quality:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Complete Pipeline Test with Real Documents")
    print("=" * 80)
    print("This test will:")
    print("1. Retrieve actual documents from vector store")
    print("2. Generate literature review")
    print("3. Perform initial coding")
    print("4. Create thematic groupings")
    print("5. Refine themes with academic polish")
    print("6. Generate complete academic paper")
    print("=" * 80)
    
    success = await test_complete_pipeline()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ Complete pipeline test completed successfully!")
        print("🎓 Generated a complete academic paper from real documents!")
    else:
        print("⚠️  Complete pipeline test failed - check the output above for details")
    
    print(f"📅 Test completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main()) 