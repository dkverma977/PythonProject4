/* -------------------------------------------------------------
 * MOTO-TWIN Right Panel Component (RightPanelComponent.js)
 * Motor details card, SCADA feeding path SVG, document viewer, 
 * image lightbox, and maintenance logs manager
 * ------------------------------------------------------------- */

import { state, loadData } from '../app.js';

let activeMotorTag = '';
let zoomScale = 1.0;
let isPanning = false;
let startX = 0, startY = 0;
let translateX = 0, translateY = 0;

export const RightPanelComponent = {
  init() {
    setupTabControls();
    setupLightbox();
    setupDocViewer();
    setupMaintenanceLogger();
    
    // Bind print button
    document.getElementById('print-motor-btn').addEventListener('click', () => {
      window.print();
    });
  },

  // Hide Card when intermediate nodes are selected
  hideCard() {
    document.getElementById('right-empty-state').style.display = 'flex';
    document.getElementById('right-asset-card').style.display = 'none';
    activeMotorTag = '';
  },

  // Loads technical spec card details for a motor
  async loadMotor(tag) {
    try {
      const res = await fetch(`/api/motors/${tag}`);
      if (!res.ok) return;
      const m = await res.json();
      
      activeMotorTag = tag;
      
      // Update DOM selectors
      document.getElementById('right-empty-state').style.display = 'none';
      document.getElementById('right-asset-card').style.display = 'block';

      // Header Specs
      document.getElementById('asset-tag').textContent = m.tag;
      document.getElementById('asset-name').textContent = m.name;
      
      const badge = document.getElementById('asset-status-badge');
      badge.textContent = m.status;
      badge.className = `status-badge ${m.status.toLowerCase()}`;

      // Quick Spec Row
      document.getElementById('quick-power').textContent = `${m.power_kw} kW`;
      document.getElementById('quick-voltage').textContent = m.voltage < 1000 ? `${m.voltage} V` : `${(m.voltage/1000).toFixed(1)} kV`;
      document.getElementById('quick-rpm').textContent = m.rpm;
      
      const crit = document.getElementById('quick-critical');
      if (m.is_critical) {
        crit.textContent = 'Critical';
        crit.className = 'val critical';
      } else {
        crit.textContent = 'Standard';
        crit.className = 'val';
      }

      // TAB 1: General Specs
      document.getElementById('lbl-tag').textContent = m.tag;
      document.getElementById('lbl-name').textContent = m.name;
      document.getElementById('lbl-area').textContent = m.area;
      document.getElementById('lbl-service').textContent = m.service;
      document.getElementById('lbl-make').textContent = m.make;
      document.getElementById('lbl-model').textContent = m.model;
      document.getElementById('lbl-serial').textContent = m.serial_number;
      document.getElementById('lbl-year').textContent = m.mfg_year;
      document.getElementById('lbl-location').textContent = m.location;
      document.getElementById('lbl-remarks').textContent = m.remarks || "No supplementary remarks.";

      // TAB 2: Electrical Specs
      document.getElementById('lbl-power').textContent = `${m.power_kw} kW (${(m.power_kw * 1.34).toFixed(1)} HP)`;
      document.getElementById('lbl-voltage').textContent = `${m.voltage} V AC`;
      document.getElementById('lbl-current').textContent = `${m.current_amp} A`;
      document.getElementById('lbl-freq').textContent = `${m.frequency_hz} Hz`;
      document.getElementById('lbl-pf').textContent = m.pf;
      document.getElementById('lbl-cable-size').textContent = m.cable_size;
      document.getElementById('lbl-cable-len').textContent = `${m.cable_length_m} m`;
      document.getElementById('lbl-starter').textContent = m.starter_type;
      document.getElementById('lbl-breaker').textContent = m.breaker_details;
      document.getElementById('lbl-relay').textContent = m.relay_details;

      // TAB 3: Mechanical Specs
      document.getElementById('lbl-frame').textContent = m.frame_size;
      document.getElementById('lbl-protection').textContent = m.protection_class;
      document.getElementById('lbl-insulation').textContent = m.insulation_class;
      document.getElementById('lbl-duty').textContent = m.duty;
      document.getElementById('lbl-bearing-de').textContent = m.bearing_de;
      document.getElementById('lbl-bearing-nde').textContent = m.bearing_nde;
      document.getElementById('lbl-lubrication').textContent = m.lubrication_type;

      // TAB 4: Drawing SVG flowchart generator
      this.drawFeedingPath(m);

      // TAB 7: Maintenance Logs loading
      this.loadMaintenanceHistory(m.tag);

    } catch (err) {
      console.error("Error loading motor specification telemetry.", err);
    }
  },

  // Generates and inserts an interactive SVG SCADA flowchart representing the power path
  drawFeedingPath(m) {
    const container = document.getElementById('feeding-path-svg-wrapper');
    container.innerHTML = '';

    const isRunning = m.status === 'Running';
    const isFault = m.status === 'Fault';
    const flowColor = isRunning ? 'var(--color-success)' : (isFault ? 'var(--color-danger)' : 'var(--color-warning)');
    
    // Draw flow path utilizing dynamic HSL variables and classes
    const svgHTML = `
      <svg width="280" height="420" viewBox="0 0 280 420" xmlns="http://www.w3.org/2000/svg" style="background:#151518; border-radius:6px; border:1px solid var(--border-color);">
        <style>
          .flow-line {
            fill: none;
            stroke: var(--border-color-light);
            stroke-width: 3;
          }
          .flow-line.active {
            stroke: var(--color-success);
            stroke-dasharray: 8 6;
            animation: dash 1s linear infinite;
          }
          .flow-line.warning {
            stroke: var(--color-warning);
          }
          .flow-line.fault {
            stroke: var(--color-danger);
          }
          @keyframes dash {
            to { stroke-dashoffset: -14; }
          }
          .node-box {
            fill: var(--bg-card);
            stroke: var(--border-color-light);
            stroke-width: 1.5;
            rx: 4;
          }
          .node-box.active { stroke: var(--color-success); }
          .node-box.warning { stroke: var(--color-warning); }
          .node-box.fault { stroke: var(--color-danger); }
          .lbl-title { font-family: 'Source Code Pro', monospace; font-size: 11px; fill: var(--text-main); font-weight: bold; }
          .lbl-val { font-family: 'Outfit', sans-serif; font-size: 9px; fill: var(--text-muted); }
        </style>

        <!-- Connecting Lines -->
        <path class="flow-line ${isRunning ? 'active' : (isFault ? 'fault' : 'warning')}" d="M140,40 L140,360" />
        
        <!-- Grid Source (Incomer) -->
        <g transform="translate(40, 15)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.incoming || '33kV GRID'}</text>
          <text class="lbl-val" x="10" y="34">Primary Energy Feed Source</text>
        </g>

        <!-- Transformer Substation -->
        <g transform="translate(40, 85)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.substation}</text>
          <text class="lbl-val" x="10" y="34">Transformer Station Step-down</text>
        </g>

        <!-- PCC -->
        <g transform="translate(40, 155)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.pcc}</text>
          <text class="lbl-val" x="10" y="34">Power Control Busbar Breaker</text>
        </g>

        <!-- MCC -->
        <g transform="translate(40, 225)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.mcc}</text>
          <text class="lbl-val" x="10" y="34">Motor Control Cabinet Distribution</text>
        </g>

        <!-- Feeder Switch -->
        <g transform="translate(40, 295)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.feeder} (${m.starter_type})</text>
          <text class="lbl-val" x="10" y="34">MPCB: ${m.breaker_details}</text>
        </g>

        <!-- Motor Endpoint -->
        <g transform="translate(40, 365)">
          <rect class="node-box ${isRunning ? 'active' : (isFault ? 'fault' : 'warning')}" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24" fill="${flowColor}">${m.tag} - MTR</text>
          <text class="lbl-val" x="10" y="34">Power: ${m.power_kw} kW | Current: ${m.current_amp} A</text>
        </g>
      </svg>
    `;
    container.innerHTML = svgHTML;
  },

  // Renders the maintenance timeline
  async loadMaintenanceHistory(tag) {
    try {
      const res = await fetch(`/api/motors/${tag}/maintenance`);
      if (!res.ok) return;
      const logs = await res.json();
      
      const timeline = document.getElementById('maintenance-timeline');
      timeline.innerHTML = '';

      if (logs.length === 0) {
        timeline.innerHTML = '<div style="font-size:12px;color:var(--text-muted);text-align:center;padding:20px;">No historical maintenance logged.</div>';
        return;
      }

      logs.forEach(log => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        
        let paramsHTML = '';
        if (log.vibration_de_mm_s || log.vibration_nde_mm_s || log.megger_mohm) {
          paramsHTML = `
            <div class="timeline-params">
              ${log.vibration_de_mm_s ? `<span>DE Vib: ${log.vibration_de_mm_s} mm/s</span>` : ''}
              ${log.vibration_nde_mm_s ? `<span>NDE Vib: ${log.vibration_nde_mm_s} mm/s</span>` : ''}
              ${log.megger_mohm ? `<span>Megger: ${log.megger_mohm} M&Omega;</span>` : ''}
            </div>
          `;
        }

        item.innerHTML = `
          <div class="timeline-card">
            <div class="timeline-header">
              <span class="timeline-date">${log.log_date}</span>
              <span class="timeline-tech"><i class="fa-solid fa-user-gear"></i> ${log.technician}</span>
            </div>
            <div class="timeline-type">${log.type}</div>
            <div class="timeline-notes">${log.notes}</div>
            ${paramsHTML}
          </div>
        `;
        timeline.appendChild(item);
      });
    } catch (err) {
      console.error("Failed to load historical timeline.", err);
    }
  }
};

