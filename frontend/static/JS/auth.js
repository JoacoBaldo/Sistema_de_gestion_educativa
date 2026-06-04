document.addEventListener("DOMContentLoaded", () => {
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

    const subtitles = {
        login: "Accede a tu portal académico",
        register: "Crea tu cuenta académica",
        recover: "Recupera el acceso a tu cuenta",
    };

    let currentMainView = "login";

    function getActiveMainBox() {
        if (loginBox.classList.contains("active")) return loginBox;
        if (registerBox.classList.contains("active")) return registerBox;
        return recoverBox;
    }

    function setSubtitle(view) {
        if (authSubtitle && subtitles[view]) {
            authSubtitle.textContent = subtitles[view];
        }
    }

    function setTabsVisible(visible) {
        if (authTabs) {
            authTabs.classList.toggle("hidden", !visible);
        }
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

        currentMainView = view;
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

    if (goToRecover) {
        goToRecover.addEventListener("click", (e) => {
            e.preventDefault();
            showMainView("recover");
        });
    }

    if (backToLoginFromRecover) {
        backToLoginFromRecover.addEventListener("click", (e) => {
            e.preventDefault();
            showMainView("login");
        });
    }

    if (sendTokenBtn && recoverEmail) {
        sendTokenBtn.addEventListener("click", () => {
            if (!recoverEmail.value.trim()) {
                recoverEmail.focus();
                recoverEmail.reportValidity();
                return;
            }

            sendTokenBtn.disabled = true;
            const originalText = sendTokenBtn.textContent;
            sendTokenBtn.textContent = "Token enviado";

            setTimeout(() => {
                sendTokenBtn.disabled = false;
                sendTokenBtn.textContent = originalText;
            }, 3000);
        });
    }
});
