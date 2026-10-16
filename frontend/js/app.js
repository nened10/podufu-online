// State
let allTools = [];
let activeTool = null;
let selectedFiles = [];
let organizePages = []; // [{ page_index: 0, rotation: 0, original_number: 1 }]
let activeJobId = null;
let heroDroppedFile = null;

// DOM Elements
const toolsGrid = document.getElementById("tools-grid");
const searchInput = document.getElementById("search-input");
const filterButtons = document.querySelectorAll(".filter-btn");

// Hero Dropzone
const heroDropzone = document.getElementById("hero-dropzone");
const heroFileInput = document.getElementById("hero-file-input");

// Quick Action Modal
const quickActionModal = document.getElementById("quick-action-modal");
const closeQuickModalBtn = document.getElementById("close-quick-modal-btn");
const quickFileName = document.getElementById("quick-file-name");
const quickActionButtons = document.getElementById("quick-action-buttons");

// Workspace Modal
const workspaceOverlay = document.getElementById("workspace-overlay");
const closeModalBtn = document.getElementById("close-modal-btn");
const modalTitle = document.getElementById("modal-title");
const modalIcon = document.getElementById("modal-icon");
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const fileList = document.getElementById("file-list");
const toolOptions = document.getElementById("tool-options");
const pageGridContainer = document.getElementById("page-grid-container");
const pageGrid = document.getElementById("page-grid");
const actionSubmitBtn = document.getElementById("action-submit-btn");
const submitBtnText = document.getElementById("submit-btn-text");
const submitSpinner = document.getElementById("submit-spinner");
const workspaceBody = document.getElementById("workspace-body");
const workspaceFooter = document.getElementById("workspace-footer");
const resultScreen = document.getElementById("result-screen");
const downloadLink = document.getElementById("download-link");
const resetToolBtn = document.getElementById("reset-tool-btn");
const themeToggleBtn = document.getElementById("theme-toggle-btn");
const toastContainer = document.getElementById("toast-container");

// Progress & Queue Elements
const progressContainer = document.getElementById("progress-container");
const progressStatusLabel = document.getElementById("progress-status-label");
const progressPercentageLabel = document.getElementById("progress-percentage-label");
const progressBarFill = document.getElementById("progress-bar-fill");
const minimizeTaskBtn = document.getElementById("minimize-task-btn");
const queueDock = document.getElementById("queue-dock");
const queueDockTitle = document.getElementById("queue-dock-title");
const queueDockItems = document.getElementById("queue-dock-items");
const queueDockToggleBtn = document.getElementById("queue-dock-toggle-btn");

// Queue State
let taskQueue = [];
let activeTask = null;

