document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("st-dropzone");
  const fileInput = document.getElementById("st-file-input");
  const csvForm = document.getElementById("st-csv-form");
  const searchInput = document.getElementById("st-search-input");
  const statusFilter = document.getElementById("st-status-filter");
  const teamFilter = document.getElementById("st-team-filter");
  const tbody = document.getElementById("st-tbody");
  
  const addBtn = document.getElementById("st-add-btn") || document.getElementById("add-btn");

  function applyFilters() {
    if (!tbody) return;
    const q = (searchInput?.value || "").trim().toLowerCase();
    const status = statusFilter?.value || "all";
    const team = teamFilter?.value || "all";

    Array.from(tbody.querySelectorAll("tr[data-padron]")).forEach((tr) => {
      const rowNombre = (tr.dataset.nombre || "").toLowerCase();
      const rowApellido = (tr.dataset.apellido || "").toLowerCase();
      const rowPadron = (tr.dataset.padron || "").toLowerCase();
      const rowStatus = tr.dataset.status || "active";
      const rowTeam = (tr.dataset.team || "").toLowerCase();

      const fullName = `${rowNombre} ${rowApellido}`.trim();
      const matchQuery = q === "" || fullName.includes(q) || rowPadron.includes(q);
      const matchStatus = status === "all" || rowStatus === status;
      const matchTeam = team === "all" || rowTeam === team.toLowerCase();

      tr.style.display = matchQuery && matchStatus && matchTeam ? "" : "none";
    });
  }

  if (dropzone && fileInput && csvForm) {
    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("dragover", (e) => e.preventDefault());
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        csvForm.submit();
      }
    });
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) csvForm.submit();
    });
  }

  searchInput?.addEventListener("input", applyFilters);
  statusFilter?.addEventListener("change", applyFilters);
  teamFilter?.addEventListener("change", applyFilters);

  applyFilters();
});