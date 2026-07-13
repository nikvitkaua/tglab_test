from sqlalchemy.orm import Session
from app.users import models, schemas
from app.core.security import get_password_hash
from app.users.models import User


def get_user_by_email(db: Session, email: str) -> type[User] | None:
    """
    Looking for a user in db with an email.
    Return User object or None if not found.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Get a pydantic user object and add it to the database.
    """
    hashed_pwd = get_password_hash(user_in.password)

    db_user = models.User(
        email=user_in.email,
        name=user_in.name,
        role=user_in.role,
        hashed_password=hashed_pwd
    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user