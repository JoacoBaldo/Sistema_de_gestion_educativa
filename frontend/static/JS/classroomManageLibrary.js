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

  let activeType = "all";

  function render() {
    if (!grid) return;
    const cards = Array.from(grid.querySelectorAll(".lb-card"));
    const q = (searchInput?.value || "").trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const type = card.dataset.type || "all";
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

  uploadBtn?.addEventListener("click", () => openModal());
  modalClose?.addEventListener("click", closeModal);
  modalCancel?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("La biblioteca no tiene el endpoint para añadir recursos en el backend todavía.");
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