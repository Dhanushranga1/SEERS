import random
from faker import Faker
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.threat import ThreatLog

fake = Faker()

# Attack Types & Severity Mapping
ATTACK_TYPES = [
    ("DDoS Attack", "Critical"),
    ("SQL Injection", "High"),
    ("XSS Attack", "Medium"),
    ("Brute Force", "High"),
    ("Phishing Attempt", "Medium"),
    ("Unauthorized Access", "Critical"),
    ("Port Scanning", "Low"),
]

def seed_threat_logs():
    db: Session = SessionLocal()
    
    for _ in range(50):  # Generate 50 fake threat logs
        attack_type, severity = random.choice(ATTACK_TYPES)
        log = ThreatLog(
            type=attack_type,
            severity=severity,
            source_ip=fake.ipv4(),
            is_alert=True if severity in ["Critical", "High"] else False
        )
        db.add(log)

    db.commit()
    db.close()
    print("✅ 50 Fake Threat Logs Inserted Successfully!")

if __name__ == "__main__":
    seed_threat_logs()
