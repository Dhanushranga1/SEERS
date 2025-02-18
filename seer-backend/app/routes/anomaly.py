from fastapi import APIRouter
import random

router = APIRouter(prefix="/threats/anomalies", tags=["Anomaly Detection"])

# 🔹 Mock Anomalies
ANOMALY_EVENTS = [
    "Unusual login from Russia",
    "Multiple failed SSH logins",
    "Large data transfer detected",
    "Unrecognized API key usage",
    "Spike in outbound traffic",
]

def detect_anomalies():
    return [
        {"event": random.choice(ANOMALY_EVENTS), "risk_score": random.randint(30, 100)}
        for _ in range(3)
    ]

# ✅ Get AI-Detected Anomalies
@router.get("/")
def get_anomalies():
    return {"anomalies": detect_anomalies()}
