document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("st-dropzone");
  const fileInput = document.getElementById("st-file-input");
  const csvForm = document.getElementById("st-csv-form");
  const searchInput = document.getElementById("st-search-input");
  const statusFilter = document.getElementById("st-status-filter");
  const teamFilter = document.getElementById("st-team-filter");
  const tbody = document.getElementById("st-tbody");

  const addBtn = document.getElementById("st-add-btn") || document.getElementById("add-btn");

  function applyFilters() {
    if (!tbody) return;
    const q = (searchInput?.value || "").trim().toLowerCase();
    const status = statusFilter?.value || "all";
    const team = teamFilter?.value || "all";

    Array.from(tbody.querySelectorAll("tr[data-padron]")).forEach((tr) => {
      const rowNombre = (tr.dataset.nombre || "").toLowerCase();
      const rowApellido = (tr.dataset.apellido || "").toLowerCase();
      const rowPadron = (tr.dataset.padron || "").toLowerCase();
      const rowStatus = tr.dataset.status || "active";
      const rowTeam = (tr.dataset.team || "").toLowerCase();

      const fullName = `${rowNombre} ${rowApellido}`.trim();
      const matchQuery = q === "" || fullName.includes(q) || rowPadron.includes(q);
      const matchStatus = status === "all" || rowStatus === status;
      const matchTeam = team === "all" || rowTeam === team.toLowerCase();

      tr.style.display = matchQuery && matchStatus && matchTeam ? "" : "none";
    });
  }

  if (dropzone && fileInput && csvForm) {
    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("dragover", (e) => e.preventDefault());
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        csvForm.submit();
      }
    });
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) csvForm.submit();
    });
  }

  searchInput?.addEventListener("input", applyFilters);
  statusFilter?.addEventListener("change", applyFilters);
  teamFilter?.addEventListener("change", applyFilters);

  applyFilters();
});

