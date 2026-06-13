import { bindModalButtons, bindModalDismiss, bindToast } from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("st-student-modal");
  const form = document.getElementById("formEstudiante");
  const toast = document.getElementById("st-student-toast");
  const newBtn = document.getElementById("st-add-btn");
  const cancelBtn = document.getElementById("st-student-cancel-btn");
  const closeBtn = document.getElementById("st-student-close");

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
  }

  newBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    resetForm();
    openModal();
  });

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const studentIdRaw = document.getElementById("st_student_id")?.value?.trim();
    const email = document.getElementById("st_email")?.value?.trim();

    if (!studentIdRaw && !email) {
      showToast("Debes completar el ID de usuario o el email para agregar un estudiante existente.");
      return;
    }

    if (studentIdRaw && isNaN(studentIdRaw)) {
      showToast("El ID de usuario debe ser un número.");
      return;
    }

    try {
      const formData = new FormData(form);
      const resp = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "Accept": "application/json",
        },
      });

      if (resp.headers.get("Content-Type")?.includes("application/json")) {
        const body = await resp.json();
        if (resp.ok && body && body.success) {
          showToast("Estudiante agregado con éxito.");
          closeModal();
          setTimeout(() => location.reload(), 700);
          return;
        }
        const errorMsg = body?.error || "Error al agregar estudiante.";
        showToast(errorMsg);
        return;
      }

      if (resp.ok) {
        closeModal();
        setTimeout(() => location.reload(), 400);
        return;
      }

      showToast("Error al agregar estudiante.");
    } catch (err) {
      console.error(err);
      showToast("Error de conexión al agregar el estudiante.");
    }
  });
});