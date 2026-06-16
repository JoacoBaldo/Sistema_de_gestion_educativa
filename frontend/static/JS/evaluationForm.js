import {
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  getQueryParam,
} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("ev-evaluation-modal");
  const form = document.getElementById("ev-evaluation-form");
  const toast = document.getElementById("ev-evaluation-toast");
  const modalTitle = document.getElementById("ev-modal-title");
  const saveBtn = document.getElementById("ev-evaluation-save-btn");
  const nameInput = document.getElementById("ev-evaluation-name");
  const typeSelect = document.getElementById("ev-evaluation-type");
  const individualInput = document.getElementById("ev-evaluation-individual");
  const newBtn = document.getElementById("ev-new-btn");
  const cancelBtn = document.getElementById("ev-evaluation-cancel-btn");
  const closeBtn = document.getElementById("ev-evaluation-close");

  if (!modal || !form) return;

  const showToast = bindToast(toast);

  function openModal() {
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function resetForm() {
    form.reset();
    if (typeSelect) typeSelect.value = "";
    if (individualInput) individualInput.checked = false;

    // Solución al error de codificación usando la secuencia de escape unicode para la ó (\u00f3)
    if (modalTitle) modalTitle.textContent = "Nueva Evaluaci\u00f3n";
    if (saveBtn) saveBtn.textContent = "Guardar";
  }

  newBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    resetForm();
    openModal();
  });

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  if (getQueryParam("vista") === "evaluations" && getQueryParam("accion") === "nueva") {
    resetForm();
    openModal();
  }

  form.addEventListener("submit", (event) => {
    const nombre = nameInput?.value.trim();
    const tipo = typeSelect?.value;

    if (!nombre || !tipo) {
      event.preventDefault();
      showToast("Completa nombre y tipo antes de guardar.");
      return;
    }
  });
});