import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import { authHeaders, requireAuth } from "./common/auth.js";
import {
  APP_EVENTS,
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  getQueryParam,
  goTo,
  onAppEvent,
  reloadPage,
} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("ca-aula-modal");
  const form = document.getElementById("formAula");
  const toast = document.getElementById("ca-aula-toast");
  const horariosList = document.getElementById("horarios-list");
  const btnAddHorario = document.getElementById("btn-add-horario");
  const btnGuardar = document.getElementById("btnGuardar");
  const cancelBtn = document.getElementById("ca-aula-cancel-btn");
  const closeBtn = document.getElementById("ca-aula-close");
  const createBtn = document.getElementById("btnCrearAula");

  if (!modal || !form) return;

  const showToast = bindToast(toast);

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
    if (!requireAuth()) return;
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

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!requireAuth()) return;

    const name = document.getElementById("nombre")?.value.trim() ?? "";
    const department = document.getElementById("catedra")?.value.trim() ?? "";
    const university = document.getElementById("universidad")?.value.trim() ?? "";

    const fechaInicio = document.getElementById("fecha_inicio")?.value ?? "";
    const fechaFin = document.getElementById("fecha_fin")?.value ?? "";
    const horarioRows = form.querySelectorAll(".glass-list-row--schedule");

    if (!name || !department || !university) {
      showToast("Completa nombre, cátedra y universidad.");
      return;
    }

    if (fechaInicio && fechaFin && fechaInicio > fechaFin) {
      showToast("La fecha de inicio debe ser anterior a la fecha de fin.");
      return;
    }

    for (const row of horarioRows) {
      const hInicio = row.querySelector('input[name="h_inicio"]')?.value ?? "";
      const hFin = row.querySelector('input[name="h_fin"]')?.value ?? "";
      if (hInicio && hFin && hInicio >= hFin) {
        showToast("La hora de inicio debe ser anterior a la de fin.");
        return;
      }
    }

    if (btnGuardar) {
      btnGuardar.textContent = "Guardando...";
      btnGuardar.disabled = true;
    }

    try {
      const response = await requestJson(apiUrl("/api/v1/classrooms"), {
        method: "POST",
        headers: authHeaders(),
        body: { name, department, university },
      });
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "Error al crear el aula"));
      }

      showToast("Aula creada correctamente.");
      setTimeout(() => {
        closeModal();
        reloadPage();
      }, 600);
    } catch (error) {
      console.error(error);
      showToast(error.message || "No se pudo crear el aula. Intenta nuevamente.");
      if (btnGuardar) {
        btnGuardar.textContent = "Crear Aula";
        btnGuardar.disabled = false;
      }
    }
  });

  onAppEvent(APP_EVENTS.AULA_MODAL_OPEN, openFromQuery);

  if (getQueryParam("accion") === "crear") {
    openFromQuery();
  }
});
