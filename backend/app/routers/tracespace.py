"""API router for Trace.Space integration."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Parameter
from app.models.schemas import TraceSpaceConnect, LinkParameterRequest, SyncRequest
from app.services.tracespace_client import TraceSpaceClient

# Global Trace.Space client instance
tracespace_client: TraceSpaceClient = None

router = APIRouter(prefix="/api/tracespace", tags=["tracespace"])


@router.post("/connect")
async def connect_tracespace(
    credentials: TraceSpaceConnect, db: Session = Depends(get_db)
):
    """Connect to Trace.Space and store credentials."""
    global tracespace_client

    tracespace_client = TraceSpaceClient(
        credentials.client_id, credentials.client_secret, credentials.org
    )

    authenticated = await tracespace_client.authenticate()

    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate with Trace.Space",
        )

    return {
        "status": "connected",
        "org": credentials.org,
        "message": "Successfully connected to Trace.Space",
    }


@router.get("/items")
async def get_tracespace_items(db: Session = Depends(get_db)):
    """Fetch items from Trace.Space."""
    if not tracespace_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to Trace.Space. Call /connect first.",
        )

    items = await tracespace_client.get_items()

    if items is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch items from Trace.Space",
        )

    return {"items": items}


@router.post("/link-parameter")
async def link_parameter(
    request: LinkParameterRequest, db: Session = Depends(get_db)
):
    """Link a local parameter to a Trace.Space field."""
    param = db.query(Parameter).filter(Parameter.id == request.parameter_id).first()

    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    param.tracespace_field_name = request.tracespace_field_name
    param.item.tracespace_item_id = request.tracespace_item_id

    db.commit()

    return {
        "status": "linked",
        "parameter_id": request.parameter_id,
        "tracespace_field_name": request.tracespace_field_name,
        "tracespace_item_id": request.tracespace_item_id,
    }


@router.post("/sync")
async def sync_parameters(request: SyncRequest, db: Session = Depends(get_db)):
    """Sync parameter values from Trace.Space."""
    if not tracespace_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to Trace.Space. Call /connect first.",
        )

    # Get parameters to sync
    if request.parameter_ids:
        parameters = db.query(Parameter).filter(
            Parameter.id.in_(request.parameter_ids)
        ).all()
    else:
        # Sync all parameters with Trace.Space links
        parameters = (
            db.query(Parameter)
            .filter(Parameter.tracespace_field_name.isnot(None))
            .all()
        )

    synced = []
    failed = []

    for param in parameters:
        success = await tracespace_client.sync_parameter(param, db)

        if success:
            synced.append(
                {
                    "parameter_id": param.id,
                    "parameter_name": param.name,
                    "new_value": param.value,
                }
            )
        else:
            failed.append(
                {
                    "parameter_id": param.id,
                    "parameter_name": param.name,
                    "reason": "Sync failed",
                }
            )

    return {
        "synced": len(synced),
        "failed": len(failed),
        "synced_parameters": synced,
        "failed_parameters": failed,
    }


@router.post("/push")
async def push_parameters(request: SyncRequest, db: Session = Depends(get_db)):
    """Push parameter values to Trace.Space."""
    if not tracespace_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not connected to Trace.Space. Call /connect first.",
        )

    # Get parameters to push
    if request.parameter_ids:
        parameters = db.query(Parameter).filter(
            Parameter.id.in_(request.parameter_ids)
        ).all()
    else:
        # Push all parameters with Trace.Space links
        parameters = (
            db.query(Parameter)
            .filter(Parameter.tracespace_field_name.isnot(None))
            .all()
        )

    pushed = []
    failed = []

    for param in parameters:
        success = await tracespace_client.push_parameter(param, db)

        if success:
            pushed.append(
                {
                    "parameter_id": param.id,
                    "parameter_name": param.name,
                    "value": param.value,
                }
            )
        else:
            failed.append(
                {
                    "parameter_id": param.id,
                    "parameter_name": param.name,
                    "reason": "Push failed",
                }
            )

    return {
        "pushed": len(pushed),
        "failed": len(failed),
        "pushed_parameters": pushed,
        "failed_parameters": failed,
    }
