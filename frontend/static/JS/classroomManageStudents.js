document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("st-dropzone");
  const fileInput = document.getElementById("st-file-input");
  const exportBtn = document.getElementById("st-export-btn");
  const addBtn = document.getElementById("st-add-student-btn");
  const searchInput = document.getElementById("st-search-input");
  const statusFilter = document.getElementById("st-status-filter");
  const teamFilter = document.getElementById("st-team-filter");
  const tbody = document.getElementById("st-tbody");

  function openFilePicker() {
    if (fileInput) fileInput.click();
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

    Array.from(tbody.querySelectorAll("tr")).forEach((tr) => {
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
    dropzone.addEventListener("drop", (e) => {
      const file = e.dataTransfer?.files?.[0];
      if (file) alert(`Archivo seleccionado: ${file.name} (importación pendiente)`);
    });
  }

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const file = fileInput.files?.[0];
      if (file) alert(`Archivo seleccionado: ${file.name} (importación pendiente)`);
    });
  }

  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      alert("Exportación (pendiente de implementar).");
    });
  }

  if (addBtn) {
    addBtn.addEventListener("click", () => {
      const classroomId = window.location.pathname.split("/")[2];
      
      window.location.href = `/aulas/${classroomId}/gestionar/estudiantes/crear`;
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }
  if (statusFilter) {
    statusFilter.addEventListener("change", applyFilters);
  }
  if (teamFilter) {
    teamFilter.addEventListener("change", applyFilters);
  }

  // Poblar filtro por equipos a partir de los datos en la tabla.
  if (teamFilter && tbody) {
    const teams = Array.from(tbody.querySelectorAll("tr"))
      .map((tr) => tr.dataset.team)
      .filter(Boolean);

    const uniqueTeams = Array.from(new Set(teams)).sort((a, b) => a.localeCompare(b, "es"));

    // Conserva la opción inicial (Todos los equipos) y reemplaza el resto.
    while (teamFilter.options.length > 1) {
      teamFilter.remove(1);
    }

    uniqueTeams.forEach((team) => {
      const opt = document.createElement("option");
      opt.value = team;
      opt.textContent = team;
      teamFilter.appendChild(opt);
    });
  }

  applyFilters();
});

