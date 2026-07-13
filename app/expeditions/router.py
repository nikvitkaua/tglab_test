from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.users.router import get_current_user
from app.users.models import User, UserRole
from app.expeditions import service, schemas
from app.core.websocket_manager import socket_manager


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


@router.patch("/{expedition_id}/status", response_model=schemas.ExpeditionResponse)
async def change_expedition_status(
    expedition_id: int,
    status_data: schemas.ExpeditionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update status (DRAFT -> READY -> ACTIVE -> FINISHED).
    """
    if current_user.role != UserRole.CHIEF:
        raise HTTPException(status_code=403, detail="Тільки керівники можуть змінювати статус")

    updated_expedition = service.update_expedition_status(
        db=db,
        expedition_id=expedition_id,
        new_status=status_data.status,
        chief_id=current_user.id
    )

    await socket_manager.broadcast({
        "event": "expedition_status_changed",
        "expedition_id": updated_expedition.id,
        "new_status": updated_expedition.status.value,
        "title": updated_expedition.title
    })

    return updated_expedition


@router.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint for websocket connections.
    """
    await socket_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        socket_manager.disconnect(websocket)
