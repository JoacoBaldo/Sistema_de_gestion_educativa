import {
  bindModalButtons,
  bindModalDismiss,
  bindToast,
  getQueryParam,
} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("tm-team-modal");
  const form = document.getElementById("formEquipo");
  const toast = document.getElementById("tm-team-toast");
  const miembrosList = document.getElementById("miembros-list");
  const btnAddMember = document.getElementById("btn-add-member");
  const newBtn = document.getElementById("tm-new-btn");
  const cancelBtn = document.getElementById("tm-team-cancel-btn");
  const closeBtn = document.getElementById("tm-team-close");
  const memberTemplate = document.getElementById("tm-member-select-template");
  const evaluationSelect = document.getElementById("tm-evaluation-id");

  if (!modal || !form) return;

  const showToast = bindToast(toast);

  function openModal() {
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function createMemberRow() {
    if (memberTemplate) {
      const fragment = memberTemplate.content.cloneNode(true);
      const row = fragment.querySelector(".glass-list-row--member");
      row?.querySelector(".glass-btn-remove")?.addEventListener("click", () => {
        if (miembrosList.children.length === 1) {
          const select = row.querySelector("select");
          if (select) select.value = "";
          return;
        }
        row.remove();
      });
      miembrosList.appendChild(fragment);
      return row;
    }

    const row = document.createElement("div");
    row.className = "glass-list-row--member";
    const select = document.createElement("select");
    select.name = "miembros";
    select.className = "glass-input";
    select.required = true;
    row.appendChild(select);
    miembrosList.appendChild(row);
    return row;
  }

  function resetForm() {
    form.reset();
    if (!miembrosList) return;
    miembrosList.innerHTML = "";
    createMemberRow();
  }

  btnAddMember?.addEventListener("click", () => {
    createMemberRow();
  });

  newBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    resetForm();
    openModal();
  });

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  if (getQueryParam("vista") === "teams" && getQueryParam("accion") === "nueva") {
    resetForm();
    openModal();
  }

  form.addEventListener("submit", (event) => {
    const nombreEquipo = document.getElementById("nombre_equipo")?.value.trim();
    const miembros = Array.from(form.querySelectorAll("select[name='miembros']"))
      .map((select) => select.value.trim())
      .filter(Boolean);

    if (!nombreEquipo) {
      showToast("El nombre del equipo es obligatorio.");
      event.preventDefault();
      return;
    }

    if (!miembros.length) {
      showToast("Selecciona al menos un miembro del aula.");
      event.preventDefault();
      return;
    }

    if (!evaluationSelect?.value) {
      showToast("Seleccioná una evaluación.");
      event.preventDefault();
    }
  });
});
