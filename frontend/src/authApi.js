const API_PREFIX = "/api/auth";
const TOKEN_KEY = "retailo_access_token";

async function request(path, options = {}) {
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = "No fue posible completar la solicitud.";
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
      if (Array.isArray(body.detail)) message = body.detail[0]?.msg ?? message;
    } catch {
      // La API puede responder sin cuerpo en errores de infraestructura.
    }
    throw new Error(message);
  }

  return response.status === 204 ? null : response.json();
}

function authorizationHeaders() {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function saveSession(session) {
  localStorage.setItem(TOKEN_KEY, session.access_token);
  return session.user;
}

export async function registerAccount(payload) {
  return saveSession(await request("/register", { method: "POST", body: JSON.stringify(payload) }));
}

export async function loginAccount(payload) {
  return saveSession(await request("/login", { method: "POST", body: JSON.stringify(payload) }));
}

export async function getCurrentUser() {
  return request("/me", { headers: authorizationHeaders() });
}

export async function changeAccountPassword(payload) {
  return request("/password", {
    method: "PATCH",
    headers: authorizationHeaders(),
    body: JSON.stringify(payload),
  });
}

export async function logoutAccount() {
  try {
    await request("/logout", { method: "POST", headers: authorizationHeaders() });
  } finally {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function hasStoredSession() {
  return Boolean(localStorage.getItem(TOKEN_KEY));
}

export function clearStoredSession() {
  localStorage.removeItem(TOKEN_KEY);
}
