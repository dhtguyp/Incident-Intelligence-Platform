from fastapi import APIRouter, HTTPException, status

from app.models.search_schemas import SearchRequest, SearchResponse
from app.retrieval.semantic_search import SemanticRetrievalService

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def semantic_search(request: SearchRequest) -> SearchResponse:
    try:
        service = SemanticRetrievalService()
        results = service.search(
            request.query,
            service=request.service,
            document_type=request.document_type,
            limit=request.limit,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Semantic search failed. Confirm Qdrant is available and the collection has been indexed.",
        ) from exc
    return SearchResponse(query=request.query, results=results)
