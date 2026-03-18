from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime



class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int
    user_id: int
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)