from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage] | None = None 
    message: str | None = None

class ChatResponse(BaseModel):
    reply: str
    data: dict | None = None
