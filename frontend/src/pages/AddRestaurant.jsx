import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { selectUser } from "../store/slices/authSlice";
import { restaurantApi } from "../api/axios";

const CUISINES = ["italian", "chinese", "mexican", "indian", "japanese", "american", "french", "thai", "mediterranean", "other"];
const PRICES = ["$", "$$", "$$$", "$$$$"];
const AMBIANCES = ["casual", "fine_dining", "family_friendly", "romantic", "outdoor", "bar"];

export default function AddRestaurant() {
  const user = useSelector(selectUser);
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "", cuisine_type: "italian", city: "", description: "", address: "",
    state: "", zip_code: "", phone: "", price_range: "", ambiance: "", hours: "", amenities: "",
  });

  if (!user) { navigate("/login"); return null; }

  function updateField(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    const payload = { ...form };
    if (!payload.price_range) delete payload.price_range;
    if (!payload.ambiance) delete payload.ambiance;
    try {
      const response = await restaurantApi.post("/restaurants", payload);
      navigate(`/restaurants/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Error creating restaurant");
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card card-clean">
          <div className="card-header"><h5 className="mb-0">Add a Restaurant</h5></div>
          <div className="card-body">
            {error && <div className="alert alert-danger alert-clean py-2">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                <div className="col-md-6"><label className="form-label">Name *</label><input className="form-control" value={form.name} onChange={updateField("name")} required /></div>
                <div className="col-md-3"><label className="form-label">Cuisine *</label>
                  <select className="form-select" value={form.cuisine_type} onChange={updateField("cuisine_type")}>
                    {CUISINES.map((c) => (<option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>))}
                  </select>
                </div>
                <div className="col-md-3"><label className="form-label">City *</label><input className="form-control" value={form.city} onChange={updateField("city")} required /></div>
                <div className="col-md-8"><label className="form-label">Address</label><input className="form-control" value={form.address} onChange={updateField("address")} /></div>
                <div className="col-md-2"><label className="form-label">State</label><input className="form-control" value={form.state} onChange={updateField("state")} maxLength={5} placeholder="CA" /></div>
                <div className="col-md-2"><label className="form-label">Zip</label><input className="form-control" value={form.zip_code} onChange={updateField("zip_code")} /></div>
                <div className="col-md-4"><label className="form-label">Phone</label><input className="form-control" value={form.phone} onChange={updateField("phone")} /></div>
                <div className="col-md-4"><label className="form-label">Price Range</label>
                  <select className="form-select" value={form.price_range} onChange={updateField("price_range")}>
                    <option value="">Select</option>
                    {PRICES.map((p) => (<option key={p} value={p}>{p}</option>))}
                  </select>
                </div>
                <div className="col-md-4"><label className="form-label">Ambiance</label>
                  <select className="form-select" value={form.ambiance} onChange={updateField("ambiance")}>
                    <option value="">Select</option>
                    {AMBIANCES.map((a) => (<option key={a} value={a}>{a.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</option>))}
                  </select>
                </div>
                <div className="col-12"><label className="form-label">Description</label><textarea className="form-control" rows={3} value={form.description} onChange={updateField("description")} /></div>
                <div className="col-md-6"><label className="form-label">Hours</label><input className="form-control" value={form.hours} onChange={updateField("hours")} placeholder="Mon-Fri 9am-10pm" /></div>
                <div className="col-md-6"><label className="form-label">Amenities</label><input className="form-control" value={form.amenities} onChange={updateField("amenities")} placeholder="wifi, outdoor seating" /></div>
              </div>
              <button className="btn btn-brand mt-3" type="submit">Create Restaurant</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
