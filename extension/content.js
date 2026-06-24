// content.js - Extracts webpage content and sends it to the background script

(function() {
  // Only execute in the top-level document, avoiding iframe contexts
  if (window.self !== window.top) {
    return;
  }

  /**
   * Extracts clean, readable text from the document body,
   * removing scripts, styling, navigation links, and structural boilerplate.
   */
  function extractPageText() {
    const body = document.body;
    if (!body) return "";

    // Clone the body to safely manipulate the DOM structure without affecting the user's view
    const clone = body.cloneNode(true);

    // Identify and remove elements that do not contain main readable article text
    const selectorsToRemove = [
      "script",
      "style",
      "noscript",
      "iframe",
      "svg",
      "nav",
      "footer",
      "header",
      "aside",
      "form",
      "dialog"
    ];

    const unneededElements = clone.querySelectorAll(selectorsToRemove.join(","));
    unneededElements.forEach(el => el.remove());

    // Extract the remaining text content
    const textContent = clone.innerText || clone.textContent || "";
    
    // Normalize spacing and whitespace
    return textContent.replace(/\s+/g, " ").trim();
  }

  // Gather metadata and content from the page
  const pageData = {
    title: document.title || window.location.hostname || "Untitled Page",
    url: window.location.href,
    content: extractPageText()
  };

  // Filter for HTTP and HTTPS protocols to avoid attempting to save internal chrome pages or file URLs
  if (pageData.url.startsWith("http://") || pageData.url.startsWith("https://")) {
    console.log("[Internet Memory] Capturing memory for:", pageData.url);
    
    // Send the captured data to the background service worker
    chrome.runtime.sendMessage({
      action: "SAVE_MEMORY",
      data: pageData
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.warn("[Internet Memory] Message failed (normal if background service worker is initializing):", chrome.runtime.lastError.message);
        return;
      }
      if (response && response.success) {
        console.log("[Internet Memory] Memory saved successfully.");
      } else {
        console.error("[Internet Memory] Memory save failed:", response ? response.error : "Unknown error");
      }
    });
  }
})();
