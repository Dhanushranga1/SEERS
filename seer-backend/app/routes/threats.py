# app/routes/threats.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.threat_log import ThreatLog
from app.schemas.threat import ThreatLogSchema  # ✅ Import Pydantic schema
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/threats", tags=["Threat Intelligence"])

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Fetch all threat logs with filtering options
@router.get("/logs", response_model=List[ThreatLogSchema])  # ✅ Use Pydantic schema
def get_threat_logs(
    db: Session = Depends(get_db),
    severity: str = Query(None, description="Filter by severity"),
    threat_type: str = Query(None, description="Filter by type"),
    time_range: int = Query(24, description="Time range in hours")
):
    """Fetch threat logs with optional filters."""
    query = db.query(ThreatLog)
    if severity:
        query = query.filter(ThreatLog.severity == severity)
    if threat_type:
        query = query.filter(ThreatLog.type == threat_type)
    if time_range:
        time_limit = datetime.utcnow() - timedelta(hours=time_range)
        query = query.filter(ThreatLog.timestamp >= time_limit)

    return query.all()  # ✅ FastAPI now serializes using ThreatLogSchema

# ✅ Fetch threat statistics
@router.get("/stats")
def get_threat_stats(db: Session = Depends(get_db)):
    """Fetch aggregated threat statistics."""
    total_threats = db.query(ThreatLog).count()
    active_alerts = db.query(ThreatLog).filter(ThreatLog.is_alert == True).count()
    severity_counts = db.query(ThreatLog.severity, func.count(ThreatLog.severity)).group_by(ThreatLog.severity).all()
    severity_distribution = {sev: count for sev, count in severity_counts}
    
    return {
        "total_threats": total_threats,
        "active_alerts": active_alerts,
        "severity_distribution": severity_distribution
    }

# ✅ Mark a threat as resolved
@router.put("/logs/{log_id}/resolve")
def resolve_threat(log_id: int, db: Session = Depends(get_db)):
    """Mark a threat as resolved."""
    threat = db.query(ThreatLog).filter(ThreatLog.id == log_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat log not found")
    threat.is_alert = False
    db.commit()
    return {"message": "Threat resolved successfully"}
