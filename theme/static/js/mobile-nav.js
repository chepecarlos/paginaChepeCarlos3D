(function () {
  const header = document.getElementById("site-header");
  const toggleButton = document.querySelector(".nav-toggle");
  const panel = document.getElementById("header-panel");
  const mobileSearchBtn = document.getElementById("mobile-search-btn");
  const mobileSearchClose = document.getElementById("mobile-search-close");
  const mobileSearchBar = document.getElementById("mobile-search-bar");
  const mobileSearchInput = mobileSearchBar && mobileSearchBar.querySelector(".mobile-search-input");

  if (!header || !toggleButton || !panel) {
    return;
  }

  const mobileMedia = window.matchMedia("(max-width: 768px)");

  /* ── Menú ── */
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
    if (nextState) closeSearch();
    header.classList.toggle("menu-open", nextState);
    setExpanded(nextState);
  }

  toggleButton.addEventListener("click", toggleMenu);

  /* ── Búsqueda móvil ── */
  function isSearchOpen() {
    return header.classList.contains("search-open");
  }

  function openSearch() {
    closeMenu();
    header.classList.add("search-open");
    if (mobileSearchBar) mobileSearchBar.setAttribute("aria-hidden", "false");
    if (mobileSearchInput) {
      setTimeout(function () { mobileSearchInput.focus(); }, 260);
    }
  }

  function closeSearch() {
    if (!isSearchOpen()) return;
    header.classList.remove("search-open");
    if (mobileSearchBar) mobileSearchBar.setAttribute("aria-hidden", "true");
  }

  if (mobileSearchBtn) mobileSearchBtn.addEventListener("click", openSearch);
  if (mobileSearchClose) mobileSearchClose.addEventListener("click", closeSearch);

  /* ── Escape y clic fuera ── */
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeMenu();
      closeSearch();
    }
  });

  document.addEventListener("click", function (event) {
    if (!mobileMedia.matches) return;
    if (header.contains(event.target)) return;
    closeMenu();
    closeSearch();
  });

  panel.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (mobileMedia.matches) closeMenu();
    });
  });

  /* ── Resetear al pasar a desktop ── */
  function onBreakpoint(event) {
    if (!event.matches) {
      closeMenu();
      closeSearch();
    }
  }

  if (mobileMedia.addEventListener) {
    mobileMedia.addEventListener("change", onBreakpoint);
  } else if (mobileMedia.addListener) {
    mobileMedia.addListener(onBreakpoint);
  }

  setExpanded(false);
})();
