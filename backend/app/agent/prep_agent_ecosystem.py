import json
import re
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.services.eligibility import check_eligibility, parse_skills
from app.services.prep_planner import generate_interview_prep_plan


# ==============================================================================
# 1. State Definition for the Multi-Agent Preparation Ecosystem
# ==============================================================================
class PrepOrchestratorState(TypedDict):
    # Context
    student_id: int
    student_name: str
    student_branch: str
    student_cgpa: float
    student_skills: List[str]
    job_id: int
    job_title: str
    company_name: str
    required_skills: List[str]
    target_days: int
    user_query: str
    
    # Active Agent Outputs
    routing_decision: str
    technical_assessment: Dict[str, Any]
    behavioral_assessment: Dict[str, Any]
    rebalanced_plan: Dict[str, Any]
    final_readiness_score: int
    final_feedback_report: Dict[str, Any]
    final_response: str


# ==============================================================================
# 2. Agent 1: Placement Prep Master Orchestrator
# Classifies intent, inspects gaps, and delegates to specialist agents
# ==============================================================================
def master_orchestrator_node(state: PrepOrchestratorState) -> Dict[str, Any]:
    query = (state.get("user_query") or "").lower().strip()
    
    # Check if student requested behavioral/STAR round
    if any(k in query for k in ["star", "behavioral", "tell me about yourself", "leadership", "conflict", "weakness", "hr round"]):
        decision = "star_bar_raiser"
    # Check if student requested schedule adjustment or dynamic rebalance
    elif any(k in query for k in ["rebalance", "reschedule", "adjust plan", "missed", "fast track", "timeline", "crash", "days"]):
        decision = "plan_rebalancer"
    # Default or coding/technical queries route to Technical Examiner
    elif any(k in query for k in ["code", "algo", "dsa", "technical", "system design", "sql", "react", "python", "questions"]):
        decision = "technical_examiner"
    else:
        # Full multi-agent consensus evaluation
        decision = "full_consensus"
        
    return {"routing_decision": decision}


# ==============================================================================
# 3. Agent 2: Technical & Code Examiner Agent
# Drills down on DSA, architecture trade-offs, and skill deficiencies
# ==============================================================================
def technical_examiner_node(state: PrepOrchestratorState) -> Dict[str, Any]:
    req = set(s.lower() for s in state.get("required_skills", []))
    acquired = set(s.lower() for s in state.get("student_skills", []))
    missing = sorted(req - acquired)
    matched = sorted(req & acquired)
    
    # Calculate baseline technical competency
    tech_score = round(100 * len(matched) / len(req)) if req else 85
    company = state.get("company_name", "Target Company")
    title = state.get("job_title", "Software Engineer")
    
    assessment = {
        "agent_name": "Technical & Code Examiner Agent",
        "technical_score": tech_score,
        "matched_skills": matched,
        "critical_gaps": missing,
        "recommended_challenges": [
            f"Optimize lookup and aggregation for {company}'s scale using {missing[0] if missing else 'Advanced Indexing'}",
            f"Handle high-concurrency race conditions in {title} pipeline",
            f"Prove Big-O time and space tradeoffs for real-time data ingestion"
        ],
        "verdict": "Qualified with Remediation" if tech_score >= 60 else "Requires Intensive Algorithmic Drill"
    }
    return {"technical_assessment": assessment}


# ==============================================================================
# 4. Agent 3: STAR Behavioral & Bar-Raiser Agent
# Evaluates communication, leadership principles, and STAR metric impact
# ==============================================================================
def star_bar_raiser_node(state: PrepOrchestratorState) -> Dict[str, Any]:
    company = state.get("company_name", "Company")
    student = state.get("student_name", "Candidate")
    
    # Assess behavioral profile readiness
    principles = [
        "Customer Obsession / User Empathy",
        "Ownership & Bias for Action",
        "Dive Deep & Root Cause Analysis",
        "Deliver Results with Measurable Metrics"
    ]
    
    assessment = {
        "agent_name": "STAR Behavioral & Bar-Raiser Agent",
        "culture_fit_score": 88,
        "rubric": {
            "Situation": "Clear context setting (15% weighting)",
            "Task": "Specific objective and bottleneck (15% weighting)",
            "Action": "Personal technical ownership and execution (50% weighting)",
            "Result": "Quantifiable metrics, e.g. latency down 40% (20% weighting)"
        },
        "target_principles": principles,
        "trap_question": f"Tell me about a time on your capstone project where your solution failed in production or testing. How did you diagnose it?",
        "feedback": f"{student} should articulate personal contributions using numerical outcomes rather than generic team descriptions."
    }
    return {"behavioral_assessment": assessment}


