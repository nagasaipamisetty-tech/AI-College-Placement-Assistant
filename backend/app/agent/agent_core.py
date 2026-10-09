import re
import json
from typing import Dict, Any, List
from app.services.eligibility import check_eligibility, parse_skills
from app.services.prep_planner import generate_interview_prep_plan

# Company-specific interview focus areas & culture
COMPANY_KNOWLEDGE = {
    "google": {
        "culture": "Googleyness, intellectual humility, navigating ambiguity, scalable thinking, and collaborative ownership.",
        "rounds": ["Round 1: Online Coding Assessment (2 Medium DSA Problems)", "Round 2: Technical Coding (Graphs, Dynamic Programming, Trees)", "Round 3: System Architecture & Data Structures", "Round 4: Googleyness & Leadership"],
        "key_focus": "Time and space complexity proofs, handling extreme edge cases, modular and clean code structure.",
        "tips": "Always ask clarifying questions before writing code, state your brute-force complexity, then optimize to O(N) or O(log N)."
    },
    "microsoft": {
        "culture": "Growth mindset, customer obsession, team collaboration, and diversity of perspectives.",
        "rounds": ["Round 1: Online Technical Assessment (Algorithms & Data Structures)", "Round 2: Low-Level Design & Object-Oriented Programming", "Round 3: High-Level System Design & Coding", "Round 4: Managerial, Values & Culture Fit"],
        "key_focus": "Maintainability, test-driven approach, clean design patterns (SOLID), and defensive error handling.",
        "tips": "Focus on modular class design, separation of concerns, and writing comprehensive test cases."
    },
    "amazon": {
        "culture": "16 Leadership Principles (Customer Obsession, Ownership, Bias for Action, Deliver Results, Invent and Simplify, Earn Trust).",
        "rounds": ["Round 1: Online Assessment (Coding + Work Simulation)", "Round 2: Data Structures & Problem Solving", "Round 3: Low-Level & High-Level System Design", "Round 4: Bar Raiser (Behavioral + Architecture)"],
        "key_focus": "Strict STAR format answers with quantitative impact metrics, customer-centric architecture, and operational scalability.",
        "tips": "Every behavioral answer must tie directly to an Amazon Leadership Principle with concrete numerical results."
    },
    "uber": {
        "culture": "Go get it, trip obsessed, see the forest and the trees, build globally, live locally.",
        "rounds": ["Round 1: Coding Challenge (Concurrency & High Throughput)", "Round 2: Algorithmic Problem Solving", "Round 3: Distributed System Design (Geohashing, Real-Time Dispatch)", "Round 4: Behavioral & Culture"],
        "key_focus": "Low-latency distributed systems, concurrency, geohashing/spatial indexing, and fault tolerance.",
        "tips": "Familiarize yourself with Redis caching, WebSockets, and geospatial data indexing (QuadTree/H3)."
    },
    "stripe": {
        "culture": "Users first, rigorous craft, macro optimism, micro speed, clear written communication.",
        "rounds": ["Round 1: Practical Bug Squash / Code Integration", "Round 2: Real-World API Design & Idempotency", "Round 3: System Architecture & Data Reliability", "Round 4: Behavioral & Values"],
        "key_focus": "Code readability, idempotency keys, financial ACID transaction guarantees, and production debugging.",
        "tips": "Write clean, self-documenting code with comprehensive unit tests and focus on defensive error handling."
    },
    "default": {
        "culture": "Analytical problem-solving, structured communication, fundamental computer science foundation, and teamwork.",
        "rounds": ["Round 1: Technical Online Assessment", "Round 2: Core Technical & Coding Round", "Round 3: System Design / Problem Solving", "Round 4: HR & Leadership Round"],
        "key_focus": "Strong CS fundamentals (DSA, DBMS, OS, Networks), clear verbalization of thought process, and adaptability.",
        "tips": "Think aloud as you solve problems, communicate tradeoffs clearly, and test your code with boundary cases."
    }
}

