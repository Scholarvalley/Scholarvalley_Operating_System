from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import create_token, hash_password, verify_password
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
settings = get_settings()


@router.post("/register", response_model=UserRead)
def register_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        role="client",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_expires = timedelta(days=settings.refresh_token_expire_days)

    access_token = create_token(str(user.id), user.role, access_expires)
    refresh_token = create_token(str(user.id), user.role, refresh_expires)

    return Token(access_token=access_token, refresh_token=refresh_token)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    from app.core.security import decode_token

    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = session.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or missing user",
        )
    return user


def require_role(*roles: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if roles and current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return dependency

