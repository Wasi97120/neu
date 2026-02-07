from pydantic import BaseModel


class OutboundCallRequest(BaseModel):
    """Request to initiate an outbound call."""

    to: str
    greeting: str | None = None
    context: str | None = None


class CallStatus(BaseModel):
    """Status of a call."""

    call_sid: str
    status: str
    to: str
    from_: str
    direction: str


class ConversationTurn(BaseModel):
    """A single turn in the conversation."""

    role: str
    content: str
