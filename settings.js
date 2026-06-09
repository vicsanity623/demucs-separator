/* =====================================================
   DIY Electronics Workbench — settings.js
   Dynamic Performance, Sizing & Simulation controls
   ===================================================== */

// Global Settings Configuration Object
let workbenchSettings = {
    fontSize: 12,           // Base UI size in px
    cardScale: 1.0,         // Width scale factor for components
    cardHeightScale: 1.0,   // Height scale factor for components
    simSpeed: 300,          // Simulation speed time dilation multiplier
    perfMode: false         // CPU optimization mode
};

// Load saved settings on startup
function loadSettingsFromStorage() {
    const saved = localStorage.getItem('workbench_settings');
    if (saved) {
        try {
            workbenchSettings = { ...workbenchSettings, ...JSON.parse(saved) };
        } catch (e) {
            console.error("Error reading settings", e);
        }
    }
    applySettingsToDOM();
}

// Apply settings instantly to the active viewport
function applySettingsToDOM() {
    const root = document.documentElement;

    // 1. Apply global font scaling
    root.style.setProperty('--base-font-size', `${workbenchSettings.fontSize}px`);

    // 2. Apply component card width & height scaling
    root.style.setProperty('--card-scale', workbenchSettings.cardScale);
    root.style.setProperty('--card-height-scale', workbenchSettings.cardHeightScale);

    // 3. Sync time dilation factor with app.js sim engine
    if (typeof simSpeedMultiplier !== 'undefined') {
        simSpeedMultiplier = workbenchSettings.simSpeed;
    }

    // 4. Toggle performance engine class on body
    document.body.classList.toggle('perf-mode-active', workbenchSettings.perfMode);
}

