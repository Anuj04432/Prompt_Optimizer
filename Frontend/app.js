// Determine API base URL: relative if served via FastAPI, otherwise default to http://127.0.0.1:8000
const API_BASE = window.location.origin && window.location.origin.startsWith("http")
  ? (window.location.port === "8000" ? window.location.origin : "http://127.0.0.1:8000")
  : "http://127.0.0.1:8000";

const samplePrompts = {
  python: "write a python function for binary search and explain it",
  email: "compose a formal email to manager requesting one week vacation for family travel",
  sql: "write a query to find top 5 customers with highest total spending across all orders and optimize performance",
  resume: "summarize my 4 years experience as full stack engineer with react and python for resume",
  blog: "write a blog article explaining why docker containers are useful in modern web development"
};

// State
let currentMode = "hybrid";
let history = JSON.parse(localStorage.getItem("prompt_history") || "[]");

// Elements
const promptInput = document.getElementById("promptInput");
const optimizeBtn = document.getElementById("optimizeBtn");
const clearBtn = document.getElementById("clearBtn");
const charCount = document.getElementById("charCount");
const wordCount = document.getElementById("wordCount");
const estTokens = document.getElementById("estTokens");
const modeBtns = document.querySelectorAll(".mode-btn");
const sampleChips = document.querySelectorAll(".sample-chip");
const statusBadge = document.getElementById("statusBadge");
const statusText = document.getElementById("statusText");
const themeToggle = document.getElementById("themeToggle");

const emptyState = document.getElementById("emptyState");
const resultContent = document.getElementById("resultContent");
const optimizedOutput = document.getElementById("optimizedOutput");
const copyBtn = document.getElementById("copyBtn");
const intentsList = document.getElementById("intentsList");
const tokenStats = document.getElementById("tokenStats");
const tokenBadge = document.getElementById("tokenBadge");
const similarityScore = document.getElementById("similarityScore");
const similarityBadge = document.getElementById("similarityBadge");
const fidelityBar = document.getElementById("fidelityBar");
const latencyStat = document.getElementById("latencyStat");
const historyList = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const historySection = document.getElementById("historySection");

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupEventListeners();
  updateInputStats();
  renderHistory();
  checkBackendHealth();
  setInterval(checkBackendHealth, 10000);
});

