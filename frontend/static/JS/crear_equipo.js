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
    event.preventDefault();

    const nombreEquipo = document.getElementById("nombre_equipo")?.value.trim();
    const miembros = Array.from(form.querySelectorAll("input[name='miembros']"))
      .map((input) => input.value.trim())
      .filter(Boolean);

    if (!nombreEquipo) {
      showToast("El nombre del equipo es obligatorio.");
      document.getElementById("nombre_equipo")?.focus();
      return;
    }

    if (miembros.length === 0) {
      showToast("Agrega al menos un miembro al equipo.");
      miembrosList?.querySelector("input")?.focus();
      return;
    }

    if (btnGuardar) {
      btnGuardar.textContent = "Creando...";
      btnGuardar.disabled = true;
    }

    const classroomId = getQueryParam("id") || getQueryParam("classroom_id");

    const payload = {
      classroom_id: classroomId ? parseInt(classroomId) : null,
      nombre: nombreEquipo,
      miembros: miembros
    };

    const xhr = new XMLHttpRequest();
    // Apuntamos al proxy de Flask en el frontend
    xhr.open("POST", "/api/v1/teams/", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    // Si tu API requiere token de autenticación (JWT)
    const token = localStorage.getItem("token");
    if (token) {
      xhr.setRequestHeader("Authorization", "Bearer " + token);
    }

    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        // Restaurar el botón al finalizar la petición
        if (btnGuardar) {
          btnGuardar.textContent = "Crear Equipo";
          btnGuardar.disabled = false;
        }

        if (xhr.status >= 200 && xhr.status < 300) {
          showToast("Equipo creado exitosamente.");
          closeModal();
          // Recargamos la grilla después de 1 segundo para ver el nuevo equipo
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        } else {
          // Manejo de errores devueltos por el backend
          let msjError = "Ocurrió un error al crear el equipo.";
          try {
            const respuesta = JSON.parse(xhr.responseText);
            if (respuesta.error) msjError = respuesta.error;
            if (respuesta.message) msjError = respuesta.message;
          } catch (ex) {
            console.error("Error parseando la respuesta:", ex);
          }
          showToast(msjError);
        }
      }
    };

    xhr.send(JSON.stringify(payload));
  });
});
