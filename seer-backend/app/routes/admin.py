from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database.database import SessionLocal
from app.models.user import User, Role, Permission
from app.core.permissions import require_permission
from pydantic import BaseModel
import logging

# ✅ Initialize Router
router = APIRouter(prefix="/admin", tags=["Admin"])

# ✅ Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Dependency to get DB session
def get_db():
    """Provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Schema for creating roles
class RoleCreateRequest(BaseModel):
    name: str

# ✅ Schema for assigning/removing permissions
class PermissionAssignRequest(BaseModel):
    role_name: str
    permission_name: str

# ✅ Admin Dashboard Statistics
@router.get("/stats", dependencies=[Depends(require_permission("VIEW_ADMIN_STATS"))])
def get_admin_stats(db: Session = Depends(get_db)):
    """Fetch admin dashboard stats"""

    total_users = db.query(User).count()
    total_admins = db.query(User).join(Role).filter(Role.name == "ADMIN").count()
    total_roles = db.query(Role).count()
    total_permissions = db.query(Permission).count()

    stats = {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_roles": total_roles,
        "total_permissions": total_permissions,
        "message": "Admin stats fetched successfully"
    }
    
    logger.info(f"✅ Admin Stats Retrieved: {stats}")  # ✅ Logging
    
    return stats

# ✅ Get all users (requires "MANAGE_USERS" permission)
@router.get("/users", dependencies=[Depends(require_permission("MANAGE_USERS"))])
def get_all_users(
    db: Session = Depends(get_db),
    role: str = Query(None, description="Filter users by role")
):
    """Fetch all users, optionally filter by role."""
    
    query = db.query(User).options(joinedload(User.role))

    if role:
        role_obj = db.query(Role).filter(Role.name == role.upper()).first()
        if not role_obj:
            raise HTTPException(status_code=400, detail="Invalid role filter")
        query = query.filter(User.role_id == role_obj.id)

    users = query.all()

    logger.info(f"✅ Retrieved {len(users)} Users")  # ✅ Logging
    return users

# ✅ Change user role (requires "MANAGE_USERS" permission)
@router.put("/users/{user_id}/role", dependencies=[Depends(require_permission("MANAGE_USERS"))])
def change_user_role(user_id: int, new_role: str, db: Session = Depends(get_db)):
    """Update a user's role, ensuring the role exists in DB."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Validate role exists in DB
    role = db.query(Role).filter(Role.name == new_role.upper()).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Invalid role '{new_role}'")

    # ✅ Assign correct role_id
    user.role_id = role.id
    db.commit()
    db.refresh(user)

    logger.info(f"✅ User {user.email} role updated to {new_role.upper()}")  # ✅ Logging
    return {"message": f"User {user.email} role updated to {new_role.upper()}"}

# ✅ Get all roles (requires "MANAGE_ROLES" permission)
@router.get("/roles", dependencies=[Depends(require_permission("MANAGE_ROLES"))])
def get_all_roles(db: Session = Depends(get_db)):
    """Fetch all available roles."""
    roles = db.query(Role).all()

    logger.info(f"✅ Retrieved {len(roles)} Roles")  # ✅ Logging
    return roles

# ✅ Create a new role (requires "MANAGE_ROLES" permission)
@router.post("/roles", dependencies=[Depends(require_permission("MANAGE_ROLES"))])
def create_role(role_data: RoleCreateRequest, db: Session = Depends(get_db)):
    """Create a new role if it doesn't exist."""
    
    role_name = role_data.name.upper()  # ✅ Normalize case
    existing_role = db.query(Role).filter(Role.name == role_name).first()
    
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")

    new_role = Role(name=role_name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    logger.info(f"✅ Role '{new_role.name}' created successfully")  # ✅ Logging
    return {"message": f"Role '{new_role.name}' created successfully"}

# ✅ Delete a role (requires "MANAGE_ROLES" permission)
@router.delete("/roles/{role_id}", dependencies=[Depends(require_permission("MANAGE_ROLES"))])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Delete a role if it's not 'ADMIN' and has no users assigned."""
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role.name == "ADMIN":
        raise HTTPException(status_code=400, detail="Cannot delete the ADMIN role")

    # ✅ Prevent deleting roles with assigned users
    if db.query(User).filter(User.role_id == role_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete role with assigned users")

    db.delete(role)
    db.commit()

    logger.info(f"✅ Role '{role.name}' deleted successfully")  # ✅ Logging
    return {"message": f"Role '{role.name}' deleted successfully"}

# ✅ Assign a permission to a role (requires "MANAGE_PERMISSIONS" permission)
@router.post("/permissions", dependencies=[Depends(require_permission("MANAGE_PERMISSIONS"))])
def assign_permission(request: PermissionAssignRequest, db: Session = Depends(get_db)):
    """Assign a permission to a role."""
    
    role = db.query(Role).options(joinedload(Role.permissions)).filter(Role.name == request.role_name.upper()).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permission = db.query(Permission).filter(Permission.name == request.permission_name).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    # ✅ Prevent duplicate permissions
    if permission in role.permissions:
        return {"message": f"Permission '{request.permission_name}' is already assigned to role '{request.role_name}'"}

    role.permissions.append(permission)
    db.commit()

    logger.info(f"✅ Permission '{request.permission_name}' assigned to role '{request.role_name}'")  # ✅ Logging
    return {"message": f"Permission '{request.permission_name}' assigned to role '{request.role_name}'"}

# ✅ Remove a permission from a role (requires "MANAGE_PERMISSIONS" permission)
@router.delete("/permissions", dependencies=[Depends(require_permission("MANAGE_PERMISSIONS"))])
def remove_permission(request: PermissionAssignRequest, db: Session = Depends(get_db)):
    """Remove a permission from a role."""
    
    role = db.query(Role).options(joinedload(Role.permissions)).filter(Role.name == request.role_name.upper()).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permission = db.query(Permission).filter(Permission.name == request.permission_name).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if permission not in role.permissions:
        raise HTTPException(status_code=400, detail=f"Permission '{request.permission_name}' is not assigned to role '{request.role_name}'")

    role.permissions.remove(permission)
    db.commit()

    logger.info(f"✅ Permission '{request.permission_name}' removed from role '{request.role_name}'")  # ✅ Logging
    return {"message": f"Permission '{request.permission_name}' removed from role '{request.role_name}'"}
