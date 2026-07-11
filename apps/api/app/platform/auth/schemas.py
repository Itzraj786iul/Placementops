import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import UserResponse


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_new_user: bool = False


class AuthCodeExchangeRequest(BaseModel):
    code: str = Field(min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class MessageResponse(BaseModel):
    message: str


class DevLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
