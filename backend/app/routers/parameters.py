"""API router for parameters."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Parameter, Item
from app.models.schemas import (
    ParameterCreate,
    ParameterUpdate,
    ParameterValueUpdate,
    ParameterResponse,
)

router = APIRouter(prefix="/api/parameters", tags=["parameters"])


@router.post("/", response_model=ParameterResponse, status_code=status.HTTP_201_CREATED)
def create_parameter(param: ParameterCreate, db: Session = Depends(get_db)):
    """Create a new parameter for an item."""
    # Verify item exists
    item = db.query(Item).filter(Item.id == param.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    db_param = Parameter(**param.model_dump())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return db_param


@router.put("/{param_id}", response_model=ParameterResponse)
def update_parameter(
    param_id: str, param_update: ParameterUpdate, db: Session = Depends(get_db)
):
    """Update a parameter."""
    param = db.query(Parameter).filter(Parameter.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    update_data = param_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(param, field, value)

    db.add(param)
    db.commit()
    db.refresh(param)
    return param


@router.put("/{param_id}/value", response_model=ParameterResponse)
def update_parameter_value(
    param_id: str, value_update: ParameterValueUpdate, db: Session = Depends(get_db)
):
    """Quick endpoint to update just the parameter value."""
    param = db.query(Parameter).filter(Parameter.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    param.value = value_update.value
    db.add(param)
    db.commit()
    db.refresh(param)
    return param


@router.delete("/{param_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parameter(param_id: str, db: Session = Depends(get_db)):
    """Delete a parameter."""
    param = db.query(Parameter).filter(Parameter.id == param_id).first()
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parameter not found"
        )

    db.delete(param)
    db.commit()
