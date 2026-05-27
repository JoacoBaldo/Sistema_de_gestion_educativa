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

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const btn = document.getElementById("btnCompartir");
    const id_clase = document.getElementById("classId")?.value ?? "";
    const email = document.getElementById("shareEmail")?.value ?? "";
    const rol = document.getElementById("shareRol")?.value ?? "Lector";

    if (!email.trim()) {
      alert("Ingresa un email válido");
      return;
    }

    const originalText = btn?.textContent ?? "";
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Enviando...";
    }

    try {
      const res = await fetch("/clases/compartir", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_clase, email, rol }),
      });

      if (res.ok) {
        alert(`Acceso concedido exitosamente a ${email}`);
        window.history.back();
        return;
      }

      let err = {};
      try {
        err = await res.json();
      } catch {
        err = {};
      }
      alert("Error: " + (err.error || "No se pudo compartir"));
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = originalText || "Conceder Acceso";
      }
    }
  });
})();

