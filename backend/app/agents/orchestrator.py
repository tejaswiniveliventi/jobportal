"""Orchestrator Agent — LangGraph state machine coordinating all sub-agents."""
import logging, re
from typing import TypedDict, Optional
from datetime import datetime, timezone
from langgraph.graph import StateGraph, END

from app.agents.discovery_agent import run_discovery_agent
from app.agents.matcher_agent import run_matcher_agent

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict):
    user_id: str
    profile: Optional[dict]
    search_queries: list[str]
    discovered_jobs: list[dict]
    matched_jobs: list[dict]
    approved_jobs: list[dict]
    applied_jobs: list[dict]
    errors: list[str]
    status: str


def profile_check_node(state: OrchestratorState) -> OrchestratorState:
    profile = state.get("profile", {})
    if not profile:
        return {**state, "status": "error", "errors": ["No profile"]}
    entities = profile.get("entities", {})
    skills = entities.get("skills", {}).get("hard", [])
    summary = entities.get("summary", "")
    queries = []
    if skills:
        queries.append(" ".join(skills[:3]))
    if summary:
        titles = re.findall(r"\b(engineer|developer|manager|analyst|scientist|designer|architect)\b", summary, re.IGNORECASE)
        if titles:
            queries.append(f"{titles[0]} {skills[0] if skills else ''}")
    if not queries:
        queries = ["software engineer"]
    logger.info(f"[Orchestrator] queries={queries}")
    return {**state, "search_queries": queries[:3], "status": "discovering"}


async def discovery_node(state: OrchestratorState) -> OrchestratorState:
    jobs = await run_discovery_agent(queries=state["search_queries"])
    return {**state, "discovered_jobs": jobs, "status": "matching"}


def match_node(state: OrchestratorState) -> OrchestratorState:
    entities = state.get("profile", {}).get("entities", {})
    skills = entities.get("skills", {}).get("hard", [])
    summary = entities.get("summary", "")
    profile_summary = f"Skills: {', '.join(skills)}. Summary: {summary}"
    matched = run_matcher_agent(state["user_id"], profile_summary, state["discovered_jobs"])
    return {**state, "matched_jobs": matched, "status": "awaiting_approval"}


def approval_node(state: OrchestratorState) -> OrchestratorState:
    logger.info(f"[Orchestrator] {len(state['matched_jobs'])} jobs awaiting approval")
    return {**state, "status": "awaiting_approval"}


def should_apply(state: OrchestratorState) -> str:
    return "apply" if state.get("approved_jobs") else "end"


def apply_node(state: OrchestratorState) -> OrchestratorState:
    applied = []
    for job in state.get("approved_jobs", []):
        logger.info(f"[Orchestrator] Queuing apply for job={job.get('id')}")
        applied.append({**job, "queued_at": datetime.now(timezone.utc).isoformat()})
    return {**state, "applied_jobs": applied, "status": "applied"}


def build_graph():
    g = StateGraph(OrchestratorState)
    g.add_node("profile_check", profile_check_node)
    g.add_node("discovery", discovery_node)
    g.add_node("match", match_node)
    g.add_node("approval", approval_node)
    g.add_node("apply", apply_node)
    g.set_entry_point("profile_check")
    g.add_edge("profile_check", "discovery")
    g.add_edge("discovery", "match")
    g.add_edge("match", "approval")
    g.add_conditional_edges("approval", should_apply, {"apply": "apply", "end": END})
    g.add_edge("apply", END)
    return g.compile()


orchestrator = build_graph()


async def run_orchestrator(user_id: str, profile: dict, approved_jobs: list = None) -> dict:
    state: OrchestratorState = {
        "user_id": user_id, "profile": profile,
        "search_queries": [], "discovered_jobs": [],
        "matched_jobs": [], "approved_jobs": approved_jobs or [],
        "applied_jobs": [], "errors": [], "status": "starting",
    }
    logger.info(f"[Orchestrator] Starting for user={user_id}")
    final = await orchestrator.ainvoke(state)
    logger.info(f"[Orchestrator] Done. status={final['status']}")
    return final
