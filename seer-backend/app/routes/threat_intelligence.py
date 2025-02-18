from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.threat import ThreatLog
from app.core.threat_ai import analyze_threat
import requests

router = APIRouter(prefix="/threats", tags=["Threat Intelligence"])

# ✅ Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Fetch External Threat Intelligence Data
@router.get("/external")
def fetch_external_threats():
    sources = [
        "https://www.virustotal.com/api/v3/intelligence",
        "https://otx.alienvault.com/api/v1/pulses",
    ]
    threats = []
    
    for source in sources:
        try:
            response = requests.get(source)
            if response.status_code == 200:
                threats.extend(response.json())
        except Exception as e:
            print(f"Failed to fetch data from {source}: {e}")
    
    return {"external_threats": threats}

# ✅ Log Cyber Threats and Apply AI Risk Scoring
@router.post("/log")
def log_threat(ip_address: str, description: str, db: Session = Depends(get_db)):
    risk_score = analyze_threat(ip_address, description)
    new_threat = ThreatLog(ip=ip_address, description=description, risk_score=risk_score)
    
    db.add(new_threat)
    db.commit()
    db.refresh(new_threat)
    
    return {"message": "Threat logged successfully", "risk_score": risk_score}

# ✅ Retrieve Threat Logs
@router.get("/logs")
def get_threat_logs(db: Session = Depends(get_db)):
    threats = db.query(ThreatLog).all()
    return threats
