"""
Agentic RAG (Retrieval-Augmented Generation) for IFS documentation
Uses LangChain to create an intelligent agent that can answer questions with code examples
"""

import os
from typing import List, Dict, Optional
import logging

try:
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Optional imports based on availability
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


from vector_db import VectorDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IFSAgenticRAG:
    """Agentic RAG system for IFS documentation queries"""
    
    def __init__(self, vector_db: VectorDatabase, openai_api_key: Optional[str] = None, 
                 provider: str = 'openai', model: str = None):
        """
        Initialize the agentic RAG system
        
        Args:
            vector_db: VectorDatabase instance
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            provider: LLM provider ('openai' or 'groq')
            model: Specific model name to use
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "langchain is required but not installed. "
                "Install it with: pip install langchain"
            )
        
        self.vector_db = vector_db
        self.provider = provider.lower()
        
        # Initialize LLM based on provider
        if self.provider == 'groq':
            if not GROQ_AVAILABLE:
                raise ImportError("langchain-groq is required for Groq provider. Install with: pip install langchain-groq")
            
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY is required for Groq provider. Set GROQ_API_KEY environment variable.")
            
            model_name = model or "llama3-70b-8192"
            logger.info(f"Initializing Groq LLM with model: {model_name}")
            self.llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name=model_name,
                temperature=0.7
            )
        else:
            # Default to OpenAI
            if not OPENAI_AVAILABLE:
                raise ImportError("langchain-openai is required for OpenAI provider. Install with: pip install langchain-openai")

            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
            
            model_name = model or "gpt-3.5-turbo"
            logger.info(f"Initializing OpenAI LLM with model: {model_name}")
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0.7,
                api_key=api_key
            )
        
        # System prompt for the agent
        self.system_prompt = """You are an expert IFS (Industrial and Financial Systems) assistant. 
You help developers by providing accurate code examples and explanations based on IFS documentation and CORE SOURCE CODE.

Your responsibilities:
1. Answer questions about IFS systems and customizations
2. Provide working code examples when requested
3. Explain IFS concepts clearly and concisely
4. Always base your answers on the provided documentation context
5. If you're not sure or the documentation doesn't cover a topic, say so

When providing code:
- Include complete, working examples
- Add comments to explain the code
- Follow IFS best practices and conventions
- Specify the language/framework being used
- When referencing Core Source Code, explain that this is from the actual IFS codebase
"""
        
        self.conversation_history = []
        logger.info("Agentic RAG system initialized")
    
    def retrieve_context(self, query: str, n_results: int = 5) -> Dict[str, List[Dict]]:
        """
        Retrieve relevant context from the vector database
        
        Args:
            query: User query
            n_results: Number of results to retrieve
            
        Returns:
            Dictionary with content and code contexts
        """
        # Retrieve general content
        content_results = self.vector_db.search(query, n_results=n_results, filter_type='content')
        
        # Retrieve code examples
        code_results = self.vector_db.search(query, n_results=3, filter_type='code')
        
        # Retrieve core code
        core_code_results = self.vector_db.search(query, n_results=3, filter_type='core_code')
        
        return {
            'content': content_results,
            'code': code_results,
            'core_code': core_code_results
        }
    
    def format_context(self, context: Dict[str, List[Dict]]) -> str:
        """
        Format retrieved context for the LLM
        
        Args:
            context: Retrieved context dictionary
            
        Returns:
            Formatted context string
        """
        formatted = []
        
        # Add content sections
        if context['content']:
            formatted.append("=== Relevant Documentation ===\n")
            for i, item in enumerate(context['content'], 1):
                title = item['metadata'].get('title', 'Unknown')
                url = item['metadata'].get('url', '')
                formatted.append(f"{i}. {title}")
                if url:
                    formatted.append(f"   Source: {url}")
                formatted.append(f"   {item['content'][:500]}...\n")
        
        # Add code examples
        if context['code']:
            formatted.append("\n=== Relevant Code Examples ===\n")
            for i, item in enumerate(context['code'], 1):
                title = item['metadata'].get('title', 'Unknown')
                formatted.append(f"{i}. From: {title}")
                formatted.append(f"   {item['content']}\n")
                
        # Add core code
        if context.get('core_code'):
            formatted.append("\n=== Relevant Core Source Code (Ref_Core) ===\n")
            for i, item in enumerate(context['core_code'], 1):
                title = item['metadata'].get('title', 'Unknown')
                formatted.append(f"{i}. File: {title}")
                formatted.append(f"   {item['content']}\n")
        
        return "\n".join(formatted)
    
    def generate_response(self, query: str, use_history: bool = True) -> str:
        """
        Generate a response to the user query
        
        Args:
            query: User query
            use_history: Whether to use conversation history
            
        Returns:
            Generated response
        """
        logger.info(f"Processing query: {query}")
        
        # Retrieve relevant context
        context = self.retrieve_context(query)
        formatted_context = self.format_context(context)
        
        # Build messages for the LLM
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add conversation history if requested
        if use_history and self.conversation_history:
            messages.extend(self.conversation_history[-6:])  # Last 3 exchanges
        
        # Add current query with context
        user_message = f"""Based on the following IFS documentation context, please answer this question:

CONTEXT:
{formatted_context}

QUESTION:
{query}

Please provide a detailed answer with code examples if relevant. If the question asks for code, 
provide complete, working code with explanations.
"""
        
        messages.append(HumanMessage(content=user_message))
        
        # Generate response
        try:
            response = self.llm.invoke(messages)
            answer = response.content
            
            # Update conversation history
            self.conversation_history.append(HumanMessage(content=query))
            self.conversation_history.append(AIMessage(content=answer))
            
            logger.info("Response generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def ask(self, query: str) -> str:
        """
        Simple interface to ask a question
        
        Args:
            query: User question
            
        Returns:
            Answer with code examples if relevant
        """
        return self.generate_response(query)


if __name__ == "__main__":
    # Test the RAG agent
    from dotenv import load_dotenv
    load_dotenv()
    
    db = VectorDatabase()
    agent = IFSAgenticRAG(db)
    
    # Test query
    response = agent.ask("How do I customize an IFS form?")
    print(response)
