import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import { authHeaders, requireAuth } from "./common/auth.js";
import { createCmrToast } from "./common/ui.js";

ddocument.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("tm-grid");
  if (!grid) return;

  const showToast = createCmrToast();

  grid.addEventListener("click", (event) => {
    const deleteBtn = event.target.closest(".tm-delete-btn");
    if (!deleteBtn) return;
    event.preventDefault();

    const teamId = deleteBtn.dataset.id;
    const nombre = deleteBtn.dataset.nombre || "este equipo";
    if (!teamId) return;
    if (!confirm(`¿Eliminar "${nombre}"?`)) return;

    const xhr = new XMLHttpRequest();
    xhr.open("DELETE", "/api/v1/teams", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", "Bearer " + localStorage.getItem("token"));

    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          deleteBtn.closest(".tm-card")?.remove();
          showToast("Equipo eliminado.");
          if (!grid.querySelector(".tm-card")) {
            const empty = document.getElementById("tm-empty");
            if (empty) empty.hidden = false;
          }
        } else {
          showToast("Error al eliminar el equipo.");
        }
      }
    };
    xhr.send(JSON.stringify({ id: Number(teamId) }));
  });
});