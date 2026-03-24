from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db
from .. import schemas, crud, models
from ..auth import get_current_user

router = APIRouter(prefix="/restaurants/{restaurant_id}/reviews", tags=["Reviews"])


@router.post("", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    restaurant_id: int,
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.create_review(db, restaurant_id, payload, user.id)


@router.get("", response_model=List[schemas.ReviewOut])
def list_reviews(restaurant_id: int, db: Session = Depends(get_db)):
    return crud.list_reviews(db, restaurant_id)


@router.put("/{review_id}", response_model=schemas.ReviewOut)
def update_review(
    restaurant_id: int,
    review_id: int,
    payload: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.update_review(db, review_id, payload, user.id)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    restaurant_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    crud.delete_review(db, review_id, user.id)
