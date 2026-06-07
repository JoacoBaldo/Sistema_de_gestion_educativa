import { bindToast } from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("st-student-modal");
  const form = document.getElementById("st-student-form");
  const toast = document.getElementById("st-student-toast");
  const cancelBtn = document.getElementById("st-student-cancel-btn");

  const showToast = bindToast(toast, 2500);

  function closeModal() {
    modal?.classList.add("hidden");
  }

  cancelBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    closeModal();
  });

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    showToast("Edición local sin endpoint PUT de alumnos.");
    setTimeout(closeModal, 800);
  });
});
