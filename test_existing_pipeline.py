#!/usr/bin/env python3
"""
Test to retrieve the specific pipeline that was saved: 96720687-abd8-4b7d-95a5-cb6f674050eb
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.utils.pipeline_storage_manager import PipelineStorageManager

def test_existing_pipeline():
    """Test retrieval of the specific pipeline that was saved."""
    
    print("🧪 Testing Existing Pipeline Retrieval...")
    
    # The actual pipeline ID from the logs
    pipeline_id = "96720687-abd8-4b7d-95a5-cb6f674050eb"
    
    try:
        # Initialize storage manager
        storage = PipelineStorageManager()
        print("✅ PipelineStorageManager initialized")
        
        print(f"🔍 Trying to retrieve pipeline: {pipeline_id}")
        
        # Try to get the pipeline
        pipeline_data = storage.get_pipeline(pipeline_id)
        
        if pipeline_data:
            print(f"✅ Pipeline retrieved successfully!")
            print(f"   Status: {pipeline_data.get('status')}")
            print(f"   Query: {pipeline_data.get('query')}")
            print(f"   Research Domain: {pipeline_data.get('research_domain')}")
            print(f"   Current Step: {pipeline_data.get('current_step')}")
            print(f"   Total Steps: {pipeline_data.get('total_steps')}")
            print(f"   Created At: {pipeline_data.get('created_at')}")
            print(f"   Updated At: {pipeline_data.get('updated_at')}")
            
            # Check if results exist
            results = pipeline_data.get('results', {})
            if results:
                print(f"   Results: {len(results)} result sections")
                for key in results.keys():
                    print(f"     - {key}")
            else:
                print(f"   Results: No results found")
                
        else:
            print(f"❌ Pipeline NOT found!")
            
            # Try listing all pipelines to see what's available
            print(f"📋 Listing all pipelines to see what's available...")
            pipelines = storage.list_pipelines(limit=20)
            print(f"✅ Found {len(pipelines)} pipelines in storage")
            
            for pipeline in pipelines:
                print(f"   - {pipeline.get('pipeline_id')}: {pipeline.get('status')} ({pipeline.get('query')})")
        
        print(f"\n🎉 Existing pipeline test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_existing_pipeline() 