TECHNICAL_EXPLANATIONS = {
    "sql": """### 📊 SQL Mastery & Interview Essentials
1. **Window Functions**: `RANK()`, `DENSE_RANK()`, `ROW_NUMBER()` compute rankings within partitions without collapsing rows.
   ```sql
   SELECT department_id, employee_name, salary,
          DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank
   FROM employees;
   ```
2. **JOINs**: `INNER JOIN` (only matching rows), `LEFT JOIN` (all left rows + matching right), `CROSS JOIN` (cartesian product).
3. **Indexing**: B-Tree indexes optimize equality (`=`) and range queries (`BETWEEN`, `<`, `>`). Clustered indexes dictate physical row storage order.
4. **ACID Properties**: Atomicity (all or nothing), Consistency (valid state transitions), Isolation (independent transactions), Durability (persisted on disk).""",

    "react": """### ⚛️ React 19 & Frontend Core Concepts
1. **Hooks Optimization**:
   - `useMemo`: Caches expensive computation results between re-renders.
   - `useCallback`: Memoizes function instance references to prevent re-rendering memoized child components.
   - `useRef`: Retains mutable state across renders without triggering a re-render.
2. **Virtual DOM & Reconciliation**: React Fiber creates a lightweight in-memory representation of the DOM, diffs the tree using heuristic O(N) reconciliation, and batches minimal DOM updates.
3. **State Management**: Use local state (`useState`) for isolated UI, Context API for low-frequency global settings (themes/auth), and Redux Toolkit/Zustand for high-frequency complex state.""",

    "dsa": """### 💡 Algorithmic Patterns & LeetCode Strategies
1. **Two Pointers**: Optimal for sorted arrays, palindrome validation, and collision traps (e.g. *Container With Most Water*). O(N) time, O(1) space.
2. **Sliding Window**: Ideal for contiguous subarrays/substrings with length constraints or target sums (e.g. *Longest Substring Without Repeating Characters*).
3. **Monotonic Stack**: For finding the Next Greater / Smaller element in linear O(N) time (e.g. *Daily Temperatures*, *Largest Rectangle in Histogram*).
4. **Topological Sort**: BFS (Kahn's algorithm using in-degrees) or DFS for dependency resolution (e.g. *Course Schedule*).
5. **Dynamic Programming**: Identify base case + overlapping subproblems + state transition equation (e.g. *0/1 Knapsack*, *Coin Change*, *LCS*).""",

    "system design": """### 🏗️ System Design & Scalability Principles
1. **Load Balancing**: Distribute incoming traffic across server pools using Round Robin, Least Connections, or Consistent Hashing.
2. **Caching Strategy**: Redis / Memcached. Use **Cache-Aside** for read-heavy workloads. Prevent cache stampedes with mutex locks or probabilistic early expiration.
3. **Database Scaling**: Read Replicas (scale reads), Sharding / Partitioning (scale writes horizontally by shard key).
4. **CAP Theorem**: In distributed network partitions (P), choose between Consistency (C - e.g. CockroachDB/Zookeeper) vs Availability (A - e.g. Cassandra/DynamoDB).
5. **Rate Limiting**: Token Bucket, Leaky Bucket, or Redis Sliding Window Log."""
}


