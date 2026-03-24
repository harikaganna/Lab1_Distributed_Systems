import React, { useState, useEffect } from "react";
import { api } from "../api/axios";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";

export default function OwnerDashboard() {
  const { user } = useAuth();
  const [restaurants, setRestaurants] = useState([]);
  const [selectedReviews, setSelectedReviews] = useState(null);
  const [selectedName, setSelectedName] = useState("");
  const [analytics, setAnalytics] = useState(null);
  const [claimId, setClaimId] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (!user) return;
    api.get("/restaurants?limit=200").then((res) => {
      const owned = res.data.filter((r) => r.owner_id === user.id);
      setRestaurants(owned);
      buildAnalytics(owned);
    });
  }, [user]);

  const buildAnalytics = async (owned) => {
    if (!owned.length) return;
    let allReviews = [];
    for (const r of owned) {
      try {
        const res = await api.get(`/restaurants/${r.id}/reviews`);
        allReviews.push(...res.data.map((rev) => ({ ...rev, restaurant_name: r.name })));
      } catch {}
    }

    const dist = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    allReviews.forEach((r) => { dist[r.rating] = (dist[r.rating] || 0) + 1; });

    const totalRating = allReviews.reduce((s, r) => s + r.rating, 0);
    const avgRating = allReviews.length ? (totalRating / allReviews.length).toFixed(2) : "N/A";

    const positive = allReviews.filter((r) => r.rating >= 4).length;
    const neutral = allReviews.filter((r) => r.rating === 3).length;
    const negative = allReviews.filter((r) => r.rating <= 2).length;

    const recent = [...allReviews].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5);

    setAnalytics({ dist, avgRating, totalReviews: allReviews.length, positive, neutral, negative, recent });
  };

  const viewReviews = async (id, name) => {
    const res = await api.get(`/restaurants/${id}/reviews`);
    setSelectedReviews(res.data);
    setSelectedName(name);
  };

  const claimRestaurant = async () => {
    setMsg("");
    try {
      await api.post(`/restaurants/${claimId}/claim`);
      setMsg("Restaurant claimed!");
      setClaimId("");
      const res = await api.get("/restaurants?limit=200");
      const owned = res.data.filter((r) => r.owner_id === user.id);
      setRestaurants(owned);
      buildAnalytics(owned);
    } catch (err) {
      setMsg(err.response?.data?.detail || "Error claiming restaurant");
    }
  };

  if (!user || user.role !== "owner") return <p>Owner access only.</p>;

  const maxDist = analytics ? Math.max(...Object.values(analytics.dist), 1) : 1;

  return (
    <div>
      <h4 className="mb-3">Owner Dashboard</h4>
      {msg && <div className="alert alert-info alert-clean py-2">{msg}</div>}

      {/* Analytics */}
      {analytics && (
        <div className="row g-3 mb-4">
          <div className="col-md-3">
            <div className="card card-clean text-center">
              <div className="card-body">
                <h2 style={{ color: "var(--brand)" }}>{analytics.totalReviews}</h2>
                <p className="small text-muted mb-0">Total Reviews</p>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card card-clean text-center">
              <div className="card-body">
                <h2 style={{ color: "var(--brand)" }}>{analytics.avgRating}</h2>
                <p className="small text-muted mb-0">Average Rating</p>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card card-clean text-center">
              <div className="card-body">
                <h2 style={{ color: "var(--brand)" }}>{restaurants.length}</h2>
                <p className="small text-muted mb-0">Restaurants</p>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card card-clean text-center">
              <div className="card-body">
                <h2 style={{ color: "#2e7d32" }}>{analytics.positive}</h2>
                <p className="small text-muted mb-0">Positive (4-5★)</p>
              </div>
            </div>
          </div>

          {/* Ratings Distribution */}
          <div className="col-md-6">
            <div className="card card-clean">
              <div className="card-header"><strong>Ratings Distribution</strong></div>
              <div className="card-body">
                {[5, 4, 3, 2, 1].map((star) => (
                  <div key={star} className="d-flex align-items-center gap-2 mb-2">
                    <span className="small" style={{ width: 30 }}>{star} ★</span>
                    <div className="flex-grow-1" style={{ background: "var(--border)", borderRadius: 4, height: 20 }}>
                      <div style={{
                        width: `${(analytics.dist[star] / maxDist) * 100}%`,
                        background: "var(--brand)", borderRadius: 4, height: 20,
                        minWidth: analytics.dist[star] > 0 ? 8 : 0,
                        transition: "width 0.3s"
                      }} />
                    </div>
                    <span className="small text-muted" style={{ width: 24 }}>{analytics.dist[star]}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sentiment */}
          <div className="col-md-6">
            <div className="card card-clean">
              <div className="card-header"><strong>Sentiment Analysis</strong></div>
              <div className="card-body">
                {analytics.totalReviews > 0 ? (
                  <>
                    <div className="d-flex gap-2 mb-3" style={{ height: 24, borderRadius: 4, overflow: "hidden" }}>
                      {analytics.positive > 0 && <div style={{ flex: analytics.positive, background: "#2e7d32" }} />}
                      {analytics.neutral > 0 && <div style={{ flex: analytics.neutral, background: "#f9a825" }} />}
                      {analytics.negative > 0 && <div style={{ flex: analytics.negative, background: "#c62828" }} />}
                    </div>
                    <div className="d-flex justify-content-between small">
                      <span style={{ color: "#2e7d32" }}>😊 Positive: {analytics.positive} ({((analytics.positive / analytics.totalReviews) * 100).toFixed(0)}%)</span>
                      <span style={{ color: "#f9a825" }}>😐 Neutral: {analytics.neutral} ({((analytics.neutral / analytics.totalReviews) * 100).toFixed(0)}%)</span>
                      <span style={{ color: "#c62828" }}>😞 Negative: {analytics.negative} ({((analytics.negative / analytics.totalReviews) * 100).toFixed(0)}%)</span>
                    </div>
                  </>
                ) : <p className="text-muted mb-0">No reviews yet to analyze.</p>}
              </div>
            </div>
          </div>

          {/* Recent Reviews */}
          {analytics.recent.length > 0 && (
            <div className="col-12">
              <div className="card card-clean">
                <div className="card-header"><strong>Recent Reviews</strong></div>
                <div className="card-body">
                  {analytics.recent.map((r) => (
                    <div key={r.id} className="mb-2 pb-2 border-bottom">
                      <div className="d-flex justify-content-between">
                        <div>
                          <strong>{r.user_name || "User"}</strong>
                          <span className="ms-2 badge badge-soft">{r.rating} ★</span>
                          <span className="ms-2 small text-muted">on {r.restaurant_name}</span>
                        </div>
                        <span className="small text-muted">{new Date(r.created_at).toLocaleDateString()}</span>
                      </div>
                      {r.comment && <p className="mb-0 mt-1 small">{r.comment}</p>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Claim section */}
      <div className="card card-clean mb-4">
        <div className="card-header"><strong>Claim a Restaurant</strong></div>
        <div className="card-body">
          <div className="input-group" style={{ maxWidth: 400 }}>
            <input className="form-control" placeholder="Restaurant ID" value={claimId} onChange={(e) => setClaimId(e.target.value)} />
            <button className="btn btn-brand" onClick={claimRestaurant}>Claim</button>
          </div>
        </div>
      </div>

      {/* Owned restaurants */}
      <h5>My Restaurants ({restaurants.length})</h5>
      {restaurants.map((r) => (
        <div key={r.id} className="card card-clean mb-2">
          <div className="card-body py-2 d-flex justify-content-between align-items-center">
            <div>
              <Link to={`/restaurants/${r.id}`} style={{ color: "var(--brand)", textDecoration: "none" }}>
                {r.name}
              </Link>
              <span className="ms-2 small text-muted">
                {r.avg_rating ? `${r.avg_rating} ★` : "No ratings"} · {r.review_count} reviews
              </span>
            </div>
            <div>
              <button className="btn btn-sm btn-soft me-1" onClick={() => viewReviews(r.id, r.name)}>View Reviews</button>
              <Link to={`/restaurants/${r.id}/edit`} className="btn btn-sm btn-soft">Edit</Link>
            </div>
          </div>
        </div>
      ))}

      {/* Reviews panel */}
      {selectedReviews && (
        <div className="card card-clean mt-4">
          <div className="card-header d-flex justify-content-between">
            <strong>Reviews for {selectedName}</strong>
            <button className="btn btn-sm btn-soft" onClick={() => setSelectedReviews(null)}>Close</button>
          </div>
          <div className="card-body">
            {selectedReviews.length === 0 ? <p className="text-muted">No reviews yet.</p> : (
              selectedReviews.map((r) => (
                <div key={r.id} className="mb-2 pb-2 border-bottom">
                  <strong>{r.user_name || "User"}</strong>
                  <span className="ms-2 badge badge-soft">{r.rating} ★</span>
                  <span className="ms-2 small text-muted">{new Date(r.created_at).toLocaleDateString()}</span>
                  {r.comment && <p className="mb-0 mt-1 small">{r.comment}</p>}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
