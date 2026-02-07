import logging

from fastapi import APIRouter, HTTPException

from app.models.call import OutboundCallRequest
from app.services.call_service import call_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/outbound")
async def initiate_outbound_call(request: OutboundCallRequest):
    """Start a new outbound call."""
    try:
        call_sid = call_service.make_call(
            to=request.to,
            greeting=request.greeting,
            context=request.context,
        )
        return {"call_sid": call_sid, "status": "initiated", "to": request.to}
    except Exception as e:
        logger.error("Failed to initiate call: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{call_sid}")
async def get_call_status(call_sid: str):
    """Get the status of a call."""
    try:
        return call_service.get_call_status(call_sid)
    except Exception as e:
        logger.error("Failed to get call status: %s", e)
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/end/{call_sid}")
async def end_call(call_sid: str):
    """End an active call."""
    try:
        call_service.end_call(call_sid)
        return {"call_sid": call_sid, "status": "completed"}
    except Exception as e:
        logger.error("Failed to end call: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
