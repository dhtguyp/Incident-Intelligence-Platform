from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import IncidentRead, IncidentDetailRead, TimelineItem
from app.repositories.incident_repository import IncidentRepository
from app.services.investigation_retrieval import InvestigationRetrievalService, IncidentNotFoundError
from app.llm.investigation import LLMInvestigationService

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

@router.post("/{incident_id}/investigate")
async def investigate_incident(incident_id: str, db: Session = Depends(get_db)):
    """Run full hybrid retrieval and LLM investigation pipeline for an incident."""
    try:
        retrieval_service = InvestigationRetrievalService(db=db)
        context = retrieval_service.build_context(incident_id)
        
        llm_service = LLMInvestigationService()
        analysis = await llm_service.analyze(context)
        return analysis
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )

