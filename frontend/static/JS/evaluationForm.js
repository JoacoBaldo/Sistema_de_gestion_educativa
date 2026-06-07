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

const EVALUATION_TYPE_IDS = {
  parcial: 1,
  tp: 2,
  recuperatorio: 3,
  parcialito: 4,
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
    if (individualInput) individualInput.checked = false;
    if (modalTitle) modalTitle.textContent = "Nueva Evaluación";
    if (saveBtn) saveBtn.textContent = "Guardar";
  }

  function typeIdForType(tipo) {
    return EVALUATION_TYPE_IDS[tipo] ?? null;
  }

  function appendEvaluationCard({ nombre, tipo, evaluationId, individual }) {
    if (!grid) return;
    const id = evaluationId ? `ev-${evaluationId}` : `ev-${Date.now()}`;
    const cardHtml = `
      <article class="ev-card" data-id="${escapeHtml(id)}" data-evaluation-id="${escapeHtml(
      evaluationId ?? ""
    )}" data-type="${escapeHtml(tipo)}"
        data-date="${escapeHtml(fecha || "")}" data-nombre="${escapeHtml(nombre)}"
        data-classroom="${escapeHtml(aula)}" data-individual="${escapeHtml(
      individual ? "true" : "false"
    )}">
        <div class="ev-card__top">
          <span class="ev-badge ev-badge--${escapeHtml(tipo)}">${escapeHtml(
      EVALUATION_TYPE_LABELS[tipo] || tipo
    )}</span>
          <time class="ev-card__date">${escapeHtml(dateLabel)}</time>
        </div>
        <div class="ev-card__body">
          <h2 class="ev-card__title">${escapeHtml(nombre)}</h2>
        </div>
        <footer class="ev-card__footer">
          <button type="button" class="ev-card__edit-btn" aria-label="Editar evaluación">Editar</button>
          <p class="ev-card__progress">Notas cargadas: <strong>—</strong></p>
        </footer>
      </article>`;
    grid.insertAdjacentHTML("afterbegin", cardHtml);
    if (emptyState) emptyState.hidden = true;
  }

  function applyEvaluationToCard(card, { nombre, tipo, classroom, fecha, individual }) {
    card.dataset.nombre = nombre;
    card.dataset.type = tipo;
    card.dataset.classroom = classroom;
    card.dataset.date = fecha;
    card.dataset.individual = individual ? "true" : "false";

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
    const editBtn = event.target.closest(".ev-card__edit-btn");
    if (!editBtn) return;
    event.preventDefault();
    const card = editBtn.closest(".ev-card");
    if (card) populateFromCard(card);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const nombre = nameInput.value.trim();
    const tipo = typeSelect.value;
    const classroom = classroomInput.value.trim();
    const fecha = dateInput.value;
    const aulas = resolveAulas(classroom);
    const individual = individualInput.checked ? 1 : 0;
    const evaluationTypeId = typeIdForType(tipo);

    if (!nombre || !tipoString) {
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
      const evaluationId = currentEvaluationCard.dataset.evaluationId;
      if (!evaluationId) {
        showToast("No se puede actualizar esta evaluación: falta el ID de backend.");
        return;
      }

      try {
        const response = await requestJson(
          apiUrl(`/api/v1/evaluaciones/${encodeURIComponent(evaluationId)}`),
          {
            method: "PATCH",
            headers: authHeaders(),
            body: {
              name: nombre,
              evaluation_type_id: evaluationTypeId,
              individual,
            },
          }
        );
        const body = response.json();
        if (!response.ok) {
          throw new Error(apiErrorMessage(body, "Error al actualizar la evaluación"));
        }

        applyEvaluationToCard(currentEvaluationCard, {
          nombre,
          tipo,
          classroom: aulas[0],
          fecha,
          individual: individual === 1,
        });

        showToast(body.message || "Evaluación actualizada correctamente.");
        setTimeout(closeModal, 900);
      } catch (error) {
        console.error(error);
        showToast(error.message || "No se pudo actualizar. Intenta nuevamente.");
      }

      return;
    }

    if (!classroomId) {
      showToast("No se encontró el aula para crear la evaluación.");
      return;
    }

    try {
      const response = await requestJson(
        apiUrl(`/api/v1/classroom/${encodeURIComponent(classroomId)}/evaluaciones`),
        {
          method: "POST",
          headers: authHeaders(),
          body: {
            name: nombre,
            evaluation_type_id: evaluationTypeId,
            individual,
          },
        }
      );
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "Error al crear la evaluación"));
      }

      appendEvaluationCard({
        nombre,
        tipo,
        fecha,
        aula: aulas[0],
        evaluationId: body.id,
        individual: individual === 1,
      });
      showToast(body.message || "Evaluación creada correctamente.");
      setTimeout(closeModal, 900);
      resetForm();
    } catch (error) {
      console.error(error);
      showToast(error.message || "No se pudo guardar. Intenta nuevamente.");
    }
  });
});