import asyncio
import sys
import os

# Add parent directory to path to ensure proper imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
import models
from services.llm import generate_user_insights


async def run_intelligence_job_loop():
    """
    Background loop that runs periodically to analyze memories, cluster topics,
    and save user interests to the insights table.
    """
    # 10 minutes (600s) default. Configurable via environment variables.
    interval = int(os.getenv("INTELLIGENCE_INTERVAL_SECONDS", "600"))
    
    print(f"[Intelligence Service] Starting background intelligence task loop (Interval: {interval}s)...")
    while True:
        try:
            db = SessionLocal()
            try:
                # 1. Fetch all memories
                memories = db.query(models.Memory).all()
                if not memories:
                    print("[Intelligence Service] No memories in database. Skipping intelligence analysis.")
                else:
                    # 2. Package summaries & tags for LLM analysis
                    memory_list = []
                    for m in memories:
                        memory_list.append({
                            "title": m.title or "Untitled",
                            "url": m.url,
                            "summary": m.summary or "No summary available.",
                            "tags": m.tags or []
                        })
                    
                    print(f"[Intelligence Service] Analyzing {len(memories)} memories for interest insights...")
                    # 3. Call LLM to detect user interests
                    insight_text = generate_user_insights(memory_list)
                    
                    # 4. Save new insight record
                    new_insight = models.Insight(summary=insight_text)
                    db.add(new_insight)
                    db.commit()
                    print(f"[Intelligence Service] Successfully saved new insights: \"{insight_text}\"")
            except Exception as e:
                print(f"[Intelligence Service] Error during user profiling: {e}")
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            print(f"[Intelligence Service] Database connection error: {e}")
            
        await asyncio.sleep(interval)