// Icon mapping
const ICONS = {
  combine: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/><rect x="7" y="7" width="10" height="10" rx="1"/></svg>`,
  split: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 3h5v5"/><path d="M8 3H3v5"/><path d="M12 22v-8.3"/><path d="M21 3l-7.7 7.7"/><path d="M3 3l7.7 7.7"/></svg>`,
  "layout-grid": `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>`,
  "minimize-2": `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="14" y1="10" x2="21" y2="3"/><line x1="3" y1="21" x2="10" y2="14"/></svg>`,
  "file-text": `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
  presentation: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="12" y2="17"/><line x1="16" y1="21" x2="12" y2="17"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
  table: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>`,
  image: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`,
  images: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 22H4a2 2 0 0 1-2-2V6"/><rect x="6" y="2" width="16" height="16" rx="2"/><circle cx="12" cy="8" r="1.5"/><path d="m22 14-4-4-6 6"/></svg>`,
  code: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
  lock: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`,
  unlock: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>`,
  stamp: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 22h14"/><path d="M19.27 13.73A2.5 2.5 0 0 0 17.5 13h-11A2.5 2.5 0 0 0 4 15.5V17a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-1.5c0-.66-.26-1.3-.73-1.77Z"/><path d="M14 13V8.5C14 7.12 12.88 6 11.5 6S9 7.12 9 8.5V13"/></svg>`,
  hash: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></svg>`,
  "eye-off": `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>`,
  wrench: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`,
  trash: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>`,
  rotate: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6"/><path d="M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>`,
  arrowLeft: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>`,
  arrowRight: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`,
  check: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>`
};

const CATEGORY_NAMES = {
  organize: "Düzenle",
  optimize: "Optimize Et",
  convert: "Dönüştür",
  security: "Güvenlik",
  edit: "Düzenle"
};

// Initialize App
async function init() {
  setupTheme();
  setupEventListeners();
  await loadTools();
}

// Fetch Tools Catalog
async function loadTools() {
  try {
    const res = await fetch("/api/tools");
    const data = await res.json();
    allTools = data.tools || [];
    renderTools(allTools);
  } catch (err) {
    showToast("Araçlar yüklenirken hata oluştu: " + err.message, "error");
  }
}

// Render Tools in Grid with direct drag-and-drop capability!
function renderTools(tools) {
  toolsGrid.innerHTML = "";
  if (!tools.length) {
    toolsGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">Aradığınız kriterlere uygun araç bulunamadı.</p>`;
    return;
  }

  tools.forEach(tool => {
    const card = document.createElement("div");
    card.className = "tool-card";

    // Direct click handler
    card.onclick = () => openToolModal(tool);

    // DIRECT DESKTOP DRAG & DROP ONTO THIS CARD!
    card.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.stopPropagation();
      card.classList.add("drag-target");
    });

    card.addEventListener("dragleave", (e) => {
      e.preventDefault();
      e.stopPropagation();
      card.classList.remove("drag-target");
    });

    card.addEventListener("drop", (e) => {
      e.preventDefault();
      e.stopPropagation();
      card.classList.remove("drag-target");
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        openToolModal(tool);
        handleFiles(e.dataTransfer.files);
      }
    });

    const iconHtml = ICONS[tool.icon] || ICONS.combine;
    const catName = CATEGORY_NAMES[tool.category] || tool.category;

    card.innerHTML = `
      <div class="tool-icon-wrapper">
        ${iconHtml}
      </div>
      <h3>${tool.title}</h3>
      <p>${tool.description}</p>
      <span class="tool-tag">${catName}</span>
    `;
    toolsGrid.appendChild(card);
  });
}

let activeCategoryFilter = null;

// Filter Tools
function filterTools() {
  const query = searchInput.value.toLowerCase().trim();

  const filtered = allTools.filter(tool => {
    const matchesSearch = !query || tool.title.toLowerCase().includes(query) || tool.description.toLowerCase().includes(query);
    const matchesCategory = !activeCategoryFilter || tool.category === activeCategoryFilter;
    return matchesSearch && matchesCategory;
  });

  renderTools(filtered);
}

// Open Workspace Modal for Tool
function openToolModal(tool) {
  activeTool = tool;
  selectedFiles = [];
  organizePages = [];
  activeJobId = null;

  modalTitle.textContent = tool.title;
  modalIcon.innerHTML = ICONS[tool.icon] || ICONS.combine;
  fileInput.multiple = tool.multiple_files;
  fileInput.accept = tool.accept || ".pdf";

  // Reset Views
  workspaceBody.style.display = "block";
  workspaceFooter.style.display = "flex";
  resultScreen.style.display = "none";
  pageGridContainer.style.display = "none";
  pageGrid.innerHTML = "";
  fileList.innerHTML = "";
  actionSubmitBtn.disabled = true;
  submitBtnText.textContent = "İşlemi Başlat";
  submitSpinner.style.display = "none";

  if (progressContainer) {
    progressContainer.style.display = "none";
    progressBarFill.style.width = "0%";
    progressBarFill.classList.remove("processing");
  }
  if (minimizeTaskBtn) minimizeTaskBtn.style.display = "none";

  renderToolOptions(tool);
  workspaceOverlay.classList.add("active");
}

// Close Modal
function closeModal() {
  workspaceOverlay.classList.remove("active");
  activeTool = null;
  selectedFiles = [];
  organizePages = [];
}