class AutonomousPlacementAgent:
    """
    Self-contained, Zero-API-Key Intelligent Placement Copilot Agent.
    Orchestrates intent classification, dynamic multi-day roadmap generation, technical explanations, and mock interviews.
    """

    def __init__(self):
        pass

    def get_company_intel(self, company_name: str) -> dict:
        key = (company_name or "").lower().strip()
        for k in COMPANY_KNOWLEDGE:
            if k in key:
                return COMPANY_KNOWLEDGE[k]
        return COMPANY_KNOWLEDGE["default"]

    def analyze_profile(self, student, job) -> dict:
        eligibility = check_eligibility(student, job)
        required = parse_skills(job.required_skills)
        acquired = parse_skills(student.skills)

        matched_skills = sorted(required & acquired)
        missing_skills = sorted(required - acquired)
        company_intel = self.get_company_intel(job.company_name)

        return {
            "eligible": eligibility["eligible"],
            "reasons": eligibility["reasons"],
            "skill_match_percentage": eligibility["skill_match_percentage"],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "company_intel": company_intel
        }

    def generate_plan(self, student, job, duration_days: int = 30) -> dict:
        """Generates dynamic N-day preparation plan reusing prep planner engine."""
        return generate_interview_prep_plan(student, job, target_days=duration_days)

    def chat_interact(self, student, job, query: str) -> dict:
        """
        Conversational assistant logic.
        Intelligently routes user queries, provides rich markdown responses, and supports dynamic day roadmaps.
        """
        q = (query or "").lower().strip()
        analysis = self.analyze_profile(student, job)
        company = job.company_name or "Target Company"
        title = job.title or "Target Role"
        intel = analysis["company_intel"]
        missing = analysis["missing_skills"]

        # INTENT 0: Multi-Agent Prep Ecosystem & Readiness Consensus
        if any(k in q for k in ["readiness", "consensus", "ecosystem", "panel", "evaluate me", "overall score", "bar raiser", "examiner", "comprehensive review"]):
            try:
                from app.agent.prep_agent_ecosystem import prep_agent_ecosystem_graph
                initial_state = {
                    "student_id": student.id,
                    "student_name": student.name,
                    "student_branch": getattr(student, "branch", "CSE"),
                    "student_cgpa": float(getattr(student, "cgpa", 8.0) or 8.0),
                    "student_skills": list(parse_skills(student.skills)),
                    "job_id": job.id,
                    "job_title": title,
                    "company_name": company,
                    "required_skills": list(parse_skills(job.required_skills)),
                    "target_days": 30,
                    "user_query": q,
                    "routing_decision": "",
                    "technical_assessment": {},
                    "behavioral_assessment": {},
                    "rebalanced_plan": {},
                    "final_readiness_score": 0,
                    "final_feedback_report": {},
                    "final_response": ""
                }
                ecosystem_result = prep_agent_ecosystem_graph.invoke(initial_state)
                reply = ecosystem_result.get("final_response") or "Multi-Agent readiness evaluation completed."
                return {
                    "reply": reply,
                    "message": reply,
                    "type": "consensus",
                    "data": {
                        "readiness_score": ecosystem_result.get("final_readiness_score", 80),
                        "report": ecosystem_result.get("final_feedback_report", {}),
                        "ecosystem": "LangGraph Multi-Agent Panel"
                    }
                }
            except Exception as e:
                # Graceful fallback to profile analysis
                pass

        # INTENT 1: Dynamic Multi-Day Timeline Request (e.g. "30 day plan", "14 days", "3 days", "crash course", "60 days")
        day_match = re.search(r'(\d+)\s*(?:day|days)', q)
        if day_match or any(k in q for k in ["crash", "roadmap", "schedule", "study plan", "how to prepare", "timeline"]):
            days = int(day_match.group(1)) if day_match else (3 if "crash" in q or "urgent" in q else 30)
            plan = self.generate_plan(student, job, duration_days=days)
            reply = (
                f"### 🎯 Custom {days}-Day Preparation Plan Generated for {title} @ {company}\n\n"
                f"I have constructed a comprehensive **{days}-Day Day-by-Day Roadmap** tailored to bridge your {len(missing)} missing skill gap(s).\n\n"
                f"- **Target Role**: {title} ({plan.get('job_archetype', 'Technical Role')})\n"
                f"- **Duration**: {days} Days (Divided across 4 learning phases)\n"
                f"- **Focus Areas**: {', '.join(s.title() for s in missing) if missing else 'Advanced System Architecture & Coding'}\n\n"
                f"👉 *The interactive checklist below has been updated with your full {days}-day schedule.*"
            )
            return {
                "reply": reply,
                "message": reply,
                "type": "plan",
                "data": plan
            }

        # INTENT 2: Mock Interview Questions & Answers
        if any(k in q for k in ["mock", "question", "questions", "interview question", "screening", "practice question"]):
            plan = self.generate_plan(student, job, duration_days=30)
            mock_data = plan.get("mock_questions", {})
            tech_q = mock_data.get("technical_coding", [])[:3]
            concept_q = mock_data.get("core_conceptual", [])[:2]
            behavioral_q = mock_data.get("behavioral_star", [])[:2]

            reply = f"### 📝 High-Yield Mock Questions for {company} ({title})\n\n"
            if tech_q:
                reply += "**💻 Technical & Coding Challenges:**\n"
                for i, tq in enumerate(tech_q, 1):
                    reply += f"{i}. {tq}\n"
                reply += "\n"
            if concept_q:
                reply += "**🔍 Core Conceptual & Architecture Questions:**\n"
                for i, cq in enumerate(concept_q, 1):
                    reply += f"{i}. {cq}\n"
                reply += "\n"
            if behavioral_q:
                reply += f"**🤝 {company} Culture & Behavioral (STAR) Questions:**\n"
                for i, bq in enumerate(behavioral_q, 1):
                    reply += f"{i}. {bq}\n"
                reply += "\n"
            reply += "💡 *Tip: Answer behavioral questions using the STAR framework (Situation, Task, Action, Result) with quantitative metrics!*"

            return {
                "reply": reply,
                "message": reply,
                "type": "questions",
                "data": mock_data
            }

        # INTENT 3: Missing Skill Gaps & Readiness Diagnosis
        if any(k in q for k in ["gap", "missing", "skill", "skills", "fit", "eligible", "readiness", "score"]):
            if missing:
                reply = (
                    f"### 🔍 Skill Gap Diagnosis for {title} @ {company}\n\n"
                    f"Your current technical alignment is **{analysis['skill_match_percentage']}%** with **{len(missing)} missing competency gap(s)**:\n\n"
                )
                for s in missing:
                    reply += f"- ❌ **{s.title()}**: Required by {company}. Recommended study: syntax basics, practical coding exercises, and documentation.\n"
                if analysis["matched_skills"]:
                    reply += f"\n**✓ Verified Matched Skills ({len(analysis['matched_skills'])}):** {', '.join(s.title() for s in analysis['matched_skills'])}\n"
                reply += f"\n💡 *Recommendation: Use the 30-day preparation roadmap to resolve these gaps before your drive.*"
            else:
                reply = (
                    f"### 🎉 Outstanding Profile Alignment!\n\n"
                    f"You have a **100% skill match** for **{title} at {company}**! You meet all required technical competencies: "
                    f"*{', '.join(s.title() for s in analysis['matched_skills'])}*.\n\n"
                    f"Focus your preparation on **System Design**, **LeetCode Hard problems**, and **{company}'s behavioral culture round**."
                )
            return {
                "reply": reply,
                "message": reply,
                "type": "text",
                "data": {"missing_skills": missing, "matched_skills": analysis["matched_skills"], "match_percentage": analysis["skill_match_percentage"]}
            }

        # INTENT 4: STAR Behavioral & HR Round Coaching
        if any(k in q for k in ["behavioral", "star", "tell me about yourself", "conflict", "weakness", "strength", "hr", "leadership"]):
            reply = (
                f"### 🌟 STAR Framework Guide for {company} Interviews\n\n"
                f"To ace behavioral rounds, structure every response into the 4 STAR components:\n\n"
                f"1. **Situation (15%)**: Set the context (e.g. *'During my 6th semester capstone project, our team built a microservices application...'*)\n"
                f"2. **Task (15%)**: Define the specific challenge or goal you were responsible for solving.\n"
                f"3. **Action (50%)**: Detail the exact technical steps YOU took (e.g. *'I implemented Redis caching, profiled slow queries using EXPLAIN, and restructured database indexes...'*)\n"
                f"4. **Result (20%)**: Deliver concrete, measurable impact (e.g. *'This reduced endpoint latency by 42% and supported 5,000 concurrent user sessions.'*)\n\n"
                f"💡 **Key Tip for {company}**: {intel['culture']}"
            )
            return {
                "reply": reply,
                "message": reply,
                "type": "text",
                "data": {"framework": "STAR", "company": company}
            }

        # INTENT 5: Specific Technical Concept Explanations (SQL, React, DSA, System Design, Python, Docker, etc.)
        for topic_key, explanation in TECHNICAL_EXPLANATIONS.items():
            if topic_key in q:
                return {
                    "reply": explanation,
                    "message": explanation,
                    "type": "technical",
                    "data": {"topic": topic_key}
                }

        # INTENT 6: Company-Specific Culture & Intel
        if any(k in q for k in ["culture", "company", "intel", "rounds", "hiring process", "salary", "interview process"]):
            reply = (
                f"### 🏢 {company} Placement & Interview Intel\n\n"
                f"- **Engineering Culture**: {intel['culture']}\n"
                f"- **Interview Pipeline**:\n"
            )
            for idx, r in enumerate(intel["rounds"], 1):
                reply += f"  {idx}. {r}\n"
            reply += (
                f"- **Evaluator Core Focus**: {intel['key_focus']}\n"
                f"- **Preparation Advice**: {intel.get('tips', 'Review DSA and system design fundamentals.')}\n"
            )
            return {
                "reply": reply,
                "message": reply,
                "type": "text",
                "data": intel
            }

        # INTENT 7: Resume & Project Guidance
        if any(k in q for k in ["resume", "project", "latex", "elevator pitch", "ats", "projects"]):
            reply = (
                f"### 📄 ATS Resume & Project Defense Strategy for {company}\n\n"
                f"1. **Use Jake's Resume Template**: Our built-in **Tailor LaTeX Resume** button formats your resume in clean, single-page ATS format.\n"
                f"2. **Write Action-Driven Bullets**: Use the Google XYZ formula: *'Accomplished [X], as measured by [Y], by doing [Z]'*.\n"
                f"3. **2-Minute Project Elevator Pitch**:\n"
                f"   - *Problem Statement*: What real-world bottleneck did you solve?\n"
                f"   - *Architecture & Stack*: Tech stack chosen and why (e.g. FastAPI + SQLite + Redis).\n"
                f"   - *Key Engineering Hurdle*: Difficult bug or concurrency challenge overcome.\n"
                f"   - *Outcome*: Quantifiable result (response time, throughput, accuracy)."
            )
            return {
                "reply": reply,
                "message": reply,
                "type": "text",
                "data": {"category": "resume"}
            }

        # DEFAULT INTELLIGENT COPILOT RESPONSE
        default_reply = (
            f"Hello {student.name}! I am your AI Placement Copilot for **{title} at {company}**.\n\n"
            f"Here is how I can assist your placement preparation:\n"
            f"- 🎯 **Custom Roadmap**: Ask *'Generate a 30-day preparation plan'* or *'Create a 7-day sprint'*.\n"
            f"- 📝 **Mock Questions**: Ask *'Give me high-yield mock interview questions for {company}'*.\n"
            f"- 🔍 **Skill Gap Analysis**: Ask *'What are my missing skill gaps?'*.\n"
            f"- 💡 **Technical Explanations**: Ask me about *'SQL Window Functions'*, *'React Hooks'*, *'Two Pointers'*, or *'System Design'*\n"
            f"- 🤝 **HR & Behavioral**: Ask *'How to answer behavioral questions using STAR method?'*.\n"
            f"- 🏢 **Company Intel**: Ask *'What is {company} interview process and culture?'*."
        )
        return {
            "reply": default_reply,
            "message": default_reply,
            "type": "text",
            "data": {"student": student.name, "job": title, "company": company}
        }
