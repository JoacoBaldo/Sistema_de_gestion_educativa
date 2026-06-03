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

  function openModal() {
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
    const fecha = card.dataset.date || "";

    currentEvaluationCard = card;
    if (modalTitle) modalTitle.textContent = "Editar Evaluación";
    if (saveBtn) saveBtn.textContent = "Guardar cambios";
    nameInput.value = nombre;
    typeSelect.value = tipo;
    classroomInput.value = classroom;
    dateInput.value = fecha;
    individualInput.checked = individual;
    openModal();
  }

  newBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    resetForm();
    openModal();
  });

  cancelBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });

  closeBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get("vista") === "evaluations" && params.get("accion") === "nueva") {
    resetForm();
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

    if (!validateName(nombre)) {
      showToast("El nombre de la evaluación no puede estar vacío.");
      nameInput.focus();
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      if (currentEvaluationCard) {
        currentEvaluationCard.dataset.nombre = nombre;
        currentEvaluationCard.dataset.type = tipo;
        currentEvaluationCard.dataset.classroom = classroom;
        currentEvaluationCard.dataset.date = fecha;
        currentEvaluationCard.dataset.individual = individual ? "true" : "false";

        const title = currentEvaluationCard.querySelector(".ev-card__title");
        if (title) title.textContent = nombre;
        setCardClassroom(currentEvaluationCard, classroom);

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

        showToast("Evaluación actualizada.");
        setTimeout(closeModal, 900);
        return;
      }

      showToast("Evaluación creada correctamente.");
      setTimeout(closeModal, 900);
      return;
    }

    const payload = {
      nombre,
      tipo,
      classroom,
      fecha,
      individual,
    };

    try {
      if (currentEvaluationCard) {
        const evaluationId = currentEvaluationCard.dataset.id;
        const response = await fetch(`/api/evaluations/${encodeURIComponent(evaluationId)}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Error en la actualización");

        currentEvaluationCard.dataset.nombre = nombre;
        currentEvaluationCard.dataset.type = tipo;
        currentEvaluationCard.dataset.classroom = classroom;
        currentEvaluationCard.dataset.date = fecha;
        currentEvaluationCard.dataset.individual = individual ? "true" : "false";

        const title = currentEvaluationCard.querySelector(".ev-card__title");
        if (title) title.textContent = nombre;
        setCardClassroom(currentEvaluationCard, classroom);

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

        showToast("Evaluación guardada correctamente.");
        setTimeout(closeModal, 900);
      } else {
        const response = await fetch("/api/evaluations", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Error al crear la evaluación");

        showToast("Evaluación creada correctamente.");
        setTimeout(() => {
          closeModal();
          window.location.reload();
        }, 900);
      }
    } catch (error) {
      console.error(error);
      showToast("No se pudo guardar. Intenta nuevamente.");
    }
  });
});
