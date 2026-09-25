from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import IncidentRead, IncidentDetailRead, TimelineItem
from app.repositories.incident_repository import IncidentRepository

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

@router.get("", response_model=List[IncidentRead])
def list_incidents(db: Session = Depends(get_db)):
    """List all production incidents chronologically."""
    return IncidentRepository.get_all_incidents(db)

@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get metadata for a specific incident."""
    incident = IncidentRepository.get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found"
        )
    return incident

@router.get("/{incident_id}/timeline", response_model=List[TimelineItem])
def get_incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    """Get aggregated chronological timeline of events & deployments for an incident."""
    incident = IncidentRepository.get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found"
        )
    return IncidentRepository.get_incident_timeline(db, incident_id)
