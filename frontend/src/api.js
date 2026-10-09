const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

export function getToken() {
  return localStorage.getItem("placement_token");
}

export function saveSession(token, user) {
  localStorage.setItem("placement_token", token);
  localStorage.setItem("placement_user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("placement_token");
  localStorage.removeItem("placement_user");
}

export async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const isFormData = options.body instanceof FormData;

  if (options.body && !isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  let result;

  if (contentType.includes("application/json")) {
    result = await response.json();
  } else {
    result = await response.text();
  }

  if (!response.ok) {
    let detail = "Request failed";
    if (typeof result === "object" && result !== null) {
      if (typeof result.detail === "string") {
        detail = result.detail;
      } else if (typeof result.detail === "object" && result.detail?.message) {
        detail = result.detail.message;
      } else if (result.message) {
        detail = result.message;
      } else {
        detail = JSON.stringify(result.detail || result);
      }
    } else if (typeof result === "string") {
      detail = result;
    }

    if (response.status === 401) {
      clearSession();
    }

    throw new Error(detail || `Request failed (${response.status})`);
  }

  return result;
}

export async function login(email, password) {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email: email.trim(), password })
  });

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(result.detail || "Login failed");
  }

  const token = result.access_token;

  if (!token) {
    throw new Error("The server did not return an access token.");
  }

  const user = result.user || await api("/api/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  saveSession(token, user);

  return user;
}

export function logout() {
  clearSession();
}

export function getSavedUser() {
  try {
    const value = localStorage.getItem("placement_user");
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}