document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("ev-grid");
  const emptyState = document.getElementById("ev-empty");
  const searchInput = document.getElementById("ev-search-input");
  const typeFilter = document.getElementById("ev-type-filter");
  const dateSort = document.getElementById("ev-date-sort");
  const editModal = document.getElementById("ev-edit-modal");
  const editForm = document.getElementById("ev-edit-form");
  const editClose = document.getElementById("ev-edit-close");
  const editCancel = document.getElementById("ev-edit-cancel");
  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id");

  function applyFiltersAndSort() {
    const cards = Array.from(grid?.querySelectorAll(".ev-card") || []);
    if (!cards.length) {
      if (emptyState) emptyState.classList.remove("hidden");
      return;
    }

    const q = (searchInput?.value || "").trim().toLowerCase();
    const type = typeFilter?.value || "all";
    const sortDir = dateSort?.value || "desc";

    const visible = cards.filter((card) => {
      const nombre = (card.dataset.nombre || "").toLowerCase();
      const cardType = card.dataset.type || "";
      return (q === "" || nombre.includes(q)) && (type === "all" || cardType === type);
    });

    visible.sort((a, b) => {
      const dateA = a.dataset.date || "";
      const dateB = b.dataset.date || "";
      return sortDir === "asc" ? dateA.localeCompare(dateB) : dateB.localeCompare(dateA);
    });

    cards.forEach((card) => card.classList.add("is-hidden"));
    visible.forEach((card) => {
      card.classList.remove("is-hidden");
      grid.appendChild(card);
    });

    if (emptyState) emptyState.classList.toggle("hidden", visible.length > 0);
  }

  function closeEditModal() {
    editModal?.classList.add("hidden");
    editForm?.reset();
  }

  function openEditModal(btn) {
    if (!editForm || !editModal || !classroomId) return;
    const evaluationId = btn.dataset.id;
    editForm.action = `/aulas/${classroomId}/gestionar/evaluaciones/${evaluationId}/actualizar`;
    const deleteBtn = document.getElementById("ev-edit-delete-btn");
    if (deleteBtn) {
      deleteBtn.onclick = null;

      deleteBtn.onclick = function (e) {
        e.preventDefault();
        if (confirm("¿Estás seguro de que querés eliminar esta evaluación de forma permanente?")) {
          editForm.action = `/aulas/${classroomId}/gestionar/evaluaciones/${evaluationId}/eliminar`;
          editForm.submit();
        }
      };
    }

    document.getElementById("ev-edit-name").value = btn.dataset.nombre || "";
    document.getElementById("ev-edit-type").value = btn.dataset.tipo || "parcial";
    document.getElementById("ev-edit-individual").checked = btn.dataset.individual === "1";

    // Mapeamos la fecha guardada en la tarjeta hacia el input del modal
    const editDateInput = document.getElementById("ev-edit-due-date");
    if (editDateInput) {
      editDateInput.value = btn.dataset.date || "";
    }

    editModal.classList.remove("hidden");
  }

  grid?.addEventListener("click", (event) => {
    const editBtn = event.target.closest(".ev-edit-btn");
    if (!editBtn) return;
    event.preventDefault();
    openEditModal(editBtn);
  });

  editClose?.addEventListener("click", closeEditModal);
  editCancel?.addEventListener("click", closeEditModal);
  editModal?.addEventListener("click", (event) => {
    if (event.target === editModal) closeEditModal();
  });

  searchInput?.addEventListener("input", applyFiltersAndSort);
  typeFilter?.addEventListener("change", applyFiltersAndSort);
  dateSort?.addEventListener("change", applyFiltersAndSort);

  applyFiltersAndSort();
});

