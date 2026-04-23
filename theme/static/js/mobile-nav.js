(function () {
  const header = document.getElementById("site-header");
  const toggleButton = document.querySelector(".nav-toggle");
  const panel = document.getElementById("header-panel");

  if (!header || !toggleButton || !panel) {
    return;
  }

  const mobileMedia = window.matchMedia("(max-width: 768px)");

  function isMenuOpen() {
    return header.classList.contains("menu-open");
  }

  function setExpanded(open) {
    toggleButton.setAttribute("aria-expanded", String(open));
    toggleButton.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
  }

  function closeMenu() {
    if (!isMenuOpen()) return;
    header.classList.remove("menu-open");
    setExpanded(false);
  }

  function toggleMenu() {
    const nextState = !isMenuOpen();
    header.classList.toggle("menu-open", nextState);
    setExpanded(nextState);
  }

  toggleButton.addEventListener("click", function () {
    toggleMenu();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeMenu();
    }
  });

  document.addEventListener("click", function (event) {
    if (!mobileMedia.matches || !isMenuOpen()) return;
    if (header.contains(event.target)) return;
    closeMenu();
  });

  panel.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (mobileMedia.matches) {
        closeMenu();
      }
    });
  });

  if (mobileMedia.addEventListener) {
    mobileMedia.addEventListener("change", function (event) {
      if (!event.matches) {
        closeMenu();
      }
    });
  } else if (mobileMedia.addListener) {
    mobileMedia.addListener(function (event) {
      if (!event.matches) {
        closeMenu();
      }
    });
  }

  setExpanded(false);
})();
