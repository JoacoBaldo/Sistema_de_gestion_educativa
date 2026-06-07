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
  const btnGuardar = document.getElementById("btnGuardarEquipo");
  const newBtn = document.getElementById("tm-new-btn");
  const cancelBtn = document.getElementById("tm-team-cancel-btn");
  const closeBtn = document.getElementById("tm-team-close");

  if (!modal || !form) return;

  const showToast = bindToast(toast);

  function openModal() {
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function createMemberRow(value = "") {
    const row = document.createElement("div");
    row.className = "glass-list-row--member";

    const input = document.createElement("input");
    input.type = "text";
    input.name = "miembros";
    input.className = "glass-input";
    input.placeholder = "Nombre del miembro";
    input.value = value;
    input.required = true;

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "glass-btn-remove";
    remove.textContent = "✕";
    remove.setAttribute("aria-label", "Eliminar miembro");
    remove.addEventListener("click", () => removeMemberRow(row));

    row.appendChild(input);
    row.appendChild(remove);
    return row;
  }

  function removeMemberRow(row) {
    if (!row || !miembrosList) return;
    if (miembrosList.children.length === 1) {
      const input = row.querySelector("input");
      if (input) input.value = "";
      return;
    }
    miembrosList.removeChild(row);
  }

  function resetForm() {
    form.reset();
    if (!miembrosList) return;
    miembrosList.innerHTML = "";
    miembrosList.appendChild(createMemberRow());
    
    // Agregar classroom_id como campo hidden si es necesario
    const classroomId = getQueryParam("id") || getQueryParam("classroom_id");
    let classroomInput = form.querySelector('input[name="classroom_id"]');
    if (!classroomInput && classroomId) {
      classroomInput = document.createElement("input");
      classroomInput.type = "hidden";
      classroomInput.name = "classroom_id";
      classroomInput.value = classroomId;
      form.appendChild(classroomInput);
    } else if (classroomInput && classroomId) {
      classroomInput.value = classroomId;
    }
  }

  btnAddMember?.addEventListener("click", () => {
    const row = createMemberRow();
    miembrosList.appendChild(row);
    row.querySelector("input")?.focus();
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
    const miembros = Array.from(form.querySelectorAll("input[name='miembros']"))
      .map((input) => input.value.trim())
      .filter(Boolean);

    if (!nombreEquipo) {
      showToast("El nombre del equipo es obligatorio.");
      document.getElementById("nombre_equipo")?.focus();
      event.preventDefault();
      return;
    }

    if (miembros.length === 0) {
      showToast("Agrega al menos un miembro al equipo.");
      miembrosList?.querySelector("input")?.focus();
      event.preventDefault();
      return;
    }

    // Agregar token al formulario si es necesario
    const token = localStorage.getItem("token");
    if (token) {
      const tokenInput = document.createElement("input");
      tokenInput.type = "hidden";
      tokenInput.name = "token";
      tokenInput.value = token;
      form.appendChild(tokenInput);
    }

    // El formulario se enviará normalmente con POST a /equipos
  });
});

