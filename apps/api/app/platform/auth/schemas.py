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


class PasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    remember_me: bool = False


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    password: str = Field(min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=1)


class CreatePasswordRequest(BaseModel):
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class ActivateAccountRequest(BaseModel):
    token: str = Field(min_length=1)
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)
