# IFS-CAS (IFS Customization Agent Studio)

An intelligent agentic RAG (Retrieval-Augmented Generation) system that scrapes documentation from docs.ifs.com and provides code-based answers to user queries about IFS customization.

## Features

- 🤖 **Agentic RAG System**: Uses advanced AI to understand queries and generate relevant code examples
- 🚀 **Multi-Provider Support**: Supports OpenAI (GPT-4/3.5) and **Groq** (Llama 3, Mixtral) for ultra-fast responses
- 🌐 **Optimized Scraper**: persistent browser session for fast, robust documentation scraping
- 💾 **Vector Database**: Efficient semantic search using ChromaDB (with OpenAI embeddings fallback)
- 📂 **Core Code Ingestion**: Ingests local IFS source code (`.plsql`, `.svc`, etc.) for deep codebase understanding
- 💬 **Interactive CLI**: User-friendly command-line interface
- 🔍 **Smart Retrieval**: Finds the most relevant documentation and actual source code examples

## Architecture

The system consists of four main components:

1. **Web Scraper** (`scraper.py`): Uses a persistent Playwright session to efficiently scrape documentation.
2. **Vector Database** (`vector_db.py`): Stores embeddings of documentation and source code. Supports OpenAI embeddings if local models fail.
3. **RAG Agent** (`rag_agent.py`): Intelligent agent that generates answers using OpenAI or Groq LLMs.
4. **Main Application** (`main.py`): CLI interface for scraping, ingestion, and querying.

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for embeddings/agent)
- (Optional) Groq API key (for fast inference)

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
```
Edit `.env` and add your keys:
```env
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key_if_using_groq
```

## Usage

### 1. Scrape IFS Documentation

First, scrape and index the IFS documentation:

```bash
python main.py --scrape --max-pages 50
```

### 2. Ingest Core Source Code

Ingest your local IFS source code (e.g., from a Build Home or Workspace) to let the agent answer questions about your specific implementation:

```bash
python main.py --ingest-core --core-path "C:/MyWorkspace/Ref_Core"
```

### 3. Interactive Mode

Launch the interactive CLI. By default it uses OpenAI:

```bash
python main.py
```

To use **Groq** for faster inference:

```bash
python main.py --provider groq --model llama-3.3-70b-versatile
```

### 4. Single Query Mode

Execute a single query directly:

```bash
python main.py --query "How does AccPeriodCloseUtil work?" --provider groq
```

## CLI Options

| Argument | Description | Default |
|----------|-------------|---------|
| `--scrape` | Run documentation scraper | False |
| `--ingest-core` | Run core code ingestion | False |
| `--core-path` | Path to core code directory | `./Ref_Core` |
| `--url` | Start URL for scraping | `https://docs.ifs.com` |
| `--max-pages` | Max pages to scrape | 50 |
| `--query` | Run a single query | None |
| `--provider` | LLM Provider (`openai` or `groq`) | `openai` |
| `--model` | Specific model to use | `gpt-3.5-turbo` or `llama-3.3-70b-versatile` |

## Project Structure

```
IFS-CAS/
├── main.py              # Entry point & CLI
├── scraper.py           # Persistent browser scraper
├── vector_db.py         # ChromaDB wrapper (OpenAI embedding support)
├── rag_agent.py         # RAG logic & LLM integration (OpenAI/Groq)
├── requirements.txt     # Dependencies
├── .env.example         # Template for env vars
└── README.md            # Documentation
```

## Troubleshooting

### "Agent not initialized" error
- Ensure `OPENAI_API_KEY` is set.
- If using Groq, ensure `GROQ_API_KEY` is set.

### Database dependencies (Windows)
- If you see errors about `torch` or `sentence-transformers` on Windows, the system automatically falls back to **OpenAI Embeddings**. Ensure your `OPENAI_API_KEY` is valid.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
