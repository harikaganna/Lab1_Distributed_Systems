from sqlalchemy import (
    String, Integer, Float, Text, ForeignKey, DateTime, Enum as SAEnum, Boolean, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
import enum


class UserRole(str, enum.Enum):
    user = "user"
    owner = "owner"

class CuisineType(str, enum.Enum):
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

class PriceRange(str, enum.Enum):
    one = "$"
    two = "$$"
    three = "$$$"
    four = "$$$$"

class AmbianceType(str, enum.Enum):
    casual = "casual"
    fine_dining = "fine_dining"
    family_friendly = "family_friendly"
    romantic = "romantic"
    outdoor = "outdoor"
    bar = "bar"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(SAEnum('user','owner', name='userrole'), nullable=False, default='user')
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    about_me: Mapped[str] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(5), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    languages: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    profile_picture: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    favourites = relationship("Favourite", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    owned_restaurants = relationship("Restaurant", back_populates="owner", foreign_keys="Restaurant.owner_id")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    cuisine_preferences: Mapped[str] = mapped_column(String(500), nullable=True)
    price_range: Mapped[str] = mapped_column(String(10), nullable=True)
    preferred_location: Mapped[str] = mapped_column(String(255), nullable=True)
    search_radius: Mapped[int] = mapped_column(Integer, nullable=True)
    dietary_needs: Mapped[str] = mapped_column(String(500), nullable=True)
    ambiance_preferences: Mapped[str] = mapped_column(String(500), nullable=True)
    sort_preference: Mapped[str] = mapped_column(String(50), nullable=True)

    user = relationship("User", back_populates="preferences")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cuisine_type: Mapped[str] = mapped_column(SAEnum('italian','chinese','mexican','indian','japanese','american','french','thai','mediterranean','other', name='cuisinetype'), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(5), nullable=True)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    price_range: Mapped[str] = mapped_column(SAEnum('$','$$','$$$','$$$$', name='pricerange'), nullable=True)
    ambiance: Mapped[str] = mapped_column(SAEnum('casual','fine_dining','family_friendly','romantic','outdoor','bar', name='ambiancetype'), nullable=True)
    hours: Mapped[str] = mapped_column(String(500), nullable=True)
    photos: Mapped[str] = mapped_column(Text, nullable=True)
    amenities: Mapped[str] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="owned_restaurants", foreign_keys=[owner_id])
    creator = relationship("User", foreign_keys=[created_by])
    reviews = relationship("Review", back_populates="restaurant", cascade="all, delete-orphan")
    favourites = relationship("Favourite", back_populates="restaurant", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    photos: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")


class Favourite(Base):
    __tablename__ = "favourites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favourites")
    restaurant = relationship("Restaurant", back_populates="favourites")
