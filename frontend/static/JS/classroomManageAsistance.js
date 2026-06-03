(function () {
  const RECORDS = [
    { fecha: "2026-06-03", hora: "09:00", presentes: "42/45", pct: 93 },
    { fecha: "2026-06-02", hora: "11:00", presentes: "38/42", pct: 90 },
    { fecha: "2026-06-01", hora: "14:00", presentes: "35/40", pct: 88 },
    { fecha: "2026-05-30", hora: "09:00", presentes: "40/45", pct: 89 },
    { fecha: "2026-05-29", hora: "16:00", presentes: "28/35", pct: 80 },
  ];

  const TODAY_ATTENDANCE = 42;

  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id") || "1";

  const qrContainer = document.getElementById("at-qrcode");
  const codeText = document.getElementById("at-code-text");
  const sessionDateEl = document.getElementById("at-session-date");
  const autoRefresh = document.getElementById("at-auto-refresh");
  const recordsTbody = document.getElementById("at-records-tbody");
  const searchInput = document.getElementById("at-search");
  const emailModal = document.getElementById("at-email-modal");
  const emailForm = document.getElementById("at-email-form");
  const emailTo = document.getElementById("at-email-to");
  const emailPreview = document.getElementById("at-email-code-preview");
  const statToday = document.getElementById("at-stat-today");
  const statRate = document.getElementById("at-stat-rate");

  let refreshTimer = null;
  let currentToken = "";

  function todayIso() {
    return new Date().toISOString().slice(0, 10);
  }

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function buildToken() {
    const dateStr = todayIso();
    const now = new Date();
    const stamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
    const nonce = Math.random().toString(36).slice(2, 8).toUpperCase();
    return `UNI-ATT-${classroomId}-${dateStr}-${stamp}-${nonce}`;
  }

  function formatSessionDate() {
    const dateStr = todayIso();
    return new Date(dateStr + "T12:00:00").toLocaleDateString("es-AR", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  function showToast(msg) {
    let toast = document.getElementById("cmr-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "cmr-toast";
      toast.className = "cmr-toast";
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add("is-visible");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove("is-visible"), 2800);
  }

  function renderQr() {
    currentToken = buildToken();
    if (codeText) codeText.textContent = currentToken;
    if (sessionDateEl) sessionDateEl.textContent = formatSessionDate();
    if (emailPreview) emailPreview.textContent = currentToken;

    if (!qrContainer || typeof QRCode === "undefined") return;
    qrContainer.innerHTML = "";
    new QRCode(qrContainer, {
      text: currentToken,
      width: 200,
      height: 200,
      colorDark: "#0f172a",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.M,
    });
  }

  function scheduleRefresh() {
    clearInterval(refreshTimer);
    if (!autoRefresh?.checked) return;
    refreshTimer = setInterval(renderQr, 30000);
  }

  function openEmailModal() {
    if (!currentToken) renderQr();
    if (emailPreview) emailPreview.textContent = currentToken;
    emailModal?.classList.remove("hidden");
  }

  function closeEmailModal() {
    emailModal?.classList.add("hidden");
  }

  function downloadPng() {
    const canvas = qrContainer?.querySelector("canvas");
    const img = qrContainer?.querySelector("img");
    if (!canvas && !img) {
      showToast("Genera un QR primero.");
      return;
    }
    const link = document.createElement("a");
    link.download = `qr-asistencia-${Date.now()}.png`;
    if (canvas) link.href = canvas.toDataURL("image/png");
    else if (img?.src) link.href = img.src;
    link.click();
    showToast("QR descargado.");
  }

  function renderRecords() {
    if (!recordsTbody) return;
    const q = (searchInput?.value || "").trim().toLowerCase();
    const rows = RECORDS.filter((r) => !q || r.fecha.includes(q));
    recordsTbody.innerHTML = rows
      .map(
        (r) => `<tr>
          <td>${r.fecha}</td>
          <td>${r.hora}</td>
          <td>${r.presentes}</td>
          <td class="cmr-pct-good">${r.pct}%</td>
        </tr>`
      )
      .join("");
  }

  function updateStats() {
    if (statToday) statToday.textContent = String(TODAY_ATTENDANCE);
    const avg = Math.round(RECORDS.reduce((s, r) => s + r.pct, 0) / RECORDS.length);
    if (statRate) statRate.textContent = `${avg}%`;
  }

  updateStats();
  renderRecords();
  renderQr();
  scheduleRefresh();

  autoRefresh?.addEventListener("change", scheduleRefresh);
  searchInput?.addEventListener("input", renderRecords);

  document.getElementById("at-generate")?.addEventListener("click", renderQr);
  document.getElementById("at-send-email")?.addEventListener("click", openEmailModal);
  document.getElementById("at-email-all")?.addEventListener("click", openEmailModal);
  document.getElementById("at-download-png")?.addEventListener("click", downloadPng);
  document.getElementById("at-email-cancel")?.addEventListener("click", closeEmailModal);
  emailModal?.addEventListener("click", (e) => {
    if (e.target === emailModal) closeEmailModal();
  });

  emailForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const to = emailTo?.value?.trim();
    if (!to) return;
    closeEmailModal();
    showToast(`QR enviado a ${to} (simulación).`);
  });
})();
