import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { selectUser } from "../store/slices/authSlice";
import { fetchFavourites, removeFavourite, selectFavourites } from "../store/slices/favouriteSlice";

export default function Favourites() {
  const user = useSelector(selectUser);
  const favourites = useSelector(selectFavourites);
  const dispatch = useDispatch();

  useEffect(() => {
    if (user) dispatch(fetchFavourites());
  }, [user]);

  function handleRemove(restaurantId) {
    dispatch(removeFavourite(restaurantId));
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
              <Link to={`/restaurants/${fav.restaurant_id}`} style={{ color: "var(--brand)", textDecoration: "none" }}>
                ❤️ {fav.restaurant_name || `Restaurant #${fav.restaurant_id}`}
              </Link>
              <button className="btn btn-sm btn-outline-danger" onClick={() => handleRemove(fav.restaurant_id)}>
                Remove
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
