import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchRestaurants, selectRestaurants, selectRestaurantsLoading } from "../store/slices/restaurantSlice";
import RestaurantCard from "../components/RestaurantCard";

const CUISINE_OPTIONS = [
  "italian", "chinese", "mexican", "indian", "japanese",
  "american", "french", "thai", "mediterranean", "other"
];

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function Explore() {
  const dispatch = useDispatch();
  const restaurants = useSelector(selectRestaurants);
  const loading = useSelector(selectRestaurantsLoading);
  const [nameFilter, setNameFilter] = useState("");
  const [cuisineFilter, setCuisineFilter] = useState("");
  const [cityFilter, setCityFilter] = useState("");
  const [keywordFilter, setKeywordFilter] = useState("");

  function doSearch() {
    const params = {};
    if (nameFilter) params.name = nameFilter;
    if (cuisineFilter) params.cuisine = cuisineFilter;
    if (cityFilter) params.city = cityFilter;
    if (keywordFilter) params.keyword = keywordFilter;
    dispatch(fetchRestaurants(params));
  }

  useEffect(() => { doSearch(); }, []);

  function handleSearch(e) {
    e.preventDefault();
    doSearch();
  }

  return (
    <div>
      <div className="card card-clean mb-4">
        <div className="card-body">
          <h4 className="mb-3">Find Restaurants</h4>
          <form onSubmit={handleSearch}>
            <div className="row g-2">
              <div className="col-md-3">
                <input className="form-control" placeholder="Restaurant name" value={nameFilter} onChange={(e) => setNameFilter(e.target.value)} />
              </div>
              <div className="col-md-2">
                <select className="form-select" value={cuisineFilter} onChange={(e) => setCuisineFilter(e.target.value)}>
                  <option value="">All Cuisines</option>
                  {CUISINE_OPTIONS.map((c) => (<option key={c} value={c}>{capitalize(c)}</option>))}
                </select>
              </div>
              <div className="col-md-2">
                <input className="form-control" placeholder="City / Zip" value={cityFilter} onChange={(e) => setCityFilter(e.target.value)} />
              </div>
              <div className="col-md-3">
                <input className="form-control" placeholder="Keywords (wifi, outdoor...)" value={keywordFilter} onChange={(e) => setKeywordFilter(e.target.value)} />
              </div>
              <div className="col-md-2">
                <button className="btn btn-brand w-100" type="submit">Search</button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {loading ? (
        <p className="text-muted text-center mt-4">Loading...</p>
      ) : restaurants.length === 0 ? (
        <p className="text-muted text-center mt-4">No restaurants found. Try a different search or add one!</p>
      ) : (
        restaurants.map((restaurant) => (
          <RestaurantCard key={restaurant.id} restaurant={restaurant} />
        ))
      )}
    </div>
  );
}
