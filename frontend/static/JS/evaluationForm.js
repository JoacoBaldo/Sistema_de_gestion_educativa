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
  const dateInput = document.getElementById("ev-evaluation-date");
  const classroomInput = document.getElementById("ev-evaluation-classroom");
  const individualInput = document.getElementById("ev-evaluation-individual");
  const newBtn = document.getElementById("ev-new-btn");
  const cancelBtn = document.getElementById("ev-evaluation-cancel-btn");
  const closeBtn = document.getElementById("ev-evaluation-close");

  if (!modal || !form) return;

  let currentEvaluationCard = null;
  const showToast = bindToast(toast);

  function openModal() {
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
    currentEvaluationCard = null;
  }

  function resetForm() {
    form.reset();
    if (typeSelect) typeSelect.value = "";
    if (modalTitle) modalTitle.textContent = "Nueva Evaluación";
    if (saveBtn) saveBtn.textContent = "Guardar";
  }

  function resolveAulas(raw) {
    const trimmed = (raw || "").trim();
    if (AULAS_VALIDAS.includes(trimmed)) return [trimmed];
    return [AULAS_VALIDAS[0]];
  }

  function appendEvaluationCard({ nombre, tipo, fecha, aula }) {
    if (!grid) return;
    const id = `ev-${Date.now()}`;
    const dateLabel = fecha
      ? new Date(fecha + "T12:00:00").toLocaleDateString("es-AR")
      : "—";
    const cardHtml = `
      <article class="ev-card" data-id="${escapeHtml(id)}" data-type="${escapeHtml(tipo)}"
        data-date="${escapeHtml(fecha || "")}" data-nombre="${escapeHtml(nombre)}"
        data-classroom="${escapeHtml(aula)}" data-individual="false">
        <div class="ev-card__top">
          <span class="ev-badge ev-badge--${escapeHtml(tipo)}">${escapeHtml(EVALUATION_TYPE_LABELS[tipo] || tipo)}</span>
          <time class="ev-card__date">${escapeHtml(dateLabel)}</time>
        </div>
        <div class="ev-card__body">
          <h2 class="ev-card__title">${escapeHtml(nombre)}</h2>
          <p class="ev-card__code">${escapeHtml(aula)}</p>
        </div>
        <footer class="ev-card__footer">
          <p class="ev-card__progress">Notas cargadas: <strong>—</strong></p>
        </footer>
      </article>`;
    grid.insertAdjacentHTML("afterbegin", cardHtml);
    if (emptyState) emptyState.hidden = true;
  }

  function applyEvaluationToCard(card, { nombre, tipo, classroom, fecha }) {
    card.dataset.nombre = nombre;
    card.dataset.type = tipo;
    card.dataset.classroom = classroom;
    card.dataset.date = fecha;

    const title = card.querySelector(".ev-card__title");
    if (title) title.textContent = nombre;
    const code = card.querySelector(".ev-card__code");
    if (code) code.textContent = classroom;

    const badge = card.querySelector(".ev-badge");
    if (badge) {
      badge.textContent = EVALUATION_TYPE_LABELS[tipo] || badge.textContent;
      badge.className = `ev-badge ev-badge--${tipo}`;
    }
  }

  function populateFromCard(card) {
    currentEvaluationCard = card;
    if (modalTitle) modalTitle.textContent = "Editar Evaluación";
    if (saveBtn) saveBtn.textContent = "Guardar cambios";
    nameInput.value = card.dataset.nombre || "";
    typeSelect.value = card.dataset.type || "";
    classroomInput.value = card.dataset.classroom || "";
    dateInput.value = card.dataset.date || "";
    individualInput.checked = card.dataset.individual === "true";
    openModal();
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

  grid?.addEventListener("click", (event) => {
    const editLink = event.target.closest("a[aria-label='Editar evaluación']");
    if (!editLink) return;
    event.preventDefault();
    const card = editLink.closest(".ev-card");
    if (card) populateFromCard(card);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const nombre = nameInput.value.trim();
    const tipo = typeSelect.value;
    const classroom = classroomInput.value.trim();
    const fecha = dateInput.value;
    const aulas = resolveAulas(classroom);

    if (!nombre || !tipo) {
      showToast("Completa nombre y tipo antes de guardar.");
      return;
    }
    if (!fecha) {
      showToast("Indica la fecha de la evaluación (YYYY-MM-DD).");
      return;
    }
    if (!getAuthToken()) {
      requireAuth();
      return;
    }

    if (currentEvaluationCard) {
      applyEvaluationToCard(currentEvaluationCard, {
        nombre,
        tipo,
        classroom: aulas[0],
        fecha,
      });
      showToast("Cambios guardados localmente (sin endpoint de actualización).");
      setTimeout(closeModal, 900);
      return;
    }

    try {
      const response = await requestJson(
        apiUrl(`/api/v1/classroom/${encodeURIComponent(classroomId)}/evaluaciones`),
        {
          method: "POST",
          headers: authHeaders(),
          body: { fecha, aulas },
        }
      );
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "Error al crear la evaluación"));
      }

      appendEvaluationCard({ nombre, tipo, fecha, aula: aulas[0] });
      showToast(body.message || "Evaluación creada correctamente.");
      setTimeout(closeModal, 900);
      resetForm();
    } catch (error) {
      console.error(error);
      showToast(error.message || "No se pudo guardar. Intenta nuevamente.");
    }
  });
});
