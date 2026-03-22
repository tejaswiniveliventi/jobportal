"""Discovery Agent — fetches jobs from Adzuna and JSearch."""
import hashlib, logging
from typing import Optional
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:64]


async def _adzuna(query: str, location: str = "us", n: int = 20) -> list[dict]:
    if not settings.adzuna_app_id:
        return []
    url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
    params = {"app_id": settings.adzuna_app_id, "app_key": settings.adzuna_api_key,
               "results_per_page": n, "what": query, "content-type": "application/json"}
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            r = await c.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logger.error(f"Adzuna: {e}")
            return []
    return [{
        "title": item.get("title",""),
        "company": item.get("company",{}).get("display_name","Unknown"),
        "location": item.get("location",{}).get("display_name",""),
        "is_remote": "remote" in item.get("title","").lower(),
        "description": item.get("description",""),
        "salary_min": item.get("salary_min"),
        "salary_max": item.get("salary_max"),
        "source_url": item.get("redirect_url",""),
        "source_board": "adzuna",
        "posted_at": item.get("created"),
        "raw_data": {k:v for k,v in item.items() if k != "description"},
    } for item in data.get("results",[])]


async def _jsearch(query: str, location: str = "United States", n: int = 10) -> list[dict]:
    if not settings.jsearch_api_key:
        return []
    headers = {"X-RapidAPI-Key": settings.jsearch_api_key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
    params = {"query": f"{query} in {location}", "page": "1", "num_pages": "1"}
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            r = await c.get("https://jsearch.p.rapidapi.com/search", headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logger.error(f"JSearch: {e}")
            return []
    return [{
        "title": item.get("job_title",""),
        "company": item.get("employer_name","Unknown"),
        "location": f"{item.get('job_city','')} {item.get('job_state','')}".strip(),
        "is_remote": item.get("job_is_remote", False),
        "description": item.get("job_description",""),
        "salary_min": item.get("job_min_salary"),
        "salary_max": item.get("job_max_salary"),
        "source_url": item.get("job_apply_link",""),
        "source_board": "jsearch",
        "posted_at": item.get("job_posted_at_datetime_utc"),
        "raw_data": {k:v for k,v in item.items() if k != "job_description"},
    } for item in data.get("data",[])[:n]]


async def run_discovery_agent(queries: list[str], locations: Optional[list[str]] = None) -> list[dict]:
    locations = locations or ["us"]
    all_jobs, seen = [], set()
    for q in queries:
        for loc in locations[:2]:
            for job in (await _adzuna(q, loc)) + (await _jsearch(q, loc)):
                url = job.get("source_url","")
                if not url:
                    continue
                h = _hash(url)
                if h in seen:
                    continue
                seen.add(h)
                job["source_hash"] = h
                all_jobs.append(job)
    logger.info(f"[Discovery] {len(all_jobs)} unique jobs")
    return all_jobs
