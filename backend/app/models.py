from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    # male | female | nonbinary | unspecified
    gender = Column(String, nullable=False, default="unspecified")
    bio = Column(Text, default="")
    instagram = Column(String, default="")
    linkedin = Column(String, default="")
    spotify = Column(String, default="")
    phone_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    external_url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    category = Column(String, default="other")
    location = Column(String, default="")
    starts_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_now)


class MatchRequest(Base):
    __tablename__ = "match_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    # casual | party | networking | chill
    vibe = Column(String, default="casual")
    # 20s | 30s | 40plus | any
    age_band = Column(String, default="any")
    # any | women_only | men_only
    gender_preference = Column(String, default="any")
    social_anxiety_friendly = Column(Boolean, default=False)
    first_timer = Column(Boolean, default=False)
    # pending | matched
    status = Column(String, default="pending")
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    created_at = Column(DateTime, default=_now)

    user = relationship("User")
    event = relationship("Event")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    vibe = Column(String, default="casual")
    # forming | active
    status = Column(String, default="active")
    created_at = Column(DateTime, default=_now)

    event = relationship("Event")
    members = relationship("GroupMember", back_populates="group")
    messages = relationship("ChatMessage", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=_now)

    group = relationship("Group", back_populates="members")
    user = relationship("User")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)

    group = relationship("Group", back_populates="messages")
    user = relationship("User")
