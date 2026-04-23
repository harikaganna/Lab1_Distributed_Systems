import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { logout, selectUser } from "../store/slices/authSlice";

export default function Navbar() {
  const user = useSelector(selectUser);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  function handleLogout() {
    dispatch(logout());
    navigate("/");
  }

  return (
    <nav
      className="navbar navbar-expand-lg"
      style={{ background: "var(--panel)", borderBottom: "1px solid var(--border)" }}
    >
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/" style={{ color: "var(--brand)" }}>
          🍽️ Yelp
        </Link>

        <div className="d-flex align-items-center gap-3">
          <Link className="btn btn-sm btn-soft" to="/">Explore</Link>

          {user ? (
            <>
              <Link className="btn btn-sm btn-soft" to="/add-restaurant">Add Restaurant</Link>
              <Link className="btn btn-sm btn-soft" to="/favourites">Favourites</Link>
              <Link className="btn btn-sm btn-soft" to="/profile">Profile</Link>

              {user.role === "owner" && (
                <Link className="btn btn-sm btn-soft" to="/owner/dashboard">Dashboard</Link>
              )}

              <span className="small text-muted">Hi, {user.name}</span>
              <button className="btn btn-sm btn-outline-danger" onClick={handleLogout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link className="btn btn-sm btn-brand" to="/login">Login</Link>
              <Link className="btn btn-sm btn-soft" to="/signup">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
