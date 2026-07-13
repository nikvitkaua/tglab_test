from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.expeditions import models, schemas
from app.expeditions.models import Expedition, ExpeditionMember
from app.users.models import User, UserRole
from fastapi import HTTPException, status


def create_expedition(db: Session, exp_in: schemas.ExpeditionCreate, chief_id: int) -> models.Expedition:
    """
    Create an expedition.
    New expedition has status DRAFT.
    """
    db_expedition = models.Expedition(
        title=exp_in.title,
        description=exp_in.description,
        start_at=exp_in.start_at,
        end_at=exp_in.end_at,
        capacity=exp_in.capacity,
        chief_id=chief_id,
        status=models.ExpeditionStatus.DRAFT
    )
    db.add(db_expedition)
    db.commit()
    db.refresh(db_expedition)
    return db_expedition

def get_expedition(db: Session, expedition_id: int) -> type[Expedition] | None:
    """
    Look up an expedition by its id.
    Add all members for this expedition.
    """
    return db.query(models.Expedition).filter(models.Expedition.id == expedition_id).first()

def get_expeditions(db: Session, skip: int = 0, limit: int = 100) -> list[type[Expedition]]:
    """
    List of all expeditions with pagination.
    """
    return db.query(models.Expedition).offset(skip).limit(limit).all()

def invite_member_to_expedition(db: Session, expedition_id: int, user_id: int,
                                chief_id: int) -> models.ExpeditionMember:
    """
    Invitation a member to an expedition.
    """
    expedition = db.query(models.Expedition).filter(models.Expedition.id == expedition_id).first()
    if not expedition:
        raise HTTPException(status_code=404, detail="Експедицію не знайдено")

    if expedition.chief_id != chief_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не є керівником цієї експедиції"
        )

    if expedition.status != models.ExpeditionStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Запрошувати учасників можна тільки в експедицію-чернетку (статус DRAFT)"
        )

    invited_user = db.query(User).filter(User.id == user_id).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="Користувача, якого ви хочете запросити, не знайдено")

    if invited_user.role != UserRole.MEMBER:
        raise HTTPException(
            status_code=400,
            detail="Запросити в експедицію можна тільки користувача з роллю 'member'"
        )

    existing_invite = db.query(models.ExpeditionMember).filter(
        models.ExpeditionMember.expedition_id == expedition_id,
        models.ExpeditionMember.user_id == user_id
    ).first()
    if existing_invite:
        raise HTTPException(status_code=400, detail="Цей користувач вже отримав запрошення")

    current_members_count = db.query(models.ExpeditionMember).filter(
        models.ExpeditionMember.expedition_id == expedition_id
    ).count()

    if current_members_count >= expedition.capacity:
        raise HTTPException(status_code=400, detail="Експедиція вже заповнена (перевищено ліміт capacity)")

    db_member = models.ExpeditionMember(
        expedition_id=expedition_id,
        user_id=user_id,
        state=models.MemberState.INVITED
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def confirm_expedition_participation(db: Session, expedition_id: int, user_id: int) -> type[ExpeditionMember]:
    """
    Accept expedition participation.
    """
    member_record = db.query(models.ExpeditionMember).filter(
        models.ExpeditionMember.expedition_id == expedition_id,
        models.ExpeditionMember.user_id == user_id
    ).first()

    if not member_record:
        raise HTTPException(
            status_code=404,
            detail="Запрошення на цю експедицію для вас не знайдено"
        )

    if member_record.state == models.MemberState.CONFIRMED:
        raise HTTPException(
            status_code=400,
            detail="Ви вже підтвердили участь у цій експедиції"
        )


    if member_record.expedition.status != models.ExpeditionStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Неможливо підтвердити участь, оскільки експедиція вже змінила статус із DRAFT"
        )

    member_record.state = models.MemberState.CONFIRMED
    member_record.confirmed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(member_record)
    return member_record


def update_expedition_status(db: Session, expedition_id: int, new_status: models.ExpeditionStatus,
                             chief_id: int) -> type[Expedition]:
    """
    Change expedition status by chief.
    """
    expedition = db.query(models.Expedition).filter(models.Expedition.id == expedition_id).first()
    if not expedition:
        raise HTTPException(status_code=404, detail="Експедицію не знайдено")

    if expedition.chief_id != chief_id:
        raise HTTPException(status_code=403, detail="Ви не є керівником цієї експедиції")

    current = expedition.status

    if new_status == models.ExpeditionStatus.READY:
        if current != models.ExpeditionStatus.DRAFT:
            raise HTTPException(status_code=400, detail="В статус READY можна перейти тільки з DRAFT")

        confirmed_count = db.query(models.ExpeditionMember).filter(
            models.ExpeditionMember.expedition_id == expedition_id,
            models.ExpeditionMember.state == models.MemberState.CONFIRMED
        ).count()
        if confirmed_count == 0:
            raise HTTPException(status_code=400,
                                detail="Не можна укомплектувати експедицію без підтверджених учасників")

    elif new_status == models.ExpeditionStatus.ACTIVE:
        if current != models.ExpeditionStatus.READY:
            raise HTTPException(status_code=400, detail="Активувати експедицію можна тільки зі статусу READY")

    elif new_status == models.ExpeditionStatus.FINISHED:
        if current != models.ExpeditionStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Завершити експедицію можна тільки якщо вона була ACTIVE")

    else:
        raise HTTPException(status_code=400, detail="Невідомий або недозволений статус")

    expedition.status = new_status
    db.commit()
    db.refresh(expedition)
    return expedition