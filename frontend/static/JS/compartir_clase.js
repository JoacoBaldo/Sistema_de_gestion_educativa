import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import { authHeaders, requireAuth } from "./common/auth.js";
import {
  APP_EVENTS,
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  getQueryParam,
  onAppEvent,
} from "./common/ui.js";

const ROLE_MAP = {
  Lector: 2,
  Editor: 1,
};

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("cc-share-modal");
  const form = document.getElementById("shareForm");
  const toast = document.getElementById("cc-share-toast");
  const titleEl = document.getElementById("cc-modal-title");
  const classIdEl = document.getElementById("classId");
  const cancelBtn = document.getElementById("cc-share-cancel-btn");
  const closeBtn = document.getElementById("cc-share-close");
  const btnCompartir = document.getElementById("btnCompartir");
  const linkResult = document.getElementById("cc-share-link-result");

  if (!modal || !form) return;

  const showToast = bindToast(toast);

  function openModal(classId = "", className = "") {
    if (classIdEl) classIdEl.value = classId;
    if (titleEl) {
      titleEl.textContent = className ? `Compartir: ${className}` : "Compartir Clase";
    }
    if (linkResult) {
      linkResult.hidden = true;
      linkResult.textContent = "";
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
    if (linkResult) {
      linkResult.hidden = true;
      linkResult.textContent = "";
    }
  }

  function openShareModal({ classId = "", className = "" } = {}) {
    if (!requireAuth()) return;
    resetForm();
    openModal(classId, className);
  }

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireAuth()) return;

    const classroomId = classIdEl?.value.trim() ?? "";
    const rolLabel = document.getElementById("shareRol")?.value ?? "Editor";
    const roleId = ROLE_MAP[rolLabel] ?? 1;

    if (!classroomId) {
      showToast("Selecciona un aula desde la grilla.");
      return;
    }

    if (btnCompartir) {
      btnCompartir.disabled = true;
      btnCompartir.textContent = "Generando enlace...";
    }

    try {
      const response = await requestJson(
        apiUrl(`/api/v1/classrooms/${encodeURIComponent(classroomId)}/link?role_id=${roleId}`),
        { headers: authHeaders() }
      );
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "No se pudo generar el enlace"));
      }

      const joinLink = body.join_link || "";
      if (linkResult) {
        linkResult.hidden = false;
        linkResult.textContent = joinLink;
      }
      try {
        await navigator.clipboard.writeText(joinLink);
        showToast("Enlace copiado al portapapeles.");
      } catch {
        showToast("Enlace generado. Copialo desde el cuadro de texto.");
      }
    } catch (error) {
      console.error(error);
      showToast(error.message || "No se pudo compartir. Intenta nuevamente.");
    } finally {
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