// 1. Tab Swapper control logic
function setupTabControls() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Toggle button
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      // Toggle pane
      const targetPaneId = tab.getAttribute('data-tab');
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      document.getElementById(targetPaneId).classList.add('active');
    });
  });
}

// 2. Lightbox Zoom image modals popup binding
function setupLightbox() {
  const lightbox = document.getElementById('modal-lightbox');
  const lbImg = document.getElementById('lightbox-img');
  const lbCap = document.getElementById('lightbox-caption');
  
  const thumbs = document.querySelectorAll('.img-thumbnail');
  thumbs.forEach(t => {
    t.addEventListener('click', () => {
      const img = t.querySelector('img');
      const cap = t.querySelector('span').textContent;
      
      lbImg.src = img.src;
      lbCap.textContent = cap;
      lightbox.classList.add('active');
    });
  });

  lightbox.querySelector('.close-modal').addEventListener('click', () => {
    lightbox.classList.remove('active');
  });
}

// 3. Document blueprints viewer zoomed modal controls
function setupDocViewer() {
  const viewer = document.getElementById('modal-viewer');
  const workspace = document.getElementById('viewer-workspace');
  const title = document.getElementById('viewer-title');
  
  // Bind Document items click to download vector svg drawings
  document.querySelectorAll('.doc-item').forEach(doc => {
    const openBtn = doc.querySelector('.open-doc-btn');
    const docFile = doc.getAttribute('data-doc');
    const docName = doc.querySelector('.doc-name').textContent;

    openBtn.addEventListener('click', async () => {
      // Reset zoom
      zoomScale = 1.0;
      translateX = 0;
      translateY = 0;
      workspace.innerHTML = '<div style="color:white;font-family:monospace;">Fetching Technical blueprint...</div>';
      title.innerHTML = `<i class="fa-solid fa-drafting-compass"></i> Drawing View: ${docName}`;
      viewer.classList.add('active');

      try {
        let fetchUrl = '';
        if (docFile.endsWith('.svg')) {
          fetchUrl = `/static/assets/drawings/${docFile}`;
          const res = await fetch(fetchUrl);
          const svgContent = await res.text();
          workspace.innerHTML = svgContent;
          
          // Apply base style to injected SVG
          const svg = workspace.querySelector('svg');
          if (svg) {
            svg.style.transform = `scale(${zoomScale}) translate(${translateX}px, ${translateY}px)`;
          }
        } else {
          // Render generic details inside the iframe viewer mock
          workspace.innerHTML = `
            <div style="background:#1e1e1e;border:1px solid #333;border-radius:6px;width:700px;padding:30px;color:white;font-family:sans-serif;">
              <h2 style="border-bottom:2px solid var(--color-primary);padding-bottom:10px;margin-bottom:15px;color:var(--color-primary);">${docName}</h2>
              <p style="margin-bottom:10px;font-size:14px;line-height:1.6;">Access Restricted: Physical document stored at central engineering vault cabinet.</p>
              <table style="width:100%;border-collapse:collapse;margin-top:15px;font-size:13px;">
                <tr style="border-bottom:1px solid #333;"><td style="padding:8px 0;color:#aaa;">Drawing Reference</td><td>MT-DOC-${activeMotorTag}-ENG</td></tr>
                <tr style="border-bottom:1px solid #333;"><td style="padding:8px 0;color:#aaa;">Revision Code</td><td>Rev. 2 (2025)</td></tr>
                <tr style="border-bottom:1px solid #333;"><td style="padding:8px 0;color:#aaa;">Storage Locker</td><td>Cabinet-A2 Shelf-3</td></tr>
              </table>
            </div>
          `;
        }
      } catch (err) {
        workspace.innerHTML = '<div style="color:#e74c3c;">Failed to pull drawing. File missing.</div>';
      }
    });
  });

  // Zooming Logic
  document.getElementById('zoom-in-btn').addEventListener('click', () => {
    adjustZoom(1.2);
  });
  document.getElementById('zoom-out-btn').addEventListener('click', () => {
    adjustZoom(0.8);
  });
  document.getElementById('zoom-fit-btn').addEventListener('click', () => {
    zoomScale = 1.0;
    translateX = 0;
    translateY = 0;
    updateViewerTransform();
  });

  function adjustZoom(factor) {
    zoomScale *= factor;
    // Limit bounds
    if (zoomScale < 0.4) zoomScale = 0.4;
    if (zoomScale > 4.0) zoomScale = 4.0;
    updateViewerTransform();
  }

  function updateViewerTransform() {
    const svg = workspace.querySelector('svg');
    if (svg) {
      svg.style.transform = `scale(${zoomScale}) translate(${translateX}px, ${translateY}px)`;
    }
  }

  // Pan dragging logic
  workspace.addEventListener('mousedown', (e) => {
    if (e.target.closest('svg')) {
      isPanning = true;
      startX = e.clientX - translateX;
      startY = e.clientY - translateY;
      e.preventDefault();
    }
  });

  document.addEventListener('mousemove', (e) => {
    if (!isPanning) return;
    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    updateViewerTransform();
  });

  document.addEventListener('mouseup', () => {
    isPanning = false;
  });
}

