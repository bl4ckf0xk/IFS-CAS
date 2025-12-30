# Project Structure

```
IFS-CAS/
│
├── README.md              # Main project documentation
├── QUICKSTART.md          # Quick start guide for new users
├── EXAMPLES.md            # Usage examples and sample outputs
├── PROJECT_STRUCTURE.md   # This file - project organization
│
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── requirements.txt       # Python dependencies
│
├── main.py               # Main application entry point
│   ├── CLI argument parsing
│   ├── Application initialization
│   ├── Interactive mode
│   └── Batch processing mode
│
├── scraper.py            # Web scraper module
│   ├── IFSDocsScraper class
│   │   ├── scrape_page()           # Scrape single page
│   │   ├── discover_links()        # Find documentation links
│   │   └── scrape_documentation()  # Scrape multiple pages
│   └── Features:
│       ├── BeautifulSoup HTML parsing
│       ├── Code example extraction
│       └── Rate limiting
│
├── vector_db.py          # Vector database management
│   ├── VectorDatabase class
│   │   ├── chunk_text()       # Split text into chunks
│   │   ├── add_documents()    # Add documents to DB
│   │   ├── search()           # Semantic search
│   │   └── get_stats()        # Database statistics
│   └── Features:
│       ├── ChromaDB integration
│       ├── Text chunking with overlap
│       └── Metadata management
│
├── rag_agent.py          # RAG agent implementation
│   ├── IFSAgenticRAG class
│   │   ├── retrieve_context()    # Get relevant docs
│   │   ├── format_context()      # Format for LLM
│   │   ├── generate_response()   # Generate answer
│   │   ├── ask()                 # Simple query interface
│   │   └── clear_history()       # Reset conversation
│   └── Features:
│       ├── LangChain integration
│       ├── OpenAI GPT integration
│       ├── Conversation history
│       └── Context-aware responses
│
├── demo.py               # Demonstration script
│   └── Shows system capabilities without full dependencies
│
└── test_system.py        # Test suite
    └── Basic functionality tests

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│          "How do I create a custom field in IFS?"               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MAIN.PY                                  │
│                  (Application Controller)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG_AGENT.PY                                │
│              (Retrieval-Augmented Generation)                    │
│                                                                  │
│  1. Query Processing                                             │
│  2. Context Retrieval ──────────┐                               │
│  3. LLM Prompt Construction     │                               │
│  4. Response Generation         │                               │
└─────────────────────────────────┼───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VECTOR_DB.PY                                 │
│                 (Semantic Search Engine)                         │
│                                                                  │
│  1. Convert query to embeddings                                  │
│  2. Search similar chunks                                        │
│  3. Return relevant content                                      │
│                                                                  │
│  Database: ./chroma_db/                                          │
│    ├── Documentation chunks                                      │
│    ├── Code examples                                             │
│    └── Embeddings                                                │
└──────────────────────────────────────────────────────────────────┘
                             ▲
                             │
                             │ (Data Population)
                             │
┌─────────────────────────────────────────────────────────────────┐
│                       SCRAPER.PY                                 │
│                   (Documentation Scraper)                        │
│                                                                  │
│  1. Fetch pages from docs.ifs.com                                │
│  2. Parse HTML content                                           │
│  3. Extract text and code                                        │
│  4. Send to vector_db                                            │
└──────────────────────────────────────────────────────────────────┘
                             ▲
                             │
┌─────────────────────────────────────────────────────────────────┐
│                     https://docs.ifs.com                         │
│                   (Source Documentation)                         │
└──────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Scraping Flow
```
User Command → main.py --scrape
              ↓
         scraper.py (IFSDocsScraper)
              ↓
         Fetch pages from docs.ifs.com
              ↓
         Extract content & code examples
              ↓
         vector_db.py (VectorDatabase)
              ↓
         Chunk text & create embeddings
              ↓
         Store in ChromaDB
```

### Query Flow
```
User Question → main.py (interactive or --query)
               ↓
          rag_agent.py (IFSAgenticRAG)
               ↓
          vector_db.py (semantic search)
               ↓
          Retrieve relevant chunks
               ↓
          Format context + user query
               ↓
          OpenAI GPT (LLM)
               ↓
          Generated response with code
               ↓
          Display to user
```

## Dependencies Tree

```
main.py
├── python-dotenv (load environment variables)
├── scraper.py
│   ├── beautifulsoup4 (HTML parsing)
│   └── requests (HTTP requests)
├── vector_db.py
│   ├── chromadb (vector database)
│   └── sentence-transformers (embeddings)
└── rag_agent.py
    ├── langchain (LLM framework)
    ├── langchain-openai (OpenAI integration)
    └── openai (API client)
```

## Configuration Files

- **.env** (not in repo, create from .env.example)
  - OPENAI_API_KEY: Your OpenAI API key
  - IFS_DOCS_URL: Base URL for scraping
  - CHROMA_DB_PATH: Database location

- **.gitignore**
  - Python artifacts (__pycache__, *.pyc)
  - Virtual environments (venv/, env/)
  - Environment files (.env)
  - Database files (chroma_db/)
  - IDE files (.vscode/, .idea/)

## Key Features

### 1. Modular Design
Each component (scraper, vector_db, rag_agent) is independent and can be used separately.

### 2. Graceful Degradation
The system provides helpful error messages when dependencies are missing.

### 3. Flexible Usage
- Interactive CLI mode for conversations
- Single query mode for quick questions
- Batch scraping mode for data collection

### 4. Data Persistence
- ChromaDB persists data between sessions
- No need to re-scrape on every use
- Incremental updates possible

### 5. Conversation Memory
- RAG agent maintains conversation history
- Context-aware follow-up questions
- Clear history when needed

## Usage Patterns

### Development Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
```

### First-Time Use
```bash
python main.py --scrape --max-pages 50    # Collect data
python main.py                             # Start asking questions
```

### Regular Use
```bash
python main.py                             # Interactive mode
python main.py --query "your question"     # Single query
```

### Maintenance
```bash
python main.py --scrape --max-pages 100    # Update database
# Optionally delete chroma_db/ to start fresh
```

## Extension Points

### Adding New Data Sources
Modify `scraper.py` to:
- Add new `scrape_*` methods for different sites
- Implement custom parsers for specific doc formats
- Add authentication for protected content

### Custom Embeddings
Modify `vector_db.py` to:
- Use different embedding models
- Implement custom chunking strategies
- Add metadata filtering

### Enhanced Agent Capabilities
Modify `rag_agent.py` to:
- Use different LLM models
- Add tool calling capabilities
- Implement custom prompt templates
- Add memory management strategies

## Security Considerations

1. **API Keys**: Never commit .env file
2. **Rate Limiting**: Scraper includes delays
3. **Input Validation**: All user inputs are validated
4. **Error Handling**: Comprehensive try-catch blocks
5. **Dependencies**: Regular updates recommended
