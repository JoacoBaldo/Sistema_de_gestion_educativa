import { createCmrToast, getJsPdfConstructor } from "./common/ui.js";

(function () {
  const showToast = createCmrToast();
  const STUDENTS = [
    { nombre: "Emma", apellido: "Thompson", padron: "S001", email: "emma.t@universidad.edu", estado: "active", equipo: "Equipo Azul", approval: "approved" },
    { nombre: "Liam", apellido: "Chen", padron: "S002", email: "liam.c@universidad.edu", estado: "active", equipo: "Equipo Azul", approval: "pending" },
    { nombre: "Sofía", apellido: "Martínez", padron: "S003", email: "sofia.m@universidad.edu", estado: "active", equipo: "Team piolas", approval: "approved" },
    { nombre: "Noah", apellido: "Williams", padron: "S004", email: "noah.w@universidad.edu", estado: "active", equipo: "Equipo Verde", approval: "approved" },
    { nombre: "Olivia", apellido: "Brown", padron: "S005", email: "olivia.b@universidad.edu", estado: "active", equipo: "Team piolas", approval: "pending" },
    { nombre: "Ethan", apellido: "Davis", padron: "S006", email: "ethan.d@universidad.edu", estado: "active", equipo: "Equipo Verde", approval: "failed" },
    { nombre: "Ava", apellido: "Wilson", padron: "S007", email: "ava.w@universidad.edu", estado: "active", equipo: "Equipo Azul", approval: "approved" },
    { nombre: "Mason", apellido: "García", padron: "S008", email: "mason.g@universidad.edu", estado: "active", equipo: "Equipo Rojo", approval: "approved" },
    { nombre: "Lucas", apellido: "Ruiz", padron: "S009", email: "lucas.r@universidad.edu", estado: "abandoned", equipo: "—", approval: "pending" },
    { nombre: "Mía", apellido: "López", padron: "S010", email: "mia.l@universidad.edu", estado: "abandoned", equipo: "—", approval: "failed" },
  ];

  const TEAMS = [
    { id: "T01", nombre: "Team piolas", proyecto: "TP APIs", miembros: 3, estado: "Sin corregir" },
    { id: "T02", nombre: "Equipo Azul", proyecto: "Microservicios", miembros: 4, estado: "En revisión" },
    { id: "T03", nombre: "Equipo Verde", proyecto: "Base de datos", miembros: 3, estado: "Aprobado" },
    { id: "T04", nombre: "Equipo Rojo", proyecto: "Frontend SPA", miembros: 5, estado: "Pendiente" },
  ];

  const ENROLLMENT = [
    { label: "Ene", value: 32 },
    { label: "Feb", value: 36 },
    { label: "Mar", value: 39 },
    { label: "Abr", value: 41 },
    { label: "May", value: 45 },
  ];

  const APPROVAL = { approved: 35, pending: 7, failed: 3 };

  const tbody = document.getElementById("db-students-tbody");
  const searchInput = document.getElementById("db-search");
  const statusFilter = document.getElementById("db-filter-status");
  const teamFilter = document.getElementById("db-filter-team");
  const emptyMsg = document.getElementById("db-empty");
  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id") || "1";

  function statusBadge(approval) {
    const map = {
      approved: ["st-badge st-badge-active", "Aprobado"],
      pending: ["st-badge", "Pendiente"],
      failed: ["st-badge st-badge-dropped", "Reprobado"],
      active: ["st-badge st-badge-active", "Activo"],
    };
    const [cls, text] = map[approval] || map.active;
    return `<span class="${cls}">${text}</span>`;
  }

  function matchesFilters(s) {
    const q = (searchInput?.value || "").trim().toLowerCase();
    const status = statusFilter?.value || "all";
    const team = teamFilter?.value || "all";

    if (q) {
      const hay = `${s.nombre} ${s.apellido} ${s.padron}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (status !== "all") {
      if (status === "active" && s.estado !== "active") return false;
      if (status === "abandoned" && s.estado !== "abandoned") return false;
      if (!["active", "abandoned"].includes(status) && s.approval !== status) return false;
    }
    if (team !== "all" && s.equipo !== team) return false;
    return true;
  }

  function renderTable() {
    if (!tbody) return;
    const rows = STUDENTS.filter(matchesFilters);
    tbody.innerHTML = rows
      .map(
        (s) => `<tr data-padron="${s.padron}">
          <td>${s.nombre}</td><td>${s.apellido}</td><td>${s.padron}</td>
          <td class="st-col-email">${s.email}</td>
          <td>${statusBadge(s.approval)}</td><td>${s.equipo}</td>
        </tr>`
      )
      .join("");
    if (emptyMsg) {
      emptyMsg.hidden = rows.length > 0;
    }
  }

  function updateKpis() {
    const total = STUDENTS.length;
    const active = STUDENTS.filter((s) => s.estado === "active").length;
    const abandoned = STUDENTS.filter((s) => s.estado === "abandoned").length;
    const evaluated = STUDENTS.filter((s) => s.approval === "approved" || s.approval === "failed").length;
    const approved = STUDENTS.filter((s) => s.approval === "approved").length;
    const approvalRate = evaluated ? Math.round((approved / evaluated) * 100) : 0;
    const dropoutRate = total ? Math.round((abandoned / total) * 100) : 0;

    const set = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };
    set("db-kpi-total", String(total));
    set("db-kpi-active", String(active));
    set("db-kpi-approval", `${approvalRate}%`);
    set("db-kpi-dropout", `${dropoutRate}%`);
  }

  function populateTeamFilter() {
    if (!teamFilter) return;
    const teams = [...new Set(STUDENTS.map((s) => s.equipo))];
    teams.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t;
      teamFilter.appendChild(opt);
    });
  }

  function renderChart() {
    const wrap = document.getElementById("db-enrollment-chart");
    if (!wrap) return;
    const max = Math.max(...ENROLLMENT.map((e) => e.value), 1);
    wrap.innerHTML = ENROLLMENT.map((e) => {
      const h = Math.round((e.value / max) * 160);
      return `<div class="cmr-bar"><div class="cmr-bar__fill" style="height:${h}px" title="${e.value}"></div><span class="cmr-bar__label">${e.label}</span></div>`;
    }).join("");
  }

  function getSelectedColumns() {
    return [...document.querySelectorAll('input[name="db-col"]:checked')].map((el) => el.value);
  }

  function getFilteredStudents() {
    return STUDENTS.filter(matchesFilters);
  }

  function exportStudentsPdf() {
    const jsPDF = getJsPdfConstructor();
    if (!jsPDF) {
      showToast("Biblioteca PDF no disponible.");
      return;
    }
    const cols = getSelectedColumns();
    const labels = {
      nombre: "Nombre",
      apellido: "Apellido",
      padron: "Padrón",
      email: "Email",
      estado: "Estado",
      equipo: "Equipo",
    };
    const headers = cols.map((c) => labels[c] || c);
    const data = getFilteredStudents().map((s) =>
      cols.map((c) => {
        if (c === "estado") {
          const m = { approved: "Aprobado", pending: "Pendiente", failed: "Reprobado" };
          return m[s.approval] || s.estado;
        }
        return s[c] ?? "";
      })
    );

    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text(`Listado de alumnos — Aula ${classroomId}`, 14, 16);
    doc.setFontSize(10);
    doc.text(`Generado: ${new Date().toLocaleString("es-AR")}`, 14, 22);

    if (typeof doc.autoTable === "function") {
      doc.autoTable({
        head: [headers],
        body: data,
        startY: 28,
        styles: { fontSize: 9 },
        headStyles: { fillColor: [99, 102, 241] },
      });
    } else {
      let y = 30;
      data.forEach((row) => {
        doc.text(row.join(" | "), 14, y);
        y += 7;
      });
    }
    doc.save(`alumnos-aula-${classroomId}.pdf`);
    showToast("PDF de alumnos descargado.");
  }

  function exportStatsPdf() {
    const jsPDF = getJsPdfConstructor();
    if (!jsPDF) return;
    const total = APPROVAL.approved + APPROVAL.pending + APPROVAL.failed;
    const rate = Math.round((APPROVAL.approved / total) * 100);
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Estadísticas de aprobación", 14, 18);
    doc.setFontSize(11);
    doc.text(`Aula: ${classroomId}`, 14, 26);
    doc.text(`Tasa de aprobación: ${rate}%`, 14, 34);
    doc.text(`Aprobados: ${APPROVAL.approved}`, 14, 42);
    doc.text(`Pendientes: ${APPROVAL.pending}`, 14, 50);
    doc.text(`Reprobados: ${APPROVAL.failed}`, 14, 58);
    doc.text(`Asistencia promedio: 91.5%`, 14, 66);
    doc.text(`Total estudiantes: ${STUDENTS.length}`, 14, 74);
    doc.save(`estadisticas-aprobacion-${classroomId}.pdf`);
    showToast("PDF de estadísticas descargado.");
  }

  function exportTeamsPdf() {
    const jsPDF = getJsPdfConstructor();
    if (!jsPDF) return;
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text(`Listado de equipos — Aula ${classroomId}`, 14, 16);
    if (typeof doc.autoTable === "function") {
      doc.autoTable({
        head: [["ID", "Equipo", "Proyecto", "Miembros", "Estado"]],
        body: TEAMS.map((t) => [t.id, t.nombre, t.proyecto, String(t.miembros), t.estado]),
        startY: 24,
        headStyles: { fillColor: [99, 102, 241] },
      });
    }
    doc.save(`equipos-aula-${classroomId}.pdf`);
    showToast("PDF de equipos descargado.");
  }

  function bindPdfButtons() {
    document.querySelectorAll("[data-pdf]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const type = btn.getAttribute("data-pdf");
        if (type === "students") exportStudentsPdf();
        else if (type === "stats") exportStatsPdf();
        else if (type === "teams") exportTeamsPdf();
      });
    });
  }

  [searchInput, statusFilter, teamFilter].forEach((el) => {
    el?.addEventListener("input", renderTable);
    el?.addEventListener("change", renderTable);
  });

  populateTeamFilter();
  updateKpis();
  renderChart();
  renderTable();
  bindPdfButtons();
})();
