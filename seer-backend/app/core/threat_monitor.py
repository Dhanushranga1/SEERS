import random
import time
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.threat import ThreatLog

# Thresholds for Automated Alerts
CRITICAL_THRESHOLD = 5  # If 5+ critical threats occur in 10 minutes, trigger an alert
HIGH_THRESHOLD = 10      # If 10+ high threats occur in 10 minutes, trigger an alert

def analyze_threats():
    """Analyzes recent threats & triggers alerts if needed."""
    db: Session = SessionLocal()

    # Get latest 10-minute threat logs
    recent_threats = db.query(ThreatLog).filter(ThreatLog.timestamp >= func.now() - func.interval("10 minutes")).all()

    # Count threats by severity
    critical_count = sum(1 for threat in recent_threats if threat.severity == "Critical")
    high_count = sum(1 for threat in recent_threats if threat.severity == "High")

    if critical_count >= CRITICAL_THRESHOLD:
        print("🚨 ALARM: Multiple Critical Threats Detected!")
        # Potential Future Enhancement: Send an automated alert (Email, Slack, etc.)

    if high_count >= HIGH_THRESHOLD:
        print("⚠️ WARNING: High Number of Threats Detected!")

    db.close()

def monitor_threats():
    """Continuously runs threat detection in real-time."""
    while True:
        analyze_threats()
        time.sleep(600)  # Run every 10 minutes

if __name__ == "__main__":
    print("🚀 Threat Monitoring System Started...")
    monitor_threats()
