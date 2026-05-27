(() => {
  const backBtns = document.querySelectorAll('[data-action="back"]');
  backBtns.forEach((btn) => {
    btn.addEventListener("click", () => window.history.back());
  });

  const form = document.getElementById("formAula");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const btn = document.getElementById("btnGuardar");
    const data = {
      nombre: document.getElementById("nombre")?.value ?? "",
      catedra: document.getElementById("catedra")?.value ?? "",
      universidad: document.getElementById("universidad")?.value ?? "",
      fecha_inicio: document.getElementById("fecha_inicio")?.value ?? "",
      fecha_fin: document.getElementById("fecha_fin")?.value ?? "",
      horario: {
        dia: document.getElementById("dia")?.value ?? "",
        hora_inicio: document.getElementById("h_inicio")?.value ?? "",
        hora_fin: document.getElementById("h_fin")?.value ?? "",
      },
    };

    if (data.fecha_inicio > data.fecha_fin) {
      alert("La fecha de inicio debe ser anterior a la fecha de fin.");
      return;
    }
    if (data.horario.hora_inicio >= data.horario.hora_fin) {
      alert("La hora de inicio debe ser anterior a la de fin.");
      return;
    }

    if (btn) {
      btn.innerText = "Guardando...";
      btn.disabled = true;
    }

    try {
      const res = await fetch("/clases", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + (localStorage.getItem("token") ?? ""),
        },
        body: JSON.stringify(data),
      });

      if (res.ok) {
        window.location.href = "/aulas";
        return;
      }

      let err = {};
      try {
        err = await res.json();
      } catch {
        err = {};
      }
      alert("Error: " + (err.error || "No se pudo guardar"));
    } catch {
      alert("Error de conexión");
    } finally {
      if (btn) {
        btn.innerText = "Crear Aula";
        btn.disabled = false;
      }
    }
  });
})();

