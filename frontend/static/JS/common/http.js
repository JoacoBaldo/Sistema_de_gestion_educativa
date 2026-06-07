/** Sin fetch ni XHR: los datos llegan renderizados desde el servidor. */
export function requestJson() {
  throw new Error("Las solicitudes AJAX no están permitidas en este frontend.");
}