// Render Options Panel per Tool (Clean & Minimalist)
function renderToolOptions(tool) {
  toolOptions.innerHTML = "";
  toolOptions.style.display = "none";

  if (tool.id === "split") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div class="form-group">
        <label>Bölme Şekli:</label>
        <div class="btn-group">
          <button type="button" class="btn-option active" onclick="setSplitMode(this, 'all')">Tüm Sayfaları Ayır</button>
          <button type="button" class="btn-option" onclick="setSplitMode(this, 'custom')">Belirli Aralıklar</button>
        </div>
      </div>
      <div class="form-group" id="split-range-group" style="display: none;">
        <label>Sayfa Aralıkları:</label>
        <input type="text" id="split-ranges" class="form-control" placeholder="1-3, 5, 8-12" value="1-2">
      </div>
    `;
  } else if (tool.id === "compress") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div class="form-group">
        <label>Sıkıştırma Seviyesi:</label>
        <div class="btn-group">
          <button type="button" class="btn-option" onclick="setOptionActive(this, 'compress-level', 'low')">Düşük</button>
          <button type="button" class="btn-option active" onclick="setOptionActive(this, 'compress-level', 'medium')">Orta</button>
          <button type="button" class="btn-option" onclick="setOptionActive(this, 'compress-level', 'high')">Yüksek</button>
        </div>
        <input type="hidden" id="compress-level" value="medium">
      </div>
    `;
  } else if (tool.id === "protect") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div class="form-group">
        <label>Belge Şifresi:</label>
        <input type="password" id="protect-password" class="form-control" placeholder="Şifrenizi girin">
      </div>
    `;
  } else if (tool.id === "unlock") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div class="form-group">
        <label>Mevcut Şifre:</label>
        <input type="password" id="unlock-password" class="form-control" placeholder="Belgenin şifresini girin">
      </div>
    `;
  } else if (tool.id === "watermark") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div class="form-group">
        <label>Filigran Metni:</label>
        <input type="text" id="watermark-text" class="form-control" value="GİZLİ">
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div class="form-group">
          <label>Açı:</label>
          <select id="watermark-rotation" class="form-control">
            <option value="45" selected>45°</option>
            <option value="0">0°</option>
            <option value="90">90°</option>
          </select>
        </div>
        <div class="form-group">
          <label>Renk:</label>
          <input type="color" id="watermark-color" class="form-control" value="#5B5CE5" style="height: 42px; padding: 2px;">
        </div>
      </div>
    `;
  } else if (tool.id === "page-numbers") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div class="form-group">
        <label>Konum:</label>
        <select id="page-num-position" class="form-control">
          <option value="bottom-center" selected>Alt Orta</option>
          <option value="bottom-right">Alt Sağ</option>
          <option value="bottom-left">Alt Sol</option>
          <option value="top-right">Üst Sağ</option>
          <option value="top-center">Üst Orta</option>
        </select>
      </div>
      <div class="form-group">
        <label>Biçim:</label>
        <input type="text" id="page-num-pattern" class="form-control" value="{n} / {total}">
      </div>
    `;
  } else if (tool.id === "redact") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div class="form-group">
        <label>Sansürlenecek Metin:</label>
        <input type="text" id="redact-term" class="form-control" placeholder="Örn: 12345678901">
        <small style="color: var(--text-secondary); margin-top: 0.25rem;">Bu ifade belgeden kalıcı olarak silinir.</small>
      </div>
    `;
  } else if (tool.id === "pdf-to-images") {
    toolOptions.style.display = "flex";
    toolOptions.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div class="form-group">
          <label>Format:</label>
          <select id="img-format" class="form-control">
            <option value="png" selected>PNG</option>
            <option value="jpg">JPG</option>
          </select>
        </div>
        <div class="form-group">
          <label>Çözünürlük:</label>
          <select id="img-dpi" class="form-control">
            <option value="150">150 DPI</option>
            <option value="200" selected>200 DPI</option>
            <option value="300">300 DPI</option>
          </select>
        </div>
      </div>
    `;
  }
}

function setSplitMode(btn, mode) {
  btn.parentElement.querySelectorAll(".btn-option").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  const rangeGroup = document.getElementById("split-range-group");
  if (rangeGroup) {
    rangeGroup.style.display = mode === "custom" ? "flex" : "none";
  }
}

function setOptionActive(btn, inputId, val) {
  btn.parentElement.querySelectorAll(".btn-option").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  const hiddenInput = document.getElementById(inputId);
  if (hiddenInput) hiddenInput.value = val;
}

// Handle File Selection
async function handleFiles(files) {
  const newFiles = Array.from(files);
  if (!newFiles.length) return;

  if (activeTool.multiple_files) {
    selectedFiles.push(...newFiles);
  } else {
    selectedFiles = [newFiles[0]];
  }

  renderFileList();
  actionSubmitBtn.disabled = selectedFiles.length === 0;

  if (activeTool.id === "organize" && selectedFiles.length > 0) {
    await setupOrganizeGrid(selectedFiles[0]);
  }
}

