from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from . import models, schemas
from .auth import hash_password


# ─── Users ───────────────────────────────────────────────────────────

def create_user(db: Session, payload: schemas.UserSignup):
    # hash the password before storing
    new_user = models.User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role.value,
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered")


def create_owner(db: Session, payload: schemas.OwnerSignup):
    new_owner = models.User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=models.UserRole.owner,
    )
    db.add(new_owner)
    try:
        db.commit()
        db.refresh(new_owner)
        return new_owner
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered")


def get_user_by_email(db: Session, email: str):
    return db.scalars(
        select(models.User).where(models.User.email == email)
    ).first()


def update_user(db: Session, user: models.User, payload: schemas.UserUpdate):
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ─── User Preferences ────────────────────────────────────────────────

def get_preferences(db: Session, user_id: int):
    return db.scalars(
        select(models.UserPreference).where(models.UserPreference.user_id == user_id)
    ).first()


def update_preferences(db: Session, user_id: int, payload: schemas.UserPreferenceUpdate):
    pref = get_preferences(db, user_id)

    # Create a new preferences row if one doesn't exist yet
    if not pref:
        pref = models.UserPreference(user_id=user_id)
        db.add(pref)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        # Convert enum values to their string representation
        if value is not None and hasattr(value, "value"):
            value = value.value
        setattr(pref, field, value)

    db.commit()
    db.refresh(pref)
    return pref


# ─── Restaurants ─────────────────────────────────────────────────────

def create_restaurant(db: Session, payload: schemas.RestaurantCreate, user_id: int):
    data = payload.model_dump()

    # Convert any enum fields to their string values
    for field in ["cuisine_type", "price_range", "ambiance"]:
        if data.get(field) and hasattr(data[field], "value"):
            data[field] = data[field].value

    restaurant = models.Restaurant(**data, created_by=user_id)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return _attach_review_stats(db, restaurant)


def list_restaurants(db: Session, skip: int, limit: int, name: str = None,
                     cuisine: str = None, city: str = None, keyword: str = None):
    # build query with optional filters
    query = select(models.Restaurant)

    if name:
        query = query.where(models.Restaurant.name.ilike(f"%{name}%"))
    if cuisine:
        query = query.where(models.Restaurant.cuisine_type == cuisine)
    if city:
        query = query.where(
            models.Restaurant.city.ilike(f"%{city}%") |
            models.Restaurant.zip_code.ilike(f"%{city}%")
        )
    if keyword:
        query = query.where(
            models.Restaurant.description.ilike(f"%{keyword}%") |
            models.Restaurant.amenities.ilike(f"%{keyword}%") |
            models.Restaurant.name.ilike(f"%{keyword}%")
        )

    query = query.offset(skip).limit(limit).order_by(models.Restaurant.id)
    restaurants = db.scalars(query).all()

    return [_attach_review_stats(db, r) for r in restaurants]


