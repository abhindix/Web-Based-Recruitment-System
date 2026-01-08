from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db, require_roles
from ...models.user import User, UserRole
from ...schemas.chat import ChatRequest, ChatResponse
from ...services.ai_agent import run_manager_agent

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(UserRole.MANAGER)),
):
    if payload.messages and len(payload.messages) > 0:
        msgs = [{"role": m.role, "content": m.content} for m in payload.messages]
    elif payload.message and payload.message.strip():
        msgs = [{"role": "user", "content": payload.message.strip()}]
    else:
        raise HTTPException(status_code=400, detail="Provide either 'messages' (non-empty) or 'message'.")
        
    # Ensure role strings align with the OpenAI chat format
    reply, data = await run_manager_agent(db=db, hiring_manager_id=current.id, chat_messages=msgs)
    return {"reply": reply, "data": data}
