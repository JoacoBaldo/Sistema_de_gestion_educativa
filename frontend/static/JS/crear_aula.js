import {
  APP_EVENTS,
  bindModalButtons,
  bindModalDismiss,
  getQueryParam,
  onAppEvent,
} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("ca-aula-modal");
  const form = document.getElementById("formAula");
  const horariosList = document.getElementById("horarios-list");
  const btnAddHorario = document.getElementById("btn-add-horario");
  const cancelBtn = document.getElementById("ca-aula-cancel-btn");
  const closeBtn = document.getElementById("ca-aula-close");
  const createBtn = document.getElementById("btnCrearAula");
  const periodSlider = document.getElementById("ca-period-slider");
  const periodHidden = document.getElementById("ca-academic-period-id");
  const toast = document.getElementById("ca-aula-toast");

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

  function selectPeriodPill(pill) {
    if (!pill || !periodSlider) return;
    const pills = periodSlider.querySelectorAll(".glass-period-pill");
    pills.forEach((p) => {
      p.classList.remove("is-active");
      p.setAttribute("aria-checked", "false");
    });
    pill.classList.add("is-active");
    pill.setAttribute("aria-checked", "true");
    if (periodHidden) {
      periodHidden.value = pill.dataset.periodId || "";
    }
  }

  function resetPeriodSlider() {
    if (!periodSlider) return;
    const firstPill = periodSlider.querySelector(".glass-period-pill");
    if (firstPill) selectPeriodPill(firstPill);
  }

  function resetForm() {
    form.reset();
    if (horariosList) {
      horariosList.innerHTML = "";
      horariosList.appendChild(createHorarioRow());
    }
    resetPeriodSlider();
    if (toast) toast.classList.add("hidden");
  }

  function openFromQuery() {
    resetForm();
    openModal();
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");
  }

  btnAddHorario?.addEventListener("click", () => {
    horariosList?.appendChild(createHorarioRow());
  });

  periodSlider?.addEventListener("click", (event) => {
    const pill = event.target.closest(".glass-period-pill");
    if (pill) selectPeriodPill(pill);
  });

  form.addEventListener("submit", (event) => {
    if (!periodHidden || !periodHidden.value) {
      event.preventDefault();
      showToast("Seleccioná un período académico.");
    }
  });

  createBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    openFromQuery();
  });

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  onAppEvent(APP_EVENTS.AULA_MODAL_OPEN, openFromQuery);
  if (getQueryParam("accion") === "crear") {
    openFromQuery();
  }
});
