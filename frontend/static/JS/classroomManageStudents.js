import { requireAuth } from "./common/auth.js";

document.addEventListener("DOMContentLoaded", () => {
  requireAuth();

  const dropzone = document.getElementById("st-dropzone");
  const fileInput = document.getElementById("st-file-input");
  const exportBtn = document.getElementById("st-export-btn");
  const addBtn = document.getElementById("st-add-student-btn");
  const searchInput = document.getElementById("st-search-input");
  const statusFilter = document.getElementById("st-status-filter");
  const teamFilter = document.getElementById("st-team-filter");
  const tbody = document.getElementById("st-tbody");

  function showEmptyTableMessage() {
    if (!tbody) return;
    if (tbody.querySelector("tr")) return;
    const tr = document.createElement("tr");
    tr.innerHTML =
      '<td colspan="6">No hay estudiantes cargados. Los endpoints de listado/alta de alumnos no están disponibles en la API.</td>';
    tbody.appendChild(tr);
  }

  function openFilePicker() {
    fileInput?.click();
  }

  function setDropzoneHint(text) {
    const subtitle = dropzone?.querySelector(".st-dropzone-subtitle");
    if (subtitle) subtitle.textContent = text;
  }

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
      const matchQuery =
        q === "" || fullName.includes(q) || rowPadron.includes(q);
      const matchStatus = status === "all" || rowStatus === status;
      const matchTeam = team === "all" || rowTeam === team.toLowerCase();

      tr.style.display = matchQuery && matchStatus && matchTeam ? "" : "none";
    });
  }

  if (dropzone) {
    dropzone.addEventListener("click", () => openFilePicker());
    dropzone.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openFilePicker();
      }
    });

    ["dragenter", "dragover"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        setDropzoneHint("Suelta el archivo para importarlo");
      });
    });
    ["dragleave", "drop"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        setDropzoneHint("Arrastra tu archivo aquí o haz clic para buscar");
      });
    });
    dropzone.addEventListener("drop", () => {
      alert("Importación CSV no disponible (endpoint no implementado en la API).");
    });
  }

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      alert("Importación CSV no disponible (endpoint no implementado en la API).");
      fileInput.value = "";
    });
  }

  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      alert("Exportación no disponible sin endpoint de estudiantes.");
    });
  }

  if (addBtn) {
    addBtn.addEventListener("click", () => {
      alert("Alta de estudiantes no disponible sin endpoint POST de alumnos.");
    });
  }

  searchInput?.addEventListener("input", applyFilters);
  statusFilter?.addEventListener("change", applyFilters);
  teamFilter?.addEventListener("change", applyFilters);

  showEmptyTableMessage();
  applyFilters();
});
