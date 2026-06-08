import { requireAuth } from "./common/auth.js";

document.addEventListener("DOMContentLoaded", () => {
  requireAuth();

  const grid = document.getElementById("ev-grid");
  const emptyState = document.getElementById("ev-empty");
  const searchInput = document.getElementById("ev-search-input");
  const typeFilter = document.getElementById("ev-type-filter");
  const dateSort = document.getElementById("ev-date-sort");

  if (grid && !grid.querySelector(".ev-card")) {
    if (emptyState) {
      emptyState.hidden = false;
      emptyState.textContent =
        "No hay evaluaciones cargadas. Creá una con «Nueva Evaluación» (el listado por API no está disponible).";
    }
  }

  function getCards() {
    if (!grid) return [];
    return Array.from(grid.querySelectorAll(".ev-card"));
  }

  function applyFiltersAndSort() {
    const cards = getCards();
    if (!cards.length) {
      if (emptyState) emptyState.hidden = false;
      return;
    }

    const q = (searchInput?.value || "").trim().toLowerCase();
    const type = typeFilter?.value || "all";
    const sortDir = dateSort?.value || "asc";

    const visible = cards.filter((card) => {
      const nombre = (card.dataset.nombre || "").toLowerCase();
      const cardType = card.dataset.type || "";
      const matchQuery = q === "" || nombre.includes(q);
      const matchType = type === "all" || cardType === type;
      return matchQuery && matchType;
    });

    visible.sort((a, b) => {
      const dateA = a.dataset.date || "";
      const dateB = b.dataset.date || "";
      if (dateA === dateB) return 0;
      return sortDir === "asc"
        ? dateA.localeCompare(dateB)
        : dateB.localeCompare(dateA);
    });

    cards.forEach((card) => {
      card.classList.add("is-hidden");
    });

    visible.forEach((card) => {
      card.classList.remove("is-hidden");
      grid.appendChild(card);
    });

    if (emptyState) {
      emptyState.hidden = visible.length > 0;
    }
  }

  function handleDelete(btn) {
    const nombre = btn.dataset.nombre || "esta evaluación";
    const confirmed = confirm(
      `¿Eliminar "${nombre}"?\n\nSolo se quitará de la vista (sin endpoint DELETE en la API).`
    );
    if (!confirmed) return;

    const card = btn.closest(".ev-card");
    if (card) {
      card.remove();
      applyFiltersAndSort();
    }
  }

  grid?.addEventListener("click", (e) => {
    const deleteBtn = e.target.closest(".ev-delete-btn");
    if (deleteBtn) {
      e.preventDefault();
      handleDelete(deleteBtn);
    }
  });

  searchInput?.addEventListener("input", applyFiltersAndSort);
  typeFilter?.addEventListener("change", applyFiltersAndSort);
  dateSort?.addEventListener("change", applyFiltersAndSort);

  applyFiltersAndSort();
});
