// Botón flotante de WhatsApp
(function () {
  const WHATSAPP_NUMBER = document.documentElement.getAttribute("data-whatsapp-number");
  if (!WHATSAPP_NUMBER) return;

  function getProductName() {
    // Intenta obtener el nombre del producto de múltiples fuentes
    const h1 = document.querySelector("article.product-detail h1");
    if (h1) return h1.textContent.trim();

    // Alternativa: buscar en meta tags
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) return ogTitle.getAttribute("content");

    return null;
  }

  function getProductPageUrl() {
    return window.location.href;
  }

  function createWhatsAppMessage() {
    const productName = getProductName();

    if (productName) {
      // Es una página de producto
      const message = `Hola, quiero preguntar de este producto: ${productName}`;
      return { message, isProduct: true };
    } else {
      // Es una página genérica
      const message = `Hola, quiero más información`;
      return { message, isProduct: false };
    }
  }

  function initFloatingButton() {
    const btn = document.getElementById("whatsapp-floating-btn");
    if (!btn) return;

    btn.addEventListener("click", function (e) {
      e.preventDefault();

      // En producto, reutiliza el enlace del CTA principal (incluye URL y variación elegida)
      const productCta = document.getElementById("whatsapp-cta");
      if (productCta) {
        window.open(productCta.href, "_blank", "noopener,noreferrer");
        return;
      }

      const { message } = createWhatsAppMessage();
      const cleanNumber = WHATSAPP_NUMBER.replace(/[^0-9]/g, "");
      const encodedMessage = encodeURIComponent(message);
      const waUrl = `https://wa.me/${cleanNumber}?text=${encodedMessage}`;

      window.open(waUrl, "_blank", "noopener,noreferrer");
    });

    // Se oculta mientras el precio, las variaciones o el CTA principal están en pantalla, para no duplicarlo ni taparlos
    const buyBox = document.querySelectorAll("#product-price, .variation-selector, #whatsapp-cta");
    if (buyBox.length && "IntersectionObserver" in window) {
      const visible = new Set();
      const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) visible.add(entry.target);
          else visible.delete(entry.target);
        });
        btn.classList.toggle("is-hidden", visible.size > 0);
      });
      buyBox.forEach(function (el) { observer.observe(el); });
    }

    // Tooltip/hint al pasar el mouse
    const productName = getProductName();
    if (productName) {
      btn.setAttribute("title", `Cotizar: ${productName}`);
    } else {
      btn.setAttribute("title", "Contáctanos por WhatsApp");
    }
  }

  // Inicializar cuando el DOM esté listo
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFloatingButton);
  } else {
    initFloatingButton();
  }
})();
