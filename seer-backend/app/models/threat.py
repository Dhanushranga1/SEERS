from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class ThreatLog(Base):
    __tablename__ = "threat_logs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    source_ip = Column(String, nullable=False)
    is_alert = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
