import {
    bindModalButtons,
    bindModalDismiss,
    bindToast,
  } from "./common/ui.js";
  
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
  
    // Configurar cierres automáticos (botones y clic afuera)
    bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
    bindModalDismiss(modal, closeModal);
  
    // Validación antes de enviar
    form.addEventListener("submit", (event) => {
      const nombre = document.getElementById("st_nombre")?.value.trim();
      const apellido = document.getElementById("st_apellido")?.value.trim();
      const padron = document.getElementById("st_padron")?.value.trim();
      const email = document.getElementById("st_email")?.value.trim();
      const career = document.getElementById("st_career")?.value.trim();

      if (!nombre || !apellido || !padron || !email || !career) {
        showToast("Todos los campos con asterisco (*) son obligatorios.");
        event.preventDefault();
        return;
      }
    });
  });