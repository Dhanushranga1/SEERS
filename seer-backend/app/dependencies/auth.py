from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from app.core.auth import decode_access_token
from app.database.database import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Security(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    email: str = payload.get("sub")
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_role(role_name: str):
    def role_dependency(user: User = Depends(get_current_user)):
        if user.role.name != role_name:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return user
    return role_dependency
