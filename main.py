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
    
    def __init__(self, db_path: str = "./chroma_db", provider: str = 'openai', model: str = None):
        """
        Initialize the application
        
        Args:
            db_path: Path to the vector database
            provider: LLM provider
            model: Model name
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
        
        # Initialize agent
        try:
            self.agent = IFSAgenticRAG(self.vector_db, provider=provider, model=model)
            logger.info(f"IFS Customization Agent Studio initialized successfully (Provider: {provider})")
        except (ValueError, ImportError) as e:
            logger.warning(f"Agent not initialized: {e}")
            logger.warning("You can still scrape documentation, but queries require dependencies and API keys")


    
    def scrape_docs(self, start_url: str = None, max_pages: int = 50, output_dir: str = None) -> None:
        """
        Scrape IFS documentation and add to vector database
        
        Args:
            start_url: Starting URL for scraping
            max_pages: Maximum number of pages to scrape
            output_dir: Directory to save scraped pages to
        """
        if not self.vector_db and not output_dir:
            logger.error("Vector database not initialized and no output directory specified.")
            return
        
        logger.info("Starting documentation scraping...")
        
        scraper = IFSDocsScraper()
        
        if start_url is None:
            start_url = os.getenv('IFS_DOCS_URL', 'https://docs.ifs.com')
        
        # Scrape documentation
        documents = scraper.scrape_documentation(start_url=start_url, max_pages=max_pages, output_dir=output_dir)
        
        if documents:
            logger.info(f"Scraped {len(documents)} documents")
            
            if self.vector_db:
                # Add to vector database
                self.vector_db.add_documents(documents)
                
                stats = self.vector_db.get_stats()
                logger.info(f"Database now contains {stats['total_chunks']} chunks")
        else:
            logger.warning("No documents were scraped")
    
    def ingest_core_code(self, dir_path: str) -> None:
        """
        Ingest IFS core code files from a directory
        
        Args:
            dir_path: Path to the directory containing core code
        """
        if not self.vector_db:
            logger.error("Vector database not initialized.")
            return
            
        if not os.path.isdir(dir_path):
            logger.error(f"Directory not found: {dir_path}")
            return
            
        logger.info(f"Scanning {dir_path} for core code files...")
        
        documents = []
        target_extensions = {'.plsql', '.plsvc', '.views', '.api', '.svc', '.ins', '.cpp', '.java', '.cs'}
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in target_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        if content:
                            documents.append({
                                'title': file,
                                'url': file_path,  # Use file path as URL for reference
                                'content': content,
                                'type': 'core_code',
                                'code_examples': [] # No separate code examples for core code
                            })
                            
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
        
        if documents:
            logger.info(f"Found {len(documents)} core code files. Ingesting...")
            self.vector_db.add_documents(documents)
            
            stats = self.vector_db.get_stats()
            logger.info(f"Database now contains {stats['total_chunks']} chunks")
        else:
            logger.warning("No matching core code files found.")

    def query(self, question: str) -> str:
        """
        Query the RAG agent
        
        Args:
            question: User question
            
        Returns:
            Agent response
        """
        if not self.agent:
            return "Error: Agent not initialized. Please ensure dependencies are installed and API keys (OPENAI_API_KEY or GROQ_API_KEY) are set in .env file"
        
        return self.agent.ask(question)
    
    def interactive_mode(self) -> None:
        """Run in interactive CLI mode"""
        if not self.agent:
            print("\n❌ Error: Agent not initialized. Please ensure dependencies are installed and API keys are set in .env file")
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
        '--ingest-core',
        action='store_true',
        help='Ingest IFS core code files from directory'
    )
    
    parser.add_argument(
        '--core-path',
        type=str,
        default='./Ref_Core',
        help='Path to core code directory (default: ./Ref_Core)'
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
        '--output-dir',
        type=str,
        help='Directory to save scraped pages to (optional)'
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

    parser.add_argument(
        '--provider',
        type=str,
        default='openai',
        choices=['openai', 'groq'],
        help='LLM provider to use (openai or groq)'
    )

    parser.add_argument(
        '--model',
        type=str,
        help='Specific model name to use (e.g. gpt-4, llama3-70b-8192)'
    )
    
    args = parser.parse_args()
    
    # Initialize the studio
    studio = IFSCustomizationStudio(
        db_path=args.db_path,
        provider=args.provider,
        model=args.model
    )
    
    # Handle scripting
    if args.scrape:
        studio.scrape_docs(start_url=args.url, max_pages=args.max_pages, output_dir=args.output_dir)
        return
        
    if args.ingest_core:
        studio.ingest_core_code(dir_path=args.core_path)
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
