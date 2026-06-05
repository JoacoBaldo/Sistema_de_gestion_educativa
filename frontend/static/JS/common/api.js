/** Rutas relativas al servidor del frontend (proxy /api → backend en app.py). */
export function apiUrl(path) {
  if (!path) return "/";
  return path.startsWith("/") ? path : `/${path}`;
}

export function apiErrorMessage(body, fallback = "Error en la solicitud") {
  if (body && typeof body.error === "string") return body.error;
  return fallback;
}
