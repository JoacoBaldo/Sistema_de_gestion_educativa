import { clearSession, getUser, requireAuth, userInitials } from "./common/auth.js";
import { goTo } from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  if (!requireAuth()) return;

  const user = getUser();
  const brandSubtitle = document.querySelector(".cm-brand-subtitle");
  if (brandSubtitle && user?.username) {
    brandSubtitle.textContent = user.username;
  }

  const root = document.querySelector(".cm-layout");
  if (!root) return;

  const vistaActual = root.getAttribute("data-vista-actual") || "students";
  const links = document.querySelectorAll(".cm-nav-item[data-vista]");

  links.forEach((link) => {
    link.classList.toggle("is-active", link.dataset.vista === vistaActual);
  });

  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const action = btn.getAttribute("data-action");
      if (!action) return;
      e.preventDefault();

      if (action === "back-to-classes") {
        goTo("/");
        return;
      }

      if (action === "logout") {
        clearSession();
        goTo("/auth");
        return;
      }

      if (action === "settings") {
        alert("Configuración (sin endpoint en la API actual).");
      }
    });
  });
});
