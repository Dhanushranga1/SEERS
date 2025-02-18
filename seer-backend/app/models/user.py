from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum

# ✅ Shared Many-to-Many Table for Roles & Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=2)  # Default to USER role

    role = relationship("Role", back_populates="users")

    def set_password(self, password: str):
        """Set the password for the user"""
        from app.core.auth import hash_password  # ✅ Fix circular import
        self.hashed_password = hash_password(password)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(UserRole), unique=True, nullable=False)

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
