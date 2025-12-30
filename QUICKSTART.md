# Quick Start Guide - IFS Customization Agent Studio

## What is this?

An **Agentic RAG (Retrieval-Augmented Generation)** system that:
1. Scrapes documentation from docs.ifs.com
2. Stores it in a vector database for semantic search
3. Uses AI to answer your questions with relevant code examples

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you encounter space issues, install core packages only:

```bash
pip install beautifulsoup4 requests python-dotenv chromadb langchain langchain-openai
```

### 2. Set up OpenAI API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
IFS_DOCS_URL=https://docs.ifs.com
CHROMA_DB_PATH=./chroma_db
```

## Usage

### Step 1: Scrape Documentation

Collect and index IFS documentation:

```bash
python main.py --scrape --max-pages 50
```

This will:
- Scrape up to 50 pages from docs.ifs.com
- Extract text content and code examples
- Store them in a local vector database (`./chroma_db`)

### Step 2: Ask Questions

Start the interactive assistant:

```bash
python main.py
```

Then ask questions like:
- "How do I create a custom field in IFS?"
- "Show me code to add a custom button to a page"
- "How do I implement a custom event action?"
- "What's the best way to integrate with IFS API?"

### Alternative: Single Query

Execute a single query without interactive mode:

```bash
python main.py --query "How do I customize an IFS form?"
```

## Commands

In interactive mode, you can use:
- **Type your question** - Get an AI-powered answer with code
- **`clear`** - Clear conversation history
- **`stats`** - Show database statistics
- **`quit`** or **`exit`** - Exit the application

## Demo

Want to see how it works without installing dependencies?

```bash
python demo.py
```

This shows the system architecture and capabilities.

## Troubleshooting

### "chromadb not installed"
```bash
pip install chromadb sentence-transformers
```

### "langchain not installed"
```bash
pip install langchain langchain-openai
```

### "Agent not initialized"
Make sure your `OPENAI_API_KEY` is set in the `.env` file.

### Scraping issues
- Check your internet connection
- Try reducing `--max-pages` if you hit rate limits
- Some pages may be behind authentication

## Architecture

```
User Query → Scraper → Vector DB → RAG Agent → Code Response
              ↓          ↓           ↓
         docs.ifs.com  ChromaDB   OpenAI GPT
```

## Example Output

```
You: How do I create a custom field in IFS?

Agent: To create a custom field in IFS, you need to:

1. Define the custom field in the projection:
   ```sql
   projection CustomFieldExample {
     entity MyEntity {
       attribute CustomField Text;
     }
   }
   ```

2. Add it to the client:
   ```javascript
   field CustomField {
     label = "My Custom Field";
     required = [true];
   }
   ```

3. Implement business logic if needed...
[Full response with more details and code]
```

## Features

✅ Intelligent document scraping  
✅ Semantic search with vector embeddings  
✅ Context-aware responses  
✅ Code generation with explanations  
✅ Conversation history  
✅ Multiple query modes  

## Next Steps

1. Scrape more documentation for better coverage
2. Experiment with different queries
3. Clear and rebuild the database periodically for updates
4. Customize the scraper for specific documentation sections

Enjoy using IFS Customization Agent Studio! 🚀
