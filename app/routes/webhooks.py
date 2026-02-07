import logging
from urllib.parse import unquote

from fastapi import APIRouter, Form, Query, Response

from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])


def twiml_response(twiml: str) -> Response:
    """Return a TwiML XML response."""
    return Response(content=twiml, media_type="application/xml")


@router.post("/outbound")
async def handle_outbound(
    CallSid: str = Form(""),
    greeting: str = Query(default=""),
    context: str = Query(default=""),
):
    """Handle the initial outbound call connection.

    Twilio calls this webhook when the recipient picks up.
    """
    logger.info("Outbound call answered: SID=%s", CallSid)

    # Initialize conversation with optional context
    decoded_context = unquote(context) if context else None
    ai_service.start_conversation(CallSid, context=decoded_context)

    # Use custom greeting or default
    if greeting:
        greet_text = unquote(greeting)
    else:
        greet_text = (
            "Hallo, hier spricht Ihr KI-Assistent. Wie kann ich Ihnen helfen?"
        )

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="de-DE" voice="Polly.Vicki">{greet_text}</Say>
    <Gather input="speech" language="de-DE" speechTimeout="auto"
            action="/webhook/respond?CallSid={CallSid}" method="POST">
        <Say language="de-DE" voice="Polly.Vicki">Ich hoere Ihnen zu.</Say>
    </Gather>
    <Say language="de-DE" voice="Polly.Vicki">
        Ich konnte Sie leider nicht verstehen. Auf Wiedersehen.
    </Say>
</Response>"""
    return twiml_response(twiml)


@router.post("/respond")
async def handle_response(
    CallSid: str = Query(default=""),
    SpeechResult: str = Form(default=""),
):
    """Handle speech input from the caller and respond with AI."""
    logger.info("Speech received for SID=%s: %s", CallSid, SpeechResult)

    if not SpeechResult:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="de-DE" voice="Polly.Vicki">
        Entschuldigung, ich konnte Sie nicht verstehen. Koennten Sie das bitte wiederholen?
    </Say>
    <Gather input="speech" language="de-DE" speechTimeout="auto"
            action="/webhook/respond?CallSid={CallSid}" method="POST">
        <Say language="de-DE" voice="Polly.Vicki">Ich hoere Ihnen zu.</Say>
    </Gather>
</Response>"""
        return twiml_response(twiml)

    # Check for goodbye signals
    goodbye_phrases = ["tschuess", "auf wiedersehen", "bye", "ende", "aufhoeren"]
    if any(phrase in SpeechResult.lower() for phrase in goodbye_phrases):
        ai_service.end_conversation(CallSid)
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="de-DE" voice="Polly.Vicki">
        Vielen Dank fuer das Gespraech. Auf Wiedersehen!
    </Say>
    <Hangup/>
</Response>"""
        return twiml_response(twiml)

    # Get AI response
    ai_response = ai_service.get_response(CallSid, SpeechResult)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="de-DE" voice="Polly.Vicki">{ai_response}</Say>
    <Gather input="speech" language="de-DE" speechTimeout="auto"
            action="/webhook/respond?CallSid={CallSid}" method="POST">
        <Say language="de-DE" voice="Polly.Vicki">Moechten Sie noch etwas sagen?</Say>
    </Gather>
    <Say language="de-DE" voice="Polly.Vicki">
        Da Sie nichts mehr sagen, beende ich das Gespraech. Auf Wiedersehen!
    </Say>
</Response>"""
    return twiml_response(twiml)


@router.post("/status")
async def handle_status_callback(
    CallSid: str = Form(""),
    CallStatus: str = Form(""),
):
    """Handle call status updates from Twilio."""
    logger.info("Call status update: SID=%s, Status=%s", CallSid, CallStatus)

    if CallStatus in ("completed", "failed", "busy", "no-answer", "canceled"):
        ai_service.end_conversation(CallSid)

    return Response(status_code=204)