document.addEventListener("DOMContentLoaded", () => {
  const gradesModal = document.getElementById("ev-grades-modal");
  const targetNameSpan = document.getElementById("ev-grades-target-name");
  const closeBtn = document.getElementById("ev-grades-close");
  const closeModalBtns = [
    closeBtn,
    document.getElementById("ev-grades-cancel-csv"),
    document.getElementById("ev-grades-cancel-manual")
  ];

  const tabBtnCsv = document.getElementById("tab-btn-csv");
  const tabBtnManual = document.getElementById("tab-btn-manual");
  const tabContentCsv = document.getElementById("tab-content-csv");
  const tabContentManual = document.getElementById("tab-content-manual");

  const gradesForm = document.getElementById("ev-grades-form");
  const manualForm = document.getElementById("ev-manual-grades-form");

  const csvInput = document.getElementById("ev-csv-input");
  const csvFilename = document.getElementById("ev-csv-filename");
  const containerStudent = document.getElementById("ev-container-student");
  const containerTeam = document.getElementById("ev-container-team");
  const selectStudent = document.getElementById("ev-select-student");
  const selectTeam = document.getElementById("ev-select-team");
  const manualScoreInput = document.getElementById("ev-manual-score");

  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".ev-add-grades-btn");
    if (!btn) return;

    e.preventDefault();
    const evaluationId = btn.dataset.id;
    const evaluationName = btn.dataset.nombre;
    const isIndividual = btn.dataset.individual === "1" || btn.dataset.individual === "true";

    const urlParts = window.location.pathname.split('/');
    const classroomId = urlParts[urlParts.indexOf('aulas') + 1];

    targetNameSpan.textContent = evaluationName;

    gradesForm.action = `/aulas/${classroomId}/gestionar/evaluaciones/${evaluationId}/subir-notas`;
    manualForm.action = `/aulas/${classroomId}/gestionar/evaluaciones/${evaluationId}/cargar-nota-manual`;

    csvInput.value = "";
    csvFilename.textContent = "Formato requerido: columna 'documento' o 'email' o 'equipo' y columna 'nota'";
    csvFilename.style.color = "rgba(255, 255, 255, 0.7)";
    manualScoreInput.value = "";
    selectStudent.value = "";
    selectTeam.value = "";

    if (isIndividual) {
      containerStudent.classList.remove("hidden");
      selectStudent.required = true;
      selectStudent.disabled = false;

      containerTeam.classList.add("hidden");
      selectTeam.required = false;
      selectTeam.disabled = true;
    } else {
      containerTeam.classList.remove("hidden");
      selectTeam.required = true;
      selectTeam.disabled = false;

      containerStudent.classList.add("hidden");
      selectStudent.required = false;
      selectStudent.disabled = true;
    }

    switchTab("csv");
    gradesModal.classList.remove("hidden");
  });

  function switchTab(tab) {
    if (tab === "csv") {
      tabContentCsv.classList.remove("hidden");
      tabContentManual.classList.add("hidden");
      tabBtnCsv.style.background = "rgba(255,255,255,0.2)";
      tabBtnCsv.style.color = "white";
      tabBtnManual.style.background = "transparent";
      tabBtnManual.style.color = "rgba(255,255,255,0.7)";
    } else {
      tabContentManual.classList.remove("hidden");
      tabContentCsv.classList.add("hidden");
      tabBtnManual.style.background = "rgba(255,255,255,0.2)";
      tabBtnManual.style.color = "white";
      tabBtnCsv.style.background = "transparent";
      tabBtnCsv.style.color = "rgba(255,255,255,0.7)";
    }
  }

  tabBtnCsv?.addEventListener("click", () => switchTab("csv"));
  tabBtnManual?.addEventListener("click", () => switchTab("manual"));

  csvInput?.addEventListener("change", () => {
    if (csvInput.files.length > 0) {
      csvFilename.textContent = `Archivo cargado: ${csvInput.files[0].name}`;
      csvFilename.style.color = "#10b981";
    }
  });

  const closeModal = () => gradesModal.classList.add("hidden");
  closeModalBtns.forEach(btn => btn?.addEventListener("click", closeModal));
});