import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExpeditionStatus(str, enum.Enum):
    DRAFT = "draft"
    READY = "ready"
    ACTIVE = "active"
    FINISHED = "finished"

class MemberState(str, enum.Enum):
    INVITED = "invited"
    CONFIRMED = "confirmed"

class Expedition(Base):
    __tablename__ = "expeditions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(ExpeditionStatus), default=ExpeditionStatus.DRAFT, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=False)
    chief_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    chief = relationship("User", back_populates="led_expeditions")
    members = relationship("ExpeditionMember", back_populates="expedition", cascade="all, delete-orphan")

class ExpeditionMember(Base):
    __tablename__ = "expedition_members"

    id = Column(Integer, primary_key=True, index=True)
    expedition_id = Column(Integer, ForeignKey("expeditions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state = Column(SQLEnum(MemberState), default=MemberState.INVITED, nullable=False)
    invited_at = Column(DateTime, default=datetime.now(timezone.utc))
    confirmed_at = Column(DateTime, nullable=True)

    expedition = relationship("Expedition", back_populates="members")
    user = relationship("User", back_populates="expeditions_participated")
