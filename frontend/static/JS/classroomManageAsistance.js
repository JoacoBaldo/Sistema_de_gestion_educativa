import { createCmrToast } from "./common/ui.js";
import { requireAuth } from "./common/auth.js";

(function () {
  requireAuth();
  const showToast = createCmrToast();
  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id") || "";

  const qrContainer = document.getElementById("at-qrcode");
  const codeText = document.getElementById("at-code-text");
  const sessionDateEl = document.getElementById("at-session-date");
  const recordsTbody = document.getElementById("at-records-tbody");
  const searchInput = document.getElementById("at-search");
  const emailModal = document.getElementById("at-email-modal");
  const emailForm = document.getElementById("at-email-form");
  const emailTo = document.getElementById("at-email-to");
  const emailPreview = document.getElementById("at-email-code-preview");
  const statToday = document.getElementById("at-stat-today");
  const statRate = document.getElementById("at-stat-rate");
  const QRCodeLib = globalThis.QRCode;

  let currentToken = "";

  function todayIso() {
    return new Date().toISOString().slice(0, 10);
  }

  function formatSessionDate() {
    const dateStr = todayIso();
    return new Date(`${dateStr}T12:00:00`).toLocaleDateString("es-AR", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  function renderQrPlaceholder() {
    currentToken = `Aula ${classroomId} — QR no disponible sin endpoint de asistencia`;
    if (codeText) codeText.textContent = currentToken;
    if (sessionDateEl) sessionDateEl.textContent = formatSessionDate();
    if (emailPreview) emailPreview.textContent = currentToken;
    if (qrContainer) {
      qrContainer.innerHTML =
        '<p class="cmr-empty-inline">Generación de QR vía API no implementada.</p>';
    }
  }

  function renderRecordsEmpty() {
    if (!recordsTbody) return;
    recordsTbody.innerHTML = "";
    const row = document.createElement("tr");
    row.innerHTML =
      '<td colspan="4">Sin registros (endpoints GET/PATCH de asistencia no disponibles).</td>';
    recordsTbody.appendChild(row);
  }

  function updateStatsEmpty() {
    if (statToday) statToday.textContent = "—";
    if (statRate) statRate.textContent = "—";
  }

  function openEmailModal() {
    emailModal?.classList.remove("hidden");
  }

  function closeEmailModal() {
    emailModal?.classList.add("hidden");
  }

  renderRecordsEmpty();
  updateStatsEmpty();
  renderQrPlaceholder();

  searchInput?.addEventListener("input", renderRecordsEmpty);

  document.getElementById("at-generate")?.addEventListener("click", () => {
    showToast("Generación de QR no disponible en la API actual.");
    renderQrPlaceholder();
  });
  document.getElementById("at-send-email")?.addEventListener("click", openEmailModal);
  document.getElementById("at-email-all")?.addEventListener("click", openEmailModal);
  document.getElementById("at-download-png")?.addEventListener("click", () => {
    showToast("Descarga de QR no disponible sin generación en servidor.");
  });
  document.getElementById("at-email-cancel")?.addEventListener("click", closeEmailModal);
  emailModal?.addEventListener("click", (e) => {
    if (e.target === emailModal) closeEmailModal();
  });

  emailForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const to = emailTo?.value?.trim();
    if (!to) return;
    closeEmailModal();
    showToast("Envío de QR por email no disponible (endpoint no implementado).");
  });
})();
