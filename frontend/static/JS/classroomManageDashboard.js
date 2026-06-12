(function () {
  const tbody = document.getElementById("db-students-tbody");
  const searchInput = document.getElementById("db-search");
  const emptyMsg = document.getElementById("db-empty");

  function matchesSearch(row) {
    const q = (searchInput?.value || "").trim().toLowerCase();
    if (!q) return true;
    const hay = `${row.dataset.username || ""} ${row.dataset.email || ""}`.toLowerCase();
    return hay.includes(q);
  }

  function applySearch() {
    if (!tbody) return;
    let visible = 0;
    Array.from(tbody.querySelectorAll("tr[data-user-id]")).forEach((row) => {
      const show = matchesSearch(row);
      row.style.display = show ? "" : "none";
      if (show) visible += 1;
    });
    if (emptyMsg) emptyMsg.hidden = visible > 0;
  }

  searchInput?.addEventListener("input", applySearch);
  applySearch();
})();
