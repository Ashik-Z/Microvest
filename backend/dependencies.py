from fastapi import Cookie, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeSerializer, BadSignature
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.config import settings


serializer = URLSafeSerializer(settings.SECRET_KEY)


def get_current_user(
        session: str | None = Cookie(default=None),
        db: Session = Depends(get_db)
) -> User | None:
    if not session:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={
                "Location": "/login"
            }
        )
    try:
        data = serializer.loads(session)
        user_id = data.get("user_id")
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={
                "Location": "/login"
            }
        )
    

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers = {
                "Location": "/login"
            }
        )
    return user