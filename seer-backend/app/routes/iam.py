from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User, Role, Permission
from app.core.permissions import require_permission
from pydantic import BaseModel
import logging

# ✅ Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/iam", tags=["Identity & Access Management"])

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Schema for updating roles & permissions
class UserRoleUpdateRequest(BaseModel):
    user_id: int
    new_role: str

class PermissionAssignRequest(BaseModel):
    role_name: str
    permission_name: str

# ✅ Fetch all users with their roles
@router.get("/users", dependencies=[Depends(require_permission("MANAGE_USERS"))])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    
    if not users:
        logger.warning("⚠️ No users found in the system.")
    
    logger.info(f"✅ Retrieved {len(users)} users from IAM")
    return [{"id": user.id, "email": user.email, "role": user.role.name} for user in users]

# ✅ Fetch all roles
@router.get("/roles", dependencies=[Depends(require_permission("MANAGE_ROLES"))])
def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()

    if not roles:
        logger.warning("⚠️ No roles found in the system.")

    logger.info(f"✅ Retrieved {len(roles)} IAM Roles")
    return [{"id": role.id, "name": role.name} for role in roles]

# ✅ Fetch all permissions
@router.get("/permissions", dependencies=[Depends(require_permission("MANAGE_PERMISSIONS"))])
def get_all_permissions(db: Session = Depends(get_db)):
    permissions = db.query(Permission).all()

    if not permissions:
        logger.warning("⚠️ No permissions found in the system.")

    logger.info(f"✅ Retrieved {len(permissions)} IAM Permissions")
    return [{"id": perm.id, "name": perm.name} for perm in permissions]

# ✅ Update User Role
@router.put("/users/role", dependencies=[Depends(require_permission("MANAGE_USERS"))])
def update_user_role(request: UserRoleUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.name == request.new_role.upper()).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{request.new_role}' not found")

    user.role_id = role.id
    db.commit()
    logger.info(f"✅ User {user.email} role updated to {role.name}")
    return {"message": f"User {user.email} role updated to {role.name}"}

# ✅ Assign a Permission to a Role
@router.post("/permissions/assign", dependencies=[Depends(require_permission("MANAGE_PERMISSIONS"))])
def assign_permission_to_role(request: PermissionAssignRequest, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.name == request.role_name.upper()).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permission = db.query(Permission).filter(Permission.name == request.permission_name).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if permission in role.permissions:
        return {"message": f"Permission '{request.permission_name}' already assigned to role '{request.role_name}'"}

    role.permissions.append(permission)
    db.commit()
    logger.info(f"✅ Assigned permission '{request.permission_name}' to role '{request.role_name}'")
    return {"message": f"Permission '{request.permission_name}' assigned to role '{request.role_name}'"}

# ✅ Remove a Permission from a Role
@router.delete("/permissions/remove", dependencies=[Depends(require_permission("MANAGE_PERMISSIONS"))])
def remove_permission_from_role(request: PermissionAssignRequest, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.name == request.role_name.upper()).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permission = db.query(Permission).filter(Permission.name == request.permission_name).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if permission not in role.permissions:
        raise HTTPException(status_code=400, detail=f"Permission '{request.permission_name}' is not assigned to role '{request.role_name}'")

    role.permissions.remove(permission)
    db.commit()
    logger.info(f"✅ Removed permission '{request.permission_name}' from role '{request.role_name}'")
    return {"message": f"Permission '{request.permission_name}' removed from role '{request.role_name}'"}
