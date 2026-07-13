from pydantic import BaseModel, Field
from datetime import datetime
from app.expeditions.models import ExpeditionStatus, MemberState
from app.users.schemas import UserResponse
from app.expeditions import models


class ExpeditionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    capacity: int = Field(..., gt=1, description="Місткість експедиції має бути більшою за 1")


class ExpeditionCreate(ExpeditionBase):
    pass


class ExpeditionMemberResponse(BaseModel):
    id: int
    user_id: int
    state: MemberState
    invited_at: datetime
    confirmed_at: datetime | None = None
    user: UserResponse

    class Config:
        from_attributes = True


class ExpeditionResponse(ExpeditionBase):
    id: int
    status: ExpeditionStatus
    chief_id: int
    created_at: datetime
    updated_at: datetime
    members: list[ExpeditionMemberResponse] = []

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    user_id: int


class ExpeditionStatusUpdate(BaseModel):
    status: models.ExpeditionStatus

    class Config:
        from_attributes = True