from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    target_permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    admin = relationship("User", foreign_keys=[admin_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    target_role = relationship("Role", foreign_keys=[target_role_id])
    target_permission = relationship("Permission", foreign_keys=[target_permission_id])
