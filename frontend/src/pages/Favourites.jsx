import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function Favourites() {
  const { user } = useAuth();
  const [favourites, setFavourites] = useState([]);

  async function loadFavourites() {
    try {
      const response = await api.get("/favourites");
      setFavourites(response.data);
    } catch (err) {
      console.error("Failed to load favourites:", err);
    }
  }

  useEffect(() => {
    if (user) loadFavourites();
  }, [user]);

  async function removeFavourite(restaurantId) {
    await api.delete(`/favourites/${restaurantId}`);
    loadFavourites();
  }

  if (!user) return <p>Please log in to see favourites.</p>;

  return (
    <div>
      <h4 className="mb-3">My Favourites</h4>

      {favourites.length === 0 ? (
        <p className="text-muted">No favourites yet. Explore restaurants and add some!</p>
      ) : (
        favourites.map((fav) => (
          <div key={fav.id} className="card card-clean mb-2">
            <div className="card-body py-2 d-flex justify-content-between align-items-center">
              <Link
                to={`/restaurants/${fav.restaurant_id}`}
                style={{ color: "var(--brand)", textDecoration: "none" }}
              >
                ❤️ {fav.restaurant_name || `Restaurant #${fav.restaurant_id}`}
              </Link>
              <button
                className="btn btn-sm btn-outline-danger"
                onClick={() => removeFavourite(fav.restaurant_id)}
              >
                Remove
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
