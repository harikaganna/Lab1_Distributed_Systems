import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../api/axios";
import { Link } from "react-router-dom";

const COUNTRIES = [
  "United States", "Canada", "Mexico", "United Kingdom", "India",
  "China", "Japan", "Germany", "France", "Brazil", "Australia", "Other"
];
const GENDERS = ["", "Male", "Female", "Non-binary", "Prefer not to say"];
const PRICE_OPTIONS = ["$", "$$", "$$$", "$$$$"];
const SORT_OPTIONS = ["rating", "distance", "popularity", "price"];

export default function Profile() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("profile");
  const [profile, setProfile] = useState({});
  const [preferences, setPreferences] = useState({});
  const [history, setHistory] = useState({ reviews: [], restaurants_added: [] });
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!user) return;

    // Initialize profile form with current user data
    setProfile({
      name: user.name,
      phone: user.phone || "",
      about_me: user.about_me || "",
      city: user.city || "",
      state: user.state || "",
      country: user.country || "",
      languages: user.languages || "",
      gender: user.gender || "",
    });

    // Fetch preferences and history in parallel
    api.get("/users/me/preferences")
      .then((res) => setPreferences(res.data))
      .catch(() => {});

    api.get("/users/me/history")
      .then((res) => setHistory(res.data))
      .catch(() => {});
  }, [user]);

  if (!user) return <p>Please log in.</p>;

  // Helper to update a single profile field
  function updateProfileField(field) {
    return (e) => setProfile({ ...profile, [field]: e.target.value });
  }

  // Helper to update a single preference field
  function updatePrefField(field) {
    return (e) => setPreferences({ ...preferences, [field]: e.target.value });
  }

  async function saveProfile(e) {
    e.preventDefault();
    try {
      await api.put("/users/me", profile);
      setMessage("Profile updated!");
    } catch (err) {
      setMessage("Error updating profile");
    }
  }

  async function savePreferences(e) {
    e.preventDefault();
    // Clean up empty optional fields before sending
    const payload = { ...preferences };
    if (!payload.price_range) delete payload.price_range;
    if (!payload.sort_preference) delete payload.sort_preference;

    try {
      await api.put("/users/me/preferences", payload);
      setMessage("Preferences saved!");
    } catch (err) {
      setMessage("Error saving preferences");
    }
  }

  async function handlePictureUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/users/me/profile-picture", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage("Profile picture updated! Refresh to see.");
    } catch (err) {
      setMessage("Error uploading picture");
    }
  }

  const tabs = ["profile", "preferences", "history"];

  return (
    <div>
      {/* Tab navigation */}
      <ul className="nav nav-pills gap-2 mb-3">
        {tabs.map((tab) => (
          <li key={tab} className="nav-item">
            <button
              className={`nav-link ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          </li>
        ))}
      </ul>

      {message && (
        <div className="alert alert-info alert-clean py-2 mb-3">{message}</div>
      )}

      {/* Profile tab */}
      {activeTab === "profile" && (
        <div className="card card-clean">
          <div className="card-header">
            <strong>Edit Profile</strong>
          </div>
          <div className="card-body">
            <p className="small text-muted mb-3">
              Email: {user.email} · Role: {user.role}
            </p>

            {user.profile_picture && (
              <img
                src={`http://localhost:8006${user.profile_picture}`}
                alt="Profile"
                className="rounded-circle mb-3"
                style={{ width: 80, height: 80, objectFit: "cover" }}
              />
            )}

            <div className="mb-3">
              <label className="form-label">Profile Picture</label>
              <input
                type="file"
                className="form-control"
                accept="image/*"
                onChange={handlePictureUpload}
              />
            </div>

            <form onSubmit={saveProfile}>
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label">Name</label>
                  <input className="form-control" value={profile.name} onChange={updateProfileField("name")} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Phone</label>
                  <input className="form-control" value={profile.phone} onChange={updateProfileField("phone")} />
                </div>
                <div className="col-md-4">
                  <label className="form-label">City</label>
                  <input className="form-control" value={profile.city} onChange={updateProfileField("city")} />
                </div>
                <div className="col-md-4">
                  <label className="form-label">State</label>
                  <input className="form-control" value={profile.state} onChange={updateProfileField("state")} maxLength={5} />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Country</label>
                  <select className="form-select" value={profile.country} onChange={updateProfileField("country")}>
                    <option value="">Select</option>
                    {COUNTRIES.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-4">
                  <label className="form-label">Gender</label>
                  <select className="form-select" value={profile.gender} onChange={updateProfileField("gender")}>
                    {GENDERS.map((g) => (
                      <option key={g} value={g}>{g || "Select"}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-8">
                  <label className="form-label">Languages</label>
                  <input className="form-control" value={profile.languages} onChange={updateProfileField("languages")} placeholder="English, Spanish" />
                </div>
                <div className="col-12">
                  <label className="form-label">About Me</label>
                  <textarea className="form-control" rows={3} value={profile.about_me} onChange={updateProfileField("about_me")} />
                </div>
              </div>
              <button className="btn btn-brand mt-3" type="submit">Save Profile</button>
            </form>
          </div>
        </div>
      )}

      {/* Preferences tab */}
      {activeTab === "preferences" && (
        <div className="card card-clean">
          <div className="card-header">
            <strong>AI Assistant Preferences</strong>
          </div>
          <div className="card-body">
            <form onSubmit={savePreferences}>
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label">Cuisine Preferences</label>
                  <input className="form-control" value={preferences.cuisine_preferences || ""} onChange={updatePrefField("cuisine_preferences")} placeholder="italian, indian, japanese" />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Price Range</label>
                  <select className="form-select" value={preferences.price_range || ""} onChange={updatePrefField("price_range")}>
                    <option value="">Any</option>
                    {PRICE_OPTIONS.map((p) => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-3">
                  <label className="form-label">Search Radius (mi)</label>
                  <input type="number" className="form-control" value={preferences.search_radius || ""} onChange={updatePrefField("search_radius")} min={1} max={100} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Preferred Location</label>
                  <input className="form-control" value={preferences.preferred_location || ""} onChange={updatePrefField("preferred_location")} placeholder="San Jose, CA" />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Dietary Needs</label>
                  <input className="form-control" value={preferences.dietary_needs || ""} onChange={updatePrefField("dietary_needs")} placeholder="vegetarian, gluten-free" />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Ambiance Preferences</label>
                  <input className="form-control" value={preferences.ambiance_preferences || ""} onChange={updatePrefField("ambiance_preferences")} placeholder="casual, romantic" />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Sort By</label>
                  <select className="form-select" value={preferences.sort_preference || ""} onChange={updatePrefField("sort_preference")}>
                    <option value="">Default</option>
                    {SORT_OPTIONS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>
              <button className="btn btn-brand mt-3" type="submit">Save Preferences</button>
            </form>
          </div>
        </div>
      )}

      {/* History tab */}
      {activeTab === "history" && (
        <div>
          <h5>My Reviews ({history.reviews?.length || 0})</h5>
          {(history.reviews || []).map((review) => (
            <div key={review.id} className="card card-clean mb-2">
              <div className="card-body py-2">
                <Link to={`/restaurants/${review.restaurant_id}`} style={{ color: "var(--brand)" }}>
                  Restaurant #{review.restaurant_id}
                </Link>
                <span className="ms-2 badge badge-soft">{review.rating} ★</span>
                <span className="ms-2 small text-muted">
                  {new Date(review.created_at).toLocaleDateString()}
                </span>
                {review.comment && (
                  <p className="mb-0 mt-1 small">{review.comment}</p>
                )}
              </div>
            </div>
          ))}

          <h5 className="mt-4">Restaurants I Added ({history.restaurants_added?.length || 0})</h5>
          {(history.restaurants_added || []).map((rest) => (
            <div key={rest.id} className="card card-clean mb-2">
              <div className="card-body py-2">
                <Link to={`/restaurants/${rest.id}`} style={{ color: "var(--brand)" }}>
                  {rest.name}
                </Link>
                <span className="ms-2 small text-muted">
                  {rest.cuisine_type} · {rest.city}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
