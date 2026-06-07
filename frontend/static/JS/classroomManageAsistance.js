import { createCmrToast } from "./common/ui.js";
import { requireAuth } from "./common/auth.js";

(function () {
  requireAuth();
  const showToast = createCmrToast();
  const layout = document.querySelector(".cm-layout");
  const classroomId = layout?.getAttribute("data-classroom-id") || "0";

  // Selectores del DOM
  const qrContainer = document.getElementById("at-qrcode");
  const codeText = document.getElementById("at-code-text");
  const sessionDateEl = document.getElementById("at-session-date");
  const recordsTbody = document.getElementById("at-records-tbody");
  const searchInput = document.getElementById("at-search");
  const emailModal = document.getElementById("at-email-modal");
  const emailForm = document.getElementById("at-email-form");
  const emailTo = document.getElementById("at-email-to");
  const emailPreview = document.getElementById("at-email-code-preview");
  const autoRefreshCheck = document.getElementById("at-auto-refresh");
  
  const QRCodeLib = globalThis.QRCode;
  let currentToken = "";
  let refreshInterval = null;

  // --- Funciones Auxiliares ---
  function todayIso() {
    return new Date().toISOString().slice(0, 10);
  }

  function formatSessionDate() {
    return new Date().toLocaleDateString("es-AR", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  // --- Búsqueda de Alumnos en la Tabla ---
  function applySearch() {
    if (!recordsTbody || !searchInput) return;
    const q = searchInput.value.trim().toLowerCase();
    Array.from(recordsTbody.querySelectorAll("tr[data-nombre]")).forEach((row) => {
      const nombre = (row.dataset.nombre || "").toLowerCase();
      const email = (row.dataset.email || "").toLowerCase();
      row.style.display = !q || nombre.includes(q) || email.includes(q) ? "" : "none";
    });
  }

  searchInput?.addEventListener("input", applySearch);

  // --- Lógica del Código QR ---
  function generateQR() {
    if (!qrContainer || !QRCodeLib) {
      console.warn("Librería QRCode no encontrada o contenedor faltante.");
      return;
    }

    // Limpiar el QR anterior
    qrContainer.innerHTML = "";

    // Generar un token único (ej: ATT-123-A4B9F) o pedirlo a un endpoint tuyo
    const randomHash = Math.random().toString(36).substring(2, 8).toUpperCase();
    currentToken = `ATT-${classroomId}-${randomHash}`;

    // La URL o texto que se abrirá al escanear
    const qrContent = `${window.location.origin}/asistencia/registrar?aula=${classroomId}&token=${currentToken}`;

    // Dibujar el nuevo QR
    new QRCodeLib(qrContainer, {
      text: qrContent,
      width: 220,
      height: 220,
      colorDark: "#0f172a", // Gris oscuro para que combine con el diseño
      colorLight: "#ffffff",
      correctLevel: QRCodeLib.CorrectLevel.H
    });

    // Actualizar la interfaz con el nuevo código
    if (codeText) codeText.textContent = currentToken;
    if (sessionDateEl) sessionDateEl.textContent = formatSessionDate();
    if (emailPreview) emailPreview.textContent = currentToken;
  }

  function setupAutoRefresh() {
    if (refreshInterval) clearInterval(refreshInterval);
    if (autoRefreshCheck?.checked) {
      refreshInterval = setInterval(() => {
        generateQR();
      }, 30000); // Regenerar cada 30 segundos
    }
  }

  // --- Inicialización del QR ---
  generateQR();
  setupAutoRefresh();

  // --- Eventos del panel del QR ---
  autoRefreshCheck?.addEventListener("change", setupAutoRefresh);

  document.getElementById("at-generate")?.addEventListener("click", () => {
    generateQR();
    showToast("Nuevo código QR generado con éxito.");
    setupAutoRefresh(); // Reiniciar el temporizador al generar manual
  });

  document.getElementById("at-download-png")?.addEventListener("click", () => {
    // Buscar el canvas generado por la librería QRCode
    const canvas = qrContainer?.querySelector("canvas");
    if (canvas) {
      const link = document.createElement("a");
      link.download = `QR-Asistencia-Aula${classroomId}-${todayIso()}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
      showToast("Descargando imagen del QR...");
    } else {
      showToast("Error: No se pudo generar la imagen del QR.", "error");
    }
  });

  // --- Modal de Email ---
  function openEmailModal() {
    emailModal?.classList.remove("hidden");
  }

  function closeEmailModal() {
    emailModal?.classList.add("hidden");
  }

  document.getElementById("at-send-email")?.addEventListener("click", openEmailModal);
  document.getElementById("at-email-all")?.addEventListener("click", openEmailModal);
  document.getElementById("at-email-cancel")?.addEventListener("click", closeEmailModal);
  
  emailModal?.addEventListener("click", (e) => {
    if (e.target === emailModal) closeEmailModal();
  });

  emailForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const to = emailTo?.value?.trim();
    if (!to) return;
    
    // Aquí puedes enlazar tu llamada fetch() POST hacia Flask
    console.log(`Petición de envío de token ${currentToken} a ${to}`);
    
    closeEmailModal();
    emailForm.reset();
    showToast(`Código QR enviado con éxito a ${to}`);
  });

})();