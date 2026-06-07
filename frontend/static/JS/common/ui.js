export function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function getQueryParam(name) {
  return new URLSearchParams(location.search).get(name);
}

export function goTo(path) {
  location.href = path;
}

export function reloadPage() {
  location.reload();
}

export function bindToast(toastEl, durationMs = 2400) {
  let timer = null;
  return (message) => {
    if (!toastEl) return;
    clearTimeout(timer);
    toastEl.textContent = message;
    toastEl.classList.remove("hidden");
    timer = setTimeout(() => toastEl.classList.add("hidden"), durationMs);
  };
}

export function bindModalDismiss(modal, onClose) {
  modal?.addEventListener("click", (event) => {
    if (event.target === modal) onClose();
  });
}

export function bindModalButtons({ cancelBtn, closeBtn, onClose }) {
  cancelBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    onClose();
  });
  closeBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    onClose();
  });
}

export function emitAppEvent(name, detail = {}) {
  document.dispatchEvent(new CustomEvent(name, { detail, bubbles: true }));
}

export function onAppEvent(name, handler) {
  document.addEventListener(name, (event) => handler(event.detail ?? {}));
}

export const APP_EVENTS = {
  SHARE_MODAL_OPEN: "cc-share-modal:open",
  AULA_MODAL_OPEN: "ca-aula-modal:open",
};

export function createCmrToast() {
  let hideTimer = null;
  return (message) => {
    let toast = document.getElementById("cmr-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "cmr-toast";
      toast.className = "cmr-toast";
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => toast.classList.remove("is-visible"), 2800);
  };
}

export function getJsPdfConstructor() {
  const lib = globalThis.jspdf;
  return lib?.jsPDF ?? null;
}