document.addEventListener("DOMContentLoaded", () => {
  // ─── 1. LÓGICA DE FILTROS Y CSV ───
  const dropzone = document.getElementById("st-dropzone");
  const fileInput = document.getElementById("st-file-input");
  const csvForm = document.getElementById("st-csv-form");
  const searchInput = document.getElementById("st-search-input");
  const statusFilter = document.getElementById("st-status-filter");
  const teamFilter = document.getElementById("st-team-filter");
  const tbody = document.getElementById("st-tbody");

  function applyFilters() {
    if (!tbody) return;
    const q = (searchInput?.value || "").trim().toLowerCase();
    const status = statusFilter?.value || "all";
    const team = teamFilter?.value || "all";

    Array.from(tbody.querySelectorAll("tr[data-padron]")).forEach((tr) => {
      const rowNombre = (tr.dataset.nombre || "").toLowerCase();
      const rowApellido = (tr.dataset.apellido || "").toLowerCase();
      const rowPadron = (tr.dataset.padron || "").toLowerCase();
      const rowStatus = tr.dataset.status || "active";
      const rowTeam = (tr.dataset.team || "").toLowerCase();

      const fullName = `${rowNombre} ${rowApellido}`.trim();
      const matchQuery = q === "" || fullName.includes(q) || rowPadron.includes(q);
      const matchStatus = status === "all" || rowStatus === status;
      const matchTeam = team === "all" || rowTeam === team.toLowerCase();

      tr.style.display = matchQuery && matchStatus && matchTeam ? "" : "none";
    });
  }

  if (dropzone && fileInput && csvForm) {
    dropzone.addEventListener("click", () => fileInput.click());
    dropzone.addEventListener("dragover", (e) => e.preventDefault());
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        csvForm.submit();
      }
    });
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) csvForm.submit();
    });
  }

  searchInput?.addEventListener("input", applyFilters);
  statusFilter?.addEventListener("change", applyFilters);
  teamFilter?.addEventListener("change", applyFilters);

  applyFilters();

  const layoutEl = document.querySelector(".cm-layout");
  const classroomId = layoutEl ? layoutEl.getAttribute("data-classroom-id") : window.location.pathname.split('/')[2];

  const gradesModal = document.getElementById("grades-modal");
  const gradesModalTitle = document.getElementById("grades-modal-title");
  const gradesModalSubtitle = document.getElementById("grades-modal-subtitle");
  const gradesModalTableBody = document.getElementById("grades-modal-table-body");
  const btnClose = document.getElementById("grades-modal-close");
  const btnCancel = document.getElementById("grades-modal-cancel-btn");

  function hideGradesModal() {
    if (gradesModal) gradesModal.classList.add("hidden");
  }

  document.body.addEventListener("click", (e) => {

    const targetBtn = e.target.closest('[data-action="open-grades-modal"]');
    if (targetBtn) {
      const userId = targetBtn.getAttribute("data-user-id");
      const alumnoNombre = targetBtn.getAttribute("data-alumno-nombre");
      const alumnoPromedio = targetBtn.getAttribute("data-alumno-promedio");

      let gradesArray = [];
      try {
        gradesArray = JSON.parse(targetBtn.getAttribute("data-notas") || "[]");
      } catch (err) {
        console.error("Error al parsear las calificaciones:", err);
      }

      if (gradesModalTitle) gradesModalTitle.innerHTML = `✨ Notas de ${alumnoNombre}`;
      if (gradesModalSubtitle) gradesModalSubtitle.textContent = `Promedio general acumulado: ${alumnoPromedio}`;

      if (gradesModalTableBody) {
        gradesModalTableBody.innerHTML = "";

        if (gradesArray.length === 0) {
          gradesModalTableBody.innerHTML = `
            <tr>
              <td colspan="3" style="text-align: center; color: #64748b; padding: 2rem 0; font-size: 0.95rem;">
                Este estudiante no registra calificaciones.
              </td>
            </tr>`;
        } else {
          gradesArray.forEach((item) => {
            const evalName = item.evaluation_name || "Evaluación";
            const scoreVal = item.score !== undefined && item.score !== null ? item.score : "-";
            const evalId = item.evaluation_id;
            const formEditId = `form-edit-${evalId}-${userId}`;

            const tr = document.createElement("tr");
            tr.style.borderBottom = "1px solid rgba(0,0,0,0.05)";

            tr.innerHTML = `
              <td style="padding: 12px 8px; color: #334155; font-weight: 500; font-size: 0.95rem;">${evalName}</td>
              
              <td style="padding: 12px 8px; text-align: center; font-weight: 800; font-size: 1rem; color: #334155;">
                <span class="score-text">${scoreVal}</span>
                <input type="number" name="score" form="${formEditId}" class="edit-score-input hidden" value="${scoreVal}" step="0.1" style="width: 60px; text-align: center; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px;" required>
              </td>
              
              <td style="padding: 12px 8px; text-align: center;">
                <div class="action-buttons-inline view-mode">
                  <button type="button" class="st-action-btn st-action-btn-edit btn-edit-grade" title="Editar">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" width="15" height="15">
                      <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
                    </svg>
                  </button>
                  
                  <form action="/aulas/${classroomId}/evaluaciones/${evalId}/notas/${userId}/eliminar" method="POST" style="display: inline; margin: 0;" onsubmit="return confirm('¿Estás seguro de que deseas eliminar esta nota?');">
                    <button type="submit" class="st-action-btn st-action-btn-delete" title="Eliminar">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" width="15" height="15">
                        <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </form>
                </div>
                
                <div class="action-buttons-inline edit-mode hidden">
                  <form id="${formEditId}" action="/aulas/${classroomId}/evaluaciones/${evalId}/notas/${userId}/editar" method="POST" style="display: inline; margin: 0;">
                    <button type="submit" class="st-action-btn st-action-btn-confirm" title="Guardar">✔</button>
                  </form>
                  <button type="button" class="st-action-btn st-action-btn-delete btn-cancel-grade" title="Cancelar">✖</button>
                </div>
              </td>
            `;
            gradesModalTableBody.appendChild(tr);
          });
        }
      }
      if (gradesModal) gradesModal.classList.remove("hidden");
      return;
    }

    if (e.target.closest(".btn-edit-grade")) {
      const tr = e.target.closest("tr");
      if (tr) {
        tr.querySelector(".score-text").classList.add("hidden");
        tr.querySelector(".view-mode").classList.add("hidden");

        tr.querySelector(".edit-score-input").classList.remove("hidden");
        tr.querySelector(".edit-mode").classList.remove("hidden");
      }
      return;
    }

    if (e.target.closest(".btn-cancel-grade")) {
      const tr = e.target.closest("tr");
      if (tr) {
        tr.querySelector(".edit-score-input").classList.add("hidden");
        tr.querySelector(".edit-mode").classList.add("hidden");

        tr.querySelector(".score-text").classList.remove("hidden");
        tr.querySelector(".view-mode").classList.remove("hidden");

        tr.querySelector(".edit-score-input").value = tr.querySelector(".score-text").textContent.trim();
      }
      return;
    }
  });

  if (btnClose) btnClose.addEventListener("click", hideGradesModal);
  if (btnCancel) btnCancel.addEventListener("click", hideGradesModal);
  if (gradesModal) {
    gradesModal.addEventListener("click", (e) => {
      if (e.target === gradesModal) hideGradesModal();
    });
  }
});