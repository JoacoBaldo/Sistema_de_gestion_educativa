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