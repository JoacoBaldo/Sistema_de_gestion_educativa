import { requestJson } from "./common/http.js";
import { authHeaders, getAuthToken } from "./common/auth.js";
import {
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  getQueryParam,
  reloadPage,
} from "./common/ui.js";

const EVALUATION_TYPE_LABELS = {
  parcial: "Parcial",
  tp: "TP",
  parcialito: "Parcialito",
  recuperatorio: "Recuperatorio",
};

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("ev-evaluation-modal");
  const form = document.getElementById("ev-evaluation-form");
  const toast = document.getElementById("ev-evaluation-toast");
  const grid = document.getElementById("ev-grid");
  const modalTitle = document.getElementById("ev-modal-title");
  const saveBtn = document.getElementById("ev-evaluation-save-btn");

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

  function getCardClassroom(card) {
    const code = card.querySelector(".ev-card__code");
    if (code) return code.textContent.trim();
    return card.dataset.classroom || "";
  }

  function setCardClassroom(card, value) {
    const code = card.querySelector(".ev-card__code");
    if (code) code.textContent = value;
    card.dataset.classroom = value;
  }

  function applyEvaluationToCard(card, { nombre, tipo, classroom, fecha, individual }) {
    card.dataset.nombre = nombre;
    card.dataset.type = tipo;
    card.dataset.classroom = classroom;
    card.dataset.date = fecha;
    card.dataset.individual = individual ? "true" : "false";

    const title = card.querySelector(".ev-card__title");
    if (title) title.textContent = nombre;
    setCardClassroom(card, classroom);

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
    classroomInput.value = getCardClassroom(card);
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
    const individual = individualInput.checked;

    if (!nombre || !tipo) {
      showToast("Completa nombre y tipo antes de guardar.");
      return;
    }

    const payload = { nombre, tipo, classroom, fecha, individual };
    const cardData = { nombre, tipo, classroom, fecha, individual };

    if (!getAuthToken()) {
      if (currentEvaluationCard) {
        applyEvaluationToCard(currentEvaluationCard, cardData);
        showToast("Evaluación actualizada.");
      } else {
        showToast("Evaluación creada correctamente.");
      }
      setTimeout(closeModal, 900);
      return;
    }

    try {
      if (currentEvaluationCard) {
        const evaluationId = currentEvaluationCard.dataset.id;
        const response = await requestJson(`/api/evaluations/${encodeURIComponent(evaluationId)}`, {
          method: "PUT",
          headers: authHeaders(),
          body: payload,
        });
        if (!response.ok) throw new Error("Error en la actualización");

        applyEvaluationToCard(currentEvaluationCard, cardData);
        showToast("Evaluación guardada correctamente.");
        setTimeout(closeModal, 900);
      } else {
        const response = await requestJson("/api/evaluations", {
          method: "POST",
          headers: authHeaders(),
          body: payload,
        });
        if (!response.ok) throw new Error("Error al crear la evaluación");

        showToast("Evaluación creada correctamente.");
        setTimeout(() => {
          closeModal();
          reloadPage();
        }, 900);
      }
    } catch (error) {
      console.error(error);
      showToast("No se pudo guardar. Intenta nuevamente.");
    }
  });
});