function renderFileList() {
  fileList.innerHTML = "";
  selectedFiles.forEach((file, index) => {
    const item = document.createElement("div");
    item.className = "file-item";
    const sizeStr = (file.size / 1024 / 1024).toFixed(2) + " MB";

    item.innerHTML = `
      <div class="file-info">
        <span style="color: var(--brand-primary);">${ICONS["file-text"]}</span>
        <div>
          <div class="file-name">${file.name}</div>
          <div class="file-size">${sizeStr}</div>
        </div>
      </div>
      <button class="remove-file-btn" onclick="removeFile(${index})" title="Kaldır">
        ${ICONS.trash}
      </button>
    `;
    fileList.appendChild(item);
  });
}

function removeFile(index) {
  selectedFiles.splice(index, 1);
  renderFileList();
  actionSubmitBtn.disabled = selectedFiles.length === 0;
  if (activeTool.id === "organize") {
    pageGridContainer.style.display = "none";
    pageGrid.innerHTML = "";
    organizePages = [];
  }
}

// Setup Page Grid for 'organize' tool
async function setupOrganizeGrid(file) {
  pageGridContainer.style.display = "block";
  pageGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 1rem;">Sayfalar taranıyor ve önizlemeler yükleniyor...</p>`;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/inspect", {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("Dosya okunamadı");
    const data = await res.json();
    activeJobId = data.job_id;

    organizePages = [];
    for (let i = 0; i < data.page_count; i++) {
      organizePages.push({
        page_index: i,
        rotation: 0,
        original_number: i + 1
      });
    }

    renderPageGrid();
  } catch (err) {
    showToast("Sayfa önizlemeleri yüklenirken hata oluştu: " + err.message, "error");
    pageGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--accent-red);">Sayfalar yüklenemedi.</p>`;
  }
}

function renderPageGrid() {
  pageGrid.innerHTML = "";
  if (!organizePages.length) {
    pageGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">Tüm sayfalar silindi.</p>`;
    return;
  }

  organizePages.forEach((p, idx) => {
    const card = document.createElement("div");
    card.className = "page-card";

    const thumbUrl = `/api/thumbnail/${activeJobId}/${p.page_index}`;
    card.innerHTML = `
      <img src="${thumbUrl}" class="page-thumb" style="transform: rotate(${p.rotation}deg);" alt="Sayfa ${p.original_number}">
      <span class="page-number-label">Sayfa ${p.original_number}</span>
      <div class="page-actions">
        <button class="page-action-btn" onclick="movePage(${idx}, -1)" ${idx === 0 ? "disabled" : ""} title="Sola Taşı">${ICONS.arrowLeft}</button>
        <button class="page-action-btn" onclick="rotatePage(${idx})" title="90° Döndür">${ICONS.rotate}</button>
        <button class="page-action-btn" onclick="movePage(${idx}, 1)" ${idx === organizePages.length - 1 ? "disabled" : ""} title="Sağa Taşı">${ICONS.arrowRight}</button>
        <button class="page-action-btn btn-delete" onclick="deletePage(${idx})" title="Sayfayı Sil">${ICONS.trash}</button>
      </div>
    `;
    pageGrid.appendChild(card);
  });
}

function movePage(index, dir) {
  const targetIndex = index + dir;
  if (targetIndex < 0 || targetIndex >= organizePages.length) return;
  const temp = organizePages[index];
  organizePages[index] = organizePages[targetIndex];
  organizePages[targetIndex] = temp;
  renderPageGrid();
}

function rotatePage(index) {
  organizePages[index].rotation = (organizePages[index].rotation + 90) % 360;
  renderPageGrid();
}

function deletePage(index) {
  organizePages.splice(index, 1);
  renderPageGrid();
  actionSubmitBtn.disabled = organizePages.length === 0;
}