// Check if a component card is currently visible in the active viewport
function isCardInViewport(cardId) {
    const el = document.getElementById(cardId);
    if (!el) return false;

    const rect = el.getBoundingClientRect();
    return (
        rect.bottom >= 0 &&
        rect.right >= 0 &&
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.left <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// ─── SETTINGS MANAGER MODAL GUI ──────────────────────────────────────────────
function openSettingsManager() {
    let modal = document.getElementById('settings-overlay');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'settings-overlay';
        modal.className = 'overlay hidden';
        modal.onclick = (e) => { if (e.target.id === 'settings-overlay') closeSettingsManager(); };
        document.body.appendChild(modal);
    }
    modal.classList.remove('hidden');
    renderSettingsMenu();
}

function closeSettingsManager() {
    const modal = document.getElementById('settings-overlay');
    if (modal) modal.classList.add('hidden');
}

function renderSettingsMenu() {
    const overlay = document.getElementById('settings-overlay');
    if (!overlay) return;

    overlay.innerHTML = `
    <div class="modal" style="max-width: 380px; width: 92%; background: var(--bg-panel); border: 1px solid var(--border-hi); border-radius: var(--radius-lg); padding: 20px; margin: auto; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); box-shadow: var(--shadow-card); z-index: 10000; display:flex; flex-direction:column; gap:16px;">
      <div class="modal-head" style="display:flex; justify-content:space-between; align-items:center;">
        <span class="modal-title" style="font-weight:700; color:var(--teal); font-family:var(--font-mono); font-size:13px;">⚙️ Engine Settings</span>
        <button onclick="closeSettingsManager()" class="modal-close" style="background:none; border:none; color:var(--text-secondary); cursor:pointer; font-size:16px;">✕</button>
      </div>
      
      <!-- 1. Font Size Control -->
      <div style="display:flex; flex-direction:column; gap:4px;">
        <div style="display:flex; justify-content:space-between; font-size:11px;">
          <span class="text-muted">UI Font Size</span>
          <span id="val-fontSize" class="font-mono text-teal">${workbenchSettings.fontSize}px</span>
        </div>
        <input type="range" min="9" max="16" step="1" value="${workbenchSettings.fontSize}" oninput="handleSettingInput('fontSize', this.value)" onchange="saveSettingChange()">
      </div>

      <!-- 2. Component Card Width Scaling -->
      <div style="display:flex; flex-direction:column; gap:4px;">
        <div style="display:flex; justify-content:space-between; font-size:11px;">
          <span class="text-muted">Card Width Scale</span>
          <span id="val-cardScale" class="font-mono text-teal">${workbenchSettings.cardScale.toFixed(2)}x</span>
        </div>
        <input type="range" min="0.75" max="1.30" step="0.05" value="${workbenchSettings.cardScale}" oninput="handleSettingInput('cardScale', this.value)" onchange="saveSettingChange()">
      </div>

      <!-- 3. Component Card Height Scaling -->
      <div style="display:flex; flex-direction:column; gap:4px;">
        <div style="display:flex; justify-content:space-between; font-size:11px;">
          <span class="text-muted">Card Height Scale</span>
          <span id="val-cardHeightScale" class="font-mono text-teal">${workbenchSettings.cardHeightScale.toFixed(2)}x</span>
        </div>
        <input type="range" min="0.75" max="1.30" step="0.05" value="${workbenchSettings.cardHeightScale}" oninput="handleSettingInput('cardHeightScale', this.value)" onchange="saveSettingChange()">
      </div>

      <!-- 4. Simulation Speed (Time Dilation) -->
      <div style="display:flex; flex-direction:column; gap:4px;">
        <div style="display:flex; justify-content:space-between; font-size:11px;">
          <span class="text-muted">Discharge Speed (Time Dilation)</span>
          <span id="val-simSpeed" class="font-mono text-teal">${workbenchSettings.simSpeed}x</span>
        </div>
        <input type="range" min="1" max="1000" step="10" value="${workbenchSettings.simSpeed}" oninput="handleSettingInput('simSpeed', this.value)" onchange="saveSettingChange()">
      </div>

      <!-- 5. CPU & Processing Optimization Toggle -->
      <div style="display:flex; justify-content:space-between; align-items:center; background:var(--bg-deepest); padding:10px; border-radius:var(--radius); border:1px solid var(--border);">
        <div style="display:flex; flex-direction:column; gap:2px; max-width:70%;">
          <span style="font-size:11px; font-weight:600; color:var(--text-primary);">High FPS CPU Mode</span>
          <span style="font-size:9px; color:var(--text-muted);">Disables wire flow animations & limits layout updates to visible cards.</span>
        </div>
        <div class="switch-track ${workbenchSettings.perfMode ? 'on' : ''}" onclick="togglePerformanceModeUI()" style="transform: scale(0.85); cursor: pointer;">
          <div class="switch-thumb"></div>
        </div>
      </div>

      <div class="modal-foot" style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
        <button class="btn btn-secondary" style="border-color: var(--border-hi);" onclick="exportToPDF()">🖨️ Export PDF Blueprint</button>
        <button class="btn btn-teal" onclick="closeSettingsManager()">Done</button>
      </div>
    </div>
  `;
}

// 60FPS Drag handler - updates text values and CSS variables without rebuilding the modal
function handleSettingInput(field, val) {
    workbenchSettings[field] = parseFloat(val);
    applySettingsToDOM();

    // Real-time wire snap update during slider adjustments
    if (typeof updateWires !== 'undefined') {
        updateWires();
    }

    const labelMap = {
        fontSize: 'val-fontSize',
        cardScale: 'val-cardScale',
        cardHeightScale: 'val-cardHeightScale',
        simSpeed: 'val-simSpeed'
    };

    const elId = labelMap[field];
    const suffix = field === 'fontSize' ? 'px' : 'x';
    const displayVal = document.getElementById(elId);
    if (displayVal) {
        displayVal.textContent = parseFloat(val).toFixed(field === 'fontSize' ? 0 : 2) + suffix;
    }
}

// Persistent save handler - triggered when slider mouse-up release occurs
function saveSettingChange() {
    localStorage.setItem('workbench_settings', JSON.stringify(workbenchSettings));
}

function togglePerformanceModeUI() {
    workbenchSettings.perfMode = !workbenchSettings.perfMode;
    localStorage.setItem('workbench_settings', JSON.stringify(workbenchSettings));
    applySettingsToDOM();
    renderSettingsMenu();
    showToast(workbenchSettings.perfMode ? 'High FPS Mode Enabled' : 'Standard Physics Mode Active', 'info');
}

// Landscape print exporter
function exportToPDF() {
    closeSettingsManager();
    showToast('Generating PDF Blueprint... Please select Save to PDF in your print settings.', 'info');
    setTimeout(() => {
        window.print();
    }, 600);
}

// Initialize settings when file loads
loadSettingsFromStorage();