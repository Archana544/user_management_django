import axios from "axios";

const BACKEND_URL = "https://my-containerapp.redgrass-66159ae4.westus.azurecontainerapps.io";

const API = axios.create({
  baseURL: BACKEND_URL,
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export { BACKEND_URL };
export default API;