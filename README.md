# IFS-CAS (IFS Customization Agent Studio)

An intelligent agentic RAG (Retrieval-Augmented Generation) system that scrapes documentation from docs.ifs.com and provides code-based answers to user queries about IFS customization.

## Features

🤖 **Agentic RAG System**: Uses advanced AI to understand queries and generate relevant code examples  
🌐 **Documentation Scraper**: Automatically scrapes and indexes IFS documentation  
💾 **Vector Database**: Efficient semantic search using ChromaDB  
💬 **Interactive CLI**: User-friendly command-line interface  
🔍 **Smart Retrieval**: Finds the most relevant documentation and code examples  
📝 **Code Generation**: Provides working code examples with explanations

## Architecture

The system consists of four main components:

1. **Web Scraper** (`scraper.py`): Scrapes documentation from docs.ifs.com
2. **Vector Database** (`vector_db.py`): Stores and retrieves documentation using semantic search
3. **RAG Agent** (`rag_agent.py`): Intelligent agent that generates answers with code examples
4. **Main Application** (`main.py`): CLI interface for user interaction

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for the RAG agent)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/bl4ckf0xk/IFS-CAS.git
cd IFS-CAS
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

### 1. Scrape IFS Documentation

First, scrape and index the IFS documentation:

```bash
python main.py --scrape --max-pages 50
```

Options:
- `--url`: Custom starting URL (default: https://docs.ifs.com)
- `--max-pages`: Maximum number of pages to scrape (default: 50)

### 2. Interactive Mode

Launch the interactive CLI to ask questions:

```bash
python main.py
```

Example interaction:
```
You: How do I create a custom field in IFS?

Agent: To create a custom field in IFS, you can use the following approach...
[Provides detailed explanation with code examples]
```

Available commands in interactive mode:
- Type your question to get an answer
- `clear` - Clear conversation history
- `stats` - Show database statistics
- `quit` or `exit` - Exit the application

### 3. Single Query Mode

Execute a single query without entering interactive mode:

```bash
python main.py --query "How do I customize an IFS form?"
```

## Example Queries

Here are some example queries you can try:

- "How do I create a custom projection in IFS Cloud?"
- "Show me code to add a custom field to a page"
- "How do I implement a custom event action in IFS?"
- "What's the best way to extend IFS functionality?"
- "Show me an example of IFS API integration"

## Project Structure

```
IFS-CAS/
├── main.py              # Main application entry point
├── scraper.py           # Web scraper for IFS documentation
├── vector_db.py         # Vector database management
├── rag_agent.py         # Agentic RAG implementation
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: OpenAI API key for the RAG agent
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize the scraping target
IFS_DOCS_URL=https://docs.ifs.com

# Optional: Vector database path
CHROMA_DB_PATH=./chroma_db
```

## How It Works

1. **Scraping**: The scraper crawls docs.ifs.com, extracting documentation text and code examples
2. **Indexing**: Documents are chunked and stored in a vector database with embeddings
3. **Query Processing**: User queries are converted to vector embeddings
4. **Retrieval**: Relevant documentation chunks are retrieved using similarity search
5. **Generation**: The LLM generates a response with code examples based on retrieved context

## Technologies Used

- **LangChain**: Framework for building LLM applications
- **OpenAI GPT**: Large language model for generating responses
- **ChromaDB**: Vector database for semantic search
- **BeautifulSoup**: Web scraping and parsing
- **Sentence Transformers**: Text embeddings for semantic search

## Troubleshooting

### "Agent not initialized" error
- Make sure you have set `OPENAI_API_KEY` in your `.env` file
- Verify the API key is valid

### Scraping errors
- Check your internet connection
- The docs.ifs.com website structure may have changed
- Try reducing `--max-pages` if you encounter rate limiting

### Database issues
- Delete the `chroma_db` directory and re-scrape if you encounter database errors
- Make sure you have write permissions in the project directory

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and development purposes. Always respect the terms of service of the websites you scrape and use API keys responsibly.
