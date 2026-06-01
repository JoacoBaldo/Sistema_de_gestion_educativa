document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("st-student-modal");
  const form = document.getElementById("st-student-form");
  const tbody = document.getElementById("st-tbody");
  const toast = document.getElementById("st-student-toast");

  const nameInput = document.getElementById("st-student-name");
  const lastInput = document.getElementById("st-student-lastname");
  const emailInput = document.getElementById("st-student-email");
  const padronInput = document.getElementById("st-student-padron");
  const abandonedInput = document.getElementById("st-student-abandoned");
  const cancelBtn = document.getElementById("st-student-cancel-btn");

  function hasToken() {
    try {
      return !!localStorage.getItem("token");
    } catch (e) {
      return false;
    }
  }

  function openModal() {
    if (!hasToken()) return (window.location.href = "/auth");
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2500);
  }

  function populateFromRow(tr) {
    const nombre = tr.dataset.nombre || "";
    const apellido = tr.dataset.apellido || "";
    const padron = tr.dataset.padron || "";
    const email = tr.dataset.email || "";
    const status = tr.dataset.status || "active";

    nameInput.value = nombre;
    lastInput.value = apellido;
    padronInput.value = padron;
    emailInput.value = email;
    abandonedInput.checked = status === "abandoned";

    openModal();
  }

  if (tbody) {
    tbody.addEventListener("click", (e) => {
      const btn = e.target.closest("button[aria-label='Editar']");
      if (!btn) return;
      const tr = btn.closest("tr");
      if (!tr) return;
      populateFromRow(tr);
    });
  }

  cancelBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    closeModal();
  });

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  form?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const nombre = nameInput.value.trim();
    const apellido = lastInput.value.trim();
    const padron = padronInput.value.trim();
    const email = emailInput.value.trim();

    if (!nombre || !apellido || !padron || !email) {
      showToast("Completa los campos obligatorios.");
      return;
    }

    if (!validateEmail(email)) {
      showToast("Formato de email inválido.");
      emailInput.focus();
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) return (window.location.href = "/auth");

    const payload = {
      nombre,
      apellido,
      padron,
      email,
      abandoned: !!abandonedInput.checked,
    };

    try {
      const res = await fetch(`/api/students/${encodeURIComponent(padron)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Error en la actualización");

      const row = Array.from(document.querySelectorAll("#st-tbody tr")).find((r) => (r.dataset.padron || "") === padron);
      if (row) {
        row.dataset.nombre = nombre;
        row.dataset.apellido = apellido;
        row.dataset.email = email;
        row.dataset.status = payload.abandoned ? "abandoned" : "active";
        const cell1 = row.querySelector("td:nth-child(1)");
        if (cell1) cell1.textContent = nombre;
        const cell2 = row.querySelector("td:nth-child(2)");
        if (cell2) cell2.textContent = apellido;
        const emailCell = row.querySelector(".st-col-email");
        if (emailCell) emailCell.textContent = email;
        const statusCell = row.querySelector("td:nth-child(5)");
        if (statusCell) statusCell.innerHTML = payload.abandoned ? '<span class="st-badge st-badge-dropped">Abandono</span>' : '<span class="st-badge st-badge-active">Activo</span>';
      }

      showToast("Datos guardados correctamente.");
      setTimeout(closeModal, 800);
    } catch (err) {
      console.error(err);
      showToast("No se pudo guardar. Intenta nuevamente.");
    }
  });
});
