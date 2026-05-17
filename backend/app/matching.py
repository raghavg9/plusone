"""Auto-matching: groups pending requests for an event into compatible groups."""

from sqlalchemy.orm import Session

from . import models

MIN_GROUP_SIZE = 3
MAX_GROUP_SIZE = 6


def _genders(db: Session, requests: list[models.MatchRequest]) -> dict[int, str]:
    ids = {r.user_id for r in requests}
    users = db.query(models.User).filter(models.User.id.in_(ids)).all()
    return {u.id: u.gender for u in users}


def _is_valid_group(
    requests: list[models.MatchRequest], genders: dict[int, str]
) -> bool:
    """All members must share a vibe, a (non-'any') age band, and satisfy
    every member's gender preference."""
    if not requests:
        return False

    vibes = {r.vibe for r in requests}
    if len(vibes) > 1:
        return False

    bands = {r.age_band for r in requests if r.age_band != "any"}
    if len(bands) > 1:
        return False

    member_genders = {genders.get(r.user_id, "unspecified") for r in requests}
    for r in requests:
        if r.gender_preference == "women_only" and member_genders != {"female"}:
            return False
        if r.gender_preference == "men_only" and member_genders != {"male"}:
            return False

    return True


def try_match(db: Session, event_id: int) -> None:
    """Greedily cluster pending requests for an event and persist any
    cluster that reaches the minimum group size."""
    pending = (
        db.query(models.MatchRequest)
        .filter(
            models.MatchRequest.event_id == event_id,
            models.MatchRequest.status == "pending",
        )
        .order_by(models.MatchRequest.created_at.asc())
        .all()
    )
    if len(pending) < MIN_GROUP_SIZE:
        return

    genders = _genders(db, pending)

    clusters: list[list[models.MatchRequest]] = []
    for req in pending:
        placed = False
        for cluster in clusters:
            if len(cluster) >= MAX_GROUP_SIZE:
                continue
            if _is_valid_group(cluster + [req], genders):
                cluster.append(req)
                placed = True
                break
        if not placed:
            clusters.append([req])

    for cluster in clusters:
        if len(cluster) < MIN_GROUP_SIZE:
            continue
        group = models.Group(
            event_id=event_id, vibe=cluster[0].vibe, status="active"
        )
        db.add(group)
        db.flush()
        for req in cluster:
            db.add(models.GroupMember(group_id=group.id, user_id=req.user_id))
            req.status = "matched"
            req.group_id = group.id
        db.commit()
