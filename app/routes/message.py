from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.models.db import engine
from app.models.message import Message
from app.models.user import User  # ✅ move here

router = APIRouter(prefix="/messages", tags=["messages"])


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/")
def get_messages(
    room_id: int = Query(...),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    session: Session = Depends(get_session)
):
    query = (
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(Message.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )

    messages = session.exec(query).all()

    result = []

    for msg in messages:
        user = session.get(User, msg.user_id)

        result.append({
            "id": msg.id,
            "user_id": msg.user_id,
            "name": user.name,  # 🔥 FIX
            "room_id": msg.room_id,
            "content": msg.content,
            "timestamp": str(msg.timestamp)
        })

    return {
        "room_id": room_id,
        "messages": result
    }