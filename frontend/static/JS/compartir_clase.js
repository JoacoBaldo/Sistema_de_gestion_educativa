import { submitForm } from "./common/http.js";
import {
  APP_EVENTS,
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  getQueryParam,
  onAppEvent,
} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("cc-share-modal");
  const form = document.getElementById("shareForm");
  const toast = document.getElementById("cc-share-toast");
  const titleEl = document.getElementById("cc-modal-title");
  const classIdEl = document.getElementById("classId");
  const cancelBtn = document.getElementById("cc-share-cancel-btn");
  const closeBtn = document.getElementById("cc-share-close");
  const btnCompartir = document.getElementById("btnCompartir");

  if (!modal || !form) return;

  const showToast = bindToast(toast);

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

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("shareEmail")?.value.trim() ?? "";
    if (!email) {
      showToast("Ingresa un email válido.");
      return;
    }

    if (btnCompartir) {
      btnCompartir.disabled = true;
      btnCompartir.textContent = "Enviando...";
    }

    try {
      const response = await submitForm(form.action, new FormData(form));
      if (!response.ok) throw new Error("Error al compartir");

      showToast("Acceso concedido correctamente.");
      setTimeout(() => {
        closeModal();
        resetForm();
        if (btnCompartir) {
          btnCompartir.disabled = false;
          btnCompartir.textContent = "Conceder Acceso";
        }
      }, 900);
    } catch (error) {
      console.error(error);
      showToast("No se pudo compartir. Intenta nuevamente.");
      if (btnCompartir) {
        btnCompartir.disabled = false;
        btnCompartir.textContent = "Conceder Acceso";
      }
    }
  });

  onAppEvent(APP_EVENTS.SHARE_MODAL_OPEN, openShareModal);

  if (getQueryParam("accion") === "compartir") {
    const nombre = getQueryParam("nombre") || "";
    openShareModal({
      classId: getQueryParam("id") || "",
      className: nombre ? decodeURIComponent(nombre) : "",
    });
  }
});
