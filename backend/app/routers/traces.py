"""API router for traces (relationships between items)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Trace, Item
from app.models.schemas import TraceCreate, TraceUpdate, TraceResponse

router = APIRouter(prefix="/api/traces", tags=["traces"])


@router.get("/", response_model=List[TraceResponse])
def list_traces(db: Session = Depends(get_db)):
    """List all traces."""
    traces = db.query(Trace).all()
    return traces


@router.post("/", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
def create_trace(trace: TraceCreate, db: Session = Depends(get_db)):
    """Create a new trace (relationship between items)."""
    # Verify both items exist
    source_item = db.query(Item).filter(Item.id == trace.source_item_id).first()
    if not source_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source item not found"
        )

    target_item = db.query(Item).filter(Item.id == trace.target_item_id).first()
    if not target_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target item not found"
        )

    # Prevent self-traces
    if trace.source_item_id == trace.target_item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and target items cannot be the same",
        )

    db_trace = Trace(**trace.model_dump())
    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)
    return db_trace


@router.get("/{trace_id}", response_model=TraceResponse)
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    """Get a specific trace."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")
    return trace


@router.put("/{trace_id}", response_model=TraceResponse)
def update_trace(
    trace_id: str, trace_update: TraceUpdate, db: Session = Depends(get_db)
):
    """Update a trace."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")

    update_data = trace_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trace, field, value)

    db.add(trace)
    db.commit()
    db.refresh(trace)
    return trace


@router.delete("/{trace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trace(trace_id: str, db: Session = Depends(get_db)):
    """Delete a trace."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")

    db.delete(trace)
    db.commit()
