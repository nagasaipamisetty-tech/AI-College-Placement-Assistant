from fastapi import APIRouter, Depends, Query
from app.models import User
from app.dependencies import require_roles
from app.services.live_jobs import fetch_live_internet_opportunities, fetch_live_coding_practice

router = APIRouter(prefix="/api/live", tags=["Live Internet Market (Students Only)"])


@router.get("/opportunities")
def get_live_opportunities(
    search: str = Query(default="", max_length=100),
    user: User = Depends(require_roles("student"))
):
    """
    Dedicated Students-Only Endpoint:
    Fetches real-time off-campus hiring opportunities directly from the live web and top tech companies.
    """
    opportunities = fetch_live_internet_opportunities(search=search, limit=20)
    return {
        "count": len(opportunities),
        "source": "Live Internet Job Feeds & Top Tech Off-Campus Portals",
        "items": opportunities
    }


@router.get("/practice")
def get_live_practice(
    skill: str = Query(default="python", max_length=50),
    user: User = Depends(require_roles("student"))
):
    """
    Dedicated Students-Only Endpoint:
    Fetches live LeetCode coding problems mapped to a specific skill.
    """
    problems = fetch_live_coding_practice(skill=skill)
    return {
        "skill": skill,
        "problems": problems
    }
