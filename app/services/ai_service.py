import anthropic

from app.config import settings
from app.models.call import ConversationTurn


class AIService:
    """Service for generating AI responses using Claude."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.conversations: dict[str, list[ConversationTurn]] = {}

    def start_conversation(self, call_sid: str, context: str | None = None) -> None:
        """Initialize a new conversation for a call."""
        self.conversations[call_sid] = []
        if context:
            self.conversations[call_sid].append(
                ConversationTurn(role="user", content=f"[Kontext: {context}]")
            )
            self.conversations[call_sid].append(
                ConversationTurn(
                    role="assistant",
                    content="Verstanden, ich beruecksichtige diesen Kontext.",
                )
            )

    def get_response(self, call_sid: str, user_input: str) -> str:
        """Generate an AI response for the given user input."""
        if call_sid not in self.conversations:
            self.start_conversation(call_sid)

        self.conversations[call_sid].append(
            ConversationTurn(role="user", content=user_input)
        )

        messages = [
            {"role": turn.role, "content": turn.content}
            for turn in self.conversations[call_sid]
        ]

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            system=settings.agent_system_prompt,
            messages=messages,
        )

        assistant_text = response.content[0].text

        self.conversations[call_sid].append(
            ConversationTurn(role="assistant", content=assistant_text)
        )

        return assistant_text

    def end_conversation(self, call_sid: str) -> None:
        """Clean up conversation data for a completed call."""
        self.conversations.pop(call_sid, None)


ai_service = AIService()
