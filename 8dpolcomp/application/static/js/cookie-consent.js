
(function () {
    const KEY = "8dpc_cookie_consent_v1"; // "accept" | "reject"

    function getChoice() {
        try {
            return localStorage.getItem(KEY);
        } catch (e) {
            return null;
        }
    }

    function setChoice(v) {
        try {
            localStorage.setItem(KEY, v);
        } catch (e) {
            // ignore (banner will reappear if storage is blocked)
        }
    }

    function updateGoogleConsent(granted) {
        if (typeof window.gtag !== "function") return;

        window.gtag("consent", "update", {
            ad_storage: granted ? "granted" : "denied",
            analytics_storage: granted ? "granted" : "denied",
            ad_user_data: granted ? "granted" : "denied",
            ad_personalization: granted ? "granted" : "denied"
        });

        // If user accepts after page load, send page_view now
        if (granted) {
            window.gtag("event", "page_view", {
                page_path: window.location.pathname + window.location.search
            });
        }
    }

    function init() {
        const banner = document.getElementById("cookie-banner");
        const acceptBtn = document.getElementById("cookie-accept");
        const rejectBtn = document.getElementById("cookie-reject");

        if (!banner || !acceptBtn || !rejectBtn) return;

        const choice = getChoice();

        // Show only if no stored choice
        if (choice !== "accept" && choice !== "reject") {
            banner.hidden = false;
        }

        acceptBtn.addEventListener("click", function () {
            setChoice("accept");
            updateGoogleConsent(true);
            banner.hidden = true;
        });

        rejectBtn.addEventListener("click", function () {
            setChoice("reject");
            updateGoogleConsent(false);
            banner.hidden = true;
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
