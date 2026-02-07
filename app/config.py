from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Anthropic
    anthropic_api_key: str = ""

    # Server
    base_url: str = "http://localhost:8000"
    host: str = "0.0.0.0"
    port: int = 8000

    # Agent
    agent_name: str = "KI-Assistent"
    agent_language: str = "de"
    agent_system_prompt: str = (
        "Du bist ein freundlicher und professioneller Telefonassistent. "
        "Sprich klar und deutlich. Halte dich kurz und komme auf den Punkt. "
        "Antworte immer in 1-2 kurzen Saetzen, da deine Antworten vorgelesen werden."
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
