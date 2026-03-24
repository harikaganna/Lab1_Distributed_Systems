import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function RestaurantDetail() {
  const { id } = useParams();
  const { user } = useAuth();

  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [message, setMessage] = useState("");

  // New review form
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState("");

  // Edit review state
  const [editingReviewId, setEditingReviewId] = useState(null);
  const [editRating, setEditRating] = useState(5);
  const [editComment, setEditComment] = useState("");

  async function loadData() {
    const [restaurantRes, reviewsRes] = await Promise.all([
      api.get(`/restaurants/${id}`),
      api.get(`/restaurants/${id}/reviews`),
    ]);
    setRestaurant(restaurantRes.data);
    setReviews(reviewsRes.data);
  }

  useEffect(() => {
    loadData();
  }, [id]);

  // Parse the comma-separated photos string into an array of URLs
  function getPhotos() {
    if (!restaurant || !restaurant.photos) return [];
    return restaurant.photos.split(",").map((p) => p.trim()).filter(Boolean);
  }

  async function handlePhotoUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post(`/restaurants/${id}/photos`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage("Photo uploaded!");
      loadData();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Error uploading photo");
    }
  }

  async function submitReview(e) {
    e.preventDefault();
    try {
      await api.post(`/restaurants/${id}/reviews`, {
        rating: newRating,
        comment: newComment,
      });
      setNewComment("");
      setNewRating(5);
      setMessage("Review added!");
      loadData();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Error submitting review");
    }
  }

  function startEditing(review) {
    setEditingReviewId(review.id);
    setEditRating(review.rating);
    setEditComment(review.comment || "");
  }

  function cancelEditing() {
    setEditingReviewId(null);
  }

  async function saveEditedReview() {
    try {
      await api.put(`/restaurants/${id}/reviews/${editingReviewId}`, {
        rating: editRating,
        comment: editComment,
      });
      setEditingReviewId(null);
      loadData();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Error updating review");
    }
  }

  async function deleteReview(reviewId) {
    if (!confirm("Delete this review?")) return;
    await api.delete(`/restaurants/${id}/reviews/${reviewId}`);
    loadData();
  }

  async function addToFavourites() {
    try {
      await api.post(`/favourites/${id}`);
      setMessage("Added to favourites!");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Error adding to favourites");
    }
  }

  if (!restaurant) return <p>Loading...</p>;

  const photos = getPhotos();

  return (
    <div>
      {/* Restaurant info card */}
      <div className="card card-clean mb-4">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <h3>{restaurant.name}</h3>
              <p className="text-muted mb-1">
                {restaurant.cuisine_type}
                {" · "}{restaurant.city}
                {restaurant.state && `, ${restaurant.state}`}
                {restaurant.price_range && ` · ${restaurant.price_range}`}
                {restaurant.ambiance && ` · ${restaurant.ambiance}`}
              </p>
              {restaurant.address && (
                <p className="small mb-1">📍 {restaurant.address} {restaurant.zip_code || ""}</p>
              )}
              {restaurant.phone && (
                <p className="small mb-1">📞 {restaurant.phone}</p>
              )}
              {restaurant.hours && (
                <p className="small mb-1">🕐 {restaurant.hours}</p>
              )}
              {restaurant.description && (
                <p className="mt-2">{restaurant.description}</p>
              )}
            </div>

            <div className="text-end">
              {restaurant.avg_rating && (
                <span className="badge badge-soft fs-5">{restaurant.avg_rating} ★</span>
              )}
              <p className="small text-muted">{restaurant.review_count} reviews</p>
              {user && (
                <button className="btn btn-sm btn-soft" onClick={addToFavourites}>
                  ❤️ Favourite
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {message && (
        <div className="alert alert-info alert-clean py-2">{message}</div>
      )}

      {/* Photos section */}
      <div className="card card-clean mb-4">
        <div className="card-header d-flex justify-content-between align-items-center">
          <strong>Photos ({photos.length})</strong>
          {user && (
            <label className="btn btn-sm btn-soft mb-0" style={{ cursor: "pointer" }}>
              📷 Add Photo
              <input
                type="file"
                accept="image/*"
                onChange={handlePhotoUpload}
                style={{ display: "none" }}
              />
            </label>
          )}
        </div>
        <div className="card-body">
          {photos.length === 0 ? (
            <p className="text-muted mb-0">No photos yet. Be the first to add one!</p>
          ) : (
            <div className="d-flex flex-wrap gap-2">
              {photos.map((photoUrl, index) => (
                <img
                  key={index}
                  src={`http://localhost:8006${photoUrl}`}
                  alt={`${restaurant.name} photo ${index + 1}`}
                  style={{
                    width: 180,
                    height: 140,
                    objectFit: "cover",
                    borderRadius: 10,
                    border: "1px solid var(--border)",
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Write a review */}
      {user && (
        <div className="card card-clean mb-4">
          <div className="card-header">
            <strong>Write a Review</strong>
          </div>
          <div className="card-body">
            <form onSubmit={submitReview}>
              <div className="row g-2 mb-2">
                <div className="col-auto">
                  <select
                    className="form-select"
                    value={newRating}
                    onChange={(e) => setNewRating(Number(e.target.value))}
                  >
                    {[1, 2, 3, 4, 5].map((n) => (
                      <option key={n} value={n}>{n} ★</option>
                    ))}
                  </select>
                </div>
                <div className="col">
                  <textarea
                    className="form-control"
                    rows={2}
                    placeholder="Your review..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                  />
                </div>
                <div className="col-auto d-flex align-items-end">
                  <button className="btn btn-brand" type="submit">Submit</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reviews list */}
      <h5>Reviews ({reviews.length})</h5>
      {reviews.map((review) => (
        <div key={review.id} className="card card-clean mb-2">
          <div className="card-body py-2">
            {editingReviewId === review.id ? (
              <div className="d-flex gap-2 align-items-center">
                <select
                  className="form-select form-select-sm"
                  style={{ width: 80 }}
                  value={editRating}
                  onChange={(e) => setEditRating(Number(e.target.value))}
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>{n} ★</option>
                  ))}
                </select>
                <input
                  className="form-control form-control-sm"
                  value={editComment}
                  onChange={(e) => setEditComment(e.target.value)}
                />
                <button className="btn btn-sm btn-brand" onClick={saveEditedReview}>Save</button>
                <button className="btn btn-sm btn-soft" onClick={cancelEditing}>Cancel</button>
              </div>
            ) : (
              <div className="d-flex justify-content-between">
                <div>
                  <strong>{review.user_name || "User"}</strong>
                  <span className="ms-2 badge badge-soft">{review.rating} ★</span>
                  <span className="ms-2 small text-muted">
                    {new Date(review.created_at).toLocaleDateString()}
                  </span>
                  {review.comment && (
                    <p className="mb-0 mt-1">{review.comment}</p>
                  )}
                </div>

                {user && user.id === review.user_id && (
                  <div className="d-flex gap-1">
                    <button className="btn btn-sm btn-soft" onClick={() => startEditing(review)}>Edit</button>
                    <button className="btn btn-sm btn-outline-danger" onClick={() => deleteReview(review.id)}>Delete</button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
