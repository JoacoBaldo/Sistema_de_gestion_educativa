const editTeamModal = document.getElementById('tm-edit-team-modal');
const formEditarEquipo = document.getElementById('formEditarEquipo');
const btnEditTeamClose = document.getElementById('tm-edit-team-close');
const btnEditTeamCancel = document.getElementById('tm-edit-team-cancel-btn');
const btnEditAddMember = document.getElementById('btn-edit-add-member');
const editMiembrosList = document.getElementById('edit-miembros-list');

window.abrirModalEditarEquipo = function (teamId, teamName, members = []) {
    document.getElementById('edit_team_id').value = teamId;
    document.getElementById('edit_nombre_equipo').value = teamName;
    document.getElementById('edit_token').value = localStorage.getItem("token") || "";

    editMiembrosList.innerHTML = '';

    if (members && members.length > 0) {
        members.forEach(member => {
            agregarFilaMiembro(member);
        });
    } else {
        agregarFilaMiembro('');
    }

    editTeamModal.classList.remove('hidden');
};

function cerrarModalEditarEquipo() {
    editTeamModal.classList.add('hidden');
    formEditarEquipo.reset();
}

function agregarFilaMiembro(memberName = '') {
    const fila = document.createElement('div');
    fila.className = 'glass-list-row--member';
    fila.innerHTML = `
        <input type="text" name="miembros" class="glass-input" placeholder="Nombre del miembro" value="${memberName}" required>
        <button type="button" class="glass-btn-remove" aria-label="Eliminar miembro">✕</button>
    `;

    const btnRemove = fila.querySelector('.glass-btn-remove');
    btnRemove.addEventListener('click', (e) => {
        e.preventDefault();
        fila.remove();
    });

    editMiembrosList.appendChild(fila);
}

btnEditTeamClose.addEventListener('click', cerrarModalEditarEquipo);
btnEditTeamCancel.addEventListener('click', cerrarModalEditarEquipo);

btnEditAddMember.addEventListener('click', (e) => {
    e.preventDefault();
    agregarFilaMiembro();
});

editMiembrosList.addEventListener('click', (e) => {
    if (e.target.classList.contains('glass-btn-remove')) {
        e.preventDefault();
        e.target.closest('.glass-list-row--member').remove();
    }
});

formEditarEquipo.addEventListener('submit', (e) => {
    const teamId = document.getElementById('edit_team_id').value;
    const teamName = document.getElementById('edit_nombre_equipo').value.trim();

    const miembrosInputs = editMiembrosList.querySelectorAll('input[name="miembros"]');
    const miembros = Array.from(miembrosInputs).map(input => input.value.trim()).filter(v => v);

    if (!teamName) {
        alert('El nombre del equipo es requerido');
        e.preventDefault();
        return;
    }

    if (miembros.length === 0) {
        alert('Al menos un miembro es requerido');
        e.preventDefault();
        return;
    }

    // Actualizar el action del formulario para apuntar a la ruta correcta
    formEditarEquipo.action = `/equipos/${teamId}/actualizar`;
    // El formulario se enviará normalmente con POST
});

editTeamModal.addEventListener('click', (e) => {
    if (e.target === editTeamModal) {
        cerrarModalEditarEquipo();
    }
});