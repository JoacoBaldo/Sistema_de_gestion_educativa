import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import {
  authHeaders,
  clearSession,
  getUser,
  requireAuth,
  userInitials,
} from "./common/auth.js";
import { escapeHtml, emitAppEvent, APP_EVENTS } from "./common/ui.js";

const THEMES = [
  "theme-violet",
  "theme-aqua",
  "theme-emerald",
  "theme-coral",
  "theme-electric",
  "theme-orange",
];

(() => {
  const gridEl = document.getElementById("classroomsGrid");
  if (!gridEl) return;

  if (!requireAuth()) return;

  const user = getUser();
  const avatarEl = document.querySelector(".um-avatar");
  const nameEl = document.querySelector(".um-user__name");
  if (avatarEl && user) avatarEl.textContent = userInitials(user.username);
  if (nameEl && user) nameEl.textContent = user.username || user.email || "Usuario";

  document.querySelector(".um-icon-btn.icon--danger")?.addEventListener("click", () => {
    clearSession();
    location.href = "/auth";
  });

  function formatSchedules(classroom) {
    const rows = [];
    if (classroom.class_day && classroom.class_start && classroom.class_end) {
      rows.push(`${classroom.class_day} ${classroom.class_start}-${classroom.class_end}`);
    }
    if (Array.isArray(classroom.academic_periods)) {
      classroom.academic_periods.forEach((p) => {
        if (p?.name && p?.period_start && p?.period_end) {
          rows.push(`${p.name}: ${p.period_start} — ${p.period_end}`);
        } else if (p?.name) {
          rows.push(p.name);
        }
      });
    }
    return rows;
  }

  function mapClassroom(raw, index) {
    return {
      id: raw.id,
      name: raw.name ?? "",
      chair: raw.department ?? "",
      students: raw.total_students ?? 0,
      schedules: formatSchedules(raw),
      theme: THEMES[index % THEMES.length],
    };
  }

  function classroomCardTemplate(model) {
    const title = (model?.name ?? "").replace(/\n/g, "<br>");
    const chair = escapeHtml(model?.chair ?? "");
    const students = escapeHtml(String(model?.students ?? 0));
    const theme = escapeHtml(model?.theme ?? "theme-violet");
    const id = escapeHtml(String(model?.id ?? ""));
    const shareName = escapeHtml(String(model?.name ?? "").replace(/\n/g, " "));
    const schedules = Array.isArray(model?.schedules) ? model.schedules : [];

    const scheduleHtml = schedules.length
      ? schedules
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
          .join("")
      : `<div class="um-schedule__row"><span>Sin horario cargado</span></div>`;

    return `
      <article class="um-card ${theme}">
        <div class="um-card__top">
          <div class="um-card__title">${title}</div>
          <div class="um-card__chair">${chair}</div>
          <div class="um-pill">
            <span class="um-ico um-ico--users" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" aria-hidden="true"><path fill="currentColor" d="M16 24a8 8 0 1 0 0-16a8 8 0 0 0 0 16Zm18 0a6 6 0 1 0 0-12a6 6 0 0 0 0 12ZM6.75 27A3.75 3.75 0 0 0 3 30.75V32s0 9 13 9s13-9 13-9v-1.25A3.75 3.75 0 0 0 25.25 27H6.75Zm21.924 11.089c1.376.558 3.119.911 5.325.911c10.5 0 10.5-8 10.5-8v-.25A3.75 3.75 0 0 0 40.75 27H29.607a5.728 5.728 0 0 1 1.391 3.75v1.295l-.001.057a7.565 7.565 0 0 1-.04.581a9.697 9.697 0 0 1-.241 1.324a10.684 10.684 0 0 1-2.042 4.082Z"/></svg>
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
          <a class="um-link um-link--muted" href="#" data-action="share" data-class-id="${id}" data-class-name="${shareName}">
            <span class="um-ico um-ico--share" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7a2.5 2.5 0 0 0 0-1.39l7-4.11A2.99 2.99 0 1 0 14 5a2.9 2.9 0 0 0 .05.52l-7 4.11A3 3 0 1 0 6 15a2.9 2.9 0 0 0 1.05-.2l7.13 4.18c-.02.14-.04.28-.04.42a3 3 0 1 0 3-3.32z" fill="currentColor"/>
              </svg>
            </span>
            <span>Compartir</span>
          </a>

          <a class="um-link um-link--primary" href="/aulas/${id}/gestionar">
            <span>Abrir aula</span>
            <span class="um-arrow" aria-hidden="true">→</span>
          </a>
        </div>
      </article>
    `;
  }

  async function loadClassrooms() {
    gridEl.innerHTML = `<p class="um-loading">Cargando aulas...</p>`;
    try {
      const response = await requestJson(
        apiUrl(`/api/v1/classrooms/${user.id}`),
        { headers: authHeaders() }
      );
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "No se pudieron cargar las aulas"));
      }
      const list = Array.isArray(body) ? body : [];
      if (!list.length) {
        gridEl.innerHTML = `<p class="um-empty">No tenés aulas asignadas. Creá una con el botón superior.</p>`;
        return;
      }
      gridEl.innerHTML = list.map((c, i) => classroomCardTemplate(mapClassroom(c, i))).join("");
    } catch (err) {
      console.error(err);
      gridEl.innerHTML = `<p class="um-empty">${escapeHtml(err.message || "Error al cargar aulas")}</p>`;
    }
  }

  gridEl.addEventListener("click", (event) => {
    const shareLink = event.target.closest('[data-action="share"]');
    if (!shareLink) return;

    event.preventDefault();
    emitAppEvent(APP_EVENTS.SHARE_MODAL_OPEN, {
      classId: shareLink.dataset.classId || "",
      className: shareLink.dataset.className || "",
    });
  });

  loadClassrooms();
})();
