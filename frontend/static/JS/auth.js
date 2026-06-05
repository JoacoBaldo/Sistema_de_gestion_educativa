import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import {
  getCachedUserId,
  hasAuthToken,
  saveSession,
} from "./common/auth.js";
import { goTo } from "./common/ui.js";

const CREDENTIALS_ERROR = "Credenciales inválidas";
const USER_ID_MISMATCH = "user_id no coincide";

async function tryLogin(userId, email, password) {
  const response = await requestJson(apiUrl(`/api/v1/users/${userId}`), {
    method: "POST",
    body: { email, password },
  });
  let body = {};
  try {
    body = response.json();
  } catch {
    /* ignore */
  }
  return { response, body };
}

async function resolveLogin(email, password) {
  const cachedId = getCachedUserId(email);
  const tryOrder = [];
  if (cachedId != null) tryOrder.push(cachedId);
  for (let id = 1; id <= 500; id += 1) {
    if (!tryOrder.includes(id)) tryOrder.push(id);
  }

  let lastMismatch = null;
  for (const userId of tryOrder) {
    const { response, body } = await tryLogin(userId, email, password);
    if (response.ok) return body;
    const msg = body?.error || "";
    if (msg === CREDENTIALS_ERROR) {
      throw new Error(CREDENTIALS_ERROR);
    }
    if (msg === USER_ID_MISMATCH) {
      lastMismatch = msg;
      continue;
    }
    throw new Error(apiErrorMessage(body, "No se pudo iniciar sesión"));
  }
  throw new Error(lastMismatch || CREDENTIALS_ERROR);
}

document.addEventListener("DOMContentLoaded", () => {
  if (hasAuthToken()) {
    goTo("/");
    return;
  }

  const loginBox = document.getElementById("login-box");
  const registerBox = document.getElementById("register-box");
  const recoverBox = document.getElementById("recover-box");
  const authTabs = document.getElementById("auth-tabs");
  const authSubtitle = document.getElementById("auth-subtitle");
  const tabButtons = document.querySelectorAll(".auth-tab");

  const goToRecover = document.getElementById("go-to-recover");
  const backToLoginFromRecover = document.getElementById("back-to-login-from-recover");
  const sendTokenBtn = document.getElementById("send-token-btn");
  const recoverEmail = document.getElementById("recover-email");
  const recoverForm = document.getElementById("recover-form");

  const loginForm = loginBox?.querySelector("form");
  const registerForm = registerBox?.querySelector("form");

  const subtitles = {
    login: "Accede a tu portal académico",
    register: "Crea tu cuenta académica",
    recover: "Recupera el acceso a tu cuenta",
  };

  function setSubtitle(view) {
    if (authSubtitle && subtitles[view]) {
      authSubtitle.textContent = subtitles[view];
    }
  }

  function setTabsVisible(visible) {
    authTabs?.classList.toggle("hidden", !visible);
  }

  function setActiveTab(view) {
    tabButtons.forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.view === view);
    });
  }

  function showMainView(view) {
    const boxes = { login: loginBox, register: registerBox, recover: recoverBox };
    const target = boxes[view];
    if (!target) return;

    [loginBox, registerBox, recoverBox].forEach((box) => {
      box.classList.toggle("active", box === target);
    });

    setSubtitle(view);
    setTabsVisible(view === "login" || view === "register");

    if (view === "login" || view === "register") {
      setActiveTab(view);
    }
  }

  tabButtons.forEach((tab) => {
    tab.addEventListener("click", () => {
      const view = tab.dataset.view;
      if (view === "login" || view === "register") {
        showMainView(view);
      }
    });
  });

  goToRecover?.addEventListener("click", (e) => {
    e.preventDefault();
    showMainView("recover");
  });

  backToLoginFromRecover?.addEventListener("click", (e) => {
    e.preventDefault();
    showMainView("login");
  });

  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email")?.value.trim();
    const password = document.getElementById("login-password")?.value ?? "";
    const btn = loginForm.querySelector('button[type="submit"]');
    if (!email || !password) return;

    if (btn) {
      btn.disabled = true;
      btn.textContent = "Accediendo...";
    }

    try {
      const data = await resolveLogin(email, password);
      saveSession(data);
      goTo("/");
    } catch (err) {
      alert(err.message || CREDENTIALS_ERROR);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Acceder";
      }
    }
  });

  registerForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("register-name")?.value.trim();
    const email = document.getElementById("register-email")?.value.trim();
    const password = document.getElementById("register-password")?.value ?? "";
    const btn = registerForm.querySelector('button[type="submit"]');
    if (!username || !email || !password) return;

    if (btn) {
      btn.disabled = true;
      btn.textContent = "Creando cuenta...";
    }

    try {
      const response = await requestJson(apiUrl("/api/v1/create_user"), {
        method: "POST",
        body: { username, email, password },
      });
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "No se pudo registrar la cuenta"));
      }
      alert(body.message || "Cuenta creada. Inicia sesión con tu email.");
      showMainView("login");
    } catch (err) {
      alert(err.message || "Error al registrarse");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Crear Cuenta";
      }
    }
  });

  sendTokenBtn?.addEventListener("click", async () => {
    const email = recoverEmail?.value.trim();
    if (!email) {
      recoverEmail?.focus();
      recoverEmail?.reportValidity();
      return;
    }

    sendTokenBtn.disabled = true;
    const originalText = sendTokenBtn.textContent;
    sendTokenBtn.textContent = "Enviando...";

    try {
      const response = await requestJson(apiUrl("/recuperar-password"), {
        method: "POST",
        body: { email },
      });
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "No se pudo enviar el correo"));
      }
      sendTokenBtn.textContent = "Token enviado";
      alert(body.message || "Revisa tu correo para el token de recuperación.");
    } catch (err) {
      alert(err.message || "Error al enviar el token");
      sendTokenBtn.textContent = originalText;
    } finally {
      setTimeout(() => {
        sendTokenBtn.disabled = false;
        if (sendTokenBtn.textContent === "Enviando...") {
          sendTokenBtn.textContent = originalText;
        }
      }, 3000);
    }
  });

  recoverForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    alert(
      "El restablecimiento con token no está disponible en la API actual. Usa el token recibido por correo cuando el endpoint esté habilitado."
    );
  });
});
