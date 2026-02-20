from passlib.context import CryptContext
from itsdangerous import URLSafeSerializer
from backend.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeSerializer(settings.SECRET_KEY)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_session(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})