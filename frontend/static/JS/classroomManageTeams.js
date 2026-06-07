document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("tm-grid");
  if (!grid) return;

  grid.addEventListener("click", (event) => {
    const deleteBtn = event.target.closest(".tm-delete-btn");
    if (!deleteBtn) return;
    event.preventDefault();

    const teamId = deleteBtn.dataset.id;
    const nombre = deleteBtn.dataset.nombre || "este equipo";
    if (!teamId) return;
    if (!confirm(`¿Eliminar "${nombre}"?`)) return;

    // Crear y enviar un formulario POST tradicional para eliminar
    const form = document.createElement("form");
    form.method = "POST";
    form.action = `/equipos/${teamId}/eliminar`;
    
    // Agregar token si existe
    const token = localStorage.getItem("token");
    if (token) {
      const tokenInput = document.createElement("input");
      tokenInput.type = "hidden";
      tokenInput.name = "token";
      tokenInput.value = token;
      form.appendChild(tokenInput);
    }
    
    // Enviar el formulario
    document.body.appendChild(form);
    form.submit();
    // El servidor redirigirá automáticamente
  });
});