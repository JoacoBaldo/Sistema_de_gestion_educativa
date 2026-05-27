(() => {
  const gridEl = document.getElementById("classroomsGrid");
  if (!gridEl) return;

  const btnCrearAula = document.getElementById("btnCrearAula");
  if (btnCrearAula) {
    btnCrearAula.addEventListener("click", () => {
      window.location.href = "/aulas/crear";
    });
  }

  const mockClassrooms = [
    {
      id: 1,
      name: "Sistemas Operativos",
      chair: "Cátedra G",
      students: 45,
      schedules: ["Lunes 14:00-16:00", "Miércoles 14:00-16:00"],
      theme: "theme-violet",
    },
    {
      id: 2,
      name: "Algoritmos y\nEstructuras de Datos",
      chair: "Cátedra A",
      students: 52,
      schedules: ["Martes 10:00-12:00", "Jueves 10:00-12:00"],
      theme: "theme-aqua",
    },
    {
      id: 3,
      name: "Bases de Datos",
      chair: "Cátedra B",
      students: 38,
      schedules: ["Miércoles 16:00-18:00", "Viernes 16:00-18:00"],
      theme: "theme-emerald",
    },
    {
      id: 4,
      name: "Ingeniería de Software",
      chair: "Cátedra C",
      students: 41,
      schedules: ["Lunes 10:00-13:00"],
      theme: "theme-coral",
    },
    {
      id: 5,
      name: "Redes y Comunicaciones",
      chair: "Cátedra D",
      students: 36,
      schedules: ["Jueves 14:00-17:00"],
      theme: "theme-electric",
    },
    {
      id: 6,
      name: "Inteligencia Artificial",
      chair: "Cátedra E",
      students: 29,
      schedules: ["Viernes 10:00-13:00"],
      theme: "theme-orange",
    },
  ];

  function renderMock() {
    gridEl.innerHTML = mockClassrooms.map(classroomCardTemplate).join("");
  }

  function classroomCardTemplate(model) {
    const title = (model?.name ?? "").replace(/\n/g, "<br>");
    const chair = escapeHtml(model?.chair ?? "");
    const students = escapeHtml(String(model?.students ?? 0));
    const theme = escapeHtml(model?.theme ?? "theme-violet");
    const id = escapeHtml(String(model?.id ?? ""));
    const shareName = encodeURIComponent(String(model?.name ?? ""));
    const schedules = Array.isArray(model?.schedules) ? model.schedules : [];

    const scheduleHtml = schedules
      .map((s) => {
        return `
          <div class="um-schedule__row">
            <span class="um-ico um-ico--clock" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 10.41 3.3 3.3a1 1 0 0 1-1.42 1.42l-3.6-3.6A1 1 0 0 1 11 13V7a1 1 0 1 1 2 0v5.41z" fill="currentColor"/>
              </svg>
            </span>
            <span>${escapeHtml(s)}</span>
          </div>
        `;
      })
      .join("");

    return `
      <article class="um-card ${theme}">
        <div class="um-card__top">
          <div class="um-card__title">${title}</div>
          <div class="um-card__chair">${chair}</div>
          <div class="um-pill">
            <span class="um-ico um-ico--users" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M16 11a4 4 0 1 0-3.2-6.4A4 4 0 0 0 16 11zm-8 0a4 4 0 1 0-3.2-6.4A4 4 0 0 0 8 11zm0 2c-2.67 0-8 1.34-8 4v1a1 1 0 0 0 1 1h10.17a5.9 5.9 0 0 1 0-2H2c.8-1.1 3.6-2 6-2 1.03 0 2.2.17 3.26.48.25-.7.63-1.34 1.1-1.9C11.1 13.2 9.5 13 8 13zm8 0c-.7 0-1.44.05-2.2.14a5.9 5.9 0 0 1 1.73 1.93c.16-.01.31-.02.47-.02 2.33 0 5.2.9 6 2h-5.1a5.92 5.92 0 0 1 .27 2H23a1 1 0 0 0 1-1v-1c0-2.66-5.33-4-8-4z" fill="currentColor"/>
              </svg>
            </span>
            <span>${students} Alumnos</span>
          </div>
        </div>

        <div class="um-card__bottom">
          <div class="um-schedule">
            ${scheduleHtml}
          </div>
        </div>

        <div class="um-card__footer">
          <a class="um-link um-link--muted" href="/clases/compartir?id=${id}&nombre=${shareName}">
            <span class="um-ico um-ico--share" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7a2.5 2.5 0 0 0 0-1.39l7-4.11A2.99 2.99 0 1 0 14 5a2.9 2.9 0 0 0 .05.52l-7 4.11A3 3 0 1 0 6 15a2.9 2.9 0 0 0 1.05-.2l7.13 4.18c-.02.14-.04.28-.04.42a3 3 0 1 0 3-3.32z" fill="currentColor"/>
              </svg>
            </span>
            <span>Compartir</span>
          </a>

          <a class="um-link um-link--primary" href="#">
            <span>Abrir aula</span>
            <span class="um-arrow" aria-hidden="true">→</span>
          </a>
        </div>
      </article>
    `;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  renderMock();
})();



