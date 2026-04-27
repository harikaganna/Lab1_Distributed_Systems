import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { logout, selectUser } from "../store/slices/authSlice";

const IS_DOCKER = import.meta.env.VITE_DOCKER === "true";
const UPLOADS_BASE = IS_DOCKER ? "" : "http://localhost:8001";

function ProfileAvatar({ user }) {
  const initials = user.name
    ? user.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  return (
    <Link to="/profile" className="text-decoration-none d-flex flex-column align-items-center" style={{ gap: 2 }}>
      {user.profile_picture ? (
        <img
          src={`${UPLOADS_BASE}${user.profile_picture}`}
          alt={user.name}
          style={{ width: 38, height: 38, borderRadius: "50%", objectFit: "cover", border: "2px solid var(--brand)" }}
        />
      ) : (
        <div style={{
          width: 38, height: 38, borderRadius: "50%", background: "var(--brand)",
          color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "0.8rem", fontWeight: 600,
        }}>
          {initials}
        </div>
      )}
      <span style={{ fontSize: "0.7rem", color: "var(--brand)", fontWeight: 500, lineHeight: 1 }}>
        Hi {user.name?.split(" ")[0]}
      </span>
    </Link>
  );
}

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

              {user.role === "owner" && (
                <Link className="btn btn-sm btn-soft" to="/owner/dashboard">Dashboard</Link>
              )}

              <ProfileAvatar user={user} />

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
