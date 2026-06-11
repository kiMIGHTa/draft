// Feature: whisper-transcriber-ui
// All event bindings use addEventListener — no inline handlers.

(function () {
  "use strict";

  // ── DOM refs ────────────────────────────────────────────────────────────────
  const btnModeFile = document.getElementById("btn-mode-file");
  // const btnModeUrl = document.getElementById("btn-mode-url");
  const panelFile = document.getElementById("panel-file");
  const panelUrl = document.getElementById("panel-url");
  const fileInput = document.getElementById("file-input");
  const fileError = document.getElementById("file-error");
  const urlInput = document.getElementById("url-input");
  const urlError = document.getElementById("url-error");
  const translateCheckbox = document.getElementById("translate-checkbox");
  const startBtn = document.getElementById("start-btn");
  const statusArea = document.getElementById("status-area");
  const resultsSection = document.getElementById("results");
  const detectedLanguage = document.getElementById("detected-language");
  const downloadTxt = document.getElementById("download-txt");
  const downloadSrt = document.getElementById("download-srt");
  const downloadVtt = document.getElementById("download-vtt");

  // ── Supported extensions (mirrors server allowlist) ────────────────────────
  const SUPPORTED_EXTENSIONS = new Set([
    "mp3",
    "wav",
    "m4a",
    "aac",
    "mp4",
    "mkv",
    "mov",
    "avi",
  ]);

  // ── State ──────────────────────────────────────────────────────────────────
  let currentMode = "file"; // "file" | "url"

  // ── 8.1 Mode toggle ────────────────────────────────────────────────────────
  function setMode(mode) {
    currentMode = mode;

    const isFile = mode === "file";
    btnModeFile.classList.toggle("active", isFile);
    btnModeFile.setAttribute("aria-pressed", String(isFile));
    // btnModeUrl.classList.toggle("active", !isFile);
    // btnModeUrl.setAttribute("aria-pressed", String(!isFile));

    panelFile.classList.toggle("hidden", !isFile);
    panelUrl.classList.toggle("hidden", isFile);

    // Clear errors when switching modes
    fileError.textContent = "";
    urlError.textContent = "";
    startBtn.disabled = false;
  }

  btnModeFile.addEventListener("click", () => setMode("file"));
  // btnModeUrl.addEventListener("click", () => setMode("url"));

  // ── 8.2 Client-side validation ─────────────────────────────────────────────
  function getFileExtension(filename) {
    const parts = filename.split(".");
    return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : "";
  }

  function validateFileInput() {
    if (!fileInput.files || fileInput.files.length === 0) {
      fileError.textContent = "";
      startBtn.disabled = false;
      return true;
    }
    const ext = getFileExtension(fileInput.files[0].name);
    if (!SUPPORTED_EXTENSIONS.has(ext)) {
      fileError.textContent =
        "Unsupported file type. Allowed: mp3, wav, m4a, aac, mp4, mkv, mov, avi.";
      startBtn.disabled = true;
      return false;
    }
    fileError.textContent = "";
    startBtn.disabled = false;
    return true;
  }

  function validateUrlInput() {
    const val = urlInput.value.trim();
    if (val === "") {
      urlError.textContent = "";
      return false; // empty — block submit but no inline message yet
    }
    urlError.textContent = "";
    return true;
  }

  fileInput.addEventListener("change", validateFileInput);

  // ── 8.3 Progress simulation ────────────────────────────────────────────────
  const PROGRESS_STEPS = ["Starting...", "Processing...", "Transcribing..."];

  function startProgressSimulation() {
    let step = 0;
    statusArea.textContent = PROGRESS_STEPS[step];
    statusArea.classList.remove("error");

    const interval = setInterval(() => {
      step += 1;
      if (step < PROGRESS_STEPS.length) {
        statusArea.textContent = PROGRESS_STEPS[step];
      }
    }, 5000); // advance every 5 s

    return interval;
  }

  // ── 8.4 Success handler ────────────────────────────────────────────────────
  function showResults(data) {
    detectedLanguage.textContent = data.language;
    downloadTxt.href = "/download/" + encodeURIComponent(data.txt_file);
    downloadSrt.href = "/download/" + encodeURIComponent(data.srt_file);
    downloadVtt.href = "/download/" + encodeURIComponent(data.vtt_file);
    resultsSection.classList.remove("hidden");
  }

  function clearResults() {
    resultsSection.classList.add("hidden");
    detectedLanguage.textContent = "";
    downloadTxt.href = "#";
    downloadSrt.href = "#";
    downloadVtt.href = "#";
  }

  // ── 8.5 Error handler ──────────────────────────────────────────────────────
  function showError(message) {
    statusArea.textContent = message;
    statusArea.classList.add("error");
  }

  // ── 8.3 Fetch submission ───────────────────────────────────────────────────
  startBtn.addEventListener("click", function handleSubmit() {
    // Client-side validation before sending
    if (currentMode === "file") {
      if (!validateFileInput()) return;
      if (!fileInput.files || fileInput.files.length === 0) {
        fileError.textContent = "Please select a file.";
        return;
      }
    } else {
      const urlVal = urlInput.value.trim();
      if (!urlVal) {
        urlError.textContent = "Please enter a YouTube URL.";
        return;
      }
    }

    // Hide previous results and start new submission
    clearResults();
    statusArea.classList.remove("error");

    // Build FormData
    const formData = new FormData();
    if (currentMode === "file") {
      formData.append("file", fileInput.files[0]);
    } else {
      formData.append("youtube_url", urlInput.value.trim());
    }
    formData.append("translate", translateCheckbox.checked ? "true" : "false");

    // Disable button during flight
    startBtn.disabled = true;

    // Start simulated progress
    const progressInterval = startProgressSimulation();

    fetch("/transcribe", {
      method: "POST",
      body: formData,
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, data: data };
        });
      })
      .then(function (result) {
        clearInterval(progressInterval);
        startBtn.disabled = false;

        if (result.ok && result.data.success) {
          statusArea.textContent = "Completed.";
          statusArea.classList.remove("error");
          showResults(result.data);
        } else {
          showError(result.data.message || "An unexpected error occurred.");
        }
      })
      .catch(function (err) {
        clearInterval(progressInterval);
        startBtn.disabled = false;
        showError("Network error. Please try again.");
      });
  });
})();
