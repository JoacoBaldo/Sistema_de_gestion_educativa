document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("ev-evaluation-modal");
  const form = document.getElementById("ev-evaluation-form");
  const toast = document.getElementById("ev-evaluation-toast");
  const grid = document.getElementById("ev-grid");

  const nameInput = document.getElementById("ev-evaluation-name");
  const typeSelect = document.getElementById("ev-evaluation-type");
  const classroomInput = document.getElementById("ev-evaluation-classroom");
  const individualInput = document.getElementById("ev-evaluation-individual");
  const cancelBtn = document.getElementById("ev-evaluation-cancel-btn");

  let currentEvaluationCard = null;

  function hasToken() {
    try {
      return !!localStorage.getItem("token");
    } catch (e) {
      return false;
    }
  }

  function openModal() {
    if (!hasToken()) {
      window.location.href = "/auth";
      return;
    }
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
    currentEvaluationCard = null;
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2400);
  }

  function getCardClassroom(card) {
    const code = card.querySelector(".ev-card__code");
    if (code) return code.textContent.trim();
    return card.dataset.classroom || "";
  }

  function setCardClassroom(card, value) {
    const code = card.querySelector(".ev-card__code");
    if (code) {
      code.textContent = value;
    }
    card.dataset.classroom = value;
  }

  function populateFromCard(card) {
    const nombre = card.dataset.nombre || "";
    const tipo = card.dataset.type || "";
    const classroom = getCardClassroom(card);
    const individual = card.dataset.individual === "true";

    currentEvaluationCard = card;
    nameInput.value = nombre;
    typeSelect.value = tipo;
    classroomInput.value = classroom;
    individualInput.checked = individual;
    openModal();
  }

  function validateName(name) {
    return name.trim().length > 0;
  }

  if (grid) {
    grid.addEventListener("click", (event) => {
      const editLink = event.target.closest("a[aria-label='Editar evaluación']");
      if (editLink) {
        event.preventDefault();
        const card = editLink.closest(".ev-card");
        if (card) populateFromCard(card);
      }
    });
  }

  cancelBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const nombre = nameInput.value.trim();
    const tipo = typeSelect.value;
    const classroom = classroomInput.value.trim();
    const individual = individualInput.checked;

    if (!nombre || !tipo || !classroom) {
      showToast("Completa todos los campos obligatorios antes de guardar.");
      return;
    }

    if (!validateName(nombre)) {
      showToast("El nombre de la evaluación no puede estar vacío.");
      nameInput.focus();
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/auth";
      return;
    }

    const evaluationId = currentEvaluationCard?.dataset.id;
    if (!evaluationId) {
      showToast("No se pudo identificar la evaluación.");
      return;
    }

    const payload = {
      nombre,
      tipo,
      classroom,
      individual,
    };

    try {
      const response = await fetch(`/api/evaluations/${encodeURIComponent(evaluationId)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Error en la actualización");
      }

      if (currentEvaluationCard) {
        currentEvaluationCard.dataset.nombre = nombre;
        currentEvaluationCard.dataset.type = tipo;
        currentEvaluationCard.dataset.classroom = classroom;
        currentEvaluationCard.dataset.individual = individual ? "true" : "false";

        const title = currentEvaluationCard.querySelector(".ev-card__title");
        if (title) title.textContent = nombre;

        const code = currentEvaluationCard.querySelector(".ev-card__code");
        if (code) code.textContent = classroom;

        const badge = currentEvaluationCard.querySelector(".ev-badge");
        if (badge) {
          badge.textContent = {
            parcial: "Parcial",
            tp: "TP",
            parcialito: "Parcialito",
            recuperatorio: "Recuperatorio",
          }[tipo] || badge.textContent;
          badge.className = `ev-badge ev-badge--${tipo}`;
        }
      }

      showToast("Evaluación guardada correctamente.");
      setTimeout(closeModal, 900);
    } catch (error) {
      console.error(error);
      showToast("No se pudo guardar. Intenta nuevamente.");
    }
  });
});
