import { requestJson } from "./common/http.js";
import { authHeaders, getAuthToken } from "./common/auth.js";
import { bindToast, goTo } from "./common/ui.js";

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

  const showToast = bindToast(toast, 2500);

  function openModal() {
    if (!getAuthToken()) {
      goTo("/auth");
      return;
    }
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function populateFromRow(tr) {
    nameInput.value = tr.dataset.nombre || "";
    lastInput.value = tr.dataset.apellido || "";
    padronInput.value = tr.dataset.padron || "";
    emailInput.value = tr.dataset.email || "";
    abandonedInput.checked = (tr.dataset.status || "active") === "abandoned";
    openModal();
  }

  function updateStudentRow(padron, payload) {
    const row = Array.from(document.querySelectorAll("#st-tbody tr")).find(
      (r) => (r.dataset.padron || "") === padron
    );
    if (!row) return;

    row.dataset.nombre = payload.nombre;
    row.dataset.apellido = payload.apellido;
    row.dataset.email = payload.email;
    row.dataset.status = payload.abandoned ? "abandoned" : "active";

    const cell1 = row.querySelector("td:nth-child(1)");
    if (cell1) cell1.textContent = payload.nombre;
    const cell2 = row.querySelector("td:nth-child(2)");
    if (cell2) cell2.textContent = payload.apellido;
    const emailCell = row.querySelector(".st-col-email");
    if (emailCell) emailCell.textContent = payload.email;
    const statusCell = row.querySelector("td:nth-child(5)");
    if (statusCell) {
      statusCell.innerHTML = payload.abandoned
        ? '<span class="st-badge st-badge-dropped">Abandono</span>'
        : '<span class="st-badge st-badge-active">Activo</span>';
    }
  }

  tbody?.addEventListener("click", (e) => {
    const btn = e.target.closest("button[aria-label='Editar']");
    if (!btn) return;
    const tr = btn.closest("tr");
    if (tr) populateFromRow(tr);
  });

  cancelBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    closeModal();
  });

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

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showToast("Formato de email inválido.");
      emailInput.focus();
      return;
    }

    if (!getAuthToken()) {
      goTo("/auth");
      return;
    }

    const payload = {
      nombre,
      apellido,
      padron,
      email,
      abandoned: !!abandonedInput.checked,
    };

    try {
      const res = await requestJson(`/api/students/${encodeURIComponent(padron)}`, {
        method: "PUT",
        headers: authHeaders(),
        body: payload,
      });
      if (!res.ok) throw new Error("Error en la actualización");

      updateStudentRow(padron, payload);
      showToast("Datos guardados correctamente.");
      setTimeout(closeModal, 800);
    } catch (err) {
      console.error(err);
      showToast("No se pudo guardar. Intenta nuevamente.");
    }
  });
});
