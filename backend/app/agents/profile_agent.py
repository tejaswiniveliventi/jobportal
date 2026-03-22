"""
Profile Agent — parses resume PDF, extracts entities via spaCy NER,
embeds via Gemini text-embedding-004, stores in ChromaDB,
and provides per-job resume tailoring via Gemini Flash.
"""
import json, logging, re, hashlib
from typing import Optional
import spacy
import chromadb
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_nlp = None
_chroma_col = None


def _nlp_model():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _chroma():
    global _chroma_col
    if _chroma_col is None:
        client = chromadb.PersistentClient(path="/app/chromadb_data")
        _chroma_col = client.get_or_create_collection(
            name="profile_embeddings",
            metadata={"hnsw:space": "cosine"},
        )
    return _chroma_col


# ── 1. Text extraction ────────────────────────────────────────────────────────

def extract_text(path: str) -> str:
    try:
        from pdfminer.high_level import extract_text as pm
        text = pm(path)
        if text and len(text.strip()) > 100:
            return text
    except Exception as e:
        logger.warning(f"pdfminer failed: {e}")
    try:
        import fitz
        doc = fitz.open(path)
        text = "\n".join(p.get_text() for p in doc)
        doc.close()
        return text
    except Exception as e:
        raise RuntimeError(f"Cannot extract text: {e}")


# ── 2. Section segmentation ───────────────────────────────────────────────────

SECTIONS = {
    "summary":        r"(summary|objective|profile|about)",
    "experience":     r"(experience|employment|work history|career)",
    "education":      r"(education|academic|qualification|degree)",
    "skills":         r"(skills|technologies|technical|competencies)",
    "certifications": r"(certif|licence|license)",
    "projects":       r"(project|portfolio|open.?source)",
}


def segment(text: str) -> dict[str, str]:
    lines = text.split("\n")
    sections: dict[str, list] = {"raw": []}
    current = "raw"
    for line in lines:
        s = line.strip()
        matched = False
        if s and len(s) < 60:
            for name, pat in SECTIONS.items():
                if re.search(pat, s, re.IGNORECASE):
                    current = name
                    sections.setdefault(current, [])
                    matched = True
                    break
        if not matched:
            sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}


# ── 3. NER entity extraction ──────────────────────────────────────────────────

HARD_SKILLS = {
    "python","javascript","typescript","java","golang","rust","c++","c#","ruby","php",
    "react","vue","angular","nextjs","svelte","fastapi","django","flask","express","nodejs",
    "postgresql","mysql","mongodb","redis","elasticsearch","dynamodb","sqlite",
    "docker","kubernetes","aws","gcp","azure","terraform","ansible","linux","git",
    "graphql","rest","kafka","rabbitmq","grpc","websocket",
    "machine learning","deep learning","pytorch","tensorflow","scikit-learn","nlp",
    "pandas","numpy","spark","airflow","dbt","sql","bigquery","snowflake",
}

SOFT_SKILLS = {
    "leadership","communication","collaboration","agile","scrum","problem solving",
    "mentoring","project management","stakeholder management","cross-functional",
}


def extract_entities(sections: dict, full_text: str) -> dict:
    nlp = _nlp_model()
    doc = nlp(full_text[:50_000])

    txt_lower = (sections.get("skills","") + " " + full_text).lower()
    hard = sorted(s for s in HARD_SKILLS if s in txt_lower)
    soft = sorted(s for s in SOFT_SKILLS if s in txt_lower)

    orgs = list({e.text for e in doc.ents if e.label_ == "ORG"})

    exp_text = sections.get("experience", "")
    bullets = [
        ln.strip().lstrip("•\-–*▪").strip()
        for ln in exp_text.split("\n")
        if len(ln.strip()) > 30 and ln.strip()[0] in "•-–*▪"
    ]

    edu_text = sections.get("education", "")
    degrees = list({d.upper() for d in re.findall(
        r"\b(B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|Ph\.?D\.?|MBA|Bachelor|Master|Doctor)\b",
        edu_text, re.IGNORECASE
    )})

    return {
        "skills": {"hard": hard, "soft": soft, "raw": sections.get("skills","")[:400]},
        "experience": {"companies": orgs[:10], "bullets": bullets[:20]},
        "education": {"degrees": degrees, "raw": edu_text[:400]},
        "certifications": sections.get("certifications","")[:300],
        "summary": sections.get("summary","")[:500],
    }


# ── 4. Embed + store ──────────────────────────────────────────────────────────

def _embed_doc(entities: dict) -> str:
    return (
        f"SUMMARY: {entities['summary']}\n"
        f"SKILLS: {', '.join(entities['skills']['hard'])}\n"
        f"SOFT: {', '.join(entities['skills']['soft'])}\n"
        f"EXPERIENCE: {" | ".join(entities['experience']['bullets'][:10])}\n"
        f"EDUCATION: {", ".join(entities['education']['degrees'])}\n"
        f"CERTS: {entities['certifications'][:200]}"
    )


def embed_and_store(user_id: str, entities: dict) -> str:
    if not settings.gemini_api_key:
        logger.warning("No GEMINI_API_KEY — skipping embedding")
        return f"no_embed_{user_id}"

    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    doc = _embed_doc(entities)
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=doc,
        task_type="RETRIEVAL_DOCUMENT",
    )
    vector = result["embedding"]
    embed_id = f"profile_{user_id}"
    col = _chroma()
    col.upsert(
        ids=[embed_id],
        embeddings=[vector],
        documents=[doc],
        metadatas=[{"user_id": user_id, "hard_skills": ", ".join(entities["skills"]["hard"])}],
    )
    logger.info(f"Profile embedded → chroma id={embed_id}")
    return embed_id


# ── 5. Per-job tailoring ──────────────────────────────────────────────────────

def tailor_for_job(bullets: list[str], jd: str, user_id: str, job_id: str) -> dict:
    if not settings.gemini_api_key:
        return {"tailored_bullets": bullets, "match_score": 0.5, "reasoning": "No API key"}

    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""You are an expert resume editor.
Rewrite the bullets to match the JD vocabulary. Do NOT invent facts.
Return ONLY valid JSON, no markdown.

BULLETS:
{chr(10).join(f"- {b}" for b in bullets[:12])}

JD (excerpt):
{jd[:1800]}

JSON format:
{{"tailored_bullets":["..."],"match_score":0.0,"key_matches":["..."],"reasoning":"..."}}"""

    try:
        resp = model.generate_content(prompt)
        raw = re.sub(r"^```[a-z]*\n?|\n?```$", "", resp.text.strip())
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Tailor failed: {e}")
        return {"tailored_bullets": bullets, "match_score": 0.5, "reasoning": str(e)}


# ── Main entrypoint ───────────────────────────────────────────────────────────

def run_profile_agent(user_id: str, file_path: str) -> dict:
    logger.info(f"[Profile Agent] user={user_id}")
    raw = extract_text(file_path)
    sections = segment(raw)
    entities = extract_entities(sections, raw)
    embed_id = embed_and_store(user_id, entities)
    return {
        "user_id": user_id,
        "embedding_id": embed_id,
        "entities": entities,
        "raw_hash": hashlib.md5(raw.encode()).hexdigest(),
        "status": "complete",
    }
