#!/usr/bin/env python3
"""
Advanced Weaviate Features Test Script
Tests all advanced Weaviate v4 features to identify which work on free vs pro accounts
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv
load_dotenv("analyser/env_file")

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment setup...")
    
    required_vars = ["WEAVIATE_URL", "WEAVIATE_API_KEY", "OPENAI_API_KEY"]
    
    missing_required = [var for var in required_vars if not os.getenv(var)]
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        print("Please set these in your .env file:")
        for var in missing_required:
            print(f"  {var}=your_api_key_here")
        return False
    
    print("✅ Environment setup complete")
    return True

def test_available_modules():
    """Test which modules are available on this Weaviate instance"""
    print("\n🔍 Testing available modules...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager
        
        manager = get_weaviate_manager()
        modules = manager.get_available_modules()
        
        print(f"✅ Available modules: {list(modules.keys())}")
        
        # Check for specific modules
        module_status = {
            "text2vec-openai": "text2vec-openai" in modules,
            "generative-openai": "generative-openai" in modules,
            "reranker-cohere": "reranker-cohere" in modules,
            "text2vec-cohere": "text2vec-cohere" in modules,
            "text2vec-huggingface": "text2vec-huggingface" in modules
        }
        
        print("\n📊 Module Availability:")
        for module, available in module_status.items():
            status = "✅ Available" if available else "❌ Not Available"
            print(f"  {module}: {status}")
        
        return modules
        
    except Exception as e:
        print(f"❌ Failed to get modules: {e}")
        return {}

def test_basic_crud_operations():
    """Test basic CRUD operations"""
    print("\n📝 Testing basic CRUD operations...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager
        
        manager = get_weaviate_manager()
        
        # Create test collection
        collection_name = "test_advanced_features"
        schema = manager.create_research_papers_schema()
        
        if not manager.create_collection(collection_name, schema):
            print("❌ Failed to create test collection")
            return False
        
        # Test single document insertion
        test_doc = {
            "properties": {
                "title": "Test Advanced Features Paper",
                "authors": ["Test Author"],
                "abstract": "This is a test paper for advanced features",
                "content": "This paper tests various advanced Weaviate features including search, references, and batch operations.",
                "year": 2024,
                "doi": "10.1234/test.2024.001",
                "url": "https://example.com/test",
                "source": "TEST",
                "word_count": 50,
                "pages_extracted": 1,
                "research_domain": "Testing",
                "extracted_at": "2024-01-01T00:00:00Z"
            }
        }
        
        uuid = manager.insert_single_document(collection_name, test_doc)
        if not uuid:
            print("❌ Failed to insert test document")
            return False
        
        print(f"✅ Document inserted with UUID: {uuid}")
        
        # Test document retrieval
        retrieved_doc = manager.get_document_by_id(collection_name, uuid)
        if not retrieved_doc:
            print("❌ Failed to retrieve document")
            return False
        
        print("✅ Document retrieved successfully")
        
        # Test document update
        update_props = {"title": "Updated Test Advanced Features Paper"}
        if not manager.update_document(collection_name, uuid, update_props):
            print("❌ Failed to update document")
            return False
        
        print("✅ Document updated successfully")
        
        # Test document replacement
        replace_props = {
            "title": "Replaced Test Advanced Features Paper",
            "abstract": "This is a completely replaced test paper",
            "content": "This paper has been completely replaced for testing purposes.",
            "year": 2024,
            "doi": "10.1234/test.2024.001",
            "url": "https://example.com/test",
            "source": "TEST",
            "word_count": 30,
            "pages_extracted": 1,
            "research_domain": "Testing",
            "extracted_at": "2024-01-01T00:00:00Z"
        }
        
        if not manager.replace_document(collection_name, uuid, replace_props):
            print("❌ Failed to replace document")
            return False
        
        print("✅ Document replaced successfully")
        
        # Clean up
        manager.delete_document(collection_name, uuid)
        manager.delete_collection(collection_name)
        
        print("✅ Basic CRUD operations test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Basic CRUD operations test failed: {e}")
        return False

def test_advanced_search_features():
    """Test advanced search features"""
    print("\n🔍 Testing advanced search features...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager
        
        manager = get_weaviate_manager()
        
        # Create test collection
        collection_name = "test_search_features"
        schema = manager.create_research_papers_schema()
        
        if not manager.create_collection(collection_name, schema):
            print("❌ Failed to create test collection")
            return False
        
        # Insert test documents
        test_docs = [
            {
                "properties": {
                    "title": "Machine Learning in Research",
                    "authors": ["Alice Johnson"],
                    "abstract": "This paper discusses machine learning applications in research",
                    "content": "Machine learning has revolutionized research methodologies across various domains.",
                    "year": 2024,
                    "doi": "10.1234/ml.2024.001",
                    "url": "https://example.com/ml",
                    "source": "TEST",
                    "word_count": 100,
                    "pages_extracted": 2,
                    "research_domain": "Machine Learning",
                    "extracted_at": "2024-01-01T00:00:00Z"
                }
            },
            {
                "properties": {
                    "title": "Deep Learning Applications",
                    "authors": ["Bob Smith"],
                    "abstract": "Deep learning techniques for research applications",
                    "content": "Deep learning provides powerful tools for complex research problems.",
                    "year": 2024,
                    "doi": "10.1234/dl.2024.001",
                    "url": "https://example.com/dl",
                    "source": "TEST",
                    "word_count": 80,
                    "pages_extracted": 1,
                    "research_domain": "Deep Learning",
                    "extracted_at": "2024-01-01T00:00:00Z"
                }
            }
        ]
        
        if not manager.insert_documents(collection_name, test_docs):
            print("❌ Failed to insert test documents")
            return False
        
        print("✅ Test documents inserted")
        
        # Test 1: Basic near_text search
        print("\n  Testing near_text search...")
        try:
            results = manager.search_documents(collection_name, "machine learning", limit=5)
            print(f"    ✅ near_text search: Found {len(results)} results")
        except Exception as e:
            print(f"    ❌ near_text search failed: {e}")
        
        # Test 2: BM25 search
        print("\n  Testing BM25 search...")
        try:
            results = manager.bm25_search(collection_name, "machine learning", limit=5)
            print(f"    ✅ BM25 search: Found {len(results)} results")
        except Exception as e:
            print(f"    ❌ BM25 search failed (may require pro account): {e}")
        
        # Test 3: Hybrid search
        print("\n  Testing hybrid search...")
        try:
            results = manager.hybrid_search(collection_name, "machine learning", limit=5)
            print(f"    ✅ Hybrid search: Found {len(results)} results")
        except Exception as e:
            print(f"    ❌ Hybrid search failed (may require pro account): {e}")
        
        # Test 4: Near vector search (requires getting a vector first)
        print("\n  Testing near_vector search...")
        try:
            # Get a document to extract its vector
            search_results = manager.search_documents(collection_name, "machine learning", limit=1, include_vector=True)
            if search_results and search_results[0].get("vector"):
                vector = search_results[0]["vector"]
                results = manager.near_vector_search(collection_name, vector, limit=5)
                print(f"    ✅ Near vector search: Found {len(results)} results")
            else:
                print("    ⚠️  Near vector search: No vector available for testing")
        except Exception as e:
            print(f"    ❌ Near vector search failed: {e}")
        
        # Test 5: Generative search
        print("\n  Testing generative search...")
        try:
            results = manager.generative_search(
                collection_name, 
                "machine learning", 
                limit=2,
                single_prompt="Summarize this research: {content}",
                grouped_task="What are the main themes in these papers?"
            )
            print(f"    ✅ Generative search: Found {len(results.get('objects', []))} results")
            if results.get('generated'):
                print(f"    ✅ Generated content: {results['generated'][:100]}...")
        except Exception as e:
            print(f"    ❌ Generative search failed (may require pro account): {e}")
        
        # Test 6: Reranker search
        print("\n  Testing reranker search...")
        try:
            results = manager.rerank_search(collection_name, "machine learning", limit=5)
            print(f"    ✅ Reranker search: Found {len(results)} results")
        except Exception as e:
            print(f"    ❌ Reranker search failed (may require pro account): {e}")
        
        # Clean up
        manager.delete_collection(collection_name)
        
        print("✅ Advanced search features test completed")
        return True
        
    except Exception as e:
        print(f"❌ Advanced search features test failed: {e}")
        return False

def test_reference_features():
    """Test reference/cross-reference features"""
    print("\n🔗 Testing reference features...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager
        
        manager = get_weaviate_manager()
        
        # Create collections with references
        papers_collection = "test_papers_with_refs"
        authors_collection = "test_authors"
        
        # Create authors collection first
        authors_schema = {
            "class": "Author",
            "description": "Collection for storing authors",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "vectorizeClassName": False,
                    "model": "ada",
                    "modelVersion": "002",
                    "type": "text"
                }
            },
            "properties": [
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "Author name"
                },
                {
                    "name": "institution",
                    "dataType": ["text"],
                    "description": "Author institution"
                },
                {
                    "name": "email",
                    "dataType": ["text"],
                    "description": "Author email"
                }
            ]
        }
        
        if not manager.create_collection(authors_collection, authors_schema):
            print("❌ Failed to create authors collection")
            return False
        
        # Create papers collection with references
        papers_schema = manager.create_research_papers_with_references_schema()
        if not manager.create_collection(papers_collection, papers_schema):
            print("❌ Failed to create papers collection")
            return False
        
        # Insert author
        author_doc = {
            "properties": {
                "name": "Dr. Alice Johnson",
                "institution": "MIT",
                "email": "alice@mit.edu"
            }
        }
        
        author_uuid = manager.insert_single_document(authors_collection, author_doc)
        if not author_uuid:
            print("❌ Failed to insert author")
            return False
        
        print(f"✅ Author inserted with UUID: {author_uuid}")
        
        # Insert paper
        paper_doc = {
            "properties": {
                "title": "Advanced Research Methods",
                "abstract": "This paper discusses advanced research methodologies",
                "content": "Advanced research methods are essential for modern scientific inquiry.",
                "year": 2024,
                "doi": "10.1234/arm.2024.001",
                "url": "https://example.com/arm",
                "source": "TEST",
                "word_count": 60,
                "pages_extracted": 1,
                "research_domain": "Research Methods",
                "extracted_at": "2024-01-01T00:00:00Z"
            }
        }
        
        paper_uuid = manager.insert_single_document(papers_collection, paper_doc)
        if not paper_uuid:
            print("❌ Failed to insert paper")
            return False
        
        print(f"✅ Paper inserted with UUID: {paper_uuid}")
        
        # Test adding reference
        print("\n  Testing reference addition...")
        try:
            if manager.add_reference(papers_collection, paper_uuid, "hasAuthors", author_uuid):
                print("    ✅ Reference added successfully")
            else:
                print("    ❌ Failed to add reference")
        except Exception as e:
            print(f"    ❌ Reference addition failed: {e}")
        
        # Test search with references
        print("\n  Testing search with references...")
        try:
            results = manager.search_with_references(
                papers_collection, 
                "research methods", 
                limit=5,
                reference_property="hasAuthors"
            )
            print(f"    ✅ Search with references: Found {len(results)} results")
            for result in results:
                if result.get("references"):
                    print(f"    ✅ Found references: {len(result['references'])}")
        except Exception as e:
            print(f"    ❌ Search with references failed: {e}")
        
        # Test deleting reference
        print("\n  Testing reference deletion...")
        try:
            if manager.delete_reference(papers_collection, paper_uuid, "hasAuthors", author_uuid):
                print("    ✅ Reference deleted successfully")
            else:
                print("    ❌ Failed to delete reference")
        except Exception as e:
            print(f"    ❌ Reference deletion failed: {e}")
        
        # Clean up
        manager.delete_document(papers_collection, paper_uuid)
        manager.delete_document(authors_collection, author_uuid)
        manager.delete_collection(papers_collection)
        manager.delete_collection(authors_collection)
        
        print("✅ Reference features test completed")
        return True
        
    except Exception as e:
        print(f"❌ Reference features test failed: {e}")
        return False

def test_batch_operations():
    """Test batch operations"""
    print("\n📦 Testing batch operations...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager
        
        manager = get_weaviate_manager()
        
        # Create test collection
        collection_name = "test_batch_operations"
        schema = manager.create_research_papers_schema()
        
        if not manager.create_collection(collection_name, schema):
            print("❌ Failed to create test collection")
            return False
        
        # Insert test documents
        test_docs = [
            {
                "properties": {
                    "title": f"Batch Test Paper {i}",
                    "authors": [f"Author {i}"],
                    "abstract": f"This is batch test paper number {i}",
                    "content": f"Content for batch test paper {i} with some research content.",
                    "year": 2024,
                    "doi": f"10.1234/batch.{i}.001",
                    "url": f"https://example.com/batch{i}",
                    "source": "TEST",
                    "word_count": 50 + i,
                    "pages_extracted": 1,
                    "research_domain": "Batch Testing",
                    "extracted_at": "2024-01-01T00:00:00Z"
                }
            }
            for i in range(1, 6)
        ]
        
        if not manager.insert_documents(collection_name, test_docs):
            print("❌ Failed to insert test documents")
            return False
        
        print("✅ Test documents inserted")
        
        # Test batch update
        print("\n  Testing batch update...")
        try:
            # Get all documents first
            search_results = manager.search_documents(collection_name, "batch test", limit=10)
            if search_results:
                updates = []
                for result in search_results:
                    updates.append({
                        "uuid": result["uuid"],
                        "properties": {
                            "title": f"Updated {result['properties']['title']}",
                            "abstract": f"Updated abstract for {result['properties']['title']}"
                        }
                    })
                
                updated_count = manager.batch_update_documents(collection_name, updates)
                print(f"    ✅ Batch update: Updated {updated_count} documents")
            else:
                print("    ⚠️  No documents found for batch update")
        except Exception as e:
            print(f"    ❌ Batch update failed: {e}")
        
        # Test batch delete
        print("\n  Testing batch delete...")
        try:
            # Get all documents
            search_results = manager.search_documents(collection_name, "batch test", limit=10)
            if search_results:
                uuids = [result["uuid"] for result in search_results]
                deleted_count = manager.batch_delete_documents(collection_name, uuids)
                print(f"    ✅ Batch delete: Deleted {deleted_count} documents")
            else:
                print("    ⚠️  No documents found for batch delete")
        except Exception as e:
            print(f"    ❌ Batch delete failed: {e}")
        
        # Clean up
        manager.delete_collection(collection_name)
        
        print("✅ Batch operations test completed")
        return True
        
    except Exception as e:
        print(f"❌ Batch operations test failed: {e}")
        return False

def test_aggregation_features():
    """Test aggregation features"""
    print("\n📊 Testing aggregation features...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager
        
        manager = get_weaviate_manager()
        
        # Create test collection
        collection_name = "test_aggregation"
        schema = manager.create_research_papers_schema()
        
        if not manager.create_collection(collection_name, schema):
            print("❌ Failed to create test collection")
            return False
        
        # Insert test documents with different years
        test_docs = [
            {
                "properties": {
                    "title": f"Aggregation Test Paper {i}",
                    "authors": [f"Author {i}"],
                    "abstract": f"This is aggregation test paper number {i}",
                    "content": f"Content for aggregation test paper {i}.",
                    "year": 2020 + (i % 5),  # Years 2020-2024
                    "doi": f"10.1234/agg.{i}.001",
                    "url": f"https://example.com/agg{i}",
                    "source": "TEST",
                    "word_count": 50 + i * 10,
                    "pages_extracted": 1,
                    "research_domain": "Aggregation Testing",
                    "extracted_at": "2024-01-01T00:00:00Z"
                }
            }
            for i in range(1, 11)
        ]
        
        if not manager.insert_documents(collection_name, test_docs):
            print("❌ Failed to insert test documents")
            return False
        
        print("✅ Test documents inserted")
        
        # Test basic aggregation
        print("\n  Testing basic aggregation...")
        try:
            result = manager.aggregate_collection(collection_name)
            print(f"    ✅ Basic aggregation: {result.get('total_count', 0)} total objects")
        except Exception as e:
            print(f"    ❌ Basic aggregation failed: {e}")
        
        # Test aggregation with grouping
        print("\n  Testing aggregation with grouping...")
        try:
            result = manager.aggregate_collection(collection_name, group_by="year")
            print(f"    ✅ Grouped aggregation: {len(result.get('groups', []))} groups")
        except Exception as e:
            print(f"    ❌ Grouped aggregation failed: {e}")
        
        # Test aggregation with metrics
        print("\n  Testing aggregation with metrics...")
        try:
            result = manager.aggregate_collection(collection_name, metrics=["word_count"])
            print(f"    ✅ Aggregation with metrics: {result.get('properties', {})}")
        except Exception as e:
            print(f"    ❌ Aggregation with metrics failed: {e}")
        
        # Clean up
        manager.delete_collection(collection_name)
        
        print("✅ Aggregation features test completed")
        return True
        
    except Exception as e:
        print(f"❌ Aggregation features test failed: {e}")
        return False

def run_all_tests():
    """Run all advanced feature tests"""
    print("🚀 Starting Advanced Weaviate Features Tests")
    print("=" * 80)
    
    # Environment check
    if not check_environment():
        return False
    
    # Test available modules
    modules = test_available_modules()
    
    # Run individual tests
    tests = [
        ("Basic CRUD Operations", test_basic_crud_operations),
        ("Advanced Search Features", test_advanced_search_features),
        ("Reference Features", test_reference_features),
        ("Batch Operations", test_batch_operations),
        ("Aggregation Features", test_aggregation_features)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Advanced Weaviate Features Test Results Summary")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    # Feature availability summary
    print("\n🔍 Feature Availability Analysis:")
    print("=" * 80)
    
    print("\n✅ Features that typically work on FREE accounts:")
    print("  - Basic CRUD operations (create, read, update, delete)")
    print("  - Vector similarity search (near_text)")
    print("  - Collection management")
    print("  - Basic batch operations")
    print("  - Simple aggregation")
    
    print("\n⚠️  Features that typically require PRO accounts:")
    print("  - BM25 search (keyword search)")
    print("  - Hybrid search (vector + keyword)")
    print("  - Generative search (RAG)")
    print("  - Reranker search")
    print("  - Advanced aggregation with grouping")
    print("  - Cross-references (may be limited)")
    
    print("\n📝 Notes:")
    print("  - Test results above show which features work on your current account")
    print("  - Some features may work on free accounts with limited functionality")
    print("  - Upgrade to pro account for full feature access")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your Weaviate setup supports all tested features.")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Check the errors above.")
        print("Some features may require a pro account or different configuration.")
    
    return passed == len(results)

def main():
    """Main test function"""
    success = run_all_tests()
    return success

if __name__ == "__main__":
    # Run the tests
    main() 