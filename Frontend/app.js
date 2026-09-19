// Ensure script only initializes once
if (!window.__promptOptimizerLoaded) {
  window.__promptOptimizerLoaded = true;

  // Determine API endpoint:
  // - If hosted on port 8000 (FastAPI), use relative '/optimize'
  // - Otherwise (e.g. file:// or another local dev port), target http://127.0.0.1:8000/optimize
  const API_URL =
    window.location.origin && window.location.port === "8000"
      ? "/optimize"
      : "http://127.0.0.1:8000/optimize";

  function initPromptOptimizer() {
    // DOM Elements
    const promptInput = document.getElementById("promptInput");
    const modeSelect = document.getElementById("modeSelect");
    const optimizeBtn = document.getElementById("optimizeBtn");
    const charCount = document.getElementById("charCount");

    const errorBox = document.getElementById("errorBox");
    const errorMessage = document.getElementById("errorMessage");

    const result = document.getElementById("result");
    const originalText = document.getElementById("originalText");
    const optimizedText = document.getElementById("optimizedText");
    const intentText = document.getElementById("intentText");
    const tokenText = document.getElementById("tokenText");
    const scoreText = document.getElementById("scoreText");

    const copyBtn = document.getElementById("copyBtn");
    const copyBtnText = document.getElementById("copyBtnText");

    if (!optimizeBtn || !promptInput) return;

    // Store the original button inner HTML/text so we can restore it accurately
    const originalBtnContent = optimizeBtn.innerHTML;

    // Update character count on textarea input
    if (charCount) {
      promptInput.addEventListener("input", () => {
        const count = promptInput.value.length;
        charCount.textContent = `${count} character${count === 1 ? "" : "s"}`;
      });
    }

    // Keyboard shortcut: Ctrl+Enter or Cmd+Enter to optimize
    promptInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleOptimize();
      }
    });

    // Button click handler
    optimizeBtn.addEventListener("click", handleOptimize);

    // Copy to clipboard handler
    if (copyBtn) {
      copyBtn.addEventListener("click", async () => {
        const textToCopy = optimizedText ? optimizedText.textContent : "";
        if (!textToCopy) return;

        try {
          await navigator.clipboard.writeText(textToCopy);
          if (copyBtnText) copyBtnText.textContent = "Copied!";
          copyBtn.classList.add("copied");

          setTimeout(() => {
            if (copyBtnText) copyBtnText.textContent = "Copy";
            copyBtn.classList.remove("copied");
          }, 2000);
        } catch (_) {
          // Fallback if clipboard API is restricted
          const tempArea = document.createElement("textarea");
          tempArea.value = textToCopy;
          document.body.appendChild(tempArea);
          tempArea.select();
          document.execCommand("copy");
          document.body.removeChild(tempArea);

          if (copyBtnText) copyBtnText.textContent = "Copied!";
          copyBtn.classList.add("copied");
          setTimeout(() => {
            if (copyBtnText) copyBtnText.textContent = "Copy";
            copyBtn.classList.remove("copied");
          }, 2000);
        }
      });
    }

    // Main optimization logic with loading state and robust error handling
    async function handleOptimize() {
      const prompt = promptInput.value.trim();

      // Clear previous error messages
      hideError();

      // Client-side validation: prompt cannot be empty
      if (!prompt) {
        showError("Please enter a prompt to optimize.");
        promptInput.focus();
        return;
      }

      // 1. Loading state: disable button and change text to "Optimizing..."
      optimizeBtn.disabled = true;
      optimizeBtn.textContent = "Optimizing...";

      try {
        // 2. Fetch call with try/catch
        const response = await fetch(API_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            prompt: prompt,
            mode: modeSelect ? modeSelect.value : "hybrid"
          })
        });

        // Check for non-200 responses
        if (!response.ok) {
          let errorDetail = `Server returned status ${response.status} (${response.statusText})`;
          try {
            const errorJson = await response.json();
            if (errorJson && errorJson.detail) {
              if (typeof errorJson.detail === "string") {
                errorDetail = errorJson.detail;
              } else if (Array.isArray(errorJson.detail)) {
                errorDetail = errorJson.detail
                  .map((item) => item.msg || JSON.stringify(item))
                  .join(", ");
              }
            }
          } catch (_) {
            // Body was not JSON, retain default status text
          }
          throw new Error(errorDetail);
        }

        const data = await response.json();

        // Populate results
        if (originalText) {
          originalText.textContent = data.original_prompt || prompt;
        }
        if (optimizedText) {
          optimizedText.textContent = data.optimized_prompt || "";
        }

        // Format detected intents
        if (intentText) {
          if (Array.isArray(data.intent) && data.intent.length > 0) {
            intentText.textContent = data.intent.join(", ");
          } else {
            intentText.textContent = "None detected";
          }
        }

        // Format token comparison
        if (tokenText) {
          tokenText.textContent = `${data.original_tokens} → ${data.optimized_tokens}`;
        }

        // Format similarity score
        if (scoreText) {
          const score = typeof data.similarity_score === "number"
            ? data.similarity_score.toFixed(2)
            : data.similarity_score;
          scoreText.textContent = score;
        }

        // Show results
        if (result) {
          result.style.display = "block";
        }
      } catch (error) {
        // Handle network error, server offline, or HTTP error
        let displayMsg = error.message;

        // Detect network / fetch failure (backend unreachable)
        if (error.name === "TypeError" && error.message.includes("fetch")) {
          displayMsg =
            "Unable to reach the backend API. Please make sure the FastAPI server is running at " +
            API_URL +
            " (e.g. run 'uvicorn main:app --reload' in your terminal).";
        }

        showError(displayMsg);
        // Hide stale results if error occurred
        if (result) {
          result.style.display = "none";
        }
      } finally {
        // Re-enable button and restore original text / markup
        optimizeBtn.disabled = false;
        optimizeBtn.innerHTML = originalBtnContent;
      }
    }

    function showError(message) {
      if (errorMessage && errorBox) {
        errorMessage.textContent = message;
        errorBox.style.display = "flex";
      }
    }

    function hideError() {
      if (errorBox) {
        errorBox.style.display = "none";
      }
      if (errorMessage) {
        errorMessage.textContent = "";
      }
    }
  }

  // Handle both immediate execution if DOM is ready and DOMContentLoaded event
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPromptOptimizer);
  } else {
    initPromptOptimizer();
  }
}
