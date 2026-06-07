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
    if (modalTitle) modalTitle.textContent = "Nueva Evaluaci?n";
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

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const nombre = nameInput?.value.trim();
    const tipo = typeSelect?.value;
    
    if (!nombre || !tipo) {
      showToast("Completa nombre y tipo antes de guardar.");
      return;
    }

    const payload = {
      name: nombre,
      evaluation_type_id: parseInt(tipo, 10),
      individual: individualInput?.checked ? 1 : 0
    };

    const classroomId = getQueryParam("classroom_id") || "1"; 

    try {
      const response = await fetch(`/api/v1/classroom/${classroomId}/evaluaciones`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        showToast(data.error || "Ocurrió un error al guardar.");
      } else {
        showToast("Evaluación guardada con éxito.");
        closeModal();
        window.location.reload(); 
      }
    } catch (error) {
      console.error(error);
      showToast("Error de conexión con el servidor.");
    }
  });
});
