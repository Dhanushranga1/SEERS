from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class ThreatLog(Base):
    __tablename__ = "threat_logs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # Threat type (e.g., DDoS, Phishing, etc.)
    severity = Column(String, nullable=False)  # Severity level (Critical, High, Medium, Low)
    source_ip = Column(String, nullable=False)  # Attacker's IP address
    is_alert = Column(Boolean, default=True)  # Whether the threat is active
    timestamp = Column(DateTime, default=func.now())  # Time of detection
    resolved = Column(Boolean, default=False)  # Whether it has been marked as resolved
