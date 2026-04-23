import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { favouritesApi } from "../../api/axios";

export const fetchFavourites = createAsyncThunk("favourites/fetchAll", async () => {
  const res = await favouritesApi.get("/favourites");
  return res.data;
});

export const addFavourite = createAsyncThunk("favourites/add", async (restaurantId) => {
  const res = await favouritesApi.post(`/favourites/${restaurantId}`);
  return res.data;
});

export const removeFavourite = createAsyncThunk("favourites/remove", async (restaurantId) => {
  await favouritesApi.delete(`/favourites/${restaurantId}`);
  return restaurantId;
});

const favouriteSlice = createSlice({
  name: "favourites",
  initialState: {
    list: [],
    loading: false,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchFavourites.pending, (state) => { state.loading = true; })
      .addCase(fetchFavourites.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchFavourites.rejected, (state) => { state.loading = false; })
      .addCase(addFavourite.fulfilled, (state, action) => {
        state.list.push(action.payload);
      })
      .addCase(removeFavourite.fulfilled, (state, action) => {
        state.list = state.list.filter((f) => f.restaurant_id !== action.payload);
      });
  },
});

export const selectFavourites = (state) => state.favourites.list;
export const selectFavouritesLoading = (state) => state.favourites.loading;
export default favouriteSlice.reducer;
