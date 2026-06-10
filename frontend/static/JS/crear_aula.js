import {
  APP_EVENTS,
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  getQueryParam,
  onAppEvent,
} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("ca-aula-modal");
  const form = document.getElementById("formAula");
  const horariosList = document.getElementById("horarios-list");
  const fechaInicioInput = document.getElementById("fecha_inicio");
  const fechaFinInput = document.getElementById("fecha_fin");
  const btnAddHorario = document.getElementById("btn-add-horario");
  const cancelBtn = document.getElementById("ca-aula-cancel-btn");
  const closeBtn = document.getElementById("ca-aula-close");
  const createBtn = document.getElementById("btnCrearAula");
  const toast = document.getElementById("ca-aula-toast");
  const showToast = bindToast(toast);

  if (!modal || !form) return;

  function openModal() {
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function createHorarioRow() {
    const row = document.createElement("div");
    row.className = "glass-list-row--schedule";
    row.innerHTML = `
      <select name="dia" class="glass-input" required>
        <option value="Lunes">Lunes</option>
        <option value="Martes">Martes</option>
        <option value="Miércoles">Miércoles</option>
        <option value="Jueves">Jueves</option>
        <option value="Viernes">Viernes</option>
        <option value="Sábado">Sábado</option>
      </select>
      <input type="time" name="h_inicio" class="glass-input" value="10:00" required>
      <input type="time" name="h_fin" class="glass-input" value="12:00" required>
    `;
    return row;
  }

  function resetForm() {
    form.reset();
    if (!horariosList) return;
    horariosList.innerHTML = "";
    horariosList.appendChild(createHorarioRow());
  }

  function openFromQuery() {
    resetForm();
    openModal();
  }
  btnAddHorario?.addEventListener("click", () => {
    horariosList?.appendChild(createHorarioRow());
  });

  createBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    openFromQuery();
  });

  form.addEventListener("submit", (event) => {
    if (!validateForm()) {
      event.preventDefault();
    }
  });

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  onAppEvent(APP_EVENTS.AULA_MODAL_OPEN, openFromQuery);
  if (getQueryParam("accion") === "crear") {
    openFromQuery();
  }
});
