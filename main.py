"""
Main application for the IFS Agentic RAG system
Provides CLI interface for interacting with the RAG agent
"""

import os
import argparse
from dotenv import load_dotenv
import logging

from scraper import IFSDocsScraper
from vector_db import VectorDatabase
from rag_agent import IFSAgenticRAG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IFSCustomizationStudio:
    """Main application class for IFS Customization Agent Studio"""
    
    def __init__(self, db_path: str = "./chroma_db"):
        """
        Initialize the application
        
        Args:
            db_path: Path to the vector database
        """
        load_dotenv()
        
        self.db_path = db_path
        self.vector_db = None
        self.agent = None
        
        # Initialize vector database with error handling
        try:
            self.vector_db = VectorDatabase(persist_directory=db_path)
        except ImportError as e:
            logger.warning(f"Vector database not initialized: {e}")
            logger.warning("Install dependencies with: pip install chromadb sentence-transformers")
            return
        
        # Initialize agent if OpenAI key is available
        try:
            self.agent = IFSAgenticRAG(self.vector_db)
            logger.info("IFS Customization Agent Studio initialized successfully")
        except (ValueError, ImportError) as e:
            logger.warning(f"Agent not initialized: {e}")
            logger.warning("You can still scrape documentation, but queries require dependencies and OPENAI_API_KEY")
    
    def scrape_docs(self, start_url: str = None, max_pages: int = 50) -> None:
        """
        Scrape IFS documentation and add to vector database
        
        Args:
            start_url: Starting URL for scraping
            max_pages: Maximum number of pages to scrape
        """
        if not self.vector_db:
            logger.error("Vector database not initialized. Install required dependencies.")
            return
        
        logger.info("Starting documentation scraping...")
        
        scraper = IFSDocsScraper()
        
        if start_url is None:
            start_url = os.getenv('IFS_DOCS_URL', 'https://docs.ifs.com')
        
        # Scrape documentation
        documents = scraper.scrape_documentation(start_url=start_url, max_pages=max_pages)
        
        if documents:
            logger.info(f"Scraped {len(documents)} documents")
            
            # Add to vector database
            self.vector_db.add_documents(documents)
            
            stats = self.vector_db.get_stats()
            logger.info(f"Database now contains {stats['total_chunks']} chunks")
        else:
            logger.warning("No documents were scraped")
    
    def query(self, question: str) -> str:
        """
        Query the RAG agent
        
        Args:
            question: User question
            
        Returns:
            Agent response
        """
        if not self.agent:
            return "Error: Agent not initialized. Please set OPENAI_API_KEY in .env file"
        
        return self.agent.ask(question)
    
    def interactive_mode(self) -> None:
        """Run in interactive CLI mode"""
        if not self.agent:
            print("\n❌ Error: Agent not initialized. Please set OPENAI_API_KEY in .env file")
            print("You can still use the --scrape command to collect documentation.\n")
            return
        
        print("\n" + "="*70)
        print("🤖 IFS Customization Agent Studio - Interactive Mode")
        print("="*70)
        print("\nAsk questions about IFS customization and get code examples!")
        print("Commands:")
        print("  - Type your question to get an answer")
        print("  - 'clear' - Clear conversation history")
        print("  - 'stats' - Show database statistics")
        print("  - 'quit' or 'exit' - Exit the application")
        print("="*70 + "\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break
                
                if user_input.lower() == 'clear':
                    self.agent.clear_history()
                    print("✅ Conversation history cleared.\n")
                    continue
                
                if user_input.lower() == 'stats':
                    stats = self.vector_db.get_stats()
                    print(f"\n📊 Database Statistics:")
                    print(f"   Total chunks: {stats['total_chunks']}")
                    print(f"   Collection: {stats['collection_name']}\n")
                    continue
                
                # Generate response
                print("\n🤔 Thinking...\n")
                response = self.agent.ask(user_input)
                print(f"Agent: {response}\n")
                print("-" * 70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {str(e)}")
                print(f"\n❌ Error: {str(e)}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="IFS Customization Agent Studio - Agentic RAG for IFS Documentation"
    )
    
    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Scrape IFS documentation and add to vector database'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='Starting URL for scraping (default: from .env or https://docs.ifs.com)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help='Maximum number of pages to scrape (default: 50)'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Single query to execute (non-interactive mode)'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='./chroma_db',
        help='Path to vector database (default: ./chroma_db)'
    )
    
    args = parser.parse_args()
    
    # Initialize the studio
    studio = IFSCustomizationStudio(db_path=args.db_path)
    
    # Handle scraping
    if args.scrape:
        studio.scrape_docs(start_url=args.url, max_pages=args.max_pages)
        return
    
    # Handle single query
    if args.query:
        response = studio.query(args.query)
        print(f"\nQuestion: {args.query}\n")
        print(f"Answer:\n{response}\n")
        return
    
    # Default: interactive mode
    studio.interactive_mode()


if __name__ == "__main__":
    main()