// 4. Save maintenance logs dialog modal
function setupMaintenanceLogger() {
  const modal = document.getElementById('modal-maintenance');
  const tagInput = document.getElementById('maint-tag');
  const dateInput = document.getElementById('maint-date');
  const saveBtn = document.getElementById('save-maintenance-btn');

  // Trigger modal
  document.getElementById('panel-right').addEventListener('click', (e) => {
    const btn = e.target.closest('#add-log-btn');
    if (!btn) return;
    
    if (state.role === 'Viewer') {
      alert("Viewer role is not authorized to submit logs.");
      return;
    }

    tagInput.value = activeMotorTag;
    
    // Set current date
    const today = new Date();
    dateInput.value = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
    
    // Clear inputs
    document.getElementById('maint-technician').value = '';
    document.getElementById('maint-notes').value = '';
    document.getElementById('maint-vib-de').value = '';
    document.getElementById('maint-vib-nde').value = '';
    document.getElementById('maint-megger').value = '';

    modal.classList.add('active');
  });

  saveBtn.addEventListener('click', async () => {
    const type = document.getElementById('maint-type').value;
    const tech = document.getElementById('maint-technician').value.trim();
    const notes = document.getElementById('maint-notes').value.trim();
    const dateVal = dateInput.value;

    const vibDE = document.getElementById('maint-vib-de').value;
    const vibNDE = document.getElementById('maint-vib-nde').value;
    const megger = document.getElementById('maint-megger').value;

    if (!tech || !notes) {
      alert("Please provide the technician name and findings description.");
      return;
    }

    const payload = {
      type: type,
      technician: tech,
      notes: notes,
      log_date: dateVal,
      vibration_de_mm_s: vibDE ? parseFloat(vibDE) : null,
      vibration_nde_mm_s: vibNDE ? parseFloat(vibNDE) : null,
      megger_mohm: megger ? parseFloat(megger) : null
    };

    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';

    try {
      const res = await fetch(`/api/motors/${activeMotorTag}/maintenance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        modal.classList.remove('active');
        // Refresh Timeline
        RightPanelComponent.loadMaintenanceHistory(activeMotorTag);
        // Refresh global state dates
        loadData();
      } else {
        const data = await res.json();
        alert(`Failed to save log: ${data.detail}`);
      }
    } catch (err) {
      alert("Network error occurred while saving the log.");
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save Timeline Log';
    }
  });
}
