from pydantic import BaseModel
from datetime import datetime

class ThreatLogSchema(BaseModel):
    id: int
    type: str
    severity: str
    source_ip: str
    is_alert: bool
    timestamp: datetime

    class Config:
        from_attributes = True  # ✅ Converts SQLAlchemy models into Pydantic schemas
