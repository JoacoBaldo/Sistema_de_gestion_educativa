import {
  APP_EVENTS,
  bindModalButtons,
  bindModalDismiss,
  getQueryParam,
  onAppEvent,
} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("cc-share-modal");
  const form = document.getElementById("shareForm");
  const titleEl = document.getElementById("cc-modal-title");
  const classIdEl = document.getElementById("classId");
  const cancelBtn = document.getElementById("cc-share-cancel-btn");
  const closeBtn = document.getElementById("cc-share-close");
  const linkInput = document.getElementById("cc-share-link-input");
  const copyBtn = document.getElementById("cc-copy-btn");

  if (!modal || !form) return;

  function openModal(classId = "", className = "") {
    if (classIdEl) classIdEl.value = classId;
    if (titleEl) {
      titleEl.textContent = className ? `Compartir: ${className}` : "Compartir Clase";
    }
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  onAppEvent(APP_EVENTS.SHARE_MODAL_OPEN, ({ classId = "", className = "" } = {}) => {
    openModal(classId, className);
  });

  if (getQueryParam("accion") === "compartir") {
    const nombre = getQueryParam("nombre") || "";
    openModal(getQueryParam("id") || "", nombre ? decodeURIComponent(nombre) : "");
  }

  // Si hay enlace generado (post-redirect), reabrir el modal automáticamente
  if (linkInput) {
    openModal();
  }

  copyBtn?.addEventListener("click", () => {
    if (!linkInput?.value) return;
    navigator.clipboard.writeText(linkInput.value).then(() => {
      copyBtn.textContent = "✓ Copiado";
      setTimeout(() => (copyBtn.textContent = "Copiar"), 2000);
    });
  });
});