// Hero Universal Dropzone Handling
function handleHeroFile(file) {
  const name = file.name.toLowerCase();
  heroDroppedFile = file;

  // Auto-detect based on file extension
  if (name.endsWith(".docx") || name.endsWith(".doc")) {
    const wordTool = allTools.find(t => t.id === "word-to-pdf");
    if (wordTool) {
      openToolModal(wordTool);
      handleFiles([file]);
      return;
    }
  } else if (name.endsWith(".pptx") || name.endsWith(".ppt")) {
    const pptTool = allTools.find(t => t.id === "ppt-to-pdf");
    if (pptTool) {
      openToolModal(pptTool);
      handleFiles([file]);
      return;
    }
  } else if (name.endsWith(".xlsx") || name.endsWith(".xls")) {
    const excelTool = allTools.find(t => t.id === "excel-to-pdf");
    if (excelTool) {
      openToolModal(excelTool);
      handleFiles([file]);
      return;
    }
  } else if (name.endsWith(".jpg") || name.endsWith(".png") || name.endsWith(".jpeg") || name.endsWith(".webp")) {
    const imgTool = allTools.find(t => t.id === "images-to-pdf");
    if (imgTool) {
      openToolModal(imgTool);
      handleFiles([file]);
      return;
    }
  }

  // If it's a PDF, show the quick action picker
  quickFileName.textContent = file.name;
  quickActionButtons.innerHTML = "";

  const popularToolIds = ["compress", "pdf-to-word", "split", "organize", "pdf-to-images", "protect", "watermark", "page-numbers"];
  popularToolIds.forEach(id => {
    const t = allTools.find(tool => tool.id === id);
    if (t) {
      const btn = document.createElement("button");
      btn.className = "quick-action-btn";
      btn.innerHTML = `${ICONS[t.icon] || ""} <span>${t.title}</span>`;
      btn.onclick = () => {
        quickActionModal.classList.remove("active");
        openToolModal(t);
        handleFiles([heroDroppedFile]);
      };
      quickActionButtons.appendChild(btn);
    }
  });

  quickActionModal.classList.add("active");
}

// Submit Operation to Task Queue
function submitOperation() {
  if (!activeTool || selectedFiles.length === 0) return;

  const formData = new FormData();
  let endpoint = `/api/${activeTool.id}`;

  try {
    if (activeTool.id === "merge" || activeTool.id === "images-to-pdf") {
      selectedFiles.forEach(f => formData.append("files", f));
    } else if (activeTool.id === "organize") {
      formData.append("file", selectedFiles[0]);
      formData.append("instructions", JSON.stringify(organizePages));
    } else if (activeTool.id === "split") {
      formData.append("file", selectedFiles[0]);
      const isCustom = document.getElementById("split-range-group").style.display !== "none";
      const ranges = isCustom ? (document.getElementById("split-ranges").value || "1") : "all";
      formData.append("ranges", ranges);
    } else if (activeTool.id === "compress") {
      formData.append("file", selectedFiles[0]);
      const level = document.getElementById("compress-level").value;
      formData.append("level", level);
    } else if (activeTool.id === "protect") {
      formData.append("file", selectedFiles[0]);
      const pw = document.getElementById("protect-password").value;
      if (!pw) throw new Error("Lütfen bir şifre belirleyin.");
      formData.append("password", pw);
    } else if (activeTool.id === "unlock") {
      formData.append("file", selectedFiles[0]);
      const pw = document.getElementById("unlock-password").value;
      if (!pw) throw new Error("Lütfen şifreyi girin.");
      formData.append("password", pw);
    } else if (activeTool.id === "watermark") {
      formData.append("file", selectedFiles[0]);
      formData.append("text", document.getElementById("watermark-text").value || "GİZLİ");
      formData.append("rotation", document.getElementById("watermark-rotation").value);
      formData.append("color", document.getElementById("watermark-color").value);
    } else if (activeTool.id === "page-numbers") {
      formData.append("file", selectedFiles[0]);
      formData.append("position", document.getElementById("page-num-position").value);
      formData.append("pattern", document.getElementById("page-num-pattern").value);
    } else if (activeTool.id === "redact") {
      formData.append("file", selectedFiles[0]);
      const term = document.getElementById("redact-term").value;
      if (!term.trim()) throw new Error("Lütfen sansürlenecek ifadeyi girin.");
      formData.append("search_term", term);
    } else if (activeTool.id === "pdf-to-images") {
      formData.append("file", selectedFiles[0]);
      formData.append("img_format", document.getElementById("img-format").value);
      formData.append("dpi", document.getElementById("img-dpi").value);
    } else {
      formData.append("file", selectedFiles[0]);
    }
  } catch (err) {
    showToast(err.message, "error");
    return;
  }

  const taskId = "task_" + Math.random().toString(36).substring(2, 9);
  const task = {
    id: taskId,
    toolId: activeTool.id,
    toolTitle: activeTool.title,
    fileName: selectedFiles[0]?.name || activeTool.title,
    formData: formData,
    endpoint: endpoint,
    status: "waiting", // "waiting", "uploading", "processing", "completed", "error"
    progress: 0,
    downloadUrl: null,
    downloadName: null
  };

  enqueueTask(task);
}

