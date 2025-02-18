from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.database.database import SessionLocal
from app.models.user import User
from app.core.auth import SECRET_KEY, ALGORITHM
from typing import Dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get the current logged-in user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Extracts user from JWT token and verifies authentication"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload: Dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

# ✅ Enforce Role-Based Access Control
def require_role(role_name: str):
    """Returns a dependency that enforces role-based access control"""
    def role_dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        user_role = db.query(User).filter(User.id == current_user.id).first()
        if not user_role or user_role.role.name != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_dependency
