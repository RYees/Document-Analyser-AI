#!/usr/bin/env python3
"""
Test script for PipelineStorageManager
"""

import asyncio
import sys
import os

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.utils.pipeline_storage_manager import PipelineStorageManager

def test_pipeline_storage():
    """Test the PipelineStorageManager functionality."""
    print("🧪 Testing PipelineStorageManager...")
    
    try:
        # Initialize storage manager
        storage = PipelineStorageManager()
        print("✅ PipelineStorageManager initialized successfully")
        
        # Test creating a pipeline
        pipeline_data = {
            "status": "created",
            "research_domain": "Blockchain",
            "query": "transparency in blockchain technology",
            "current_step": 0,
            "total_steps": 6
        }
        
        pipeline_id = storage.create_pipeline(pipeline_data)
        print(f"✅ Created pipeline: {pipeline_id}")
        
        # Test retrieving the pipeline
        retrieved_pipeline = storage.get_pipeline(pipeline_id)
        if retrieved_pipeline:
            print(f"✅ Retrieved pipeline: {retrieved_pipeline['pipeline_id']}")
            print(f"   Status: {retrieved_pipeline['status']}")
            print(f"   Domain: {retrieved_pipeline['research_domain']}")
        else:
            print("❌ Failed to retrieve pipeline")
            return False
        
        # Test updating the pipeline
        updates = {
            "status": "running",
            "current_step": 1
        }
        
        if storage.update_pipeline(pipeline_id, updates):
            print("✅ Updated pipeline successfully")
            
            # Verify update
            updated_pipeline = storage.get_pipeline(pipeline_id)
            if updated_pipeline and updated_pipeline['status'] == 'running':
                print("✅ Update verified")
            else:
                print("❌ Update verification failed")
        else:
            print("❌ Failed to update pipeline")
            return False
        
        # Test listing pipelines
        pipelines = storage.list_pipelines(limit=10)
        print(f"✅ Listed {len(pipelines)} pipelines")
        
        # Test filtering
        blockchain_pipelines = storage.list_pipelines(research_domain="Blockchain")
        print(f"✅ Found {len(blockchain_pipelines)} Blockchain pipelines")
        
        # Test deleting the pipeline
        if storage.delete_pipeline(pipeline_id):
            print("✅ Deleted pipeline successfully")
            
            # Verify deletion
            deleted_pipeline = storage.get_pipeline(pipeline_id)
            if deleted_pipeline is None:
                print("✅ Deletion verified")
            else:
                print("❌ Deletion verification failed")
        else:
            print("❌ Failed to delete pipeline")
            return False
        
        print("🎉 All PipelineStorageManager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pipeline_storage()
    sys.exit(0 if success else 1) 