import {
    bindModalButtons,
    bindModalDismiss,
    bindToast,
  } from "./common/ui.js";

  document.addEventListener("DOMContentLoaded", () => {
    // ── Crear estudiante ──────────────────────────────────────────────────────
    const modal     = document.getElementById("st-student-modal");
    const form      = document.getElementById("formEstudiante");
    const toast     = document.getElementById("st-student-toast");
    const newBtn    = document.getElementById("st-add-btn");
    const cancelBtn = document.getElementById("st-student-cancel-btn");
    const closeBtn  = document.getElementById("st-student-close");

    if (modal && form) {
      const showToast = bindToast(toast);

      const openModal  = () => modal.classList.remove("hidden");
      const closeModal = () => modal.classList.add("hidden");

      newBtn?.addEventListener("click", (e) => { e.preventDefault(); form.reset(); openModal(); });
      bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
      bindModalDismiss(modal, closeModal);

      form.addEventListener("submit", (e) => {
        const nombre  = document.getElementById("st_nombre")?.value.trim();
        const apellido = document.getElementById("st_apellido")?.value.trim();
        const padron  = document.getElementById("st_padron")?.value.trim();
        const email   = document.getElementById("st_email")?.value.trim();
        const career  = document.getElementById("st_career")?.value.trim();
        if (!nombre || !apellido || !padron || !email || !career) {
          showToast("Todos los campos con asterisco (*) son obligatorios.");
          e.preventDefault();
        }
      });
    }

    // ── Editar estudiante ─────────────────────────────────────────────────────
    const editModal     = document.getElementById("st-edit-modal");
    const editForm      = document.getElementById("formEditarEstudiante");
    const editToast     = document.getElementById("st-edit-toast");
    const editCancelBtn = document.getElementById("st-edit-cancel-btn");
    const editCloseBtn  = document.getElementById("st-edit-close");

    if (!editModal || !editForm) return;

    const showEditToast = bindToast(editToast);
    const openEditModal  = () => editModal.classList.remove("hidden");
    const closeEditModal = () => editModal.classList.add("hidden");

    bindModalButtons({ cancelBtn: editCancelBtn, closeBtn: editCloseBtn, onClose: closeEditModal });
    bindModalDismiss(editModal, closeEditModal);

    document.getElementById("st-tbody")?.addEventListener("click", (e) => {
      const btn = e.target.closest(".js-edit-student");
      if (!btn) return;

      const row      = btn.closest("tr");
      document.getElementById("st_edit_nombre").value   = row.dataset.nombre || "";
      document.getElementById("st_edit_apellido").value = row.dataset.apellido || "";
      document.getElementById("st_edit_email").value    = row.dataset.email || "";
      document.getElementById("st_edit_padron").value   = row.dataset.document || "";
      document.getElementById("st_edit_career").value   = row.dataset.career || "";
      document.getElementById("st_edit_status").value   = row.dataset.status || "";
      document.getElementById("st_edit_user_id").value  = row.dataset.userId || "";

      // construye la action con el classroom_id embebido en la URL actual
      const classroomId = window.location.pathname.split("/")[2];
      editForm.action = `/aulas/${classroomId}/gestionar/estudiantes/editar`;

      openEditModal();
    });

    editForm.addEventListener("submit", (e) => {
      const nombre   = document.getElementById("st_edit_nombre")?.value.trim();
      const apellido = document.getElementById("st_edit_apellido")?.value.trim();
      const padron   = document.getElementById("st_edit_padron")?.value.trim();
      const email    = document.getElementById("st_edit_email")?.value.trim();
      const career   = document.getElementById("st_edit_career")?.value.trim();
      const status   = document.getElementById("st_edit_status")?.value.trim();
      if (!nombre || !apellido || !padron || !email || !career || !status) {
        showEditToast("Todos los campos con asterisco (*) son obligatorios.");
        e.preventDefault();
      }
    });
  });