function enqueueTask(task) {
  taskQueue.push(task);
  renderQueueDock();

  // Update Modal State
  actionSubmitBtn.disabled = true;
  submitBtnText.textContent = "İşlem Başlatıldı...";
  submitSpinner.style.display = "block";
  if (minimizeTaskBtn) minimizeTaskBtn.style.display = "inline-block";

  if (progressContainer) {
    progressContainer.style.display = "block";
    progressStatusLabel.textContent = "Hazırlanıyor...";
    progressPercentageLabel.textContent = "0%";
    progressBarFill.style.width = "0%";
    progressBarFill.classList.remove("processing");
  }

  showToast(`${task.fileName} sıraya eklendi!`, "info");
  processQueue();
}

function processQueue() {
  if (activeTask) return; // Process 1 by 1 sequentially to keep memory usage low

  const next = taskQueue.find(t => t.status === "waiting");
  if (!next) {
    renderQueueDock();
    return;
  }

  activeTask = next;
  activeTask.status = "uploading";
  renderQueueDock();

  // If modal is currently displaying this tool
  if (workspaceOverlay.classList.contains("active") && activeTool?.id === activeTask.toolId) {
    submitBtnText.textContent = "İşlem Yapılıyor...";
    progressStatusLabel.textContent = "Yükleniyor...";
  }

  const xhr = new XMLHttpRequest();
  xhr.open("POST", activeTask.endpoint, true);
  xhr.responseType = "blob";

  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      const percent = Math.round((e.loaded / e.total) * 100);
      activeTask.progress = Math.min(percent, 99);

      if (workspaceOverlay.classList.contains("active") && activeTool?.id === activeTask.toolId) {
        progressPercentageLabel.textContent = `${activeTask.progress}%`;
        progressBarFill.style.width = `${activeTask.progress}%`;
      }
      renderQueueDock();
    }
  };

  xhr.upload.onload = () => {
    activeTask.status = "processing";
    if (workspaceOverlay.classList.contains("active") && activeTool?.id === activeTask.toolId) {
      progressStatusLabel.textContent = "İşleniyor...";
      progressPercentageLabel.textContent = "";
      progressBarFill.classList.add("processing");
    }
    renderQueueDock();
  };

  xhr.onload = () => {
    if (xhr.status === 200) {
      const disposition = xhr.getResponseHeader("content-disposition");
      let filename = `${activeTask.toolId}_podufu.pdf`;
      if (disposition && disposition.includes("filename=")) {
        const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (match && match[1]) {
          filename = match[1].replace(/['"]/g, "");
        }
      }

      const blob = xhr.response;
      const downloadUrl = window.URL.createObjectURL(blob);

      activeTask.status = "completed";
      activeTask.progress = 100;
      activeTask.downloadUrl = downloadUrl;
      activeTask.downloadName = filename;

      // If modal is still open on this tool
      if (workspaceOverlay.classList.contains("active") && activeTool?.id === activeTask.toolId) {
        workspaceBody.style.display = "none";
        workspaceFooter.style.display = "none";
        resultScreen.style.display = "flex";
        downloadLink.href = downloadUrl;
        downloadLink.download = filename;
      }

      // Auto trigger download & notify
      triggerDownload(downloadUrl, filename);
      showToast(`${filename} hazır, indirildi!`, "success");
    } else {
      activeTask.status = "error";
      showToast("İşlem sırasında sunucu hatası oluştu.", "error");
    }

    activeTask = null;
    renderQueueDock();
    processQueue();
  };

  xhr.onerror = () => {
    activeTask.status = "error";
    showToast("Bağlantı hatası oluştu.", "error");
    activeTask = null;
    renderQueueDock();
    processQueue();
  };

  xhr.send(activeTask.formData);
}

function triggerDownload(url, filename) {
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => a.remove(), 100);
}

