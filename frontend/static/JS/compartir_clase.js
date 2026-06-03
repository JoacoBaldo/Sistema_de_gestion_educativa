document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("cc-share-modal");
  const form = document.getElementById("shareForm");
  const toast = document.getElementById("cc-share-toast");
  const titleEl = document.getElementById("cc-modal-title");
  const classIdEl = document.getElementById("classId");
  const cancelBtn = document.getElementById("cc-share-cancel-btn");
  const closeBtn = document.getElementById("cc-share-close");
  const btnCompartir = document.getElementById("btnCompartir");

  if (!modal || !form) return;

  function openModal(classId = "", className = "") {
    if (classIdEl) classIdEl.value = classId;
    if (titleEl) {
      titleEl.textContent = className
        ? `Compartir: ${className}`
        : "Compartir Clase";
    }
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2400);
  }

  function resetForm() {
    form.reset();
    if (classIdEl) classIdEl.value = "";
    if (titleEl) titleEl.textContent = "Compartir Clase";
  }

  cancelBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });

  closeBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("shareEmail")?.value.trim() ?? "";
    if (!email) {
      showToast("Ingresa un email válido.");
      return;
    }

    if (btnCompartir) {
      btnCompartir.disabled = true;
      btnCompartir.textContent = "Enviando...";
    }

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
      });

      if (!response.ok) throw new Error("Error al compartir");

      showToast("Acceso concedido correctamente.");
      setTimeout(() => {
        closeModal();
        resetForm();
        if (btnCompartir) {
          btnCompartir.disabled = false;
          btnCompartir.textContent = "Conceder Acceso";
        }
      }, 900);
    } catch (error) {
      console.error(error);
      showToast("No se pudo compartir. Intenta nuevamente.");
      if (btnCompartir) {
        btnCompartir.disabled = false;
        btnCompartir.textContent = "Conceder Acceso";
      }
    }
  });

  window.openCcShareModal = (classId = "", className = "") => {
    resetForm();
    openModal(classId, className);
  };

  const params = new URLSearchParams(window.location.search);
  if (params.get("accion") === "compartir") {
    const nombre = params.get("nombre") || "";
    window.openCcShareModal(
      params.get("id") || "",
      nombre ? decodeURIComponent(nombre) : ""
    );
  }
});
