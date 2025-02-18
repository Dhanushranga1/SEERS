from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User, Role, Permission, role_permissions
from app.core.auth import get_current_user

def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_role(required_role: str):
    """Dependency to restrict route access based on user role."""
    def role_dependency(
        current_user: User = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
        user_role = db.query(Role).filter(Role.id == current_user.role_id).first()

        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not found"
            )

        # ✅ Ensure the user has the correct role
        if user_role.name.lower() != required_role.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}, but user has role: {user_role.name}"
            )

        print(f"✅ Access granted: {current_user.email} has role '{user_role.name}'")  
        return current_user

    return role_dependency

def require_permission(permission_name: str):
    """Dependency to restrict route access based on user permissions."""
    def permission_dependency(
        current_user: User = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
        user_role = db.query(Role).filter(Role.id == current_user.role_id).first()

        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not found"
            )

        # ✅ FIX: Join `role_permissions` correctly to check if the role has the required permission
        permission_exists = (
            db.query(Permission)
            .join(role_permissions)  # ✅ Correct join with the association table
            .join(Role)
            .filter(Role.id == user_role.id, Permission.name == permission_name)
            .first()
        )

        if not permission_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Missing permission: {permission_name} for role {user_role.name}"
            )

        print(f"✅ Access granted: {current_user.email} with role '{user_role.name}' has permission '{permission_name}'")
        return current_user

    return permission_dependency
