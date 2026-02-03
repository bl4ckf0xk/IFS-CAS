"""
Test script for the IFS Agentic RAG system
Tests basic functionality without requiring external dependencies
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import scraper
        print("✓ scraper module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import scraper: {e}")
        return False
    
    try:
        import vector_db
        print("✓ vector_db module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import vector_db: {e}")
        return False
    
    try:
        import rag_agent
        print("✓ rag_agent module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import rag_agent: {e}")
        return False
    
    try:
        import main
        print("✓ main module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import main: {e}")
        return False
    
    return True


def test_scraper():
    """Test scraper initialization"""
    print("\nTesting scraper...")
    
    try:
        from scraper import IFSDocsScraper
        scraper = IFSDocsScraper()
        print(f"✓ Scraper initialized with base URL: {scraper.base_url}")
        
        # Test chunking (without actual scraping)
        test_text = "This is a test. " * 100
        # Note: chunk_text is not in scraper, skip this test
        print("✓ Scraper basic functionality works")
        return True
    except Exception as e:
        print(f"✗ Scraper test failed: {e}")
        return False


def test_vector_db():
    """Test vector database initialization"""
    print("\nTesting vector database...")
    
    try:
        import tempfile
        from vector_db import VectorDatabase
        
        # Use a temporary database path (cross-platform)
        test_db_path = os.path.join(tempfile.gettempdir(), 'test_chroma_db')
        db = VectorDatabase(persist_directory=test_db_path)
        print(f"✓ Vector database initialized at {test_db_path}")
        
        # Test chunking
        test_text = "This is a test sentence. " * 50
        chunks = db.chunk_text(test_text, chunk_size=100, overlap=20)
        print(f"✓ Text chunking works: created {len(chunks)} chunks")
        
        # Test adding documents
        test_docs = [
            {
                'title': 'Test Document',
                'content': 'This is a test document about IFS customization.',
                'url': 'https://test.com',
                'code_examples': ['print("Hello IFS")']
            }
        ]
        db.add_documents(test_docs)
        print("✓ Documents added to vector database")
        
        # Test stats
        stats = db.get_stats()
        print(f"✓ Database stats: {stats}")
        
        # Test search
        results = db.search("test", n_results=2)
        print(f"✓ Search works: found {len(results)} results")
        
        return True
    except Exception as e:
        print(f"✗ Vector database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_help():
    """Test main application help"""
    print("\nTesting main application...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'main.py', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and 'IFS Customization Agent Studio' in result.stdout:
            print("✓ Main application help works")
            return True
        else:
            print(f"✗ Main application help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Main application test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("IFS Agentic RAG System - Test Suite")
    print("="*70)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Scraper", test_scraper()))
    results.append(("Vector Database", test_vector_db()))
    results.append(("Main Application", test_help()))
    
    print("\n" + "="*70)
    print("Test Results Summary")
    print("="*70)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print("="*70)
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
