from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    age: int
    gender: str = "unspecified"
    bio: str = ""
    instagram: str = ""
    linkedin: str = ""
    spotify: str = ""
    phone_verified: bool = False


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    gender: str
    bio: str
    instagram: str
    linkedin: str
    spotify: str
    phone_verified: bool


class EventCreate(BaseModel):
    external_url: str
    title: str
    category: str = "other"
    location: str = ""
    starts_at: Optional[datetime] = None
    performer: str = ""
    venue: str = ""
    city: str = ""
    description: str = ""
    image_url: str = ""
    match_key: str = ""


class EventPreviewIn(BaseModel):
    url: str


class EventPreview(BaseModel):
    external_url: str
    title: str = ""
    category: str = "other"
    location: str = ""
    starts_at: Optional[datetime] = None
    performer: str = ""
    venue: str = ""
    city: str = ""
    description: str = ""
    image_url: str = ""
    match_key: str = ""
    ai_enriched: bool = False
    error: Optional[str] = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_url: str
    title: str
    category: str
    location: str
    starts_at: Optional[datetime]
    performer: str = ""
    venue: str = ""
    city: str = ""
    description: str = ""
    image_url: str = ""
    match_key: str = ""
    ai_enriched: bool = False


class MatchRequestCreate(BaseModel):
    user_id: int
    event_id: int
    vibe: str = "casual"
    age_band: str = "any"
    gender_preference: str = "any"
    social_anxiety_friendly: bool = False
    first_timer: bool = False


class MatchRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    event_id: int
    vibe: str
    age_band: str
    gender_preference: str
    social_anxiety_friendly: bool
    first_timer: bool
    status: str
    group_id: Optional[int]


class GroupMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserOut


class GroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    vibe: str
    status: str
    event: EventOut
    members: list[GroupMemberOut]


class MatchResult(BaseModel):
    request: MatchRequestOut
    matched: bool
    group: Optional[GroupOut] = None


class ChatMessageCreate(BaseModel):
    user_id: int
    body: str


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    user_id: int
    body: str
    created_at: datetime
