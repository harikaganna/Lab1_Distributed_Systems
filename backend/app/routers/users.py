import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from ..deps import get_db
from .. import schemas, crud, models
from ..auth import get_current_user

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=schemas.UserOut)
def get_profile(user: models.User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=schemas.UserOut)
def update_profile(
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.update_user(db, user, payload)


@router.get("/me/preferences", response_model=schemas.UserPreferenceOut)
def get_preferences(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    pref = crud.get_preferences(db, user.id)
    if not pref:
        return schemas.UserPreferenceOut()
    return pref


@router.put("/me/preferences", response_model=schemas.UserPreferenceOut)
def update_preferences(
    payload: schemas.UserPreferenceUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.update_preferences(db, user.id, payload)


@router.post("/me/profile-picture", response_model=schemas.UserOut)
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Generate a unique filename to avoid collisions
    extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    user.profile_picture = f"/uploads/{filename}"
    db.commit()
    db.refresh(user)
    return user


@router.get("/me/history")
def get_history(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.get_user_history(db, user.id)
