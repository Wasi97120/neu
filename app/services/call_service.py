import logging

from twilio.rest import Client

from app.config import settings

logger = logging.getLogger(__name__)


class CallService:
    """Service for managing outbound calls via Twilio."""

    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    def make_call(
        self, to: str, greeting: str | None = None, context: str | None = None
    ) -> str:
        """Initiate an outbound call.

        Returns the call SID.
        """
        # Build query params for the webhook so it knows the greeting/context
        webhook_url = f"{settings.base_url}/webhook/outbound"
        params = []
        if greeting:
            params.append(f"greeting={greeting}")
        if context:
            params.append(f"context={context}")
        if params:
            webhook_url += "?" + "&".join(params)

        call = self.client.calls.create(
            to=to,
            from_=settings.twilio_phone_number,
            url=webhook_url,
            status_callback=f"{settings.base_url}/webhook/status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            record=False,
        )

        logger.info("Outbound call initiated: SID=%s, to=%s", call.sid, to)
        return call.sid

    def get_call_status(self, call_sid: str) -> dict:
        """Get the current status of a call."""
        call = self.client.calls(call_sid).fetch()
        return {
            "call_sid": call.sid,
            "status": call.status,
            "to": call.to,
            "from_": call.from_,
            "direction": call.direction,
            "duration": call.duration,
            "start_time": str(call.start_time) if call.start_time else None,
            "end_time": str(call.end_time) if call.end_time else None,
        }

    def end_call(self, call_sid: str) -> None:
        """Terminate an active call."""
        self.client.calls(call_sid).update(status="completed")
        logger.info("Call ended: SID=%s", call_sid)


call_service = CallService()
