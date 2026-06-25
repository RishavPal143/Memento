// background.js - Background service worker for Internet Memory

/**
 * Updates the extension's badge UI to indicate whether the save was successful.
 * Supports custom text overrides (e.g. "Low" for skipped pages).
 */
async function showBadgeFeedback(success, textOverride = null) {
  try {
    const text = textOverride || (success ? "✓" : "Err");
    
    // Choose badge color: green for success, yellow/orange for skipped low importance, red for errors
    let color = success ? "#10B981" : "#EF4444";
    if (textOverride === "Low") {
      color = "#F59E0B"; // Amber yellow
    }

    await chrome.action.setBadgeText({ text: text });
    await chrome.action.setBadgeBackgroundColor({ color: color });

    // Reset the badge to empty after 2500ms
    setTimeout(async () => {
      await chrome.action.setBadgeText({ text: "" });
    }, 2500);
  } catch (err) {
    console.error("[Internet Memory] Error setting action badge:", err);
  }
}

// Register listener to receive messages from content scripts running in user tabs
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "SAVE_MEMORY") {
    const pageData = message.data;
    const isManual = message.manual === true;

    // Use an asynchronous IIFE to handle the async work
    (async () => {
      try {
        console.log("[Internet Memory] Sending API request to save:", pageData.url);

        const response = await fetch("http://localhost:8000/memory", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            title: pageData.title,
            url: pageData.url,
            content: pageData.content
          })
        });

        if (!response.ok) {
          const details = await response.text();
          throw new Error(`Server status ${response.status}: ${details}`);
        }

        const savedRecord = await response.json();
        console.log("[Internet Memory] API save response success:", savedRecord);

        // Check if user enabled "Save Only Important" pages AND this is an auto-saved page
        const settings = await chrome.storage.local.get({ onlyImportant: false });
        if (settings.onlyImportant && !isManual && savedRecord.importance_score !== undefined && savedRecord.importance_score < 60) {
          console.log(`[Internet Memory] Discarding memory with low importance score (${savedRecord.importance_score} < 60)`);
          
          // Delete from database
          const deleteRes = await fetch(`http://localhost:8000/memory/${savedRecord.id}`, {
            method: "DELETE"
          });
          
          if (deleteRes.ok) {
            console.log("[Internet Memory] Low importance memory deleted from DB.");
          } else {
            console.warn("[Internet Memory] Failed to delete low importance memory.");
          }

          // Show yellow "Low" badge feedback
          await showBadgeFeedback(false, "Low");
          sendResponse({ success: true, status: "ignored", record: savedRecord });
          return;
        }

        // Flash green badge feedback
        await showBadgeFeedback(true, "✓");
        sendResponse({ success: true, status: "saved", record: savedRecord });
      } catch (err) {
        console.error("[Internet Memory] Error in background API request:", err);

        // Flash red error badge feedback
        await showBadgeFeedback(false, "Err");
        sendResponse({ success: false, error: err.message });
      }
    })();

    return true; // Keep the message channel open for the async response
  }
});
