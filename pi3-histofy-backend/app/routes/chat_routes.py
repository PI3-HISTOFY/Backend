# app/routes/chat_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from app.services.auth import get_current_user  # si quieres protegerlo
from app.models.user_model import User

from app.services.chatbot_service import respond_and_query

router = APIRouter(prefix="/chat", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Mensaje del usuario en lenguaje natural")
    limit: Optional[int] = Field(50, ge=1, le=500, description="Máximo de resultados a devolver")

class ChatResponse(BaseModel):
    top_intent: str
    entities: Dict[str, Any]
    query: Dict[str, Any] | None
    answer: str
    count: int
    items: list

@router.post("/ask", response_model=ChatResponse)
def ask_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)  # quítalo si quieres endpoint público
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Debe iniciar sesión")

    out = respond_and_query(payload.message, limit=payload.limit or 50)
    # devolvemos tal cual lo que arma el servicio
    return ChatResponse(**{
        "top_intent": out.get("top_intent", "fallback"),
        "entities": out.get("entities", {}),
        "query": out.get("query"),
        "answer": out.get("answer", ""),
        "count": out.get("count", 0),
        "items": out.get("items", []),
    })
