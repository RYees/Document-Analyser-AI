#!/usr/bin/env python3
"""
Test script for Weaviate Client Module
Tests connection, CRUD operations, and research paper functionality
"""

import asyncio
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv("analyser/env_file")

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking Weaviate environment setup...")
    
    required_vars = ["WEAVIATE_URL", "WEAVIATE_API_KEY", "OPENAI_API_KEY"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these in your env_file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    print("✅ Weaviate environment setup complete")
    return True

def test_weaviate_connection():
    """Test Weaviate connection"""
    print("\n🔌 Testing Weaviate connection...")
    
    try:
        from analyser.utils.weaviate_client import WeaviateManager
        
        # Initialize manager
        manager = WeaviateManager()
        
        if not manager.is_available():
            print("❌ Weaviate connection failed")
            return False
        
        print("✅ Weaviate connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Weaviate connection test failed: {e}")
        return False

def test_collection_operations():
    """Test collection CRUD operations"""
    print("\n📚 Testing collection operations...")
    
    try:
        from analyser.utils.weaviate_client import WeaviateManager
        
        manager = WeaviateManager()
        
        if not manager.is_available():
            print("❌ Weaviate not available for collection tests")
            return False
        
        # Test collection creation
        test_collection = "test_research_papers"
        schema = manager.create_research_papers_schema()
        
        if not manager.create_collection(test_collection, schema):
            print("❌ Collection creation failed")
            return False
        
        print("✅ Collection creation successful")
        
        # Test collection info
        info = manager.get_collection_info(test_collection)
        if not info:
            print("❌ Collection info retrieval failed")
            return False
        
        print(f"✅ Collection info retrieved: {info.get('total_objects', 0)} objects")
        
        # Test document insertion
        test_documents = [
            {
                "properties": {
                    "title": "Test Paper 1",
                    "authors": ["Author 1", "Author 2"],
                    "abstract": "This is a test abstract",
                    "content": "This is test content for the first paper",
                    "year": 2023,
                    "doi": "10.1234/test.2023.001",
                    "url": "https://example.com/paper1",
                    "source": "TEST",
                    "word_count": 50,
                    "pages_extracted": 1,
                    "research_domain": "Test Domain",
                    "extracted_at": "2023-01-01T00:00:00Z"
                }
            },
            {
                "properties": {
                    "title": "Test Paper 2",
                    "authors": ["Author 3"],
                    "abstract": "Another test abstract",
                    "content": "This is test content for the second paper",
                    "year": 2023,
                    "doi": "10.1234/test.2023.002",
                    "url": "https://example.com/paper2",
                    "source": "TEST",
                    "word_count": 45,
                    "pages_extracted": 1,
                    "research_domain": "Test Domain",
                    "extracted_at": "2023-01-01T00:00:00Z"
                }
            }
        ]
        
        if not manager.insert_documents(test_collection, test_documents):
            print("❌ Document insertion failed")
            return False
        
        print("✅ Document insertion successful")
        
        # Test document search
        search_results = manager.search_documents(test_collection, "test content", limit=5)
        if not search_results:
            print("❌ Document search failed")
            return False
        
        print(f"✅ Document search successful: found {len(search_results)} results")
        
        # Test document update
        if search_results:
            first_doc = search_results[0]
            update_success = manager.update_document(
                test_collection, 
                first_doc["uuid"], 
                {"title": "Updated Test Paper 1"}
            )
            
            if not update_success:
                print("❌ Document update failed")
                return False
            
            print("✅ Document update successful")
        
        # Test document deletion
        if search_results:
            delete_success = manager.delete_document(test_collection, search_results[0]["uuid"])
            
            if not delete_success:
                print("❌ Document deletion failed")
                return False
            
            print("✅ Document deletion successful")
        
        # Test collection deletion
        if not manager.delete_collection(test_collection):
            print("❌ Collection deletion failed")
            return False
        
        print("✅ Collection deletion successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Collection operations test failed: {e}")
        return False

def test_research_papers_functionality():
    """Test research papers specific functionality"""
    print("\n📄 Testing research papers functionality...")
    
    try:
        from analyser.utils.weaviate_client import WeaviateManager
        
        manager = WeaviateManager()
        
        if not manager.is_available():
            print("❌ Weaviate not available for research papers tests")
            return False
        
        # Test schema creation
        schema = manager.create_research_papers_schema()
        if not schema or "properties" not in schema:
            print("❌ Research papers schema creation failed")
            return False
        
        print("✅ Research papers schema created successfully")
        
        # Test document preparation
        test_paper = {
            "title": "Blockchain Technology: A Comprehensive Review",
            "authors": ["John Doe", "Jane Smith"],
            "abstract": "This paper provides a comprehensive review of blockchain technology...",
            "extracted_content": "Blockchain technology has emerged as a revolutionary innovation...",
            "year": 2023,
            "doi": "10.1234/blockchain.2023.001",
            "url": "https://example.com/blockchain-paper",
            "source": "CORE",
            "word_count": 5000,
            "pages_extracted": 15
        }
        
        prepared_doc = manager.prepare_paper_document(test_paper, "Blockchain Technology")
        if not prepared_doc or "properties" not in prepared_doc:
            print("❌ Document preparation failed")
            return False
        
        print("✅ Document preparation successful")
        
        # Test collection creation and document insertion
        test_collection = "test_research_papers_v2"
        if not manager.create_collection(test_collection, schema):
            print("❌ Research papers collection creation failed")
            return False
        
        if not manager.insert_documents(test_collection, [prepared_doc]):
            print("❌ Research paper insertion failed")
            return False
        
        print("✅ Research paper insertion successful")
        
        # Test search functionality
        search_results = manager.search_documents(test_collection, "blockchain technology", limit=5)
        if not search_results:
            print("❌ Research paper search failed")
            return False
        
        print(f"✅ Research paper search successful: found {len(search_results)} results")
        
        # Cleanup
        manager.delete_collection(test_collection)
        
        return True
        
    except Exception as e:
        print(f"❌ Research papers functionality test failed: {e}")
        return False

def test_global_manager():
    """Test global manager functionality"""
    print("\n🌐 Testing global manager functionality...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager, close_weaviate_manager
        
        # Test global manager creation
        manager1 = get_weaviate_manager()
        manager2 = get_weaviate_manager()
        
        if manager1 is not manager2:
            print("❌ Global manager singleton pattern failed")
            return False
        
        print("✅ Global manager singleton pattern working")
        
        # Test manager availability
        if not manager1.is_available():
            print("❌ Global manager not available")
            return False
        
        print("✅ Global manager available")
        
        # Test collection listing
        collections = manager1.list_collections()
        print(f"✅ Found {len(collections)} existing collections")
        
        # Test cleanup
        close_weaviate_manager()
        print("✅ Global manager cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Global manager test failed: {e}")
        return False

def run_all_tests():
    """Run all Weaviate client tests"""
    print("🚀 Starting Weaviate Client Tests")
    print("=" * 60)
    
    # Environment check
    if not check_environment():
        return False
    
    # Run individual tests
    tests = [
        ("Connection", test_weaviate_connection),
        ("Collection Operations", test_collection_operations),
        ("Research Papers Functionality", test_research_papers_functionality),
        ("Global Manager", test_global_manager)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Weaviate Client Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All Weaviate client tests passed!")
        print("✅ Weaviate integration is ready for use in the literature review node")
    else:
        print("\n⚠️  Some Weaviate client tests failed. Please check the errors above.")
    
    return passed == len(results)

async def main():
    """Main test function"""
    success = run_all_tests()
    return success

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 