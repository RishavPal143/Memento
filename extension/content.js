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

  // Helper function to extract page text and send save request to background
  function handleSavePage(manual = false, callback = null) {
    const pageData = {
      title: document.title || window.location.hostname || "Untitled Page",
      url: window.location.href,
      content: extractPageText()
    };

    if (pageData.url.startsWith("http://") || pageData.url.startsWith("https://")) {
      console.log("[Internet Memory] Sending SAVE_MEMORY action. Manual:", manual);
      
      chrome.runtime.sendMessage({
        action: "SAVE_MEMORY",
        data: pageData,
        manual: manual
      }, (response) => {
        if (chrome.runtime.lastError) {
          console.warn("[Internet Memory] Extension message failed:", chrome.runtime.lastError.message);
          if (callback) callback({ success: false, error: chrome.runtime.lastError.message });
          return;
        }
        if (callback) callback(response);
      });
    } else {
      if (callback) callback({ success: false, error: "Only http:// and https:// URLs are supported." });
    }
  }

  // Auto-save on page load, if config is enabled
  (async () => {
    try {
      const settings = await chrome.storage.local.get({ autoSave: true });
      if (settings.autoSave) {
        handleSavePage(false);
      } else {
        console.log("[Internet Memory] Auto-save disabled. Page capture skipped.");
      }
    } catch (err) {
      console.error("[Internet Memory] Error reading storage settings:", err);
    }
  })();

  // Listen for manual page capture messages from the popup UI
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "MANUAL_SAVE") {
      handleSavePage(true, (response) => {
        sendResponse(response);
      });
      return true; // Keep message port active for asynchronous response
    }
  });
})();
