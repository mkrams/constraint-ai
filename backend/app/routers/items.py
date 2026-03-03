"""API router for items (engineering components)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Item, Parameter
from app.models.schemas import ItemCreate, ItemUpdate, ItemResponse, ItemDetailResponse

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("/", response_model=List[ItemDetailResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items with their parameters."""
    items = db.query(Item).all()
    return items


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    # Check if short_id already exists
    existing = db.query(Item).filter(Item.short_id == item.short_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item with short_id '{item.short_id}' already exists",
        )

    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get a specific item with its parameters."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: str, item_update: ItemUpdate, db: Session = Depends(get_db)
):
    """Update an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Check if new short_id already exists
    if item_update.short_id and item_update.short_id != item.short_id:
        existing = db.query(Item).filter(Item.short_id == item_update.short_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with short_id '{item_update.short_id}' already exists",
            )

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    """Delete an item and all its parameters."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    db.delete(item)
    db.commit()
