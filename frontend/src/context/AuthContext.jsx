import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      api.get("/users/me")
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    localStorage.setItem("token", res.data.access_token);
    const me = await api.get("/users/me");
    setUser(me.data);
    return me.data;
  };

  const signup = async (name, email, password, role = "user") => {
    await api.post("/auth/signup", { name, email, password, role });
    return login(email, password);
  };

  const ownerSignup = async (name, email, password, restaurantLocation) => {
    await api.post("/auth/signup/owner", {
      name, email, password, restaurant_location: restaurantLocation,
    });
    return login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, ownerSignup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
