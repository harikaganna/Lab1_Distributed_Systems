import axios from "axios";

// In Docker: nginx proxies everything, so use empty baseURL (same origin)
// Locally: hit individual service ports directly
const IS_DOCKER = import.meta.env.VITE_DOCKER === "true";

const API_BASE = IS_DOCKER ? "" : (import.meta.env.VITE_API_BASE || "http://localhost:8001");
const RESTAURANT_BASE = IS_DOCKER ? "/api" : (import.meta.env.VITE_RESTAURANT_BASE || "http://localhost:8002");
const REVIEW_BASE = IS_DOCKER ? "/api" : (import.meta.env.VITE_REVIEW_BASE || "http://localhost:8003");
const FAVOURITES_BASE = IS_DOCKER ? "/api" : (import.meta.env.VITE_FAVOURITES_BASE || "http://localhost:8004");

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export const restaurantApi = axios.create({
  baseURL: RESTAURANT_BASE,
  headers: { "Content-Type": "application/json" },
});

export const reviewApi = axios.create({
  baseURL: REVIEW_BASE,
  headers: { "Content-Type": "application/json" },
});

export const favouritesApi = axios.create({
  baseURL: FAVOURITES_BASE,
  headers: { "Content-Type": "application/json" },
});

// Add auth interceptor to all instances
[api, restaurantApi, reviewApi, favouritesApi].forEach((instance) => {
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });
});
