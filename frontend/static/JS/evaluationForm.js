import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import { authHeaders, getAuthToken, requireAuth } from "./common/auth.js";
import {
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  escapeHtml,
  getQueryParam,
} from "./common/ui.js";

const EVALUATION_TYPE_LABELS = {
  parcial: "Parcial",
  tp: "TP",
  parcialito: "Parcialito",
  recuperatorio: "Recuperatorio",
};

const TYPE_MAP = {
  parcial: 1,
  tp: 2,
  parcialito: 4,
  recuperatorio: 3,
};

const AULAS_VALIDAS = ["Aula 101", "Aula 102", "Aula 103"];

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("ev-evaluation-modal");
  const form = document.getElementById("ev-evaluation-form");
  const toast = document.getElementById("ev-evaluation-toast");
  const grid = document.getElementById("ev-grid");
  const emptyState = document.getElementById("ev-empty");
  const modalTitle = document.getElementById("ev-modal-title");
  const saveBtn = document.getElementById("ev-evaluation-save-btn");
  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id");

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
    if (modalTitle) modalTitle.textContent = "Nueva Evaluación";
    if (saveBtn) saveBtn.textContent = "Guardar";
  }

  function appendEvaluationCard({ nombre, tipo }) {
    if (!grid) return;
    const id = `ev-${Date.now()}`;
    const cardHtml = `
      <article class="ev-card" data-id="${escapeHtml(id)}" data-type="${escapeHtml(tipo)}" data-nombre="${escapeHtml(nombre)}">
        <div class="ev-card__top">
          <span class="ev-badge ev-badge--${escapeHtml(tipo)}">${escapeHtml(EVALUATION_TYPE_LABELS[tipo] || tipo)}</span>
        </div>
        <div class="ev-card__body">
          <h2 class="ev-card__title">${escapeHtml(nombre)}</h2>
        </div>
      </article>`;
    grid.insertAdjacentHTML("afterbegin", cardHtml);
    if (emptyState) emptyState.hidden = true;
  }

  newBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    resetForm();
    openModal();
  });

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const nombre = nameInput.value.trim();
    const tipoString = typeSelect.value;
    const individual = individualInput.checked ? 1 : 0;

    if (!nombre || !tipoString) {
      showToast("Completa nombre y tipo antes de guardar.");
      return;
    }

    if (saveBtn) {
      saveBtn.textContent = "Guardando...";
      saveBtn.disabled = true;
    }

    // --- INTEGRACIÓN AJAX (CERO FETCH) ---
    const payload = {
      name: nombre,
      evaluation_type_id: TYPE_MAP[tipoString] || 1,
      individual: individual,
      referenced_eval_id: null
    };

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `/api/v1/classroom/${encodeURIComponent(classroomId)}/evaluaciones`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));

    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (saveBtn) {
          saveBtn.textContent = "Guardar";
          saveBtn.disabled = false;
        }

        if (xhr.status >= 200 && xhr.status < 300) {
          showToast("Evaluación creada correctamente.");
          appendEvaluationCard({ nombre, tipo: tipoString });
          setTimeout(closeModal, 900);
          resetForm();
        } else {
          let errorMsg = "Error al crear la evaluación.";
          try {
            const res = JSON.parse(xhr.responseText);
            if (res.error) errorMsg = res.error;
          } catch (e) { }
          showToast(errorMsg);
        }
      }
    };
    xhr.send(JSON.stringify(payload));
  });
});