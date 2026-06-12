import { goTo } from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
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

      if (action === "back-to-classes") {
        e.preventDefault();
        goTo("/");
        return;
      }
    });
  });
});