function renderQueueDock() {
  if (!queueDock || !queueDockItems) return;

  const total = taskQueue.length;
  if (total === 0) {
    queueDock.style.display = "none";
    return;
  }

  queueDock.style.display = "block";
  const activeCount = taskQueue.filter(t => t.status !== "completed" && t.status !== "error").length;
  queueDockTitle.textContent = activeCount > 0 ? `İşlemler (${activeCount} aktif)` : `İşlemler (${total})`;

  queueDockItems.innerHTML = "";
  taskQueue.slice(-4).reverse().forEach(task => {
    const item = document.createElement("div");
    item.className = "queue-item";

    let statusText = "Sırada bekliyor...";
    let statusColor = "var(--text-secondary)";

    if (task.status === "uploading") {
      statusText = `Yükleniyor %${task.progress}`;
      statusColor = "var(--brand-primary)";
    } else if (task.status === "processing") {
      statusText = "İşleniyor...";
      statusColor = "var(--brand-primary)";
    } else if (task.status === "completed") {
      statusText = "Tamamlandı";
      statusColor = "var(--accent-green)";
    } else if (task.status === "error") {
      statusText = "Hata";
      statusColor = "var(--accent-red)";
    }

    item.innerHTML = `
      <div class="queue-item-header">
        <span class="queue-item-name" title="${task.fileName}">${task.fileName}</span>
        <span class="queue-item-status" style="color: ${statusColor};">${statusText}</span>
      </div>
      <div class="queue-item-progress-track">
        <div class="queue-item-progress-fill" style="width: ${task.progress}%; background: ${statusColor};"></div>
      </div>
    `;

    queueDockItems.appendChild(item);
  });
}

// Reset tool modal back to file upload
function resetActiveTool() {
  if (activeTool) {
    openToolModal(activeTool);
  }
}

// Setup Event Listeners
function setupEventListeners() {
  searchInput.addEventListener("input", filterTools);

  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const cat = btn.dataset.category;
      if (activeCategoryFilter === cat) {
        activeCategoryFilter = null;
        btn.classList.remove("active");
      } else {
        activeCategoryFilter = cat;
        filterButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
      }
      filterTools();
    });
  });

  closeModalBtn.addEventListener("click", closeModal);
  closeQuickModalBtn.addEventListener("click", () => quickActionModal.classList.remove("active"));
  resetToolBtn.addEventListener("click", resetActiveTool);
  actionSubmitBtn.addEventListener("click", submitOperation);
  if (minimizeTaskBtn) minimizeTaskBtn.addEventListener("click", closeModal);
  if (queueDockToggleBtn) {
    queueDockToggleBtn.addEventListener("click", () => {
      queueDock.style.display = "none";
    });
  }

  // Hero Dropzone Events
  heroDropzone.addEventListener("click", () => heroFileInput.click());
  heroFileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleHeroFile(e.target.files[0]);
    }
  });

  heroDropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    heroDropzone.classList.add("dragover");
  });

  heroDropzone.addEventListener("dragleave", () => {
    heroDropzone.classList.remove("dragover");
  });

  heroDropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    heroDropzone.classList.remove("dragover");
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleHeroFile(e.dataTransfer.files[0]);
    }
  });

  // Modal Dropzone Events
  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => handleFiles(e.target.files));

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer && e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  });

  // Close modals when clicking outside
  workspaceOverlay.addEventListener("click", (e) => {
    if (e.target === workspaceOverlay) closeModal();
  });
  quickActionModal.addEventListener("click", (e) => {
    if (e.target === quickActionModal) quickActionModal.classList.remove("active");
  });

  // ESC to close modal
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (workspaceOverlay.classList.contains("active")) closeModal();
      if (quickActionModal.classList.contains("active")) quickActionModal.classList.remove("active");
    }
  });
}

// Theme handling
function setupTheme() {
  const saved = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon(saved);

  themeToggleBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    updateThemeIcon(next);
  });
}

