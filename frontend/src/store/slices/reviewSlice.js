import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { reviewApi } from "../../api/axios";

export const fetchReviews = createAsyncThunk("reviews/fetchAll", async (restaurantId) => {
  const res = await reviewApi.get(`/restaurants/${restaurantId}/reviews`);
  return res.data;
});

export const createReview = createAsyncThunk("reviews/create", async ({ restaurantId, data }) => {
  const res = await reviewApi.post(`/restaurants/${restaurantId}/reviews`, data);
  return res.data;
});

export const updateReview = createAsyncThunk("reviews/update", async ({ restaurantId, reviewId, data }) => {
  const res = await reviewApi.put(`/restaurants/${restaurantId}/reviews/${reviewId}`, data);
  return res.data;
});

export const deleteReview = createAsyncThunk("reviews/delete", async ({ restaurantId, reviewId }) => {
  await reviewApi.delete(`/restaurants/${restaurantId}/reviews/${reviewId}`);
  return reviewId;
});

const reviewSlice = createSlice({
  name: "reviews",
  initialState: {
    list: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchReviews.pending, (state) => { state.loading = true; })
      .addCase(fetchReviews.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchReviews.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(createReview.fulfilled, (state, action) => {
        state.list.unshift(action.payload);
      })
      .addCase(updateReview.fulfilled, (state, action) => {
        const idx = state.list.findIndex((r) => r.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
      })
      .addCase(deleteReview.fulfilled, (state, action) => {
        state.list = state.list.filter((r) => r.id !== action.payload);
      });
  },
});

export const selectReviews = (state) => state.reviews.list;
export const selectReviewsLoading = (state) => state.reviews.loading;
export default reviewSlice.reducer;
