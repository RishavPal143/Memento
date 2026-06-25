import os
import json
from typing import List, Dict, Any
import httpx

# Load configurations from environment variables
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-1.5-flash")


def generate_chat_response(query: str, sources: List[Dict[str, Any]]) -> str:
    """
    Synthesizes a response to the user's query by combining retrieved memory
    sources and sending them to the configured LLM.
    """
    # 1. Format the memory context
    context = ""
    if sources:
        context_items = []
        for idx, source in enumerate(sources, 1):
            item_text = (
                f"Memory #{idx}:\n"
                f"Title: {source.get('title', 'Untitled')}\n"
                f"URL: {source.get('url', 'N/A')}\n"
                f"Content Snippet: {source.get('snippet', 'No snippet available')}\n"
            )
            context_items.append(item_text)
        context = "\n".join(context_items)
    else:
        context = "No relevant memory records found."

    # 2. System and user prompts
    system_prompt = (
        "You are the AI Chat Memory Agent for Memento, a personal internet memory assistant.\n"
        "Your task is to answer the user's question using their retrieved personal memories (saved web pages, titles, URLs, and snippets).\n"
        "Instructions:\n"
        "- Base your answer on the provided personal memories context.\n"
        "- Be conversational, helpful, and direct.\n"
        "- Synthesize findings and mention relevant source titles/websites naturally in your narrative.\n"
        "- If the retrieved memories do not contain the answer, explain what you found instead and suggest they try another query.\n"
    )

    user_message = (
        f"Retrieved Memories Context:\n"
        f"===========================\n"
        f"{context}\n"
        f"===========================\n\n"
        f"User Query: {query}"
    )

    # 3. Call the configured LLM
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please configure it in backend/.env to use OpenAI chat completions."
            )
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": OPENAI_CHAT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3
        }
        
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
        except Exception as e:
            raise Exception(f"Failed to connect to OpenAI chat completions API: {str(e)}")
            
        if response.status_code != 200:
            raise Exception(
                f"OpenAI Chat API failed (HTTP {response.status_code}): {response.text}"
            )
            
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise Exception(f"Failed to parse OpenAI chat response: {str(e)}. Response: {data}")

    elif LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. "
                "Please configure it in backend/.env to use Gemini generation."
            )
            
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\n{user_message}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3
            }
        }
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_CHAT_MODEL}:generateContent?key={GEMINI_API_KEY}"
        
        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
        except Exception as e:
            raise Exception(f"Failed to connect to Gemini generateContent API: {str(e)}")
            
        if response.status_code != 200:
            raise Exception(
                f"Gemini API failed (HTTP {response.status_code}): {response.text}"
            )
            
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            raise Exception(f"Failed to parse Gemini chat response: {str(e)}. Response: {data}")

    elif LLM_PROVIDER == "mock":
        if not sources:
            return f"You asked: '{query}', but I couldn't find any relevant memories in your database to formulate an answer."
            
        answer = f"Based on your personal memories, you previously read about several topics related to '{query}':\n\n"
        for idx, source in enumerate(sources, 1):
            title = source.get("title") or "Untitled Webpage"
            url = source.get("url", "#")
            snippet = source.get("snippet", "")
            short_snippet = snippet[:120] + "..." if len(snippet) > 120 else snippet
            answer += f"- You visited [{title}]({url}), which discussed: \"{short_snippet}\"\n"
            
        answer += "\n(Note: This is a synthetic mock response generated based on your retrieved search context.)"
        return answer

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{LLM_PROVIDER}'. "
            f"Please set it to 'openai', 'gemini', or 'mock'."
        )


