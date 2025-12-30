"""
Vector database management for storing and retrieving documentation
Uses ChromaDB for vector storage and similarity search
"""

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Install with: pip install chromadb")

from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDatabase:
    """Manages vector storage and retrieval for documentation"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector database
        
        Args:
            persist_directory: Directory to persist the database
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "chromadb is required but not installed. "
                "Install it with: pip install chromadb sentence-transformers"
            )
        
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="ifs_documentation",
            metadata={"description": "IFS documentation and code examples"}
        )
        
        logger.info(f"Vector database initialized at {persist_directory}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # Filter empty chunks
    
    def add_documents(self, documents: List[Dict[str, str]]) -> None:
        """
        Add documents to the vector database
        
        Args:
            documents: List of document dictionaries with 'title', 'content', 'url', etc.
        """
        logger.info(f"Adding {len(documents)} documents to vector database")
        
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        doc_id = 0
        for doc in documents:
            # Chunk the main content
            content_chunks = self.chunk_text(doc.get('content', ''))
            
            for i, chunk in enumerate(content_chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    'title': doc.get('title', 'Untitled'),
                    'url': doc.get('url', ''),
                    'type': 'content',
                    'chunk_index': i
                })
                all_ids.append(f"doc_{doc_id}_chunk_{i}")
            
            # Add code examples as separate entries
            for j, code in enumerate(doc.get('code_examples', [])):
                if code and len(code) > 20:  # Filter very short code snippets
                    all_chunks.append(f"Code example:\n{code}")
                    all_metadatas.append({
                        'title': doc.get('title', 'Untitled'),
                        'url': doc.get('url', ''),
                        'type': 'code',
                        'example_index': j
                    })
                    all_ids.append(f"doc_{doc_id}_code_{j}")
            
            doc_id += 1
        
        if all_chunks:
            # Add to ChromaDB in batches
            batch_size = 100
            for i in range(0, len(all_chunks), batch_size):
                batch_chunks = all_chunks[i:i + batch_size]
                batch_metadatas = all_metadatas[i:i + batch_size]
                batch_ids = all_ids[i:i + batch_size]
                
                self.collection.add(
                    documents=batch_chunks,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
            
            logger.info(f"Added {len(all_chunks)} chunks to the database")
        else:
            logger.warning("No chunks to add to database")
    
    def search(self, query: str, n_results: int = 5, filter_type: Optional[str] = None) -> List[Dict]:
        """
        Search the vector database for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_type: Optional filter for document type ('content' or 'code')
            
        Returns:
            List of relevant documents with metadata
        """
        where_filter = {"type": filter_type} if filter_type else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get statistics about the database"""
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': self.collection.name
        }


if __name__ == "__main__":
    # Test the vector database
    db = VectorDatabase()
    
    # Test data
    test_docs = [
        {
            'title': 'Test Document',
            'content': 'This is a test document about IFS.',
            'url': 'https://example.com',
            'code_examples': ['print("Hello World")']
        }
    ]
    
    db.add_documents(test_docs)
    results = db.search("test", n_results=2)
    print(f"Search results: {len(results)}")
    print(db.get_stats())
