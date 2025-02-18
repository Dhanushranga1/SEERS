from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User, Role
from app.core.auth import hash_password, verify_password, create_access_token, get_current_user
from pydantic import BaseModel, EmailStr
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Pydantic Schemas
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

# ✅ Register User
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user and assigns the default USER role"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if (existing_user):
        raise HTTPException(status_code=400, detail="Email already registered")

    # ✅ Ensure default 'USER' role exists
    user_role = db.query(Role).filter(Role.name == "USER").first()
    if not user_role:
        raise HTTPException(status_code=500, detail="Default USER role not found. Contact admin.")

    # ✅ Hash password and create new user
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        role_id=user_role.id  # ✅ Assign default role_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

# ✅ Login User
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_user(user_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - Verify user and return JWT token with role"""
    
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        print("🚨 User not found in DB")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    print("✅ User Found:", user.email, "| Role ID:", user.role_id)

    if not verify_password(user_data.password, user.hashed_password):
        print("🚨 Password incorrect for:", user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # ✅ Fetch role details
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        print("🚨 Role not found for user:", user.email)
        raise HTTPException(status_code=500, detail="User role not found. Contact admin.")

    print("✅ Role Found:", role.name)

    access_token = create_access_token(
        {"sub": user.email, "role": role.name}, 
        expires_delta=timedelta(minutes=60)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role.name
    }

# ✅ FIXED: Get Current User Details
@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch details of the currently authenticated user"""
    role = db.query(Role).filter(Role.id == current_user.role_id).first()

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=role.name if role else "UNKNOWN"
    )
