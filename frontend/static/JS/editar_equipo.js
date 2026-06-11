const editTeamModal = document.getElementById("tm-edit-team-modal");
const formEditarEquipo = document.getElementById("formEditarEquipo");
const btnEditTeamClose = document.getElementById("tm-edit-team-close");
const btnEditTeamCancel = document.getElementById("tm-edit-team-cancel-btn");
const btnEditAddMember = document.getElementById("btn-edit-add-member");
const editMiembrosList = document.getElementById("edit-miembros-list");
const memberTemplate = document.getElementById("tm-member-select-template");

function crearFilaMiembro(selectedId = "") {
  if (!memberTemplate || !editMiembrosList) return null;
  const fragment = memberTemplate.content.cloneNode(true);
  const row = fragment.querySelector(".glass-list-row--member");
  const select = row?.querySelector("select");
  if (select && selectedId) {
    select.value = String(selectedId);
  }
  row?.querySelector(".glass-btn-remove")?.addEventListener("click", (event) => {
    event.preventDefault();
    row.remove();
  });
  editMiembrosList.appendChild(fragment);
  return row;
}

window.abrirModalEditarEquipo = function (teamId, teamName, members = []) {
  document.getElementById("edit_team_id").value = teamId;
  document.getElementById("edit_nombre_equipo").value = teamName;
  formEditarEquipo.action = `/api/v1/teams/${teamId}`;

  editMiembrosList.innerHTML = "";
  if (members && members.length) {
    members.forEach((memberId) => crearFilaMiembro(memberId));
  } else {
    crearFilaMiembro();
  }

  editTeamModal.classList.remove("hidden");
};

function cerrarModalEditarEquipo() {
  editTeamModal.classList.add("hidden");
  formEditarEquipo.reset();
}

btnEditTeamClose?.addEventListener("click", cerrarModalEditarEquipo);
btnEditTeamCancel?.addEventListener("click", cerrarModalEditarEquipo);

btnEditAddMember?.addEventListener("click", (event) => {
  event.preventDefault();
  crearFilaMiembro();
});

document.getElementById("tm-grid")?.addEventListener("click", (event) => {
  const editBtn = event.target.closest(".tm-edit-btn");
  if (!editBtn) return;
  event.preventDefault();
  const miembros = (editBtn.dataset.miembros || "")
    .split(",")
    .map((id) => id.trim())
    .filter(Boolean);
  window.abrirModalEditarEquipo(editBtn.dataset.id, editBtn.dataset.nombre, miembros);
});

formEditarEquipo?.addEventListener("submit", (event) => {
  const teamName = document.getElementById("edit_nombre_equipo")?.value.trim();
  const selects = editMiembrosList?.querySelectorAll("select[name='miembros']") || [];
  const miembros = Array.from(selects)
    .map((select) => select.value.trim())
    .filter(Boolean);

  if (!teamName) {
    alert("El nombre del equipo es requerido");
    event.preventDefault();
    return;
  }

  if (!miembros.length) {
    alert("Al menos un miembro es requerido");
    event.preventDefault();
  }
});

editTeamModal?.addEventListener("click", (event) => {
  if (event.target === editTeamModal) {
    cerrarModalEditarEquipo();
  }
});
