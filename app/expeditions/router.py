from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.users.router import get_current_user
from app.users.models import User, UserRole
from app.expeditions import service, schemas


router = APIRouter(prefix="/expeditions", tags=["Expeditions"])


@router.post("/", response_model=schemas.ExpeditionResponse, status_code=status.HTTP_201_CREATED)
def create_new_expedition(
        exp_in: schemas.ExpeditionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Create new expedition.
    Only for users with role 'chief'.
    """
    if current_user.role != UserRole.CHIEF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки користувачі з роллю chief можуть створювати експедиції"
        )

    return service.create_expedition(db, exp_in=exp_in, chief_id=current_user.id)


@router.get("/", response_model=list[schemas.ExpeditionResponse])
def read_expeditions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Get all expeditions.
    For all users.
    """
    return service.get_expeditions(db, skip=skip, limit=limit)


@router.post("/{expedition_id}/members", response_model=schemas.ExpeditionMemberResponse,
             status_code=status.HTTP_201_CREATED)
def invite_user_to_expedition(
        expedition_id: int,
        invitation: schemas.InvitationCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Invite user to expedition.
    Only for users with role 'chief' and who create this expedition.
    """
    if current_user.role != UserRole.CHIEF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки керівники (chief) можуть запрошувати учасників"
        )

    return service.invite_member_to_expedition(
        db=db,
        expedition_id=expedition_id,
        user_id=invitation.user_id,
        chief_id=current_user.id
    )


@router.put("/{expedition_id}/members/confirm", response_model=schemas.ExpeditionMemberResponse)
def confirm_participation(
        expedition_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Confirm user to participate in expedition.
    Only for invited users with role 'member'
    """
    if current_user.role != UserRole.MEMBER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки користувачі з роллю 'member' можуть підтверджувати участь"
        )

    return service.confirm_expedition_participation(
        db=db,
        expedition_id=expedition_id,
        user_id=current_user.id
    )