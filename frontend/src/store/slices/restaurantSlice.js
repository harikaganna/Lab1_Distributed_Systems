import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { restaurantApi } from "../../api/axios";

export const fetchRestaurants = createAsyncThunk("restaurants/fetchAll", async (params = {}) => {
  const res = await restaurantApi.get("/restaurants", { params });
  return res.data;
});

export const fetchRestaurantDetail = createAsyncThunk("restaurants/fetchDetail", async (id) => {
  const res = await restaurantApi.get(`/restaurants/${id}`);
  return res.data;
});

const restaurantSlice = createSlice({
  name: "restaurants",
  initialState: {
    list: [],
    detail: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearDetail(state) { state.detail = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRestaurants.pending, (state) => { state.loading = true; })
      .addCase(fetchRestaurants.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchRestaurants.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchRestaurantDetail.pending, (state) => { state.loading = true; })
      .addCase(fetchRestaurantDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.detail = action.payload;
      })
      .addCase(fetchRestaurantDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearDetail } = restaurantSlice.actions;
export const selectRestaurants = (state) => state.restaurants.list;
export const selectRestaurantDetail = (state) => state.restaurants.detail;
export const selectRestaurantsLoading = (state) => state.restaurants.loading;
export default restaurantSlice.reducer;