# ==============================================================================
# 5. Agent 4: Adaptive Plan Rebalancer Agent
# Dynamically restructures preparation timeline based on current competencies
# ==============================================================================
def plan_rebalancer_node(state: PrepOrchestratorState) -> Dict[str, Any]:
    days = state.get("target_days") or 30
    user_query = state.get("user_query", "").lower()
    
    # Extract any explicit days requested in query (e.g., "7 days", "14 days")
    day_match = re.search(r'(\d+)\s*(?:day|days)', user_query)
    if day_match:
        days = int(day_match.group(1))
    elif "crash" in user_query or "urgent" in user_query:
        days = 3
        
    class MockStudent:
        id = state.get("student_id", 1)
        name = state.get("student_name", "Student")
        branch = state.get("student_branch", "CSE")
        cgpa = state.get("student_cgpa", 8.0)
        graduation_year = 2025
        skills = ", ".join(state.get("student_skills", []))
        roll_number = "23471A0501"

    class MockJob:
        id = state.get("job_id", 1)
        title = state.get("job_title", "Software Engineer")
        company_name = state.get("company_name", "Tech Corp")
        description = "Engineering role"
        required_skills = ", ".join(state.get("required_skills", []))
        minimum_cgpa = 6.5
        eligible_branches = state.get("student_branch", "CSE")
        graduation_year = 2025

    generated_plan = generate_interview_prep_plan(MockStudent(), MockJob(), target_days=days)
    
    rebalanced = {
        "agent_name": "Adaptive Plan Rebalancer Agent",
        "adjusted_days": days,
        "phases_count": 4,
        "roadmap": generated_plan.get("daily_roadmap", []),
        "gap_breakdown": generated_plan.get("gap_breakdown", []),
        "mock_questions": generated_plan.get("mock_questions", {})
    }
    return {"rebalanced_plan": rebalanced}


# ==============================================================================
# 6. Consensus Node: Final Readiness Score & Feedback Report Synthesizer
# Aggregates evaluations from all specialist agents into an actionable verdict
# ==============================================================================
def readiness_synthesizer_node(state: PrepOrchestratorState) -> Dict[str, Any]:
    tech = state.get("technical_assessment", {})
    behavioral = state.get("behavioral_assessment", {})
    rebalanced = state.get("rebalanced_plan", {})
    
    tech_score = tech.get("technical_score", 75)
    culture_score = behavioral.get("culture_fit_score", 85)
    
    # Weighted Readiness Metric: 60% Technical + 40% Behavioral/STAR
    final_score = round((tech_score * 0.6) + (culture_score * 0.4))
    
    report = {
        "final_readiness_score": final_score,
        "readiness_tier": "Highly Placement Ready" if final_score >= 80 else ("Conditionally Ready" if final_score >= 60 else "Needs Intensive Remediation"),
        "technical_summary": tech,
        "behavioral_summary": behavioral,
        "rebalanced_timeline": {
            "total_days": rebalanced.get("adjusted_days", state.get("target_days", 30)),
            "schedule_length": len(rebalanced.get("roadmap", []))
        }
    }
    
    response_markdown = (
        f"### 🎯 Placement Prep Multi-Agent Readiness Consensus\n\n"
        f"**Candidate:** {state.get('student_name')} | **Role:** {state.get('job_title')} @ {state.get('company_name')}\n\n"
        f"| Evaluation Pillar | Agent In-Charge | Status & Rating |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **Technical Mastery** | Technical & Code Examiner | `{tech_score}%` ({tech.get('verdict', 'Evaluated')}) |\n"
        f"| **Culture & STAR Metric** | STAR Behavioral Bar-Raiser | `{culture_score}%` (Rubric Aligned) |\n"
        f"| **Adaptive Prep Timeline** | Adaptive Plan Rebalancer | `{rebalanced.get('adjusted_days', 30)} Days` ({len(rebalanced.get('roadmap', []))} Structured Modules) |\n"
        f"| **Composite Placement Readiness** | **Master Consensus** | **`{final_score}/100`** ({report['readiness_tier']}) |\n\n"
        f"**Key Focus:** Address {len(tech.get('critical_gaps', []))} missing skill gaps ({', '.join(tech.get('critical_gaps', [])) or 'None'}) and apply the STAR framework to projects."
    )
    
    return {
        "final_readiness_score": final_score,
        "final_feedback_report": report,
        "final_response": response_markdown
    }


# ==============================================================================
# 7. Dynamic Router Edge
# ==============================================================================
def route_orchestrator_edge(state: PrepOrchestratorState) -> str:
    decision = state.get("routing_decision", "full_consensus")
    if decision in ["technical_examiner", "star_bar_raiser", "plan_rebalancer"]:
        return decision
    return "execute_all_parallel"


# ==============================================================================
# 8. Build the LangGraph Multi-Agent State Machine
# ==============================================================================
def build_prep_agent_ecosystem():
    workflow = StateGraph(PrepOrchestratorState)
    
    # Register Specialist Nodes
    workflow.add_node("master_orchestrator", master_orchestrator_node)
    workflow.add_node("technical_examiner", technical_examiner_node)
    workflow.add_node("star_bar_raiser", star_bar_raiser_node)
    workflow.add_node("plan_rebalancer", plan_rebalancer_node)
    workflow.add_node("readiness_synthesizer", readiness_synthesizer_node)
    
    # Setup Entry Point
    workflow.set_entry_point("master_orchestrator")
    
    # For full multi-agent consensus, pipe sequentially through specialists to synthesizer
    workflow.add_edge("master_orchestrator", "technical_examiner")
    workflow.add_edge("technical_examiner", "star_bar_raiser")
    workflow.add_edge("star_bar_raiser", "plan_rebalancer")
    workflow.add_edge("plan_rebalancer", "readiness_synthesizer")
    workflow.add_edge("readiness_synthesizer", END)
    
    return workflow.compile()


# Global Singleton Instance of the Prep Ecosystem Graph
prep_agent_ecosystem_graph = build_prep_agent_ecosystem()
