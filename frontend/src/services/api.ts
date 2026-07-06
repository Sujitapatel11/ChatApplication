import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error(
    "VITE_API_BASE_URL is not defined. Please configure it in your environment variables."
  );
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("fc_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;

    switch (status) {
      case 401:
        localStorage.removeItem("fc_token");
        window.location.href = "/login";
        break;

      case 403:
        console.error("Forbidden");
        break;

      case 404:
        console.error("API endpoint not found");
        break;

      case 500:
        console.error("Internal server error");
        break;

      default:
        console.error(error);
    }

    return Promise.reject(error);
  }
);

export default api;