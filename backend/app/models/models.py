from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Table, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Association table for Incidents and Services (Many-to-Many)
incident_services = Table(
    "incident_services",
    Base.metadata,
    Column("incident_id", String, ForeignKey("incidents.id"), primary_key=True),
    Column("service_id", String, ForeignKey("services.id"), primary_key=True)
)

class Service(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String, primary_key=True) # e.g., 'checkout-api'
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_team: Mapped[Optional[str]] = mapped_column(String)

    # Relationships
    incidents: Mapped[List["Incident"]] = relationship(
        secondary=incident_services, back_populates="affected_services"
    )
    deployments: Mapped[List["Deployment"]] = relationship(back_populates="service")
    events: Mapped[List["Event"]] = relationship(back_populates="service")
    metrics: Mapped[List["MetricSnapshot"]] = relationship(back_populates="service")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String, primary_key=True) # e.g., 'INC-1042'
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="OPEN") # OPEN, INVESTIGATING, RESOLVED
    severity: Mapped[str] = mapped_column(String, nullable=False) # SEV-1, SEV-2, SEV-3
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    affected_services: Mapped[List["Service"]] = relationship(
        secondary=incident_services, back_populates="incidents"
    )
    events: Mapped[List["Event"]] = relationship(back_populates="incident")


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    service_id: Mapped[str] = mapped_column(String, ForeignKey("services.id"), nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False) # e.g. v1.8.2
    deployed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deployed_by: Mapped[Optional[str]] = mapped_column(String)
    commit_hash: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationship
    service: Mapped["Service"] = relationship(back_populates="deployments")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("incidents.id"))
    service_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("services.id"))
    event_type: Mapped[str] = mapped_column(String, nullable=False) # e.g. deployment, error_rate_spike, db_exhaustion
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String) # INFO, WARNING, ERROR, CRITICAL

    # Relationships
    incident: Mapped[Optional["Incident"]] = relationship(back_populates="events")
    service: Mapped[Optional["Service"]] = relationship(back_populates="events")


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[str] = mapped_column(String, ForeignKey("services.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    metric_name: Mapped[str] = mapped_column(String, nullable=False) # e.g. latency_ms, error_rate, connection_count
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False) # ms, percent, count

    # Relationship
    service: Mapped["Service"] = relationship(back_populates="metrics")
