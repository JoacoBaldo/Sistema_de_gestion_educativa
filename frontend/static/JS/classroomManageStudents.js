document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("st-dropzone");
  const fileInput = document.getElementById("st-file-input");
  const exportBtn = document.getElementById("st-export-btn");
  const addBtn = document.getElementById("st-add-student-btn");
  const searchInput = document.getElementById("st-search-input");
  const statusFilter = document.getElementById("st-status-filter");
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

    Array.from(tbody.querySelectorAll("tr")).forEach((tr) => {
      const rowText = tr.textContent?.toLowerCase() || "";
      const rowStatus = tr.getAttribute("data-status") || "active";
      const matchQuery = q === "" || rowText.includes(q);
      const matchStatus = status === "all" || rowStatus === status;
      tr.style.display = matchQuery && matchStatus ? "" : "none";
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
      alert("Añadir estudiante (pendiente de implementar).");
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }
  if (statusFilter) {
    statusFilter.addEventListener("change", applyFilters);
  }
});

