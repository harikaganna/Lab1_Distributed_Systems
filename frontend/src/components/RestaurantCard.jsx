import React from "react";
import { Link } from "react-router-dom";

export default function RestaurantCard({ restaurant }) {
  const { id, name, cuisine_type, city, state, price_range, description, avg_rating, review_count } = restaurant;

  return (
    <div className="card card-clean mb-3">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h5 className="mb-1">
              <Link to={`/restaurants/${id}`} style={{ color: "var(--brand)", textDecoration: "none" }}>
                {name}
              </Link>
            </h5>
            <p className="small text-muted mb-1">
              {cuisine_type} · {city}{state ? `, ${state}` : ""}
              {price_range ? ` · ${price_range}` : ""}
            </p>
            {description && (
              <p className="mb-0 small">{description.slice(0, 150)}...</p>
            )}
          </div>

          <div className="text-end">
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
