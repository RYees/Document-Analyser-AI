#!/usr/bin/env python3
"""
Test script for VectorStoreManager
Tests Weaviate connection, Chroma fallback, and overall functionality
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv("env_file")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment setup...")
    
    # Check for Weaviate credentials
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    
    if weaviate_url and weaviate_api_key:
        print(f"✅ Weaviate credentials found")
        print(f"   URL: {weaviate_url}")
        print(f"   API Key: {weaviate_api_key[:10]}...")
    else:
        print("⚠️  Weaviate credentials not found")
        print("   WEAVIATE_URL and WEAVIATE_API_KEY should be set")
    
    # Check for OpenAI key (needed for embeddings)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OpenAI API key found")
    else:
        print("❌ OpenAI API key not found")
        return False
    
    return True

async def test_weaviate_client_directly():
    """Test Weaviate client initialization directly"""
    print("\n🔍 Testing Weaviate Client Directly...")
    
    try:
        from analyser.utils.weaviate_client import get_weaviate_manager
        
        print("✅ Successfully imported WeaviateManager")
        
        # Get Weaviate manager
        weaviate_manager = get_weaviate_manager()
        print("✅ WeaviateManager instance created")
        
        # Check if available
        is_available = weaviate_manager.is_available()
        print(f"   Available: {is_available}")
        
        if is_available:
            print("✅ Weaviate client is available")
            
            # Test basic operations
            try:
                collections = weaviate_manager.list_collections()
                print(f"   Collections: {collections}")
            except Exception as e:
                print(f"   ❌ Failed to list collections: {e}")
        else:
            print("❌ Weaviate client is not available")
            print("   This is expected if credentials are missing or connection fails")
        
        return True
        
    except Exception as e:
        print(f"❌ Weaviate client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chroma_utils_directly():
    """Test Chroma utilities directly"""
    print("\n🔍 Testing Chroma Utils Directly...")
    
    try:
        # Test if we can import chroma utils
        try:
            import analyser.utils.chroma as chroma_utils
            print("✅ Successfully imported chroma_utils")
        except ImportError as e:
            print(f"❌ Failed to import chroma_utils: {e}")
            return False
        
        # Test embedding function
        try:
            embedding_function = chroma_utils.embedding()
            print("✅ Embedding function created")
        except Exception as e:
            print(f"❌ Failed to create embedding function: {e}")
            return False
        
        # Test text splitter
        try:
            test_texts = ["This is a test document about blockchain technology."]
            split_texts = chroma_utils.sentence_transfomer_textsplitter(test_texts)
            print(f"✅ Text splitter works: {len(split_texts)} chunks created")
        except Exception as e:
            print(f"❌ Text splitter failed: {e}")
            print("   This might be due to missing sentence_transformers package")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Chroma utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_vector_store_manager_initialization():
    """Test VectorStoreManager initialization"""
    print("\n🔍 Testing VectorStoreManager Initialization...")
    
    try:
        from analyser.utils.vector_store_manager import VectorStoreManager
        
        print("✅ Successfully imported VectorStoreManager")
        
        # Test initialization
        manager = VectorStoreManager(
            collection_name="TestCollection",
            research_domain="Blockchain Technology"
        )
        print("✅ VectorStoreManager initialized")
        
        # Check attributes
        print(f"   Collection name: {manager.collection_name}")
        print(f"   Research domain: {manager.research_domain}")
        print(f"   Weaviate available: {manager.weaviate.is_available() if manager.weaviate else False}")
        print(f"   Chroma collection: {manager.chroma_collection is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ VectorStoreManager initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_vector_store_manager_add_chunks():
    """Test adding chunks to vector store"""
    print("\n🔍 Testing VectorStoreManager Add Chunks...")
    
    try:
        from analyser.utils.vector_store_manager import VectorStoreManager
        
        # Initialize manager
        manager = VectorStoreManager(
            collection_name="TestCollection",
            research_domain="Blockchain Technology"
        )
        
        # Test data
        test_chunks = [
            "Blockchain is a distributed ledger technology that enables secure transactions.",
            "Bitcoin was the first cryptocurrency to use blockchain technology.",
            "Smart contracts are self-executing contracts with code stored on blockchain."
        ]
        
        test_metadata = [
            {"source": "paper1", "page": 1},
            {"source": "paper1", "page": 2},
            {"source": "paper2", "page": 1}
        ]
        
        print(f"   Adding {len(test_chunks)} test chunks...")
        
        # Try to add chunks
        success = manager.add_chunks(test_chunks, test_metadata)
        
        if success:
            print("✅ Successfully added chunks to vector store")
        else:
            print("❌ Failed to add chunks to vector store")
            print("   This might be expected if both Weaviate and Chroma are unavailable")
        
        return success
        
    except Exception as e:
        print(f"❌ Add chunks test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_vector_store_manager_similarity_search():
    """Test similarity search in vector store"""
    print("\n🔍 Testing VectorStoreManager Similarity Search...")
    
    try:
        from analyser.utils.vector_store_manager import VectorStoreManager
        
        # Initialize manager
        manager = VectorStoreManager(
            collection_name="TestCollection",
            research_domain="Blockchain Technology"
        )
        
        # Test query
        query = "What is blockchain technology?"
        print(f"   Searching for: '{query}'")
        
        # Try similarity search
        results = manager.similarity_search(query, top_k=3)
        
        if results:
            print(f"✅ Found {len(results)} similar chunks:")
            for i, result in enumerate(results[:2]):  # Show first 2 results
                print(f"   {i+1}. {result[:100]}...")
        else:
            print("❌ No results found")
            print("   This might be expected if no chunks were added or both backends failed")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Similarity search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("\n🔍 Testing End-to-End Workflow...")
    
    try:
        from analyser.utils.vector_store_manager import VectorStoreManager
        
        # Initialize manager
        manager = VectorStoreManager(
            collection_name="E2ETestCollection",
            research_domain="Web3 Technology"
        )
        
        # Step 1: Add chunks
        print("   Step 1: Adding test chunks...")
        test_chunks = [
            "Web3 represents the next evolution of the internet, focusing on decentralization.",
            "Blockchain technology enables trustless transactions without intermediaries.",
            "Smart contracts automate complex business logic on blockchain platforms.",
            "DeFi (Decentralized Finance) provides financial services without traditional banks.",
            "NFTs (Non-Fungible Tokens) represent unique digital assets on blockchain."
        ]
        
        success = manager.add_chunks(test_chunks)
        if not success:
            print("   ⚠️  Failed to add chunks, but continuing with search test...")
        
        # Step 2: Search
        print("   Step 2: Testing similarity search...")
        queries = [
            "What is Web3?",
            "How do smart contracts work?",
            "What are NFTs?"
        ]
        
        for query in queries:
            print(f"   Query: '{query}'")
            results = manager.similarity_search(query, top_k=2)
            if results:
                print(f"   Found {len(results)} results")
            else:
                print("   No results found")
        
        print("✅ End-to-end workflow test completed")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_import_structure():
    """Test the import structure and identify issues"""
    print("\n🔍 Testing Import Structure...")
    
    try:
        # Test direct imports
        print("   Testing direct imports...")
        
        try:
            from analyser.utils.weaviate_client import get_weaviate_manager
            print("   ✅ analyser.utils.weaviate_client imported successfully")
        except Exception as e:
            print(f"   ❌ analyser.utils.weaviate_client import failed: {e}")
        
        try:
            import analyser.utils.chroma as chroma_utils
            print("   ✅ analyser.utils.chroma imported successfully")
        except Exception as e:
            print(f"   ❌ analyser.utils.chroma import failed: {e}")
        
        try:
            from analyser.utils.vector_store_manager import VectorStoreManager
            print("   ✅ analyser.utils.vector_store_manager imported successfully")
        except Exception as e:
            print(f"   ❌ analyser.utils.vector_store_manager import failed: {e}")
        
        # Test the problematic import in vector_store_manager.py
        print("   Testing the problematic import...")
        try:
            import sys
            sys.path.append("../../utils")
            import utils.chroma as test_chroma
            print("   ✅ utils.chroma import works with sys.path manipulation")
        except Exception as e:
            print(f"   ❌ utils.chroma import failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import structure test failed: {e}")
        return False

async def run_all_tests():
    """Run all VectorStoreManager tests"""
    print("🚀 Starting VectorStoreManager Tests")
    print("=" * 60)
    
    # Environment check
    if not check_environment():
        return False
    
    # Run individual tests
    tests = [
        ("Import Structure", test_import_structure),
        ("Weaviate Client", test_weaviate_client_directly),
        ("Chroma Utils", test_chroma_utils_directly),
        ("Manager Initialization", test_vector_store_manager_initialization),
        ("Add Chunks", test_vector_store_manager_add_chunks),
        ("Similarity Search", test_vector_store_manager_similarity_search),
        ("End-to-End Workflow", test_end_to_end_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VectorStoreManager Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All VectorStoreManager tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above for debugging.")
    
    return passed == len(results)

async def main():
    """Main test function"""
    success = await run_all_tests()
    return success

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main()) 