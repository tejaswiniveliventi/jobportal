"""Matcher Agent — cosine similarity + Gemini deep score."""
import json, logging, re
from typing import Optional
import chromadb
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_chroma_col = None


def _chroma():
    global _chroma_col
    if _chroma_col is None:
        client = chromadb.PersistentClient(path="/app/chromadb_data")
        _chroma_col = client.get_or_create_collection(
            name="profile_embeddings", metadata={"hnsw:space": "cosine"})
    return _chroma_col


def _embed_jd(jd: str) -> Optional[list[float]]:
    if not settings.gemini_api_key:
        return None
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    try:
        r = genai.embed_content(model="models/text-embedding-004", content=jd[:8000], task_type="RETRIEVAL_QUERY")
        return r["embedding"]
    except Exception as e:
        logger.error(f"JD embed: {e}")
        return None


def cosine_score(user_id: str, jd: str) -> float:
    vec = _embed_jd(jd)
    if not vec:
        return 0.5
    try:
        r = _chroma().query(query_embeddings=[vec], n_results=1, where={"user_id": user_id})
        if r["distances"] and r["distances"][0]:
            return round(1 - r["distances"][0][0], 4)
    except Exception as e:
        logger.warning(f"Chroma query: {e}")
    return 0.5


def gemini_score(profile_summary: str, job: dict) -> dict:
    if not settings.gemini_api_key:
        return {"match_score": 0.5, "reasoning": "No API key", "strengths": [], "gaps": []}
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""Score this candidate vs job. Return ONLY JSON, no markdown.
CANDIDATE: {profile_summary[:800]}
JOB: {job.get('title','')} at {job.get('company','')}
DESCRIPTION: {job.get('description','')[:1200]}
JSON: {{"match_score":0.0,"reasoning":"...","strengths":["..."],"gaps":["..."]}}"""
    try:
        raw = re.sub(r"^```[a-z]*\n?|\n?```$", "", model.generate_content(prompt).text.strip())
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Gemini score: {e}")
        return {"match_score": 0.5, "reasoning": str(e), "strengths": [], "gaps": []}


def run_matcher_agent(user_id: str, profile_summary: str, jobs: list[dict],
                      top_n: int = 10, threshold: float = 0.45) -> list[dict]:
    logger.info(f"[Matcher] scoring {len(jobs)} jobs for user={user_id}")
    scored = sorted(
        [(cosine_score(user_id, j.get("description","")), j)
         for j in jobs if j.get("description")],
        key=lambda x: x[0], reverse=True
    )
    results = []
    for i, (cs, job) in enumerate(scored):
        if cs < threshold:
            continue
        analysis = gemini_score(profile_summary, job) if i < top_n else                    {"match_score": cs, "reasoning": "Cosine match", "strengths": [], "gaps": []}
        final = round((cs * 0.4) + (analysis["match_score"] * 0.6), 3) if i < top_n else cs
        results.append({**job, "match_score": final, "cosine_score": cs,
                        "match_reasoning": analysis["reasoning"],
                        "strengths": analysis["strengths"], "gaps": analysis["gaps"]})
    logger.info(f"[Matcher] {len(results)} above threshold")
    return results
