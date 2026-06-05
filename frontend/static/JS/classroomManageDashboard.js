import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import { authHeaders, requireAuth } from "./common/auth.js";
import { createCmrToast, escapeHtml, getJsPdfConstructor } from "./common/ui.js";

(function () {
  const showToast = createCmrToast();
  const tbody = document.getElementById("db-students-tbody");
  const searchInput = document.getElementById("db-search");
  const emptyMsg = document.getElementById("db-empty");
  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id");
  const tableHead = document.querySelector("#db-page .st-table thead tr");
  const tableSectionTitle = document.querySelector("#db-page .cmr-table-head h2");
  const enrollmentChart = document.getElementById("db-enrollment-chart");
  const donutCenter = document.getElementById("db-donut-center");
  const approvalLegend = document.getElementById("db-approval-legend");

  if (!requireAuth() || !classroomId) return;

  let professors = [];

  function roleLabel(roleId) {
    const map = { 1: "Profesor", 2: "Ayudante", 7: "Administrador" };
    return map[roleId] ?? `Rol ${roleId}`;
  }

  function matchesProfessorSearch(p) {
    const q = (searchInput?.value || "").trim().toLowerCase();
    if (!q) return true;
    const hay = `${p.username} ${p.email}`.toLowerCase();
    return hay.includes(q);
  }

  function renderProfessorsTable() {
    if (!tbody) return;
    const rows = professors.filter(matchesProfessorSearch);
    tbody.innerHTML = rows
      .map(
        (p) => `<tr data-user-id="${p.id}">
          <td>${escapeHtml(p.username)}</td>
          <td class="st-col-email">${escapeHtml(p.email)}</td>
          <td>${escapeHtml(roleLabel(p.role_id))}</td>
          <td>
            <button type="button" class="st-btn st-btn-ghost db-remove-user" data-user-id="${p.id}"
              data-username="${escapeHtml(p.username)}">Quitar acceso</button>
          </td>
        </tr>`
      )
      .join("");
    if (emptyMsg) {
      emptyMsg.textContent = "No hay colaboradores que coincidan con la búsqueda.";
      emptyMsg.hidden = rows.length > 0;
    }
  }

  function updateKpisEmpty() {
    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };
    set("db-kpi-total", "—");
    set("db-kpi-active", "—");
    set("db-kpi-approval", "—");
    set("db-kpi-dropout", "—");
  }

  function clearCharts() {
    if (enrollmentChart) {
      enrollmentChart.innerHTML =
        '<p class="cmr-empty-inline">Sin datos (endpoint de matrícula no disponible).</p>';
    }
    if (donutCenter) donutCenter.innerHTML = `—<span>Sin datos</span>`;
    if (approvalLegend) {
      approvalLegend.innerHTML =
        '<span class="cmr-legend__item">Sin endpoint de estadísticas de alumnos.</span>';
    }
  }

  async function loadProfessors() {
    try {
      const response = await requestJson(
        apiUrl(`/api/v1/classrooms/${encodeURIComponent(classroomId)}/professors`),
        { headers: authHeaders() }
      );
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "No se pudieron cargar colaboradores"));
      }
      professors = Array.isArray(body) ? body : [];
      renderProfessorsTable();
    } catch (err) {
      console.error(err);
      if (tbody) tbody.innerHTML = "";
      if (emptyMsg) {
        emptyMsg.textContent = err.message || "Error al cargar colaboradores.";
        emptyMsg.hidden = false;
      }
    }
  }

  tbody?.addEventListener("click", async (e) => {
    const btn = e.target.closest(".db-remove-user");
    if (!btn) return;
    const userId = btn.dataset.userId;
    const username = btn.dataset.username || "usuario";
    if (!confirm(`¿Quitar acceso de ${username}?`)) return;

    try {
      const response = await requestJson(
        apiUrl(
          `/api/v1/classrooms/${encodeURIComponent(classroomId)}/user/${encodeURIComponent(userId)}`
        ),
        { method: "DELETE", headers: authHeaders() }
      );
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "No se pudo quitar el acceso"));
      }
      professors = professors.filter((p) => String(p.id) !== String(userId));
      renderProfessorsTable();
      showToast("Acceso revocado.");
    } catch (err) {
      console.error(err);
      showToast(err.message || "Error al quitar acceso.");
    }
  });

  function exportProfessorsPdf() {
    const jsPDF = getJsPdfConstructor();
    if (!jsPDF) {
      showToast("Biblioteca PDF no disponible.");
      return;
    }
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text(`Colaboradores — Aula ${classroomId}`, 14, 16);
    const data = professors.map((p) => [p.username, p.email, roleLabel(p.role_id)]);
    if (typeof doc.autoTable === "function") {
      doc.autoTable({
        head: [["Usuario", "Email", "Rol"]],
        body: data,
        startY: 24,
        headStyles: { fillColor: [99, 102, 241] },
      });
    }
    doc.save(`colaboradores-aula-${classroomId}.pdf`);
    showToast("PDF descargado.");
  }

  function bindPdfButtons() {
    document.querySelectorAll("[data-pdf]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const type = btn.getAttribute("data-pdf");
        if (type === "students" || type === "teams" || type === "stats") {
          showToast("Exportación no disponible sin endpoint de alumnos/equipos.");
          return;
        }
        exportProfessorsPdf();
      });
    });
  }

  if (tableHead) {
    tableHead.innerHTML = `
      <th>Usuario</th>
      <th class="st-col-email">Email</th>
      <th>Rol</th>
      <th>Acciones</th>`;
  }
  if (tableSectionTitle) {
    tableSectionTitle.textContent = "Colaboradores del aula";
  }

  searchInput?.addEventListener("input", renderProfessorsTable);
  updateKpisEmpty();
  clearCharts();
  bindPdfButtons();
  loadProfessors();
})();
