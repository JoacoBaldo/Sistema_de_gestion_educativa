(() => {
  const backBtns = document.querySelectorAll('[data-action="back"]');
  backBtns.forEach((btn) => {
    btn.addEventListener("click", () => window.history.back());
  });

  const form = document.getElementById("formEquipo");
  const miembrosList = document.getElementById("miembros-list");
  const btnAddMember = document.getElementById("btn-add-member");
  const btnGuardar = document.getElementById("btnGuardarEquipo");

  if (!form) return;

  function createMemberRow(value = "") {
    const row = document.createElement("div");
    row.className = "member-row";

    const input = document.createElement("input");
    input.type = "text";
    input.name = "miembros";
    input.className = "glass-input";
    input.placeholder = "Nombre del miembro";
    input.value = value;
    input.required = true;

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "btn-remove-member";
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

  form.addEventListener("submit", (e) => {
    const nombreEquipo = document.getElementById("nombre_equipo")?.value.trim();
    const miembros = Array.from(form.querySelectorAll("input[name='miembros']"))
      .map((input) => input.value.trim())
      .filter(Boolean);

    if (!nombreEquipo) {
      e.preventDefault();
      alert("El nombre del equipo es obligatorio.");
      document.getElementById("nombre_equipo")?.focus();
      return;
    }

    if (miembros.length === 0) {
      e.preventDefault();
      alert("Agrega al menos un miembro al equipo.");
      miembrosList.querySelector("input")?.focus();
      return;
    }

    if (btnGuardar) {
      btnGuardar.innerText = "Creando...";
      btnGuardar.disabled = true;
    }
  });
})();
