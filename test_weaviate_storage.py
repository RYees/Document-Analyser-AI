#!/usr/bin/env python3
"""
Test to verify if PipelineStorageManager is actually storing data in Weaviate.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.utils.pipeline_storage_manager import PipelineStorageManager
import uuid
from datetime import datetime, timezone

def test_weaviate_storage():
    """Test if data is actually being stored in Weaviate."""
    
    print("🧪 Testing Weaviate Storage...")
    
    try:
        # Initialize storage manager
        storage = PipelineStorageManager()
        print("✅ PipelineStorageManager initialized")
        
        # Create test pipeline data
        test_pipeline_id = str(uuid.uuid4())
        test_data = {
            "pipeline_id": test_pipeline_id,
            "status": "running",
            "current_step": 1,
            "total_steps": 6,
            "query": "test query",
            "research_domain": "Test",
            "max_results": 5,
            "quality_threshold": 0.6,
            "config": {"enable_supervisor": False},
            "steps": [],
            "results": {},
            "quality_scores": {},
            "supervisor_decisions": {},
            "errors": []
        }
        
        print(f"📝 Creating pipeline: {test_pipeline_id}")
        
        # Try to create pipeline
        created_id = storage.create_pipeline(test_data)
        print(f"✅ Pipeline created with ID: {created_id}")
        
        # Immediately try to retrieve it
        print(f"🔍 Retrieving pipeline: {created_id}")
        retrieved_data = storage.get_pipeline(created_id)
        
        if retrieved_data:
            print(f"✅ Pipeline retrieved successfully!")
            print(f"   Status: {retrieved_data.get('status')}")
            print(f"   Query: {retrieved_data.get('query')}")
            print(f"   Domain: {retrieved_data.get('research_domain')}")
        else:
            print(f"❌ Pipeline NOT found in storage!")
        
        # Try to update it
        print(f"🔄 Updating pipeline...")
        update_success = storage.update_pipeline(created_id, {
            "status": "completed",
            "current_step": 6,
            "results": {"test": "data"}
        })
        
        if update_success:
            print(f"✅ Pipeline updated successfully!")
            
            # Retrieve again to verify update
            updated_data = storage.get_pipeline(created_id)
            if updated_data:
                print(f"✅ Updated pipeline retrieved!")
                print(f"   New status: {updated_data.get('status')}")
                print(f"   New step: {updated_data.get('current_step')}")
            else:
                print(f"❌ Updated pipeline NOT found!")
        else:
            print(f"❌ Pipeline update failed!")
        
        # List pipelines
        print(f"📋 Listing pipelines...")
        pipelines = storage.list_pipelines(limit=10)
        print(f"✅ Found {len(pipelines)} pipelines in storage")
        
        # Check if our pipeline is in the list
        found = False
        for pipeline in pipelines:
            if pipeline.get("pipeline_id") == created_id:
                found = True
                print(f"✅ Our pipeline found in list!")
                break
        
        if not found:
            print(f"❌ Our pipeline NOT found in list!")
        
        # Clean up
        print(f"🗑️  Deleting test pipeline...")
        delete_success = storage.delete_pipeline(created_id)
        if delete_success:
            print(f"✅ Pipeline deleted successfully!")
        else:
            print(f"❌ Pipeline deletion failed!")
        
        print(f"\n🎉 Weaviate storage test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weaviate_storage() 