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
      const show =
        (activeType === "all" || type === activeType) && (!q || title.includes(q));
      card.style.display = show ? "" : "none";
      if (show) visible += 1;
    });

    if (emptyMsg) {
      emptyMsg.hidden = visible > 0 || cards.length > 0;
      if (!cards.length) emptyMsg.textContent = "No hay recursos cargados (sin endpoint de biblioteca).";
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
    alert("La biblioteca no tiene endpoint en el backend. No se puede subir recursos.");
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
