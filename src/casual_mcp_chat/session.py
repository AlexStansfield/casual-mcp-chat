from casual_mcp.models import ChatMessage
from pydantic import BaseModel


class Session(BaseModel):
    model: str | None = None
    system_prompt: str | None = None
    prompt_name: str | None = None
    messages: list[ChatMessage] = []
