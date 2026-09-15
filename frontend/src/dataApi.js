const API_PREFIX = "/api";
const STORE_KEY = "retailo_store_id";
const CAMERA_KEY = "retailo_camera_id";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = "No fue posible consultar los datos de la demo.";
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
      if (Array.isArray(body.detail)) message = body.detail[0]?.msg ?? message;
    } catch {
      // Algunos errores de infraestructura no incluyen un cuerpo JSON.
    }
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return response.status === 204 ? null : response.json();
}

function withPeriod(path, period) {
  if (!period) return path;
  const query = new URLSearchParams({
    start_date: period.start,
    end_date: period.end,
  });
  return `${path}?${query}`;
}

export function createStore(payload) {
  return apiRequest("/stores", { method: "POST", body: JSON.stringify(payload) });
}

export function getStores() {
  return apiRequest("/stores");
}

export function createCamera(storeId, payload) {
  return apiRequest(`/stores/${storeId}/cameras`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getCameras(storeId) {
  return apiRequest(`/stores/${storeId}/cameras`);
}

export function updateCamera(cameraId, payload) {
  return apiRequest(`/cameras/${cameraId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteCamera(cameraId) {
  return apiRequest(`/cameras/${cameraId}`, { method: "DELETE" });
}

export function createZone(cameraId, payload) {
  return apiRequest(`/cameras/${cameraId}/zones`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getZones(cameraId) {
  return apiRequest(`/cameras/${cameraId}/zones`);
}

export function updateZone(zoneId, payload) {
  return apiRequest(`/zones/${zoneId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteZone(zoneId) {
  return apiRequest(`/zones/${zoneId}`, { method: "DELETE" });
}

export function getSessions(cameraId) {
  return apiRequest(`/cameras/${cameraId}/sessions?limit=20`);
}

export async function getSessionResult(sessionId) {
  try {
    return await apiRequest(`/sessions/${sessionId}/video-results`);
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
}

export function getAnalyticsSummary(storeId, period) {
  return apiRequest(withPeriod(`/stores/${storeId}/analytics/summary`, period));
}

export function getTraffic(storeId, period) {
  return apiRequest(withPeriod(`/stores/${storeId}/analytics/traffic`, period));
}

export function getInsights(storeId, period) {
  return apiRequest(withPeriod(`/stores/${storeId}/analytics/insights`, period));
}

export function getRecommendations(storeId) {
  return apiRequest(`/stores/${storeId}/recommendations`);
}

export function generateRecommendations(storeId, period) {
  return apiRequest(withPeriod(`/stores/${storeId}/recommendations/generate`, period), {
    method: "POST",
  });
}

export function updateRecommendationStatus(recommendationId, status) {
  return apiRequest(`/recommendations/${recommendationId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function saveDemoContext(store, camera) {
  if (store?.id) localStorage.setItem(STORE_KEY, String(store.id));
  if (camera?.id) localStorage.setItem(CAMERA_KEY, String(camera.id));
}

export function clearDemoContext() {
  localStorage.removeItem(STORE_KEY);
  localStorage.removeItem(CAMERA_KEY);
}

export async function resolveDemoContext() {
  const stores = await getStores();
  if (!stores.length) return { store: null, camera: null };

  const savedStoreId = Number(localStorage.getItem(STORE_KEY));
  const store = stores.find((item) => item.id === savedStoreId) ?? stores[0];
  const cameras = await getCameras(store.id);
  const savedCameraId = Number(localStorage.getItem(CAMERA_KEY));
  const camera = cameras.find((item) => item.id === savedCameraId) ?? cameras[0] ?? null;
  saveDemoContext(store, camera);
  return { store, camera };
}
