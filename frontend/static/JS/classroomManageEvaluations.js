document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("ev-grid");
  const emptyState = document.getElementById("ev-empty");
  const searchInput = document.getElementById("ev-search-input");
  const typeFilter = document.getElementById("ev-type-filter");
  const dateSort = document.getElementById("ev-date-sort");

  function getCards() {
    if (!grid) return [];
    return Array.from(grid.querySelectorAll(".ev-card"));
  }

  function applyFiltersAndSort() {
    const cards = getCards();
    if (!cards.length) return;

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
    const id = btn.dataset.id || "";
    const confirmed = confirm(
      `¿Eliminar "${nombre}"?\n\nEsta acción no se puede deshacer.`
    );
    if (!confirmed) return;

    const card = btn.closest(".ev-card");
    if (card) {
      card.remove();
      applyFiltersAndSort();
    }

    // Placeholder hasta conectar con el backend
    console.info(`Evaluación ${id} eliminada (pendiente de API).`);
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
