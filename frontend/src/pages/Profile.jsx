import React, { useState, useEffect, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { selectUser, fetchCurrentUser } from "../store/slices/authSlice";
import { api } from "../api/axios";
import { Link } from "react-router-dom";

const IS_DOCKER = import.meta.env.VITE_DOCKER === "true";
const UPLOADS_BASE = IS_DOCKER ? "" : "http://localhost:8001";

const COUNTRIES = [
  "United States", "Canada", "Mexico", "United Kingdom", "India",
  "China", "Japan", "Germany", "France", "Brazil", "Australia", "Other"
];
const GENDERS = ["", "Male", "Female", "Non-binary", "Prefer not to say"];
const PRICE_OPTIONS = ["$", "$$", "$$$", "$$$$"];
const SORT_OPTIONS = ["rating", "distance", "popularity", "price"];

export default function Profile() {
  const user = useSelector(selectUser);
  const dispatch = useDispatch();
  const fileInputRef = useRef(null);
  const [activeTab, setActiveTab] = useState("profile");
  const [profile, setProfile] = useState({});
  const [preferences, setPreferences] = useState({});
  const [history, setHistory] = useState({ reviews: [], restaurants_added: [] });
  const [message, setMessage] = useState("");
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [hoverAvatar, setHoverAvatar] = useState(false);

  const initials = user?.name
    ? user.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  // Always fetch fresh data directly from the API on mount
  useEffect(() => {
    api.get("/users/me").then((res) => {
      const u = res.data;
      setProfile({
        name: u.name || "", phone: u.phone || "", about_me: u.about_me || "",
        city: u.city || "", state: u.state || "", country: u.country || "",
        languages: u.languages || "", gender: u.gender || "",
      });
    }).catch(() => {});
    api.get("/users/me/preferences").then((res) => setPreferences(res.data)).catch(() => {});
    api.get("/users/me/history").then((res) => setHistory(res.data)).catch(() => {});
  }, []);

  if (!user) return <p>Please log in.</p>;

  function updateProfileField(field) {
    return (e) => setProfile({ ...profile, [field]: e.target.value });
  }
  function updatePrefField(field) {
    return (e) => setPreferences({ ...preferences, [field]: e.target.value });
  }

  async function saveProfile(e) {
    e.preventDefault();
    try {
      const res = await api.put("/users/me", profile);
      const u = res.data;
      setProfile({
        name: u.name || "", phone: u.phone || "", about_me: u.about_me || "",
        city: u.city || "", state: u.state || "", country: u.country || "",
        languages: u.languages || "", gender: u.gender || "",
      });
      dispatch(fetchCurrentUser());
      setMessage("Profile updated!");
    } catch {
      setMessage("Error updating profile");
    }
  }

  async function savePreferences(e) {
    e.preventDefault();
    const payload = { ...preferences };
    if (!payload.price_range) delete payload.price_range;
    if (!payload.sort_preference) delete payload.sort_preference;
    try { await api.put("/users/me/preferences", payload); setMessage("Preferences saved!"); }
    catch { setMessage("Error saving preferences"); }
  }

  async function handlePictureUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setPreviewUrl(URL.createObjectURL(file));
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      await api.post("/users/me/profile-picture", formData, { headers: { "Content-Type": "multipart/form-data" } });
      await dispatch(fetchCurrentUser());
      setMessage("Profile picture updated!");
    } catch {
      setMessage("Error uploading picture");
      setPreviewUrl(null);
    }
    setUploading(false);
  }

  const tabs = ["profile", "preferences", "history"];

  return (
    <div>
      <ul className="nav nav-pills gap-2 mb-3">
        {tabs.map((tab) => (
          <li key={tab} className="nav-item">
            <button className={`nav-link ${activeTab === tab ? "active" : ""}`} onClick={() => setActiveTab(tab)}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          </li>
        ))}
      </ul>

      {message && <div className="alert alert-info alert-clean py-2 mb-3">{message}</div>}

      {activeTab === "profile" && (
        <div className="card card-clean">
          <div className="card-header"><strong>Edit Profile</strong></div>
          <div className="card-body">
            <div className="d-flex flex-column align-items-center mb-4">
              <div
                onMouseEnter={() => setHoverAvatar(true)}
                onMouseLeave={() => setHoverAvatar(false)}
                onClick={() => !uploading && fileInputRef.current?.click()}
                style={{ position: "relative", width: 100, height: 100, cursor: uploading ? "default" : "pointer" }}
              >
                {(previewUrl || user.profile_picture) ? (
                  <img
                    src={previewUrl || `${UPLOADS_BASE}${user.profile_picture}`}
                    alt={user.name}
                    style={{ width: 100, height: 100, borderRadius: "50%", objectFit: "cover", border: "3px solid var(--brand)" }}
                  />
                ) : (
                  <div style={{
                    width: 100, height: 100, borderRadius: "50%", background: "var(--brand)",
                    color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "1.8rem", fontWeight: 600,
                  }}>
                    {initials}
                  </div>
                )}
                <div style={{
                  position: "absolute", inset: 0, borderRadius: "50%",
                  background: "rgba(0,0,0,0.45)", display: "flex", alignItems: "center",
                  justifyContent: "center", opacity: (hoverAvatar && !uploading) ? 1 : 0,
                  transition: "opacity 0.15s",
                }}>
                  <span style={{ color: "#fff", fontSize: "1.4rem" }}>📷</span>
                </div>
              </div>
              <input ref={fileInputRef} type="file" accept="image/*" style={{ display: "none" }} onChange={handlePictureUpload} />
              <div className="mt-2 small text-muted">{uploading ? "Uploading…" : "Click to change photo"}</div>
              <div className="small text-muted mt-1">{user.email} · {user.role}</div>
            </div>
            <form onSubmit={saveProfile}>
              <div className="row g-3">
                <div className="col-md-6"><label className="form-label">Name</label><input className="form-control" value={profile.name} onChange={updateProfileField("name")} /></div>
                <div className="col-md-6"><label className="form-label">Phone</label><input className="form-control" value={profile.phone} onChange={updateProfileField("phone")} /></div>
                <div className="col-md-4"><label className="form-label">City</label><input className="form-control" value={profile.city} onChange={updateProfileField("city")} /></div>
                <div className="col-md-4"><label className="form-label">State</label><input className="form-control" value={profile.state} onChange={updateProfileField("state")} maxLength={5} /></div>
                <div className="col-md-4"><label className="form-label">Country</label>
                  <select className="form-select" value={profile.country} onChange={updateProfileField("country")}>
                    <option value="">Select</option>
                    {COUNTRIES.map((c) => (<option key={c} value={c}>{c}</option>))}
                  </select>
                </div>
                <div className="col-md-4"><label className="form-label">Gender</label>
                  <select className="form-select" value={profile.gender} onChange={updateProfileField("gender")}>
                    {GENDERS.map((g) => (<option key={g} value={g}>{g || "Select"}</option>))}
                  </select>
                </div>
                <div className="col-md-8"><label className="form-label">Languages</label><input className="form-control" value={profile.languages} onChange={updateProfileField("languages")} placeholder="English, Spanish" /></div>
                <div className="col-12"><label className="form-label">About Me</label><textarea className="form-control" rows={3} value={profile.about_me} onChange={updateProfileField("about_me")} /></div>
              </div>
              <button className="btn btn-brand mt-3" type="submit">Save Profile</button>
            </form>
          </div>
        </div>
      )}

      {activeTab === "preferences" && (
        <div className="card card-clean">
          <div className="card-header"><strong>AI Assistant Preferences</strong></div>
          <div className="card-body">
            <form onSubmit={savePreferences}>
              <div className="row g-3">
                <div className="col-md-6"><label className="form-label">Cuisine Preferences</label><input className="form-control" value={preferences.cuisine_preferences || ""} onChange={updatePrefField("cuisine_preferences")} placeholder="Italian, Indian, Japanese" /></div>
                <div className="col-md-3"><label className="form-label">Price Range</label>
                  <select className="form-select" value={preferences.price_range || ""} onChange={updatePrefField("price_range")}>
                    <option value="">Any</option>
                    {PRICE_OPTIONS.map((p) => (<option key={p} value={p}>{p}</option>))}
                  </select>
                </div>
                <div className="col-md-3"><label className="form-label">Search Radius (mi)</label><input type="number" className="form-control" value={preferences.search_radius || ""} onChange={updatePrefField("search_radius")} min={1} max={100} /></div>
                <div className="col-md-6"><label className="form-label">Preferred Location</label><input className="form-control" value={preferences.preferred_location || ""} onChange={updatePrefField("preferred_location")} placeholder="San Jose, CA" /></div>
                <div className="col-md-6"><label className="form-label">Dietary Needs</label><input className="form-control" value={preferences.dietary_needs || ""} onChange={updatePrefField("dietary_needs")} placeholder="Vegetarian, Gluten-Free" /></div>
                <div className="col-md-6"><label className="form-label">Ambiance Preferences</label><input className="form-control" value={preferences.ambiance_preferences || ""} onChange={updatePrefField("ambiance_preferences")} placeholder="Casual, Romantic" /></div>
                <div className="col-md-6"><label className="form-label">Sort By</label>
                  <select className="form-select" value={preferences.sort_preference || ""} onChange={updatePrefField("sort_preference")}>
                    <option value="">Default</option>
                    {SORT_OPTIONS.map((s) => (<option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>))}
                  </select>
                </div>
              </div>
              <button className="btn btn-brand mt-3" type="submit">Save Preferences</button>
            </form>
          </div>
        </div>
      )}

      {activeTab === "history" && (
        <div>
          <h5>My Reviews ({history.reviews?.length || 0})</h5>
          {(history.reviews || []).map((review) => (
            <div key={review.id} className="card card-clean mb-2">
              <div className="card-body py-2">
                <Link to={`/restaurants/${review.restaurant_id}`} style={{ color: "var(--brand)" }}>{review.restaurant_name || `Restaurant #${review.restaurant_id}`}</Link>
                <span className="ms-2 badge badge-soft">{review.rating} ★</span>
                <span className="ms-2 small text-muted">{new Date(review.created_at).toLocaleDateString()}</span>
                {review.comment && <p className="mb-0 mt-1 small">{review.comment}</p>}
              </div>
            </div>
          ))}
          <h5 className="mt-4">Restaurants I Added ({history.restaurants_added?.length || 0})</h5>
          {(history.restaurants_added || []).map((rest) => (
            <div key={rest.id} className="card card-clean mb-2">
              <div className="card-body py-2">
                <Link to={`/restaurants/${rest.id}`} style={{ color: "var(--brand)" }}>{rest.name}</Link>
                <span className="ms-2 small text-muted">{rest.cuisine_type ? rest.cuisine_type.charAt(0).toUpperCase() + rest.cuisine_type.slice(1) : ""} · {rest.city}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
