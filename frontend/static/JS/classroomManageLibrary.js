import { createCmrToast, escapeHtml } from "./common/ui.js";
import { requireAuth } from "./common/auth.js";

(function () {
  requireAuth();
  const showToast = createCmrToast();
  const grid = document.getElementById("lb-grid");
  const emptyMsg = document.getElementById("lb-empty");
  const searchInput = document.getElementById("lb-search");
  const pills = document.querySelectorAll(".cmr-pill[data-type]");
  const uploadBtn = document.getElementById("lb-upload-btn");
  const modal = document.getElementById("lb-recurso-modal");
  const modalClose = document.getElementById("lb-modal-close");
  const modalCancel = document.getElementById("lb-modal-cancel");
  const form = document.getElementById("lb-recurso-form");
  const editId = document.getElementById("lb-edit-id");
  const inputNombre = document.getElementById("lb-nombre");
  const inputTipo = document.getElementById("lb-tipo");
  const inputLink = document.getElementById("lb-link");
  const modalTitle = document.getElementById("lb-modal-title");
  const modalSubtitle = document.getElementById("lb-modal-subtitle");
  const modalSubmit = document.getElementById("lb-modal-submit");

  let activeType = "all";
  let resources = [];

  function render() {
    if (!grid) return;
    const q = (searchInput?.value || "").trim().toLowerCase();
    const list = resources.filter((r) => {
      if (activeType !== "all" && r.type !== activeType) return false;
      if (q && !r.title.toLowerCase().includes(q)) return false;
      return true;
    });

    if (!list.length) {
      grid.innerHTML = "";
      if (emptyMsg) {
        emptyMsg.hidden = false;
        emptyMsg.textContent =
          "No hay recursos. El listado y carga de archivos requiere endpoints de biblioteca en el backend.";
      }
      return;
    }

    if (emptyMsg) emptyMsg.hidden = true;
    grid.innerHTML = list
      .map((r) => {
        const safeUrl = escapeHtml(r.url);
        const safeTitle = escapeHtml(r.title);
        return `<article class="lb-card cm-panel" data-id="${r.id}">
          <a class="lb-card__link" href="${safeUrl}" target="_blank" rel="noopener noreferrer">
            <h3 class="lb-card__title">${safeTitle}</h3>
          </a>
        </article>`;
      })
      .join("");
  }

  function openModal(mode) {
    if (!modal) return;
    if (mode === "create") {
      if (editId) editId.value = "";
      form?.reset();
      if (modalTitle) modalTitle.textContent = "Subir recurso";
      if (modalSubtitle) modalSubtitle.textContent = "Requiere POST /classrooms/{id}/resources/upload";
      if (modalSubmit) modalSubmit.textContent = "Publicar";
    }
    modal.classList.remove("hidden");
    inputNombre?.focus();
  }

  function closeModal() {
    modal?.classList.add("hidden");
    form?.reset();
    if (editId) editId.value = "";
  }

  uploadBtn?.addEventListener("click", () => openModal("create"));
  modalClose?.addEventListener("click", closeModal);
  modalCancel?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    showToast("Subida de recursos no disponible (endpoint no implementado en la API).");
    closeModal();
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
