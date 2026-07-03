import axios from "axios";

// Set VITE_API_BASE_URL in Vercel dashboard to your Railway backend URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

api.interceptors.request.use((c) => {
  const t = localStorage.getItem("fc_token");
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response?.status === 401) {
      localStorage.removeItem("fc_token");
      window.location.href = "/login";
    }
    return Promise.reject(e);
  }
);

export default api;
