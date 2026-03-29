from fastapi import APIRouter
from pydantic import BaseModel
from ..services.url_analyzer import url_analyzer

router = APIRouter(prefix="/api/check_site", tags=["scanner"])

class UrlPayload(BaseModel):
    url: str

class SiteResult(BaseModel):
    is_dangerous: bool
    reason: str

@router.post("/", response_model=SiteResult)
async def check_website(payload: UrlPayload):
    """
    Called continuously by background.js to monitor web navigation dynamically across all tabs.
    Returns whether the site matches pirated/malicious rule engines.
    """
    result = url_analyzer.analyze_url(payload.url)
    return SiteResult(is_dangerous=result["is_dangerous"], reason=result["reason"])
