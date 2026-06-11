document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("tm-grid");
  const searchInput = document.getElementById("tm-search-input");
  const emptyMsg = document.getElementById("tm-empty");

  function applySearch() {
    if (!grid) return;
    const q = (searchInput?.value || "").trim().toLowerCase();
    let visible = 0;

    Array.from(grid.querySelectorAll(".tm-card")).forEach((card) => {
      const nombre = (card.dataset.nombre || "").toLowerCase();
      const show = !q || nombre.includes(q);
      card.style.display = show ? "" : "none";
      if (show) visible += 1;
    });

    if (emptyMsg) {
      const hasCards = grid.querySelectorAll(".tm-card").length > 0;
      emptyMsg.classList.toggle("hidden", !hasCards || visible > 0);
    }
  }

  searchInput?.addEventListener("input", applySearch);
  applySearch();
});
