document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("sidebar-toggle");

    if (toggle) {
        toggle.addEventListener("click", function () {
            var collapsed = document.body.classList.toggle("sidebar-collapsed");
            localStorage.setItem("sidebar-collapsed", collapsed ? "1" : "0");
        });
    }

    var themeToggle = document.getElementById("theme-toggle");
    var themeIcon = themeToggle ? themeToggle.querySelector("i") : null;

    if (themeToggle && themeIcon) {
        if (document.documentElement.dataset.theme === "dark") {
            themeIcon.className = "bi bi-sun";
        }

        themeToggle.addEventListener("click", function () {
            var isDark = document.documentElement.dataset.theme === "dark";
            document.documentElement.dataset.theme = isDark ? "light" : "dark";
            localStorage.setItem("theme", isDark ? "light" : "dark");
            themeIcon.className = isDark
                ? "bi bi-moon-stars"
                : "bi bi-sun";
        });
    }

    // Close the notification dropdown when clicking outside it.
    document.addEventListener("click", function (event) {
        var wrap = document.querySelector(".notif-bell-wrap");
        var dropdown = document.getElementById("notif-dropdown");

        if (!wrap || !dropdown) {
            return;
        }

        if (!wrap.contains(event.target)) {
            dropdown.classList.remove("open");
        }
    });
});

// Mobile Sidebar Toggle
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.getElementById('mobile-hamburger');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            document.body.classList.toggle('sidebar-open');
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', () => {
            document.body.classList.remove('sidebar-open');
        });
    }
});
