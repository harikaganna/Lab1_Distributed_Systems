import os
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db
from .. import schemas, crud, models
from ..auth import get_current_user

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("", response_model=schemas.RestaurantOut, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: schemas.RestaurantCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.create_restaurant(db, payload, user.id)


@router.get("", response_model=List[schemas.RestaurantOut])
def search_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    name: str = Query(None),
    cuisine: str = Query(None),
    city: str = Query(None),
    keyword: str = Query(None),
    db: Session = Depends(get_db),
):
    return crud.list_restaurants(db, skip, limit, name, cuisine, city, keyword)


@router.get("/{restaurant_id}", response_model=schemas.RestaurantOut)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    return crud.get_restaurant(db, restaurant_id)


@router.put("/{restaurant_id}", response_model=schemas.RestaurantOut)
def update_restaurant(
    restaurant_id: int,
    payload: schemas.RestaurantUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.update_restaurant(db, restaurant_id, payload, user)


@router.post("/{restaurant_id}/claim", response_model=schemas.RestaurantOut)
def claim_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can claim restaurants",
        )
    return crud.claim_restaurant(db, restaurant_id, user.id)


@router.post("/{restaurant_id}/photos", response_model=schemas.RestaurantOut)
async def upload_restaurant_photo(
    restaurant_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Upload a photo for a restaurant. Appends to existing photos as comma-separated URLs."""
    restaurant = db.get(models.Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"rest_{restaurant_id}_{uuid.uuid4().hex[:8]}.{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    photo_url = f"/uploads/{filename}"
    if restaurant.photos:
        restaurant.photos = restaurant.photos + "," + photo_url
    else:
        restaurant.photos = photo_url

    db.commit()
    db.refresh(restaurant)
    return crud.get_restaurant(db, restaurant_id)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    crud.delete_restaurant(db, restaurant_id, user)
