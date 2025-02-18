from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def log_audit_action(
    db: Session, admin_id: int, action: str, target_user_id=None, target_role_id=None, target_permission_id=None
):
    """Logs IAM actions performed by admins."""
    log_entry = AuditLog(
        admin_id=admin_id,
        action=action,
        target_user_id=target_user_id,
        target_role_id=target_role_id,
        target_permission_id=target_permission_id,
    )
    db.add(log_entry)
    db.commit()
