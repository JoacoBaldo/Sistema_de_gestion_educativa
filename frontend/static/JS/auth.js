document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.authenticated === "true") {
    window.location.href = "/";
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
});
