document.addEventListener("DOMContentLoaded", async () => {
  const autoSaveToggle = document.getElementById("auto-save-toggle");
  const importantToggle = document.getElementById("important-toggle");
  const savePageBtn = document.getElementById("save-page-btn");
  const statusMessage = document.getElementById("status-message");

  // Load configuration from local storage (defaults: autoSave=true, onlyImportant=false)
  const settings = await chrome.storage.local.get({
    autoSave: true,
    onlyImportant: false
  });

  autoSaveToggle.checked = settings.autoSave;
  importantToggle.checked = settings.onlyImportant;

  // Save settings when toggles are changed
  autoSaveToggle.addEventListener("change", async () => {
    await chrome.storage.local.set({ autoSave: autoSaveToggle.checked });
    showStatus("Settings updated", "success");
    resetStatusTimeout();
  });

  importantToggle.addEventListener("change", async () => {
    await chrome.storage.local.set({ onlyImportant: importantToggle.checked });
    showStatus("Settings updated", "success");
    resetStatusTimeout();
  });

  // Handle manual page save
  savePageBtn.addEventListener("click", async () => {
    showStatus("Capturing page...", "warning");
    savePageBtn.disabled = true;

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        throw new Error("No active tab detected.");
      }

      const url = tab.url || "";
      if (url.startsWith("chrome://") || url.startsWith("edge://") || url.startsWith("about:") || url.startsWith("chrome-extension://")) {
        throw new Error("Cannot save browser system pages.");
      }

      // Send message to the content script in the active tab to extract and save content
      chrome.tabs.sendMessage(tab.id, { action: "MANUAL_SAVE" }, (response) => {
        savePageBtn.disabled = false;

        if (chrome.runtime.lastError) {
          showStatus("Error: Content script not loaded. Reload tab and retry.", "error");
          return;
        }

        if (response && response.success) {
          if (response.status === "ignored") {
            showStatus(`Ignored (Low AI Importance Score: ${response.record.importance_score})`, "warning");
          } else {
            const scoreStr = response.record.importance_score !== undefined ? ` (Score: ${response.record.importance_score})` : "";
            showStatus(`Saved successfully!${scoreStr}`, "success");
          }
        } else {
          showStatus(`Save failed: ${response ? response.error : "Unknown error"}`, "error");
        }
      });
    } catch (err) {
      savePageBtn.disabled = false;
      showStatus(`Error: ${err.message}`, "error");
    }
  });

  let statusTimeout = null;
  function resetStatusTimeout() {
    if (statusTimeout) clearTimeout(statusTimeout);
    statusTimeout = setTimeout(() => {
      showStatus("Status: Idle");
    }, 3000);
  }

  function showStatus(text, type = "") {
    statusMessage.textContent = text;
    statusMessage.className = "status-msg";
    if (type === "success") statusMessage.classList.add("status-success");
    if (type === "error") statusMessage.classList.add("status-error");
    if (type === "warning") statusMessage.classList.add("status-warning");
  }
});
