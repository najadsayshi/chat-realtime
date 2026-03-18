from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.models.db import engine
from app.models.message import Message

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

    return {
        "room_id": room_id,
        "count": len(messages),
        "messages": messages
    }