def get_restaurant(db: Session, restaurant_id: int):
    restaurant = db.get(models.Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")
    return _attach_review_stats(db, restaurant)


def update_restaurant(db: Session, restaurant_id: int, payload: schemas.RestaurantUpdate, user: models.User):
    restaurant = db.get(models.Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    # only owner or creator can edit
    if restaurant.owner_id != user.id and restaurant.created_by != user.id:
        raise HTTPException(403, "Not authorized to update this restaurant")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if value is not None and hasattr(value, "value"):
            value = value.value
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)
    return _attach_review_stats(db, restaurant)


def claim_restaurant(db: Session, restaurant_id: int, owner_id: int):
    restaurant = db.get(models.Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")
    if restaurant.owner_id:
        raise HTTPException(409, "Restaurant already claimed")

    restaurant.owner_id = owner_id
    db.commit()
    db.refresh(restaurant)
    return _attach_review_stats(db, restaurant)


def delete_restaurant(db: Session, restaurant_id: int, user: models.User):
    restaurant = db.get(models.Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")
    if restaurant.owner_id != user.id and restaurant.created_by != user.id:
        raise HTTPException(403, "Not authorized to delete this restaurant")

    db.delete(restaurant)
    db.commit()


def _attach_review_stats(db: Session, restaurant: models.Restaurant):
    # calculate avg rating and review count for a restaurant
    stats = db.execute(
        select(func.avg(models.Review.rating), func.count(models.Review.id))
        .where(models.Review.restaurant_id == restaurant.id)
    ).first()

    restaurant.avg_rating = round(float(stats[0]), 2) if stats[0] else None
    restaurant.review_count = stats[1] or 0
    return restaurant


# ─── Reviews ─────────────────────────────────────────────────────────

def create_review(db: Session, restaurant_id: int, payload: schemas.ReviewCreate, user_id: int):
    if not db.get(models.Restaurant, restaurant_id):
        raise HTTPException(404, "Restaurant not found")

    review = models.Review(
        **payload.model_dump(),
        user_id=user_id,
        restaurant_id=restaurant_id,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    review.user_name = review.user.name
    return review


def list_reviews(db: Session, restaurant_id: int):
    # get all reviews sorted by newest first
    reviews = db.scalars(
        select(models.Review)
        .where(models.Review.restaurant_id == restaurant_id)
        .order_by(models.Review.created_at.desc())
    ).all()

    for review in reviews:
        review.user_name = review.user.name
    return reviews


def update_review(db: Session, review_id: int, payload: schemas.ReviewUpdate, user_id: int):
    review = db.get(models.Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    if review.user_id != user_id:
        raise HTTPException(403, "Can only edit your own reviews")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    review.user_name = review.user.name
    return review


def delete_review(db: Session, review_id: int, user_id: int):
    review = db.get(models.Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    if review.user_id != user_id:
        raise HTTPException(403, "Can only delete your own reviews")

    db.delete(review)
    db.commit()


# ─── Favourites ──────────────────────────────────────────────────────

def add_favourite(db: Session, user_id: int, restaurant_id: int):
    if not db.get(models.Restaurant, restaurant_id):
        raise HTTPException(404, "Restaurant not found")

    # Check if already favourited
    existing = db.scalars(
        select(models.Favourite).where(
            models.Favourite.user_id == user_id,
            models.Favourite.restaurant_id == restaurant_id,
        )
    ).first()
    if existing:
        raise HTTPException(409, "Already in favourites")

    favourite = models.Favourite(user_id=user_id, restaurant_id=restaurant_id)
    db.add(favourite)
    db.commit()
    db.refresh(favourite)
    favourite.restaurant_name = favourite.restaurant.name
    return favourite


def list_favourites(db: Session, user_id: int):
    favourites = db.scalars(
        select(models.Favourite).where(models.Favourite.user_id == user_id)
    ).all()

    for fav in favourites:
        fav.restaurant_name = fav.restaurant.name
    return favourites


def remove_favourite(db: Session, user_id: int, restaurant_id: int):
    favourite = db.scalars(
        select(models.Favourite).where(
            models.Favourite.user_id == user_id,
            models.Favourite.restaurant_id == restaurant_id,
        )
    ).first()
    if not favourite:
        raise HTTPException(404, "Favourite not found")

    db.delete(favourite)
    db.commit()


# ─── User History ────────────────────────────────────────────────────

def get_user_history(db: Session, user_id: int):
    # pull reviews and restaurants the user has added
    reviews = db.scalars(
        select(models.Review)
        .where(models.Review.user_id == user_id)
        .order_by(models.Review.created_at.desc())
    ).all()
    for review in reviews:
        review.user_name = review.user.name

    # also get restaurants this user created
    restaurants_added = db.scalars(
        select(models.Restaurant)
        .where(models.Restaurant.created_by == user_id)
        .order_by(models.Restaurant.created_at.desc())
    ).all()
    for restaurant in restaurants_added:
        _attach_review_stats(db, restaurant)

    return {
        "reviews": reviews,
        "restaurants_added": restaurants_added,
    }
