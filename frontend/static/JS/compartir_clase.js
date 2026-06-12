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
  const linkResult = document.getElementById("cc-share-link-result");

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

  function resetForm() {
    form.reset();
    if (classIdEl) classIdEl.value = "";
    if (titleEl) titleEl.textContent = "Compartir Clase";
  }

  function openShareModal({ classId = "", className = "" } = {}) {
    resetForm();
    openModal(classId, className);
  }

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  onAppEvent(APP_EVENTS.SHARE_MODAL_OPEN, openShareModal);

  if (getQueryParam("accion") === "compartir") {
    const nombre = getQueryParam("nombre") || "";
    openShareModal({
      classId: getQueryParam("id") || "",
      className: nombre ? decodeURIComponent(nombre) : "",
    });
  }

  if (linkResult && linkResult.textContent.trim()) {
    openModal();
  }
});
