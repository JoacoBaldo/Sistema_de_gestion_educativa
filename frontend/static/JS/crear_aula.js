(() => {
  const backBtns = document.querySelectorAll('[data-action="back"]');
  backBtns.forEach((btn) => {
    btn.addEventListener("click", () => window.history.back());
  });

  const form = document.getElementById("formAula");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const btn = document.getElementById("btnGuardar");
    const fecha_inicio = document.getElementById("fecha_inicio")?.value ?? "";
    const fecha_fin = document.getElementById("fecha_fin")?.value ?? "";
    const h_inicio = document.getElementById("h_inicio")?.value ?? "";
    const h_fin = document.getElementById("h_fin")?.value ?? "";

    if (fecha_inicio && fecha_fin && fecha_inicio > fecha_fin) {
      e.preventDefault();
      alert("La fecha de inicio debe ser anterior a la fecha de fin.");
      return;
    }
    if (h_inicio && h_fin && h_inicio >= h_fin) {
      e.preventDefault();
      alert("La hora de inicio debe ser anterior a la de fin.");
      return;
    }

    if (btn) {
      btn.innerText = "Guardando...";
      btn.disabled = true;
    }
  });
})();

