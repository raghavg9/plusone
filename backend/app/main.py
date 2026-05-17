from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import matching, models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PlusOne — Social Coordination Layer for Events")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------- users
@app.post("/users", response_model=schemas.UserOut)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


# --------------------------------------------------------------- events
@app.post("/events", response_model=schemas.EventOut)
def create_event(payload: schemas.EventCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.Event)
        .filter(models.Event.external_url == payload.external_url)
        .first()
    )
    if existing:
        return existing
    event = models.Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/events", response_model=list[schemas.EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).order_by(models.Event.created_at.desc()).all()


@app.get("/events/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    return event


# ------------------------------------------------------- match requests
@app.post("/match-requests", response_model=schemas.MatchResult)
def create_match_request(
    payload: schemas.MatchRequestCreate, db: Session = Depends(get_db)
):
    if not db.get(models.User, payload.user_id):
        raise HTTPException(404, "User not found")
    if not db.get(models.Event, payload.event_id):
        raise HTTPException(404, "Event not found")

    req = models.MatchRequest(**payload.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)

    matching.try_match(db, payload.event_id)
    db.refresh(req)

    group = db.get(models.Group, req.group_id) if req.group_id else None
    return schemas.MatchResult(
        request=req, matched=req.status == "matched", group=group
    )


@app.get("/match-requests/{request_id}", response_model=schemas.MatchResult)
def get_match_request(request_id: int, db: Session = Depends(get_db)):
    req = db.get(models.MatchRequest, request_id)
    if not req:
        raise HTTPException(404, "Match request not found")
    group = db.get(models.Group, req.group_id) if req.group_id else None
    return schemas.MatchResult(
        request=req, matched=req.status == "matched", group=group
    )


# --------------------------------------------------------------- groups
@app.get("/groups/{group_id}", response_model=schemas.GroupOut)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.get(models.Group, group_id)
    if not group:
        raise HTTPException(404, "Group not found")
    return group


@app.get(
    "/groups/{group_id}/messages",
    response_model=list[schemas.ChatMessageOut],
)
def list_messages(group_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Group, group_id):
        raise HTTPException(404, "Group not found")
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.group_id == group_id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )


@app.post(
    "/groups/{group_id}/messages", response_model=schemas.ChatMessageOut
)
def post_message(
    group_id: int,
    payload: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
):
    group = db.get(models.Group, group_id)
    if not group:
        raise HTTPException(404, "Group not found")
    is_member = (
        db.query(models.GroupMember)
        .filter(
            models.GroupMember.group_id == group_id,
            models.GroupMember.user_id == payload.user_id,
        )
        .first()
    )
    if not is_member:
        raise HTTPException(403, "User is not a member of this group")
    msg = models.ChatMessage(
        group_id=group_id, user_id=payload.user_id, body=payload.body
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
