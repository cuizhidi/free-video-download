import { getToken, getRefreshToken, setAuth, clearAuth } from "../stores/auth.js";

const API_BASE = "/api/auth";

async function request(url, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || "请求失败");
  }
  return res.json();
}

export async function register(email, password, name) {
  const data = await request(`${API_BASE}/register`, {
    method: "POST",
    body: JSON.stringify({ email, password, name }),
  });
  setAuth(data);
  return data;
}

export async function login(email, password) {
  const data = await request(`${API_BASE}/login`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAuth(data);
  return data;
}

export async function fetchMe() {
  return request(`${API_BASE}/me`);
}

export async function refreshToken() {
  const rt = getRefreshToken();
  if (!rt) throw new Error("No refresh token");
  const data = await request(`${API_BASE}/refresh`, {
    method: "POST",
    body: JSON.stringify({ refresh_token: rt }),
  });
  setAuth(data);
  return data;
}

export function logout() {
  clearAuth();
}
