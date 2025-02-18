from fastapi import APIRouter, Depends
from app.dependencies.auth import require_role

router = APIRouter()

@router.get("/admin")
def admin_route(user=Depends(require_role("admin"))):
    return {"message": f"Welcome, {user.username}. You have admin access!"}

@router.get("/user")
def user_route(user=Depends(require_role("user"))):
    return {"message": f"Welcome, {user.username}. You have user access!"}
