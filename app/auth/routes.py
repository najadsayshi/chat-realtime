from fastapi import APIRouter
from pydantic import BaseModel
from app.auth.jwt_handler import create_token

router = APIRouter()


class LoginRequest(BaseModel):
    user_id: int


@router.post("/login")
async def login(request: LoginRequest):
    token = create_token(request.user_id)

    return {
        "access_token": token
    }