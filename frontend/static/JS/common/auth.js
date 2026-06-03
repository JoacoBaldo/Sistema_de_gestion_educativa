export function getAuthToken() {
  try {
    return localStorage.getItem("token");
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
