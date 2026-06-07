export function httpRequest(url, { method = "GET", headers = {}, body = null, formData = null } = {}) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    Object.entries(headers).forEach(([key, value]) => {
      xhr.setRequestHeader(key, value);
    });
    xhr.addEventListener("load", () => {
      resolve({
        ok: xhr.status >= 200 && xhr.status < 300,
        status: xhr.status,
        json() {
          try {
            return JSON.parse(xhr.responseText);
          } catch {
            throw new Error("Respuesta JSON inválida");
          }
        },
        text: () => xhr.responseText,
      });
    });
    xhr.addEventListener("error", () => reject(new Error("Error de red")));
    xhr.send(formData ?? body);
  });
}

export function submitForm(url, formData) {
  return httpRequest(url, { method: "POST", formData });
}

export function requestJson(url, { method = "GET", headers = {}, body = null } = {}) {
  const jsonHeaders = { "Content-Type": "application/json", ...headers };
  const payload = body != null ? JSON.stringify(body) : null;
  return httpRequest(url, { method, headers: jsonHeaders, body: payload });
}