function updateThemeIcon(theme) {
  themeToggleBtn.innerHTML = theme === "dark"
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`
    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
}

// Legal Modal Logic
const legalModal = document.getElementById("legal-modal");
const legalModalTitle = document.getElementById("legal-modal-title");
const legalModalBody = document.getElementById("legal-modal-body");
const closeLegalModalBtn = document.getElementById("close-legal-modal-btn");

if (closeLegalModalBtn) {
  closeLegalModalBtn.addEventListener("click", () => legalModal.classList.remove("active"));
}
if (legalModal) {
  legalModal.addEventListener("click", (e) => {
    if (e.target === legalModal) legalModal.classList.remove("active");
  });
}

function openLegalModal(type) {
  if (!legalModal) return;

  if (type === "privacy") {
    legalModalTitle.textContent = "Gizlilik Politikası";
    legalModalBody.innerHTML = `
      <p><strong>Pödüfü.online</strong> olarak kullanıcılarımızın gizliliğine ve belge güvenliğine en üst düzeyde önem veriyoruz.</p>
      <br>
      <p><strong>1. Belge Güvenliği:</strong> Yüklediğiniz tüm PDF, Word, Excel ve görsel dosyaları yalnızca talep ettiğiniz dönüştürme ve düzenleme işleminin gerçekleştirilmesi amacıyla geçici olarak işlenir.</p>
      <br>
      <p><strong>2. Kalıcı Saklama Yoktur:</strong> Dosyalarınız kalıcı olarak sunucuda depolanmaz. İşlem tamamlandıktan sonra geçici çalışma alanları otomatik olarak temizlenir (maksimum 1 saat içinde tamamen silinir).</p>
      <br>
      <p><strong>3. Üçüncü Taraflarla Paylaşım:</strong> Belgeleriniz hiçbir üçüncü taraf kişi, kurum veya yapay zeka eğitim havuzuyla paylaşılmaz.</p>
      <br>
      <p><strong>4. KVKK & GDPR Uyumu:</strong> Hizmetimiz Avrupa Genel Veri Koruma Tüzüğü (GDPR) ve 6698 sayılı KVKK ilkelerine tam uyumludur.</p>
    `;
  } else if (type === "terms") {
    legalModalTitle.textContent = "Kullanım Koşulları";
    legalModalBody.innerHTML = `
      <p><strong>Pödüfü.online</strong> hizmetini kullanarak aşağıdaki şartları kabul etmiş sayılırsınız:</p>
      <br>
      <p><strong>1. Ücretsiz Hizmet:</strong> Platform tüm bireysel ve kurumsal kullanıcılara ücretsiz olarak sunulmaktadır.</p>
      <br>
      <p><strong>2. Yasal Sorumluluk:</strong> Kullanıcılar platforma yükledikleri belgelerin yasal mülkiyetine veya yetkisine sahip olduklarını beyan ederler. Yasadışı veya telif hakkı ihlali içeren materyallerin işlenmesi yasaktır.</p>
      <br>
      <p><strong>3. Hizmet Sürekliliği:</strong> Hizmet "olduğu gibi" sunulmakta olup, olası teknik aksaklıklardan doğabilecek durumlardan platform sorumlu tutulamaz.</p>
    `;
  } else if (type === "cookies") {
    legalModalTitle.textContent = "Çerez Politikası";
    legalModalBody.innerHTML = `
      <p><strong>1. Zorunlu Tercihler:</strong> Pödüfü.online yalnızca platformun doğru çalışabilmesi ve tema tercihinizin (Açık/Koyu Mod) hatırlanabilmesi için yerel tarayıcı depolamasını (localStorage) kullanır.</p>
      <br>
      <p><strong>2. Takip Çerezi Yoktur:</strong> Sitemizde kişisel verilerinizi toplayan, kimliğinizi tespit eden veya sizi web genelinde takip eden agresif üçüncü taraf reklam takip çerezleri kullanılmaz.</p>
    `;
  } else if (type === "contact") {
    legalModalTitle.textContent = "İletişim & Topluluk";
    legalModalBody.innerHTML = `
      <p>Pödüfü.online, <strong>MeadSocial</strong> topluluğu için geliştirilmiş bağımsız bir projedir.</p>
      <br>
      <p>Görüş, öneri, hata bildirimi veya iş birliği talepleriniz için topluluk kanallarımızdan bize ulaşabilirsiniz:</p>
      <br>
      <p>🌐 <strong>Topluluk:</strong> @meadsocial</p>
      <p>✉️ <strong>E-Posta:</strong> iletisim@meadsocial.com</p>
    `;
  }

  legalModal.classList.add("active");
}

// Toast Notifications
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Bootstrap
document.addEventListener("DOMContentLoaded", init);
