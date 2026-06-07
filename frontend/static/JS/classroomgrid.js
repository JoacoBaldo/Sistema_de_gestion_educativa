import { emitAppEvent, APP_EVENTS } from "./common/ui.js";

(() => {
  const gridEl = document.getElementById("classroomsGrid");
  if (!gridEl) return;

  gridEl.addEventListener("click", (event) => {
    const shareLink = event.target.closest('[data-action="share"]');
    if (!shareLink) return;

    event.preventDefault();
    emitAppEvent(APP_EVENTS.SHARE_MODAL_OPEN, {
      classId: shareLink.dataset.classId || "",
      className: shareLink.dataset.className || "",
    });
  });
})();
