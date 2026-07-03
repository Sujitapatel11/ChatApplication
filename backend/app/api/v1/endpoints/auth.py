from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository

router = APIRouter()


class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: UUID
    username: str
    email: str
    display_name: str | None
    profile_picture: str | None
    online: bool
    is_verified: bool
    model_config = {"from_attributes": True}

class UpdateIn(BaseModel):
    display_name: str | None = Field(None, max_length=64)
    bio: str | None = Field(None, max_length=300)


@router.post("/register", response_model=UserOut, status_code=201)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    if await repo.exists(body.email, body.username):
        raise HTTPException(409, "Email or username already taken")
    user = await repo.create(
        username=body.username.lower(),
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        display_name=body.username,
    )
    return user


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_email(body.email)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(403, "Account deactivated")
    return TokenOut(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(body: UpdateIn, user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    updates = body.model_dump(exclude_none=True)
    if updates:
        repo = UserRepository(db)
        user = await repo.update(user, **updates)
    return user
