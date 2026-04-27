import React from "react";
import { Link } from "react-router-dom";

const IS_DOCKER = import.meta.env.VITE_DOCKER === "true";
const UPLOADS_BASE = IS_DOCKER ? "" : "http://localhost:8001";

function getImageUrl(restaurant) {
  if (restaurant.cover_image) return `${UPLOADS_BASE}${restaurant.cover_image}`;
  if (restaurant.photos) {
    const first = restaurant.photos.split(",")[0].trim();
    if (first) return `${UPLOADS_BASE}${first}`;
  }
  return "/restaurant-placeholder.png";
}

export default function RestaurantCard({ restaurant }) {
  const { id, name, cuisine_type, city, state, price_range, description, avg_rating, review_count } = restaurant;

  return (
    <div className="card card-clean mb-3 d-flex flex-row" style={{ overflow: "hidden" }}>
      <Link to={`/restaurants/${id}`} style={{ display: "block", lineHeight: 0, flexShrink: 0 }}>
        <img
          src={getImageUrl(restaurant)}
          alt={name}
          style={{ width: 160, height: "100%", minHeight: 120, objectFit: "cover" }}
          onError={(e) => { e.target.src = "/restaurant-placeholder.png"; }}
        />
      </Link>
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h5 className="mb-1">
              <Link to={`/restaurants/${id}`} style={{ color: "var(--brand)", textDecoration: "none" }}>
                {name}
              </Link>
            </h5>
            <p className="small text-muted mb-1">
              {city}{state ? `, ${state}` : ""}
              {price_range ? ` · ${price_range}` : ""}
            </p>
            {description && (
              <p className="mb-1 small">{description.slice(0, 150)}</p>
            )}
            {cuisine_type && (
              <span className="badge badge-soft me-1">
                {cuisine_type.charAt(0).toUpperCase() + cuisine_type.slice(1)}
              </span>
            )}
          </div>

          <div className="text-end ms-3" style={{ flexShrink: 0 }}>
            {avg_rating && (
              <span className="badge badge-soft fs-6">{avg_rating} ★</span>
            )}
            <p className="small text-muted mb-0">{review_count || 0} reviews</p>
          </div>
        </div>
      </div>
    </div>
  );
}
