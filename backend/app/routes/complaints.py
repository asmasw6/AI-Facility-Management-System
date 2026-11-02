from fastapi import APIRouter

from app.models.models import ComplaintRequest
from app.agents.complaint_agent import complaint_agent


async def process_complaint(
    customer_id: str,
    text: str,
    call_id: str | None = None
):
    return await complaint_agent.ainvoke({
        "customer_id": customer_id,
        "call_id": call_id,
        "text": text
    })
    
 