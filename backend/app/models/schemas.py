from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class ServiceBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner_team: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ServiceRead(ServiceBase):
    pass

class DeploymentBase(BaseModel):
    id: str
    service_id: str
    version: str
    deployed_at: datetime
    deployed_by: Optional[str] = None
    commit_hash: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DeploymentRead(DeploymentBase):
    pass

class EventBase(BaseModel):
    id: str
    incident_id: Optional[str] = None
    service_id: Optional[str] = None
    event_type: str
    timestamp: datetime
    description: str
    severity: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EventRead(EventBase):
    pass

class MetricSnapshotBase(BaseModel):
    id: int
    service_id: str
    timestamp: datetime
    metric_name: str
    value: float
    unit: str

    model_config = ConfigDict(from_attributes=True)

class MetricSnapshotRead(MetricSnapshotBase):
    pass

class IncidentBase(BaseModel):
    id: str
    title: str
    status: str
    severity: str
    started_at: datetime
    resolved_at: Optional[datetime] = None
    summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class IncidentRead(IncidentBase):
    affected_services: List[ServiceRead] = []

class IncidentDetailRead(IncidentRead):
    events: List[EventRead] = []

class TimelineItem(BaseModel):
    id: str
    timestamp: datetime
    type: str # 'event', 'deployment', 'metric'
    service_id: Optional[str] = None
    title: str
    description: str
    severity: Optional[str] = None
    details: Optional[dict] = None
