import React, { useState, useEffect } from "react";
import { api } from "../api/axios";
import RestaurantCard from "../components/RestaurantCard";

const CUISINE_OPTIONS = [
  "italian", "chinese", "mexican", "indian", "japanese",
  "american", "french", "thai", "mediterranean", "other"
];

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function Explore() {
  const [restaurants, setRestaurants] = useState([]);
  const [nameFilter, setNameFilter] = useState("");
  const [cuisineFilter, setCuisineFilter] = useState("");
  const [cityFilter, setCityFilter] = useState("");
  const [keywordFilter, setKeywordFilter] = useState("");

  async function fetchRestaurants() {
    const params = {};
    if (nameFilter) params.name = nameFilter;
    if (cuisineFilter) params.cuisine = cuisineFilter;
    if (cityFilter) params.city = cityFilter;
    if (keywordFilter) params.keyword = keywordFilter;

    try {
      const response = await api.get("/restaurants", { params });
      setRestaurants(response.data);
    } catch (err) {
      console.error("Failed to fetch restaurants:", err);
    }
  }

  // Load all restaurants on first render
  useEffect(() => {
    fetchRestaurants();
  }, []);

  function handleSearch(e) {
    e.preventDefault();
    fetchRestaurants();
  }

  return (
    <div>
      {/* Search filters */}
      <div className="card card-clean mb-4">
        <div className="card-body">
          <h4 className="mb-3">Find Restaurants</h4>
          <form onSubmit={handleSearch}>
            <div className="row g-2">
              <div className="col-md-3">
                <input
                  className="form-control"
                  placeholder="Restaurant name"
                  value={nameFilter}
                  onChange={(e) => setNameFilter(e.target.value)}
                />
              </div>
              <div className="col-md-2">
                <select
                  className="form-select"
                  value={cuisineFilter}
                  onChange={(e) => setCuisineFilter(e.target.value)}
                >
                  <option value="">All Cuisines</option>
                  {CUISINE_OPTIONS.map((c) => (
                    <option key={c} value={c}>{capitalize(c)}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-2">
                <input
                  className="form-control"
                  placeholder="City / Zip"
                  value={cityFilter}
                  onChange={(e) => setCityFilter(e.target.value)}
                />
              </div>
              <div className="col-md-3">
                <input
                  className="form-control"
                  placeholder="Keywords (wifi, outdoor...)"
                  value={keywordFilter}
                  onChange={(e) => setKeywordFilter(e.target.value)}
                />
              </div>
              <div className="col-md-2">
                <button className="btn btn-brand w-100" type="submit">Search</button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Results */}
      {restaurants.length === 0 ? (
        <p className="text-muted text-center mt-4">
          No restaurants found. Try a different search or add one!
        </p>
      ) : (
        restaurants.map((restaurant) => (
          <RestaurantCard key={restaurant.id} restaurant={restaurant} />
        ))
      )}
    </div>
  );
}
