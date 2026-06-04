import {bindModalButtons, bindModalDismiss, bindToast} from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {

  const modal = document.getElementById("tm-edit-team-modal");
  const form = document.getElementById("formEditarEquipo");
  const toast = document.getElementById("tm-team-toast");
  const miembrosList = document.getElementById("edit-miembros-list");
  const btnAddMember = document.getElementById("btn-edit-add-member");
  const btnGuardar = document.getElementById("btnActualizarEquipo");
  const cancelBtn = document.getElementById("tm-edit-team-cancel-btn");
  const closeBtn = document.getElementById("tm-edit-team-close");

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

  window.abrirModalEditar = (datosEquipo) => {
    form.reset();
    if (!miembrosList) return;
    miembrosList.innerHTML = "";

    document.getElementById("edit_nombre_equipo").value = datosEquipo.nombre || "";
    document.getElementById("edit_proyecto").value = datosEquipo.proyecto || "";
    document.getElementById("edit_fecha_entrega").value = datosEquipo.fecha || "";
    document.getElementById("edit_estado").value = datosEquipo.estado || "activo";
    
    const descInput = document.getElementById("edit_descripcion");
    if (descInput) descInput.value = datosEquipo.descripcion || "";

    if (datosEquipo.miembros && datosEquipo.miembros.length > 0) {
      datosEquipo.miembros.forEach(miembro => {
        miembrosList.appendChild(createMemberRow(miembro));
      });
    } else {
      miembrosList.appendChild(createMemberRow());
    }

    openModal();
  };

  btnAddMember?.addEventListener("click", () => {
    const row = createMemberRow();
    miembrosList.appendChild(row);
    row.querySelector("input")?.focus();
  });

  bindModalButtons({ cancelBtn, closeBtn, onClose: closeModal });
  bindModalDismiss(modal, closeModal);

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const nombreEquipo = document.getElementById("edit_nombre_equipo")?.value.trim();
    const miembros = Array.from(form.querySelectorAll("input[name='miembros']"))
      .map((input) => input.value.trim())
      .filter(Boolean);

    if (!nombreEquipo) {
      showToast("El nombre del equipo es obligatorio.");
      document.getElementById("edit_nombre_equipo")?.focus();
      return;
    }

    if (miembros.length === 0) {
      showToast("Agrega al menos un miembro al equipo.");
      miembrosList?.querySelector("input")?.focus();
      return;
    }

    if (btnGuardar) {
      btnGuardar.textContent = "Guardando...";
      btnGuardar.disabled = true;
    }

    showToast("Modificación de equipos no disponible (Ruta de API no implementada).");
    
    if (btnGuardar) {
      btnGuardar.textContent = "Guardar Cambios";
      btnGuardar.disabled = false;
    }
    
    closeModal(); // borrar cuando conecten con backend
  });
});