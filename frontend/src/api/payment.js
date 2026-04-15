import { getToken } from "../stores/auth.js";

const API_BASE = "/api/payment";

async function authRequest(url, options = {}) {
  const token = getToken();
  if (!token) throw new Error("请先登录");
  const headers = { "Content-Type": "application/json", ...options.headers };
  headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || "请求失败");
  }
  return res.json();
}

export async function createCheckoutSession(plan) {
  return authRequest(`${API_BASE}/create-checkout-session`, {
    method: "POST",
    body: JSON.stringify({ plan }),
  });
}

export async function getSessionStatus(sessionId) {
  return authRequest(`${API_BASE}/session-status?session_id=${sessionId}`);
}

export async function getSubscription() {
  return authRequest(`${API_BASE}/subscription`);
}

export async function createPortalSession() {
  return authRequest(`${API_BASE}/create-portal-session`, { method: "POST" });
}

export async function fetchConfig() {
  const res = await fetch("/api/config");
  return res.json();
}
