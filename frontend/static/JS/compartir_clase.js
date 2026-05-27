(() => {
  const backBtns = document.querySelectorAll('[data-action="back"]');
  backBtns.forEach((btn) => {
    btn.addEventListener("click", () => window.history.back());
  });

  const params = new URLSearchParams(window.location.search);
  const id = params.get("id") || "";
  const nombre = params.get("nombre") || "";

  const titleEl = document.getElementById("shareTitle");
  if (titleEl && nombre) {
    titleEl.textContent = `Compartir: ${nombre}`;
  }

  const classIdEl = document.getElementById("classId");
  if (classIdEl) classIdEl.value = id;

  const form = document.getElementById("shareForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const btn = document.getElementById("btnCompartir");
    const email = document.getElementById("shareEmail")?.value ?? "";

    if (!email.trim()) {
      e.preventDefault();
      alert("Ingresa un email válido");
      return;
    }

    const originalText = btn?.textContent ?? "";
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Enviando...";
    }
    window.setTimeout(() => {
      if (btn) {
        btn.disabled = false;
        btn.textContent = originalText || "Conceder Acceso";
      }
    }, 5000);
  });
})();

