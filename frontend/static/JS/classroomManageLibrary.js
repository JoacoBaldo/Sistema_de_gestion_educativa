(function () {
  const STORAGE_KEY = "unimanage_library_public";

  const DEFAULT_RESOURCES = [
    {
      id: "r1",
      type: "pdf",
      title: "Introducción a estructuras de datos",
      url: "https://example.com/apuntes-estructuras.pdf",
      public: true,
    },
    {
      id: "r2",
      type: "video",
      title: "Clase 5: Árboles binarios",
      url: "https://example.com/video-arboles",
      public: true,
    },
    {
      id: "r3",
      type: "link",
      title: "Documentación oficial Python",
      url: "https://docs.python.org/3/",
      public: true,
    },
    {
      id: "r4",
      type: "pdf",
      title: "Guía de estilo para informes",
      url: "https://example.com/guia-informes.pdf",
      public: true,
    },
  ];

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
  let resources = loadResources();

  function loadResources() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        return parsed.map(normalizeResource);
      }
    } catch (_) {
      /* ignore */
    }
    return DEFAULT_RESOURCES.map(normalizeResource);
  }

  function normalizeResource(r) {
    return {
      id: r.id,
      type: r.type || "link",
      title: r.title || r.nombre || "Sin título",
      url: r.url || r.link || "#",
      public: r.public !== false,
    };
  }

  function saveResources() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(resources));
    } catch (_) {
      /* ignore */
    }
  }

  function iconSvg(type) {
    if (type === "video") {
      return '<svg viewBox="0 0 24 24" fill="none"><path d="M8 5v14l11-7L8 5Z" fill="currentColor"/></svg>';
    }
    if (type === "link") {
      return '<svg viewBox="0 0 24 24" fill="none"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" stroke="currentColor" stroke-width="1.6"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" stroke="currentColor" stroke-width="1.6"/></svg>';
    }
    return '<svg viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6Z" stroke="currentColor" stroke-width="1.5"/><path d="M14 2v6h6" stroke="currentColor" stroke-width="1.5"/></svg>';
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function matches(r) {
    const q = (searchInput?.value || "").trim().toLowerCase();
    if (activeType !== "all" && r.type !== activeType) return false;
    if (!r.public) return false;
    if (q && !r.title.toLowerCase().includes(q)) return false;
    return true;
  }

  function render() {
    if (!grid) return;
    const list = resources.filter(matches);
    grid.innerHTML = list
      .map((r) => {
        const safeUrl = escapeHtml(r.url);
        const safeTitle = escapeHtml(r.title);
        return `<article class="lb-card cm-panel" data-id="${r.id}">
          <a class="lb-card__link" href="${safeUrl}" target="_blank" rel="noopener noreferrer" data-action="open">
            <div class="lb-card__icon lb-card__icon--${r.type}" aria-hidden="true">${iconSvg(r.type)}</div>
            <h3 class="lb-card__title">${safeTitle}</h3>
          </a>
          <div class="lb-card__actions" aria-label="Acciones del recurso">
            <button class="st-icon-btn lb-icon-btn" type="button" data-action="edit" data-id="${r.id}"
              aria-label="Editar recurso" title="Editar">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M12 20h9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
                <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5Z"
                  stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
            <button class="st-icon-btn danger lb-icon-btn" type="button" data-action="delete" data-id="${r.id}"
              aria-label="Eliminar recurso" title="Eliminar">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M3 6h18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                  stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.75" />
                <path d="M6 6l1 16a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-16"
                  stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.75" />
                <path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
              </svg>
            </button>
          </div>
        </article>`;
      })
      .join("");

    if (emptyMsg) emptyMsg.hidden = list.length > 0;

    grid.querySelectorAll("[data-action=edit]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        openModal("edit", btn.getAttribute("data-id"));
      });
    });

    grid.querySelectorAll("[data-action=delete]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        deleteResource(btn.getAttribute("data-id"));
      });
    });

    grid.querySelectorAll(".lb-card__actions").forEach((el) => {
      el.addEventListener("click", (e) => e.stopPropagation());
    });
  }

  function showToast(msg) {
    let toast = document.getElementById("cmr-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "cmr-toast";
      toast.className = "cmr-toast";
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add("is-visible");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove("is-visible"), 2800);
  }

  function openModal(mode, id) {
    if (!modal) return;
    if (mode === "edit" && id) {
      const r = resources.find((x) => x.id === id);
      if (!r) return;
      if (editId) editId.value = r.id;
      if (inputNombre) inputNombre.value = r.title;
      if (inputTipo) inputTipo.value = r.type;
      if (inputLink) inputLink.value = r.url;
      if (modalTitle) modalTitle.textContent = "Editar recurso";
      if (modalSubtitle) modalSubtitle.textContent = "Modifica la información del material";
      if (modalSubmit) modalSubmit.textContent = "Guardar";
    } else {
      if (editId) editId.value = "";
      form?.reset();
      if (modalTitle) modalTitle.textContent = "Subir recurso";
      if (modalSubtitle) modalSubtitle.textContent = "Completa la información del material público";
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

  function deleteResource(id) {
    const r = resources.find((x) => x.id === id);
    if (!r) return;
    if (!confirm(`¿Eliminar "${r.title}"?`)) return;
    resources = resources.filter((x) => x.id !== id);
    saveResources();
    render();
    showToast("Recurso eliminado.");
  }

  uploadBtn?.addEventListener("click", () => openModal("create"));
  modalClose?.addEventListener("click", closeModal);
  modalCancel?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = inputNombre?.value?.trim();
    const type = inputTipo?.value || "pdf";
    const url = inputLink?.value?.trim();
    const id = editId?.value?.trim();

    if (!title || !url) {
      showToast("Completa todos los campos.");
      return;
    }

    if (id) {
      const idx = resources.findIndex((x) => x.id === id);
      if (idx >= 0) {
        resources[idx] = { ...resources[idx], title, type, url };
        saveResources();
        render();
        closeModal();
        showToast("Recurso actualizado.");
      }
      return;
    }

    resources.unshift({
      id: `r-${Date.now()}`,
      type,
      title,
      url,
      public: true,
    });
    saveResources();
    render();
    closeModal();
    showToast("Recurso publicado.");
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