function initTheme() {
  const savedTheme = localStorage.getItem("app_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("app_theme", newTheme);
  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
  if (!themeToggle) return;
  themeToggle.innerHTML = theme === "dark" 
    ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
    : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
}

async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/docs`, { method: "HEAD", mode: "cors" });
    if (res.ok || res.status === 200 || res.status === 304 || res.type === "opaque") {
      setConnectionStatus(true);
    } else {
      setConnectionStatus(true); // Server responded
    }
  } catch (e) {
    // Try simple GET
    try {
      const ping = await fetch(`${API_BASE}/findintent/test`, { method: "GET" });
      setConnectionStatus(ping.ok);
    } catch (err) {
      setConnectionStatus(false);
    }
  }
}

function setConnectionStatus(isConnected) {
  if (!statusBadge || !statusText) return;
  if (isConnected) {
    statusBadge.className = "status-badge connected";
    statusText.textContent = "API Ready";
  } else {
    statusBadge.className = "status-badge disconnected";
    statusText.textContent = "Backend Offline";
  }
}

function setupEventListeners() {
  // Input tracking
  promptInput.addEventListener("input", updateInputStats);

  // Keyboard shortcut Ctrl+Enter / Cmd+Enter
  promptInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      handleOptimize();
    }
  });

  // Mode Selection
  modeBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      modeBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentMode = btn.dataset.mode;
    });
  });

  // Sample Chips
  sampleChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const type = chip.dataset.sample;
      if (samplePrompts[type]) {
        promptInput.value = samplePrompts[type];
        updateInputStats();
        promptInput.focus();
      }
    });
  });

  // Optimize button
  optimizeBtn.addEventListener("click", handleOptimize);

  // Clear button
  clearBtn.addEventListener("click", () => {
    promptInput.value = "";
    updateInputStats();
    promptInput.focus();
  });

  // Copy button
  copyBtn.addEventListener("click", copyToClipboard);

  // Clear history
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", () => {
      history = [];
      localStorage.removeItem("prompt_history");
      renderHistory();
      showToast("History cleared");
    });
  }

  // Theme toggle
  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }
}

function updateInputStats() {
  const text = promptInput.value;
  const chars = text.length;
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  // Estimate tokens (~ 1 token per 4 chars or 0.75 words)
  const tokens = text.trim() ? Math.ceil(chars / 4) : 0;

  charCount.textContent = `${chars} chars`;
  wordCount.textContent = `${words} words`;
  estTokens.textContent = `~${tokens} tokens`;

  optimizeBtn.disabled = chars === 0;
}

async function handleOptimize() {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    showToast("Please enter a prompt to optimize", "error");
    return;
  }

  setLoading(true);
  const startTime = performance.now();

  try {
    const response = await fetch(`${API_BASE}/optimize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt: prompt,
        mode: currentMode
      })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server returned ${response.status}`);
    }

    const data = await response.json();
    const elapsedMs = Math.round(performance.now() - startTime);

    displayResult(data, elapsedMs);
    addToHistory(prompt, data.optimized_prompt, currentMode);
    setConnectionStatus(true);
  } catch (error) {
    console.error("Optimization error:", error);
    showToast(`Error: ${error.message || "Failed to reach backend API"}. Make sure FastAPI server is running.`, "error");
    setConnectionStatus(false);
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  if (isLoading) {
    optimizeBtn.classList.add("is-loading");
    optimizeBtn.disabled = true;
  } else {
    optimizeBtn.classList.remove("is-loading");
    optimizeBtn.disabled = promptInput.value.trim().length === 0;
  }
}

function displayResult(data, latencyMs) {
  emptyState.style.display = "none";
  resultContent.style.display = "flex";

  // Set optimized text
  optimizedOutput.textContent = data.optimized_prompt;

  // Intents
  intentsList.innerHTML = "";
  if (data.intent && data.intent.length > 0) {
    data.intent.forEach(intent => {
      const tag = document.createElement("span");
      tag.className = "intent-tag";
      tag.textContent = intent;
      intentsList.appendChild(tag);
    });
  } else {
    const emptyTag = document.createElement("span");
    emptyTag.className = "intent-tag empty";
    emptyTag.textContent = "general";
    intentsList.appendChild(emptyTag);
  }

  // Token Stats
  const orig = data.original_tokens || 0;
  const opt = data.optimized_tokens || 0;
  tokenStats.textContent = `${orig} → ${opt}`;

  const diff = opt - orig;
  if (diff > 0) {
    tokenBadge.innerHTML = `<span style="color: #818cf8; font-size: 0.75rem; font-weight: 600;">+${diff} tokens (+${Math.round((diff / (orig || 1)) * 100)}% detail)</span>`;
  } else if (diff < 0) {
    tokenBadge.innerHTML = `<span style="color: #34d399; font-size: 0.75rem; font-weight: 600;">${diff} tokens (${Math.round((diff / (orig || 1)) * 100)}% compressed)</span>`;
  } else {
    tokenBadge.innerHTML = `<span style="color: #94a3b8; font-size: 0.75rem;">No size change</span>`;
  }

  // Similarity / Retention Score
  const rawScore = typeof data.similarity_score === "number" ? data.similarity_score : 0;
  const percentage = Math.round(rawScore * 100);
  similarityScore.textContent = `${percentage}% (${rawScore.toFixed(3)})`;

  // Score Bar & Status
  fidelityBar.style.width = `${Math.min(percentage, 100)}%`;
  if (rawScore >= 0.6) {
    fidelityBar.style.background = "#10b981";
    similarityBadge.className = "fidelity-badge badge-high";
    similarityBadge.textContent = "High Retention";
  } else if (rawScore >= 0.3) {
    fidelityBar.style.background = "#3b82f6";
    similarityBadge.className = "fidelity-badge badge-mid";
    similarityBadge.textContent = "Moderate";
  } else {
    fidelityBar.style.background = "#f59e0b";
    similarityBadge.className = "fidelity-badge badge-low";
    similarityBadge.textContent = "Low Retention";
  }

  // Latency
  if (latencyStat) {
    latencyStat.textContent = `${latencyMs}ms`;
  }
}

async function copyToClipboard() {
  const text = optimizedOutput.textContent;
  if (!text) return;

  try {
    await navigator.clipboard.writeText(text);
    copyBtn.classList.add("copied");
    copyBtn.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
      Copied!
    `;
    showToast("Optimized prompt copied to clipboard!");

    setTimeout(() => {
      copyBtn.classList.remove("copied");
      copyBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        Copy
      `;
    }, 2000);
  } catch (err) {
    showToast("Failed to copy to clipboard", "error");
  }
}

function addToHistory(original, optimized, mode) {
  const item = {
    id: Date.now(),
    original,
    optimized,
    mode,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };

  history.unshift(item);
  if (history.length > 8) history.pop();

  localStorage.setItem("prompt_history", JSON.stringify(history));
  renderHistory();
}

function renderHistory() {
  if (!historyList) return;
  if (history.length === 0) {
    historySection.style.display = "none";
    return;
  }

  historySection.style.display = "block";
  historyList.innerHTML = "";

  history.forEach(item => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `
      <span class="history-text" title="${escapeHtml(item.original)}">${escapeHtml(item.original)}</span>
      <span class="history-meta">${item.mode} • ${item.timestamp}</span>
    `;

    div.addEventListener("click", () => {
      promptInput.value = item.original;
      updateInputStats();
      // Also switch active mode if needed
      modeBtns.forEach(btn => {
        if (btn.dataset.mode === item.mode) {
          btn.click();
        }
      });
      promptInput.focus();
    });

    historyList.appendChild(div);
  });
}

function showToast(message, type = "success") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === "error" ? "⚠️" : "✨"}</span>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.2s ease";
    setTimeout(() => toast.remove(), 200);
  }, 3200);
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