def analyze_memory_content(title: str, content: str) -> dict:
    """
    Analyzes the title and content of a web page and returns a dictionary
    containing 'summary', 'tags', and 'importance_score' (0-100) generated by the LLM.
    """
    default_response = {
        "summary": f"A saved webpage memory of '{title or 'Untitled'}'.",
        "tags": ["webpage"],
        "importance_score": 50
    }
    
    if not content:
        return default_response
        
    # Truncate content to keep API requests fast and stay within token limits
    truncated_content = content[:3000]
    
    system_prompt = (
        "You are an AI webpage content analyzer.\n"
        "Analyze the title and content of the page and generate three metadata fields:\n"
        "1. summary: A concise summary of exactly 2-3 lines.\n"
        "2. tags: A list of relevant tags (e.g. AI, finance, startup, productivity, programming, health, tech, etc.). Maximum of 5 tags.\n"
        "3. importance_score: An integer score from 0 to 100, where 0 is completely trivial or spam, and 100 is highly critical/important personal research.\n\n"
        "You MUST return your response as a valid JSON object matching this schema:\n"
        "{\n"
        "  \"summary\": \"your 2-3 line summary here\",\n"
        "  \"tags\": [\"tag1\", \"tag2\", ...],\n"
        "  \"importance_score\": 85\n"
        "}\n"
        "Do not include any markup, backticks (like ```json), or text outside the JSON object."
    )
    
    user_message = f"Page Title: {title or 'Untitled'}\nPage Content:\n{truncated_content}"
    
    try:
        if LLM_PROVIDER == "openai":
            if not OPENAI_API_KEY:
                return default_response
                
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": OPENAI_CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                text_content = data["choices"][0]["message"]["content"]
                parsed = json.loads(text_content)
                return {
                    "summary": str(parsed.get("summary", default_response["summary"])),
                    "tags": list(parsed.get("tags", default_response["tags"])),
                    "importance_score": int(parsed.get("importance_score", default_response["importance_score"]))
                }
                
        elif LLM_PROVIDER == "gemini":
            if not GEMINI_API_KEY:
                return default_response
                
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"{system_prompt}\n\n{user_message}"
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_CHAT_MODEL}:generateContent?key={GEMINI_API_KEY}"
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                return {
                    "summary": str(parsed.get("summary", default_response["summary"])),
                    "tags": list(parsed.get("tags", default_response["tags"])),
                    "importance_score": int(parsed.get("importance_score", default_response["importance_score"]))
                }
                
        elif LLM_PROVIDER == "mock":
            text_lower = (title + " " + content).lower()
            tags = []
            if "ai" in text_lower or "artificial intelligence" in text_lower:
                tags.append("AI")
            if "accounting" in text_lower or "bookkeeping" in text_lower or "finance" in text_lower:
                tags.append("finance")
            if "startup" in text_lower or "yc" in text_lower or "company" in text_lower:
                tags.append("startup")
            if "programming" in text_lower or "code" in text_lower or "fastapi" in text_lower:
                tags.append("programming")
            if not tags:
                tags.append("webpage")
                
            summary = f"Synthesized webpage memory for '{title or 'Untitled'}'. Explores key content regarding " + ", ".join(tags).lower() + "."
            importance_score = min(100, max(20, (len(title or "") * 3 + len(tags) * 12) % 100))
            
            return {
                "summary": summary,
                "tags": tags,
                "importance_score": importance_score
            }
            
    except Exception as e:
        print(f"Error generating AI enhancements, falling back to default: {e}")
        
    return default_response


def generate_user_insights(memories: List[Dict[str, Any]]) -> str:
    """
    Analyzes the user's saved memory summaries and tags to identify their core
    interests and current research focus.
    """
    if not memories:
        return "No memories available to analyze. Please add some webpage memories."

    # 1. Format the memory history as a text block
    history_items = []
    for idx, m in enumerate(memories, 1):
        tags_str = ", ".join(m.get("tags", []))
        item = (
            f"Webpage #{idx}: {m.get('title', 'Untitled')}\n"
            f"Tags: {tags_str}\n"
            f"Summary: {m.get('summary', 'No summary available.')}\n"
        )
        history_items.append(item)
    history_context = "\n".join(history_items)

    system_prompt = (
        "You are a personal user profiling intelligence agent.\n"
        "Your task is to analyze the user's saved pages, summaries, and tags to detect their core interests and active research areas.\n"
        "Generate a brief natural language summary (1-2 sentences) of their profile.\n"
        "Instructions:\n"
        "- Do NOT start with 'The user is...' or 'Based on the context...'. State the interests directly.\n"
        "- Mention specific themes from their reading (e.g. AI startups, programming, cooking methods, etc.).\n"
        "- Keep it professional, conversational, and direct.\n"
    )

    user_message = (
        f"Saved Webpages History:\n"
        f"=======================\n"
        f"{history_context}\n"
        f"=======================\n"
    )

    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            return "Unable to generate insights: OPENAI_API_KEY not configured."
            
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": OPENAI_CHAT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.4
        }
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Error analyzing interests via OpenAI: {str(e)}"

    elif LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            return "Unable to generate insights: GEMINI_API_KEY not configured."
            
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\n{user_message}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4
            }
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_CHAT_MODEL}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            return f"Error analyzing interests via Gemini: {str(e)}"

    # Fallback/Mock provider logic
    unique_tags = set()
    for m in memories:
        for tag in m.get("tags", []):
            if tag.lower() != "webpage":
                unique_tags.add(tag)

    if not unique_tags:
        return "Actively exploring general web articles and saving bookmarks for general reference."
        
    tags_list = list(unique_tags)
    if len(tags_list) == 1:
        return f"Currently focused on researching content related to {tags_list[0]}."
    elif len(tags_list) == 2:
        return f"Actively exploring and comparing topics in {tags_list[0]} and {tags_list[1]}."
    else:
        return f"Actively researching topics in {', '.join(tags_list[:-1])}, and {tags_list[-1]}."
