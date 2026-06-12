(function () {
  const grid = document.getElementById("lb-grid");
  const emptyMsg = document.getElementById("lb-empty");
  const searchInput = document.getElementById("lb-search");
  const pills = document.querySelectorAll(".cmr-pill[data-type]");
  const uploadBtn = document.getElementById("lb-upload-btn");
  const modal = document.getElementById("lb-recurso-modal");
  const modalClose = document.getElementById("lb-modal-close");
  const modalCancel = document.getElementById("lb-modal-cancel");
  const form = document.getElementById("lb-recurso-form");
  const inputNombre = document.getElementById("lb-nombre");
  const inputLink = document.getElementById("lb-link");
  const editModal = document.getElementById("lb-edit-modal");
  const editForm = document.getElementById("lb-edit-form");
  const editClose = document.getElementById("lb-edit-close");
  const editCancel = document.getElementById("lb-edit-cancel");
  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id");

  let activeType = "all";

  function render() {
    if (!grid) return;
    const cards = Array.from(grid.querySelectorAll(".lb-card"));
    const q = (searchInput?.value || "").trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const type = (card.dataset.type || "all").trim().toLowerCase();
      const title = (card.dataset.title || "").toLowerCase();

      const matchesType = (activeType === "all" || type === activeType);
      const matchesSearch = (!q || title.includes(q));
      const show = matchesType && matchesSearch;

      card.style.display = show ? "" : "none";
      if (show) visible += 1;
    });

    if (emptyMsg) {
      emptyMsg.hidden = visible > 0;
      if (cards.length === 0) {
        emptyMsg.textContent = "No hay recursos cargados en este curso.";
      } else if (visible === 0) {
        emptyMsg.textContent = "No se encontraron recursos con esos criterios.";
      }
    }
  }

  function openModal() {
    if (!modal) return;
    modal.classList.remove("hidden");
    inputNombre?.focus();
  }

  function closeModal() {
    modal?.classList.add("hidden");
    form?.reset();
  }

  function closeEditModal() {
    editModal?.classList.add("hidden");
    editForm?.reset();
  }

  function openEditModal(btn) {
    if (!editForm || !editModal || !classroomId) return;
    const resourceId = btn.dataset.id;
    editForm.action = `/aulas/${classroomId}/gestionar/recursos/${resourceId}/actualizar`;
    const deleteBtn = document.getElementById("lb-edit-delete-btn");
    if (deleteBtn) {
      deleteBtn.formAction = `/aulas/${classroomId}/gestionar/recursos/${resourceId}/eliminar`;
      deleteBtn.onclick = null;
      deleteBtn.onclick = function (e) {
        if (!confirm("¿Estás seguro de que querés eliminar este recurso de forma permanente?")) {
          e.preventDefault();
        }
      };
    }

    document.getElementById("lb-edit-name").value = btn.dataset.nombre || "";
    document.getElementById("lb-edit-type").value = btn.dataset.tipo || "link";
    document.getElementById("lb-edit-url").value = btn.dataset.url || "";

    editModal.classList.remove("hidden");
  }

  uploadBtn?.addEventListener("click", () => openModal());
  modalClose?.addEventListener("click", closeModal);
  modalCancel?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  grid?.addEventListener("click", (event) => {
    const editBtn = event.target.closest(".lb-edit-btn");
    if (!editBtn) return;

    event.preventDefault();
    event.stopPropagation();
    openEditModal(editBtn);
  });

  editClose?.addEventListener("click", closeEditModal);
  editCancel?.addEventListener("click", closeEditModal);
  editModal?.addEventListener("click", (event) => {
    if (event.target === editModal) closeEditModal();
  });

  form?.addEventListener("submit", (e) => {
    const nombre = inputNombre?.value.trim();
    const link = inputLink?.value.trim();

    if (!nombre || !link) {
      e.preventDefault();
      alert("Por favor, completa todos los campos obligatorios.");
    }
  });

  searchInput?.addEventListener("input", render);

  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      pills.forEach((p) => p.classList.remove("is-active"));
      pill.classList.add("is-active");
      activeType = pill.getAttribute("data-type") || "all";
      render();
    });
  });

  render();
})();