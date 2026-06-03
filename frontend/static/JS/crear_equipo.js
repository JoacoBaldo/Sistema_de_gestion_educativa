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

  function openModal() {
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2400);
  }

  function resetForm() {
    form.reset();
    if (!miembrosList) return;
    miembrosList.innerHTML = "";
    miembrosList.appendChild(createMemberRow());
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

  function addMemberRow(value = "") {
    const row = createMemberRow(value);
    miembrosList.appendChild(row);
    row.querySelector("input")?.focus();
  }

  btnAddMember?.addEventListener("click", () => addMemberRow());

  newBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    resetForm();
    openModal();
  });

  cancelBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });

  closeBtn?.addEventListener("click", (event) => {
    event.preventDefault();
    closeModal();
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get("vista") === "teams" && params.get("accion") === "nueva") {
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

    showToast("Equipo creado correctamente.");
    setTimeout(() => {
      closeModal();
      resetForm();
      if (btnGuardar) {
        btnGuardar.textContent = "Crear Equipo";
        btnGuardar.disabled = false;
      }
    }, 900);
  });
});
