import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/axios";
import { useAuth } from "../context/AuthContext";

const CUISINES = [
  "italian", "chinese", "mexican", "indian", "japanese",
  "american", "french", "thai", "mediterranean", "other"
];
const PRICES = ["$", "$$", "$$$", "$$$$"];
const AMBIANCES = ["casual", "fine_dining", "family_friendly", "romantic", "outdoor", "bar"];

export default function EditRestaurant() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Load existing restaurant data
  useEffect(() => {
    api.get(`/restaurants/${id}`)
      .then((res) => {
        const r = res.data;
        setForm({
          name: r.name,
          cuisine_type: r.cuisine_type,
          city: r.city,
          description: r.description || "",
          address: r.address || "",
          state: r.state || "",
          zip_code: r.zip_code || "",
          phone: r.phone || "",
          price_range: r.price_range || "",
          ambiance: r.ambiance || "",
          hours: r.hours || "",
          amenities: r.amenities || "",
        });
      })
      .catch(() => setError("Restaurant not found"));
  }, [id]);

  if (!user) {
    navigate("/login");
    return null;
  }

  if (!form) return <p>Loading...</p>;

  function updateField(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccessMsg("");

    const payload = { ...form };
    if (!payload.price_range) delete payload.price_range;
    if (!payload.ambiance) delete payload.ambiance;

    try {
      await api.put(`/restaurants/${id}`, payload);
      setSuccessMsg("Restaurant updated!");
    } catch (err) {
      setError(err.response?.data?.detail || "Error updating restaurant");
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card card-clean">
          <div className="card-header">
            <h5 className="mb-0">Edit Restaurant</h5>
          </div>
          <div className="card-body">
            {error && (
              <div className="alert alert-danger alert-clean py-2">{error}</div>
            )}
            {successMsg && (
              <div className="alert alert-success alert-clean py-2">{successMsg}</div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label">Name</label>
                  <input className="form-control" value={form.name} onChange={updateField("name")} required />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Cuisine</label>
                  <select className="form-select" value={form.cuisine_type} onChange={updateField("cuisine_type")}>
                    {CUISINES.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-3">
                  <label className="form-label">City</label>
                  <input className="form-control" value={form.city} onChange={updateField("city")} required />
                </div>

                <div className="col-md-8">
                  <label className="form-label">Address</label>
                  <input className="form-control" value={form.address} onChange={updateField("address")} />
                </div>
                <div className="col-md-2">
                  <label className="form-label">State</label>
                  <input className="form-control" value={form.state} onChange={updateField("state")} maxLength={5} />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Zip</label>
                  <input className="form-control" value={form.zip_code} onChange={updateField("zip_code")} />
                </div>

                <div className="col-md-4">
                  <label className="form-label">Phone</label>
                  <input className="form-control" value={form.phone} onChange={updateField("phone")} />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Price Range</label>
                  <select className="form-select" value={form.price_range} onChange={updateField("price_range")}>
                    <option value="">Select</option>
                    {PRICES.map((p) => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-4">
                  <label className="form-label">Ambiance</label>
                  <select className="form-select" value={form.ambiance} onChange={updateField("ambiance")}>
                    <option value="">Select</option>
                    {AMBIANCES.map((a) => (
                      <option key={a} value={a}>{a.replace("_", " ")}</option>
                    ))}
                  </select>
                </div>

                <div className="col-12">
                  <label className="form-label">Description</label>
                  <textarea className="form-control" rows={3} value={form.description} onChange={updateField("description")} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Hours</label>
                  <input className="form-control" value={form.hours} onChange={updateField("hours")} />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Amenities</label>
                  <input className="form-control" value={form.amenities} onChange={updateField("amenities")} />
                </div>
              </div>

              <button className="btn btn-brand mt-3" type="submit">
                Save Changes
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
