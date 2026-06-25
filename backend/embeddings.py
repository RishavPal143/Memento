import os
import re
from typing import List
import httpx

# Load configuration from environment variables
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5")


def clean_and_truncate_text(text: str, max_chars: int = 8000) -> str:
    """
    Cleans webpage content by removing HTML tags and normalizing whitespace,
    then truncating it to the specified maximum character limit.
    """
    if not text:
        return ""
    
    # Remove HTML tags using regular expression
    cleaned = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace (replace newlines, tabs, and duplicate spaces with a single space)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Truncate to maximum character limit
    return cleaned[:max_chars]


def get_embedding(text: str) -> List[float]:
    """
    Generates a 1536-dimensional embedding vector for the given text
    using the configured embedding provider.
    """
    if not text:
        # Return a zero vector of 1536 dimensions if the text is empty
        return [0.0] * 1536

    if EMBEDDING_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please configure it in backend/.env to generate embeddings."
            )
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": text,
            "model": OPENAI_EMBEDDING_MODEL
        }
        
        try:
            response = httpx.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload,
                timeout=30.0
            )
        except Exception as e:
            raise Exception(f"Failed to connect to OpenAI embedding API: {str(e)}")
            
        if response.status_code != 200:
            raise Exception(
                f"OpenAI embedding generation failed (HTTP {response.status_code}): {response.text}"
            )
        
        data = response.json()
        try:
            return data["data"][0]["embedding"]
        except (KeyError, IndexError, TypeError) as e:
            raise Exception(f"Failed to parse OpenAI embedding response: {str(e)}. Response: {data}")

    elif EMBEDDING_PROVIDER == "local":
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "The 'sentence-transformers' library is required for local embeddings. "
                "Please install it in the virtual environment by running: "
                "pip install sentence-transformers"
            )
        
        try:
            # Load the local model (cached in default transformers path ~/.cache/huggingface/)
            # trust_remote_code=True is required for certain models like nomic-embed-text
            model = SentenceTransformer(LOCAL_EMBEDDING_MODEL, trust_remote_code=True)
            
            # Generate the embedding vector
            embedding = model.encode(text, convert_to_numpy=True).tolist()
            
            # Verify dimensions
            if len(embedding) != 1536:
                raise ValueError(
                    f"Local model '{LOCAL_EMBEDDING_MODEL}' produced a {len(embedding)}-dimensional vector, "
                    f"but database schema expects 1536 dimensions. Please use a model that outputs "
                    f"1536 dimensions or adjust your configuration."
                )
            return embedding
        except Exception as e:
            raise Exception(f"Failed to generate local embedding: {str(e)}")

    elif EMBEDDING_PROVIDER == "mock":
        import random
        # Return a dummy 1536-dimensional vector for testing
        return [random.uniform(-1.0, 1.0) for _ in range(1536)]

    else:
        raise ValueError(
            f"Unsupported EMBEDDING_PROVIDER '{EMBEDDING_PROVIDER}'. "
            f"Please set it to 'openai', 'local', or 'mock'."
        )


def generate_snippet(content: str, query: str, length: int = 200) -> str:
    """
    Generates a contextual snippet of the content centered around
    the query terms, falling back to the beginning of the content.
    """
    if not content:
        return ""
    if not query:
        return content[:length] + "..." if len(content) > length else content
    
    # Clean the query terms (split by space and find keywords of reasonable length)
    terms = [re.escape(word) for word in query.lower().split() if len(word) > 2]
    if not terms:
        return content[:length] + "..." if len(content) > length else content
    
    # Search for any of the terms in the content
    pattern = "|".join(terms)
    match = re.search(pattern, content.lower())
    if match:
        start_idx = match.start()
        # Center the window a bit before the matched keyword
        start = max(0, start_idx - length // 4)
        end = min(len(content), start + length)
        snippet = content[start:end]
        # Add ellipses if text is truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet
    
    # Fallback to the beginning of the content
    return content[:length] + "..." if len(content) > length else content


