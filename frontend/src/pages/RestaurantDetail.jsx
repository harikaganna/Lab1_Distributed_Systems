import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { api, restaurantApi } from "../api/axios";
import { selectUser } from "../store/slices/authSlice";
import { fetchRestaurantDetail, selectRestaurantDetail } from "../store/slices/restaurantSlice";
import { fetchReviews, createReview, updateReview, deleteReview, selectReviews } from "../store/slices/reviewSlice";
import { addFavourite } from "../store/slices/favouriteSlice";

function titleCase(str) {
  if (!str) return "";
  return str.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function RestaurantDetail() {
  const { id } = useParams();
  const dispatch = useDispatch();
  const user = useSelector(selectUser);
  const restaurant = useSelector(selectRestaurantDetail);
  const reviews = useSelector(selectReviews);
  const [message, setMessage] = useState("");
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState("");
  const [editingReviewId, setEditingReviewId] = useState(null);
  const [editRating, setEditRating] = useState(5);
  const [editComment, setEditComment] = useState("");

  useEffect(() => {
    dispatch(fetchRestaurantDetail(id));
    dispatch(fetchReviews(id));
  }, [id]);

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
      await restaurantApi.post(`/restaurants/${id}/photos`, formData, { headers: { "Content-Type": "multipart/form-data" } });
      setMessage("Photo uploaded!");
      dispatch(fetchRestaurantDetail(id));
    } catch (err) {
      setMessage(err.response?.data?.detail || "Error uploading photo");
    }
  }

  async function submitReview(e) {
    e.preventDefault();
    try {
      await dispatch(createReview({ restaurantId: id, data: { rating: newRating, comment: newComment } })).unwrap();
      setNewComment("");
      setNewRating(5);
      setMessage("Review added!");
      dispatch(fetchRestaurantDetail(id));
    } catch (err) {
      setMessage(err.message || "Error submitting review");
    }
  }

  function startEditing(review) {
    setEditingReviewId(review.id);
    setEditRating(review.rating);
    setEditComment(review.comment || "");
  }

  async function saveEditedReview() {
    try {
      await dispatch(updateReview({ restaurantId: id, reviewId: editingReviewId, data: { rating: editRating, comment: editComment } })).unwrap();
      setEditingReviewId(null);
    } catch (err) {
      setMessage(err.message || "Error updating review");
    }
  }

  async function handleDeleteReview(reviewId) {
    if (!confirm("Delete this review?")) return;
    await dispatch(deleteReview({ restaurantId: id, reviewId }));
    dispatch(fetchRestaurantDetail(id));
  }

  async function addToFavourites() {
    try {
      await dispatch(addFavourite(id)).unwrap();
      setMessage("Added to favourites!");
    } catch (err) {
      setMessage(err.message || "Error adding to favourites");
    }
  }

  if (!restaurant) return <p>Loading...</p>;
  const photos = getPhotos();

  return (
    <div>
      <div className="card card-clean mb-4">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <h3>{restaurant.name}</h3>
              <p className="text-muted mb-1">
                {titleCase(restaurant.cuisine_type)}{" · "}{restaurant.city}
                {restaurant.state && `, ${restaurant.state}`}
                {restaurant.price_range && ` · ${restaurant.price_range}`}
                {restaurant.ambiance && ` · ${titleCase(restaurant.ambiance)}`}
              </p>
              {restaurant.address && <p className="small mb-1">📍 {restaurant.address} {restaurant.zip_code || ""}</p>}
              {restaurant.phone && <p className="small mb-1">📞 {restaurant.phone}</p>}
              {restaurant.hours && <p className="small mb-1">🕐 {restaurant.hours}</p>}
              {restaurant.description && <p className="mt-2">{restaurant.description}</p>}
              {restaurant.amenities && (
                <div className="mt-2">
                  {restaurant.amenities.split(",").map((a) => a.trim()).filter(Boolean).map((a) => (
                    <span key={a} className="badge badge-soft me-1 mb-1">{titleCase(a)}</span>
                  ))}
                </div>
              )}
            </div>
            <div className="text-end">
              {restaurant.avg_rating && <span className="badge badge-soft fs-5">{restaurant.avg_rating} ★</span>}
              <p className="small text-muted">{restaurant.review_count} reviews</p>
              {user && <button className="btn btn-sm btn-soft" onClick={addToFavourites}>❤️ Favourite</button>}
            </div>
          </div>
        </div>
      </div>

      {message && <div className="alert alert-info alert-clean py-2">{message}</div>}

      <div className="card card-clean mb-4">
        <div className="card-header d-flex justify-content-between align-items-center">
          <strong>Photos ({photos.length})</strong>
          {user && (
            <label className="btn btn-sm btn-soft mb-0" style={{ cursor: "pointer" }}>
              📷 Add Photo
              <input type="file" accept="image/*" onChange={handlePhotoUpload} style={{ display: "none" }} />
            </label>
          )}
        </div>
        <div className="card-body">
          {photos.length === 0 ? (
            <p className="text-muted mb-0">No photos yet. Be the first to add one!</p>
          ) : (
            <div className="d-flex flex-wrap gap-2">
              {photos.map((photoUrl, index) => (
                <img key={index} src={`http://localhost:8006${photoUrl}`} alt={`${restaurant.name} photo ${index + 1}`}
                  style={{ width: 180, height: 140, objectFit: "cover", borderRadius: 10, border: "1px solid var(--border)" }} />
              ))}
            </div>
          )}
        </div>
      </div>

      {user && (
        <div className="card card-clean mb-4">
          <div className="card-header"><strong>Write a Review</strong></div>
          <div className="card-body">
            <form onSubmit={submitReview}>
              <div className="row g-2 mb-2">
                <div className="col-auto">
                  <select className="form-select" value={newRating} onChange={(e) => setNewRating(Number(e.target.value))}>
                    {[1, 2, 3, 4, 5].map((n) => (<option key={n} value={n}>{n} ★</option>))}
                  </select>
                </div>
                <div className="col">
                  <textarea className="form-control" rows={2} placeholder="Your review..." value={newComment} onChange={(e) => setNewComment(e.target.value)} />
                </div>
                <div className="col-auto d-flex align-items-end">
                  <button className="btn btn-brand" type="submit">Submit</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      <h5>Reviews ({reviews.length})</h5>
      {reviews.map((review) => (
        <div key={review.id} className="card card-clean mb-2">
          <div className="card-body py-2">
            {editingReviewId === review.id ? (
              <div className="d-flex gap-2 align-items-center">
                <select className="form-select form-select-sm" style={{ width: 80 }} value={editRating} onChange={(e) => setEditRating(Number(e.target.value))}>
                  {[1, 2, 3, 4, 5].map((n) => (<option key={n} value={n}>{n} ★</option>))}
                </select>
                <input className="form-control form-control-sm" value={editComment} onChange={(e) => setEditComment(e.target.value)} />
                <button className="btn btn-sm btn-brand" onClick={saveEditedReview}>Save</button>
                <button className="btn btn-sm btn-soft" onClick={() => setEditingReviewId(null)}>Cancel</button>
              </div>
            ) : (
              <div className="d-flex justify-content-between">
                <div>
                  <strong>{review.user_name || "User"}</strong>
                  <span className="ms-2 badge badge-soft">{review.rating} ★</span>
                  <span className="ms-2 small text-muted">{new Date(review.created_at).toLocaleDateString()}</span>
                  {review.comment && <p className="mb-0 mt-1">{review.comment}</p>}
                </div>
                {user && user.id === review.user_id && (
                  <div className="d-flex gap-1">
                    <button className="btn btn-sm btn-soft" onClick={() => startEditing(review)}>Edit</button>
                    <button className="btn btn-sm btn-outline-danger" onClick={() => handleDeleteReview(review.id)}>Delete</button>
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
