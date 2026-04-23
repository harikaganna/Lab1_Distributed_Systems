// Legacy AuthContext - now backed by Redux store
// Kept for backward compatibility. Use Redux selectors directly in new code.
import React, { createContext, useContext } from "react";
import { useSelector, useDispatch } from "react-redux";
import { selectUser, selectAuthLoading, loginUser, signupUser, ownerSignupUser, logout } from "../store/slices/authSlice";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  return children;
}

export const useAuth = () => {
  const user = useSelector(selectUser);
  const loading = useSelector(selectAuthLoading);
  const dispatch = useDispatch();

  return {
    user,
    loading,
    login: (email, password) => dispatch(loginUser({ email, password })).unwrap(),
    signup: (name, email, password, role) => dispatch(signupUser({ name, email, password, role })).unwrap(),
    ownerSignup: (name, email, password, loc) => dispatch(ownerSignupUser({ name, email, password, restaurant_location: loc })).unwrap(),
    logout: () => dispatch(logout()),
  };
};
