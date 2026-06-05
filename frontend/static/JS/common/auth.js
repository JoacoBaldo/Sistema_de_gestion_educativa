const TOKEN_KEY = "token";
const USER_KEY = "sge_user";
const USER_IDS_KEY = "sge_user_ids";

export function getAuthToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function hasAuthToken() {
  return !!getAuthToken();
}

export function authHeaders() {
  const token = getAuthToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export function getUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveSession(user) {
  if (!user?.token) return;
  localStorage.setItem(TOKEN_KEY, user.token);
  localStorage.setItem(
    USER_KEY,
    JSON.stringify({
      id: user.id,
      username: user.username,
      email: user.email,
      role_id: user.role_id,
    })
  );
  if (user.email && user.id != null) {
    const map = getUserIdMap();
    map[user.email.toLowerCase()] = user.id;
    localStorage.setItem(USER_IDS_KEY, JSON.stringify(map));
  }
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function getUserIdMap() {
  try {
    return JSON.parse(localStorage.getItem(USER_IDS_KEY) || "{}");
  } catch {
    return {};
  }
}

export function getCachedUserId(email) {
  const map = getUserIdMap();
  return map[email.toLowerCase()] ?? null;
}

export function requireAuth(redirectTo = "/auth") {
  if (!hasAuthToken()) {
    location.href = redirectTo;
    return false;
  }
  return true;
}

export function userInitials(username) {
  if (!username) return "??";
  const parts = String(username).trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return String(username).slice(0, 2).toUpperCase();
}
