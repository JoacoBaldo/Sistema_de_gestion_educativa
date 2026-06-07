import { requestJson } from "./common/http.js";
import { apiUrl, apiErrorMessage } from "./common/api.js";
import { authHeaders, requireAuth } from "./common/auth.js";
import { createCmrToast } from "./common/ui.js";

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("tm-grid");
  if (!grid) return;
  requireAuth();

  const showToast = createCmrToast();

  grid.addEventListener("click", async (event) => {
    const deleteBtn = event.target.closest(".tm-delete-btn");
    if (!deleteBtn) return;
    event.preventDefault();

    const teamId = deleteBtn.dataset.id;
    const nombre = deleteBtn.dataset.nombre || "este equipo";
    if (!teamId) return;
    if (!confirm(`¿Eliminar "${nombre}"?`)) return;

    try {
      const response = await requestJson(apiUrl("/api/v1/teams"), {
        method: "DELETE",
        headers: authHeaders(),
        body: { id: Number(teamId) },
      });
      const body = response.json();
      if (!response.ok) {
        throw new Error(apiErrorMessage(body, "No se pudo eliminar el equipo"));
      }
      deleteBtn.closest(".tm-card")?.remove();
      showToast("Equipo eliminado.");
      if (!grid.querySelector(".tm-card")) {
        const empty = document.getElementById("tm-empty");
        if (empty) empty.hidden = false;
      }
    } catch (err) {
      console.error(err);
      showToast(err.message || "Error al eliminar.");
    }
  });
});
