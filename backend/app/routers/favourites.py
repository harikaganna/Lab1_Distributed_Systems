from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db
from .. import schemas, crud, models
from ..auth import get_current_user

router = APIRouter(prefix="/favourites", tags=["Favourites"])


@router.post("/{restaurant_id}", response_model=schemas.FavouriteOut, status_code=status.HTTP_201_CREATED)
def add_favourite(
    restaurant_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.add_favourite(db, user.id, restaurant_id)


@router.get("", response_model=List[schemas.FavouriteOut])
def list_favourites(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.list_favourites(db, user.id)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favourite(
    restaurant_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    crud.remove_favourite(db, user.id, restaurant_id)
