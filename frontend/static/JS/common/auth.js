export function getAuthToken() {
  return null;
}

export function hasAuthToken() {
  return document.body?.dataset?.authenticated === "true";
}

export function authHeaders() {
  return {};
}

export function getUser() {
  return null;
}

export function saveSession() {}

export function clearSession() {
  window.location.href = "/auth/logout";
}

export function getCachedUserId() {
  return null;
}

export function requireAuth(redirectTo = "/auth") {
  if (hasAuthToken()) return true;
  window.location.href = redirectTo;
  return false;
}

export function userInitials(username) {
  if (!username) return "??";
  const parts = String(username).trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return String(username).slice(0, 2).toUpperCase();
}
