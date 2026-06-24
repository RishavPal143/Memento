// background.js - Background service worker for Internet Memory

/**
 * Updates the extension's badge UI to indicate whether the save was successful.
 * Displays "✓" in green for success, or "Err" in red for failure, resetting after 2.5 seconds.
 */
async function showBadgeFeedback(success) {
  try {
    const text = success ? "✓" : "Err";
    const color = success ? "#10B981" : "#EF4444"; // Emerald green vs Coral red

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

    // Use an asynchronous IIFE to handle the fetch request to bypass service worker sync constraints
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

        // Flash green badge feedback
        await showBadgeFeedback(true);
        sendResponse({ success: true, record: savedRecord });
      } catch (err) {
        console.error("[Internet Memory] Error in background API request:", err);

        // Flash red error badge feedback
        await showBadgeFeedback(false);
        sendResponse({ success: false, error: err.message });
      }
    })();

    return true; // Keep the message channel open for the async response
  }
});
