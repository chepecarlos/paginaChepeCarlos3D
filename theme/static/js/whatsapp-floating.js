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

      const { message } = createWhatsAppMessage();
      const cleanNumber = WHATSAPP_NUMBER.replace(/[^0-9]/g, "");
      const encodedMessage = encodeURIComponent(message);
      const waUrl = `https://wa.me/${cleanNumber}?text=${encodedMessage}`;

      window.open(waUrl, "_blank", "noopener,noreferrer");
    });

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
