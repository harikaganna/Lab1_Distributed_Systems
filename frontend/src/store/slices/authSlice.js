import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { api } from "../../api/axios";

export const loginUser = createAsyncThunk("auth/login", async ({ email, password }, { rejectWithValue }) => {
  try {
    const res = await api.post("/auth/login", { email, password });
    localStorage.setItem("token", res.data.access_token);
    const me = await api.get("/users/me");
    return { token: res.data.access_token, user: me.data };
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Login failed");
  }
});

export const signupUser = createAsyncThunk("auth/signup", async ({ name, email, password, role }, { dispatch, rejectWithValue }) => {
  try {
    await api.post("/auth/signup", { name, email, password, role });
    return dispatch(loginUser({ email, password })).unwrap();
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Signup failed");
  }
});

export const ownerSignupUser = createAsyncThunk("auth/ownerSignup", async ({ name, email, password, restaurant_location }, { dispatch, rejectWithValue }) => {
  try {
    await api.post("/auth/signup/owner", { name, email, password, restaurant_location });
    return dispatch(loginUser({ email, password })).unwrap();
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Signup failed");
  }
});

export const fetchCurrentUser = createAsyncThunk("auth/fetchMe", async (_, { rejectWithValue }) => {
  try {
    const res = await api.get("/users/me");
    return res.data;
  } catch (err) {
    localStorage.removeItem("token");
    return rejectWithValue("Session expired");
  }
});

const authSlice = createSlice({
  name: "auth",
  initialState: {
    user: null,
    token: localStorage.getItem("token") || null,
    loading: true,
    error: null,
  },
  reducers: {
    logout(state) {
      state.user = null;
      state.token = null;
      state.error = null;
      localStorage.removeItem("token");
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchCurrentUser.pending, (state) => { state.loading = true; })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.loading = false;
        state.user = null;
        state.token = null;
      })
      .addCase(signupUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(ownerSignupUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { logout, clearAuthError } = authSlice.actions;
export const selectUser = (state) => state.auth.user;
export const selectToken = (state) => state.auth.token;
export const selectAuthLoading = (state) => state.auth.loading;
export const selectAuthError = (state) => state.auth.error;
export default authSlice.reducer;
