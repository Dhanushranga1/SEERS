from fastapi import APIRouter
import random
from datetime import datetime, timedelta

router = APIRouter(prefix="/threats/ai", tags=["Threat AI"])

# 🔹 Mock AI Attack Predictions
THREAT_TYPES = ["DDoS", "Phishing", "Ransomware", "SQL Injection", "Brute Force", "Malware"]

def generate_threat_predictions():
    return [
        {
            "type": random.choice(THREAT_TYPES),
            "predicted_time": (datetime.now() + timedelta(minutes=random.randint(10, 60))).strftime("%H:%M:%S"),
            "risk_score": random.randint(20, 100),
        }
        for _ in range(3)
    ]

# ✅ Get AI-Based Threat Predictions
@router.get("/predictions")
def get_threat_predictions():
    return {"predictions": generate_threat_predictions()}
