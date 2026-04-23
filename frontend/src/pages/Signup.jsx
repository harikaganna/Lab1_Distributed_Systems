import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { signupUser, ownerSignupUser, selectAuthError, clearAuthError } from "../store/slices/authSlice";

export default function Signup() {
  const [isOwner, setIsOwner] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [location, setLocation] = useState("");
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const error = useSelector(selectAuthError);

  async function handleSubmit(e) {
    e.preventDefault();
    dispatch(clearAuthError());
    let result;
    if (isOwner) {
      result = await dispatch(ownerSignupUser({ name, email, password, restaurant_location: location }));
    } else {
      result = await dispatch(signupUser({ name, email, password, role: "user" }));
    }
    if (!result.error) navigate("/");
  }

  return (
    <div className="row justify-content-center mt-5">
      <div className="col-md-5">
        <div className="card card-clean">
          <div className="card-header">
            <div className="d-flex gap-2">
              <button
                className={`btn btn-sm ${!isOwner ? "btn-brand" : "btn-soft"}`}
                onClick={() => setIsOwner(false)}
              >
                User
              </button>
              <button
                className={`btn btn-sm ${isOwner ? "btn-brand" : "btn-soft"}`}
                onClick={() => setIsOwner(true)}
              >
                Restaurant Owner
              </button>
            </div>
          </div>

          <div className="card-body">
            {error && (
              <div className="alert alert-danger alert-clean py-2">{error}</div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Name</label>
                <input
                  className="form-control"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-control"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                />
              </div>

              {isOwner && (
                <div className="mb-3">
                  <label className="form-label">Restaurant Location</label>
                  <input
                    className="form-control"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    required
                  />
                </div>
              )}

              <button className="btn btn-brand w-100" type="submit">
                Sign Up
              </button>
            </form>

            <p className="text-center mt-3 mb-0 small">
              Already have an account? <Link to="/login">Login</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
