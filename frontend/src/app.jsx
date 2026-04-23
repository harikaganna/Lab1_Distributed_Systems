import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { fetchCurrentUser, selectToken, selectAuthLoading } from "./store/slices/authSlice";
import Navbar from "./components/Navbar";
import ChatBot from "./components/ChatBot";
import Explore from "./pages/Explore";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import RestaurantDetail from "./pages/RestaurantDetail";
import AddRestaurant from "./pages/AddRestaurant";
import Profile from "./pages/Profile";
import Favourites from "./pages/Favourites";
import OwnerDashboard from "./pages/OwnerDashboard";
import EditRestaurant from "./pages/EditRestaurant";

export default function App() {
  const dispatch = useDispatch();
  const token = useSelector(selectToken);
  const loading = useSelector(selectAuthLoading);

  useEffect(() => {
    if (token) dispatch(fetchCurrentUser());
  }, []);

  if (loading && token) return <div className="text-center mt-5">Loading...</div>;

  return (
    <BrowserRouter>
      <Navbar />
      <div className="container py-4">
        <Routes>
          <Route path="/" element={<Explore />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/restaurants/:id" element={<RestaurantDetail />} />
          <Route path="/restaurants/:id/edit" element={<EditRestaurant />} />
          <Route path="/add-restaurant" element={<AddRestaurant />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/favourites" element={<Favourites />} />
          <Route path="/owner/dashboard" element={<OwnerDashboard />} />
        </Routes>
      </div>
      <ChatBot />
    </BrowserRouter>
  );
}
