from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    user = "user"
    owner = "owner"

class CuisineType(str, Enum):
    italian = "italian"
    chinese = "chinese"
    mexican = "mexican"
    indian = "indian"
    japanese = "japanese"
    american = "american"
    french = "french"
    thai = "thai"
    mediterranean = "mediterranean"
    other = "other"

class PriceRange(str, Enum):
    one = "$"
    two = "$$"
    three = "$$$"
    four = "$$$$"

class AmbianceType(str, Enum):
    casual = "casual"
    fine_dining = "fine_dining"
    family_friendly = "family_friendly"
    romantic = "romantic"
    outdoor = "outdoor"
    bar = "bar"

class SortPreference(str, Enum):
    rating = "rating"
    distance = "distance"
    popularity = "popularity"
    price = "price"


class UserSignup(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.user

class OwnerSignup(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    restaurant_location: str = Field(min_length=1, max_length=255)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    about_me: Optional[str] = Field(default=None, max_length=2000)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=5)
    country: Optional[str] = Field(default=None, max_length=100)
    languages: Optional[str] = Field(default=None, max_length=255)
    gender: Optional[str] = Field(default=None, max_length=20)

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    phone: Optional[str] = None
    about_me: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    languages: Optional[str] = None
    gender: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


class UserPreferenceUpdate(BaseModel):
    cuisine_preferences: Optional[str] = Field(default=None, max_length=500)
    price_range: Optional[str] = Field(default=None, max_length=10)
    preferred_location: Optional[str] = Field(default=None, max_length=255)
    search_radius: Optional[int] = Field(default=None, ge=1, le=100)
    dietary_needs: Optional[str] = Field(default=None, max_length=500)
    ambiance_preferences: Optional[str] = Field(default=None, max_length=500)
    sort_preference: Optional[str] = Field(default=None, max_length=50)

class UserPreferenceOut(BaseModel):
    cuisine_preferences: Optional[str] = None
    price_range: Optional[str] = None
    preferred_location: Optional[str] = None
    search_radius: Optional[int] = None
    dietary_needs: Optional[str] = None
    ambiance_preferences: Optional[str] = None
    sort_preference: Optional[str] = None
    class Config:
        from_attributes = True


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    cuisine_type: CuisineType
    city: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=5000)
    address: Optional[str] = Field(default=None, max_length=500)
    state: Optional[str] = Field(default=None, max_length=5)
    zip_code: Optional[str] = Field(default=None, max_length=10)
    phone: Optional[str] = Field(default=None, max_length=20)
    price_range: Optional[PriceRange] = None
    ambiance: Optional[AmbianceType] = None
    hours: Optional[str] = Field(default=None, max_length=500)
    photos: Optional[str] = None
    amenities: Optional[str] = Field(default=None, max_length=500)

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    cuisine_type: Optional[CuisineType] = None
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=5000)
    address: Optional[str] = Field(default=None, max_length=500)
    state: Optional[str] = Field(default=None, max_length=5)
    zip_code: Optional[str] = Field(default=None, max_length=10)
    phone: Optional[str] = Field(default=None, max_length=20)
    price_range: Optional[PriceRange] = None
    ambiance: Optional[AmbianceType] = None
    hours: Optional[str] = Field(default=None, max_length=500)
    photos: Optional[str] = None
    amenities: Optional[str] = Field(default=None, max_length=500)

class RestaurantOut(BaseModel):
    id: int
    name: str
    cuisine_type: CuisineType
    description: Optional[str] = None
    address: Optional[str] = None
    city: str
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    price_range: Optional[PriceRange] = None
    ambiance: Optional[AmbianceType] = None
    hours: Optional[str] = None
    photos: Optional[str] = None
    amenities: Optional[str] = None
    owner_id: Optional[int] = None
    created_by: int
    avg_rating: Optional[float] = None
    review_count: Optional[int] = None
    created_at: datetime
    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=5000)
    photos: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=5000)
    photos: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None
    photos: Optional[str] = None
    user_id: int
    restaurant_id: int
    user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class FavouriteOut(BaseModel):
    id: int
    restaurant_id: int
    restaurant_name: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    recommendations: Optional[List[dict]] = []
