/* -------------------------------------------------------------
 * MOTO-TWIN Right Panel Component (RightPanelComponent.js)
 * Complete 14-Tab Digital Twin Specification Engine & Interactive SCADA Controls
 * ------------------------------------------------------------- */

import { state, loadData } from '../app.js';

let activeMotorTag = '';
let chartMotorTrends = null;

export const RightPanelComponent = {
  init() {
    setupTabControls();
    setupMaintenanceLogger();
    setupWorkOrderCreator();
    
    const printBtn = document.getElementById('print-motor-btn');
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.print();
      });
    }
  },

  hideCard() {
    document.getElementById('right-empty-state').style.display = 'flex';
    document.getElementById('right-asset-card').style.display = 'none';
    activeMotorTag = '';
  },

  async loadMotor(tag) {
    try {
      const res = await fetch(`/api/motors/${tag}`);
      if (!res.ok) return;
      const m = await res.json();
      
      activeMotorTag = tag;
      
      document.getElementById('right-empty-state').style.display = 'none';
      document.getElementById('right-asset-card').style.display = 'block';

      // Header Specs
      document.getElementById('asset-tag').textContent = m.tag;
      document.getElementById('asset-name').textContent = m.name;
      
      const badge = document.getElementById('asset-status-badge');
      badge.textContent = m.status;
      badge.className = `status-badge ${m.status.toLowerCase()}`;

      const hBadge = document.getElementById('asset-health-badge');
      if (hBadge) {
        hBadge.textContent = `${m.health_score || 85}% ${m.condition_status || 'GOOD'}`;
        hBadge.style.color = (m.health_score || 85) >= 75 ? '#2ecc71' : ((m.health_score || 85) >= 60 ? '#f39c12' : '#e74c3c');
      }

      // Quick Spec Ribbon
      document.getElementById('quick-power').textContent = `${m.power_kw} kW`;
      document.getElementById('quick-voltage').textContent = m.voltage < 1000 ? `${m.voltage} V` : `${(m.voltage/1000).toFixed(1)} kV`;
      document.getElementById('quick-current').textContent = `${m.current_amp} A`;
      
      const crit = document.getElementById('quick-critical');
      crit.textContent = m.criticality || (m.is_critical ? "A - Critical" : "B - Important");
      crit.className = m.is_critical ? 'val critical' : 'val';

      // TAB 1: OVERVIEW
      document.getElementById('lbl-tag').textContent = m.tag;
      document.getElementById('lbl-name').textContent = m.name;
      document.getElementById('lbl-area').textContent = m.area || 'General';
      document.getElementById('lbl-service').textContent = m.service || 'Pump/Conveyor';
      document.getElementById('lbl-location').textContent = m.location || 'Plant Floor';
      document.getElementById('lbl-health-val').textContent = `${m.health_score || 85}%`;
      document.getElementById('lbl-condition-val').textContent = m.condition_status || 'GOOD';
      document.getElementById('lbl-next-pm').textContent = m.next_maintenance_date || '2026-11-10';
      document.getElementById('lbl-remarks').textContent = m.remarks || "No supplementary engineering remarks.";

      if (m.predictive_risk && document.getElementById('lbl-risk-val')) {
        const rEl = document.getElementById('lbl-risk-val');
        rEl.textContent = m.predictive_risk.risk_level;
        rEl.style.color = m.predictive_risk.risk_level.includes('CRITICAL') ? '#e74c3c' : (m.predictive_risk.risk_level.includes('HIGH') ? '#f39c12' : '#2ecc71');
      }

      // TAB 2: NAMEPLATE
      document.getElementById('lbl-make').textContent = m.make || m.manufacturer || 'ABB';
      document.getElementById('lbl-model').textContent = m.model || 'M3BP';
      document.getElementById('lbl-serial').textContent = m.serial_number || 'SN-9021';
      document.getElementById('lbl-year').textContent = m.mfg_year || 2022;
      document.getElementById('lbl-frame').textContent = m.frame_size || '315M';
      document.getElementById('lbl-efficiency').textContent = m.efficiency || '94.5%';

      // TAB 3: ELECTRICAL
      document.getElementById('lbl-power').textContent = `${m.power_kw} kW (${(m.power_kw * 1.34).toFixed(1)} HP)`;
      document.getElementById('lbl-voltage').textContent = `${m.voltage} V AC`;
      document.getElementById('lbl-current').textContent = `${m.current_amp} A`;
      document.getElementById('lbl-freq').textContent = `${m.frequency_hz || 50} Hz`;
      document.getElementById('lbl-pf').textContent = m.pf || 0.85;
      document.getElementById('lbl-starter').textContent = m.starter_type || 'DOL';
      document.getElementById('lbl-breaker').textContent = m.breaker_details || 'MPCB Protected';
      document.getElementById('lbl-relay').textContent = m.relay_details || 'Numerical Relay';

      // TAB 4: MECHANICAL
      document.getElementById('lbl-bearing-de').textContent = m.bearing_de || '6312-C3';
      document.getElementById('lbl-bearing-nde').textContent = m.bearing_nde || '6212-C3';
      document.getElementById('lbl-lubrication').textContent = m.lubrication_type || 'Grease Mobilith SHC 100';
      document.getElementById('lbl-protection').textContent = m.protection_class || 'IP55';
      document.getElementById('lbl-insulation').textContent = m.insulation_class || 'Class F';
      document.getElementById('lbl-duty').textContent = m.duty || 'S1 Continuous';

      // TAB 5: LIVE TELEMETRY & GAUGES
      this.loadLiveTelemetry(m.tag);

      // TAB 6: TRENDS
      this.loadMotorTrends(m.tag);

      // TAB 7: HEALTH FACTORS
      this.renderHealthFactors(m.health_factors || []);

      // TAB 8: MAINTENANCE & WORK ORDERS
      this.loadMaintenanceHistory(m.tag);

      // TAB 9: ALARMS
      this.loadMotorAlarms(m.tag);

      // TAB 10: FAILURES
      this.loadMotorFailures(m.tag);

      // TAB 11: ENERGY
      document.getElementById('lbl-daily-kwh').textContent = `${(m.power_kw * 18.5).toFixed(1)} kWh`;
      document.getElementById('lbl-monthly-kwh').textContent = `${(m.power_kw * 18.5 * 30).toFixed(0)} kWh`;
      document.getElementById('lbl-daily-cost').textContent = `$${(m.power_kw * 18.5 * 0.12).toFixed(2)}`;

      // TAB 12: POWER PATH SVG
      this.drawFeedingPath(m);

      // TAB 14: AUDIT HISTORY
      this.loadMotorAuditHistory(m.tag);

    } catch (err) {
      console.error("Error loading motor digital twin details.", err);
    }
  },

  async loadLiveTelemetry(tag) {
    try {
      const res = await fetch(`/api/motors/${tag}/telemetry?hours=1`);
      if (!res.ok) return;
      const records = await res.json();
      if (records.length > 0) {
        const latest = records[records.length - 1];
        if (document.getElementById('live-vib-de')) document.getElementById('live-vib-de').textContent = `${latest.vibration_de} mm/s`;
        if (document.getElementById('live-vib-nde')) document.getElementById('live-vib-nde').textContent = `${latest.vibration_nde} mm/s`;
        if (document.getElementById('live-temp-de')) document.getElementById('live-temp-de').textContent = `${latest.temperature_de} °C`;
        if (document.getElementById('live-temp-wind')) document.getElementById('live-temp-wind').textContent = `${latest.winding_temperature} °C`;
        if (document.getElementById('live-current')) document.getElementById('live-current').textContent = `${latest.current} A`;
        if (document.getElementById('live-voltage')) document.getElementById('live-voltage').textContent = `${latest.voltage} V`;
      }
    } catch (err) {
      console.error("Failed to load live telemetry.", err);
    }
  },

  async loadMotorTrends(tag) {
    try {
      const res = await fetch(`/api/motors/${tag}/telemetry?hours=24`);
      if (!res.ok) return;
      const records = await res.json();
      
      const el = document.getElementById('chart-motor-trends');
      if (!el) return;
      if (chartMotorTrends) chartMotorTrends.destroy();

      const ctx = el.getContext('2d');
      chartMotorTrends = new Chart(ctx, {
        type: 'line',
        data: {
          labels: records.map(r => r.timestamp ? r.timestamp.split(' ')[1] : ''),
          datasets: [
            { label: 'Vibration DE (mm/s)', data: records.map(r => r.vibration_de), borderColor: '#f39c12', tension: 0.3 },
            { label: 'DE Temp (°C)', data: records.map(r => r.temperature_de), borderColor: '#e74c3c', tension: 0.3 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: '#e1e7ed', font: { size: 10 } } } },
          scales: {
            x: { grid: { color: '#2f2f35' }, ticks: { color: '#e1e7ed' } },
            y: { grid: { color: '#2f2f35' }, ticks: { color: '#e1e7ed' } }
          }
        }
      });
    } catch (err) {
      console.error("Failed to load motor trends chart.", err);
    }
  },

  renderHealthFactors(factors) {
    const list = document.getElementById('health-factors-list');
    if (!list) return;
    list.innerHTML = '';
    if (factors.length === 0) {
      list.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:10px;">All health score metrics within optimal limits.</div>';
      return;
    }
    factors.forEach(f => {
      const div = document.createElement('div');
      div.className = `health-factor-item ${f.status}`;
      div.innerHTML = `
        <div><strong>${f.factor}</strong>: ${f.value}</div>
        <span style="font-weight:bold;color:${f.status === 'CRITICAL' ? '#e74c3c' : (f.status === 'WARNING' ? '#f39c12' : '#2ecc71')}">${f.impact}</span>
      `;
      list.appendChild(div);
    });
  },

  async loadMotorAlarms(tag) {
    const list = document.getElementById('motor-alarms-list');
    if (!list) return;
    try {
      const res = await fetch(`/api/alarms?motor_tag=${tag}`);
      if (!res.ok) return;
      const alarms = await res.json();
      list.innerHTML = '';
      if (alarms.length === 0) {
        list.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:10px;">No active or historical alarms for this asset.</div>';
        return;
      }
      alarms.forEach(a => {
        const item = document.createElement('div');
        item.style.cssText = "background:var(--bg-card);border:1px solid var(--border-color);padding:10px;border-radius:6px;margin-bottom:8px;font-size:12px;";
        item.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="font-weight:bold;color:${a.severity === 'CRITICAL' ? '#e74c3c' : '#f39c12'};"><i class="fa-solid fa-triangle-exclamation"></i> ${a.severity}: ${a.parameter}</span>
            <span style="font-size:10px;color:var(--text-muted);">${a.timestamp}</span>
          </div>
          <div>Actual: <strong>${a.actual_value}</strong> (Limit: ${a.limit_value})</div>
          <div style="margin-top:6px;display:flex;gap:8px;">
            ${!a.acknowledged ? `<button class="action-btn ack-alarm-btn" data-id="${a.id}">Acknowledge</button>` : '<span style="color:#2ecc71;"><i class="fa-solid fa-check"></i> Acknowledged</span>'}
            ${!a.cleared ? `<button class="action-btn clear-alarm-btn" data-id="${a.id}">Clear</button>` : '<span style="color:#2ecc71;"><i class="fa-solid fa-check-double"></i> Cleared</span>'}
          </div>
        `;
        list.appendChild(item);
      });

      // Bind buttons
      list.querySelectorAll('.ack-alarm-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          await fetch(`/api/alarms/${btn.getAttribute('data-id')}/acknowledge`, { method: 'POST' });
          RightPanelComponent.loadMotorAlarms(tag);
        });
      });
      list.querySelectorAll('.clear-alarm-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          await fetch(`/api/alarms/${btn.getAttribute('data-id')}/clear`, { method: 'POST' });
          RightPanelComponent.loadMotorAlarms(tag);
        });
      });

    } catch (err) {
      console.error("Failed to load motor alarms.", err);
    }
  },

  async loadMotorFailures(tag) {
    const list = document.getElementById('motor-failures-list');
    if (!list) return;
    try {
      const res = await fetch(`/api/failures?motor_tag=${tag}`);
      if (!res.ok) return;
      const fails = await res.json();
      list.innerHTML = '';
      if (fails.length === 0) {
        list.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:10px;">Zero breakdown failure events recorded.</div>';
        return;
      }
      fails.forEach(f => {
        const item = document.createElement('div');
        item.style.cssText = "background:var(--bg-card);border:1px solid var(--border-color);padding:10px;border-radius:6px;margin-bottom:8px;font-size:12px;";
        item.innerHTML = `
          <div style="display:flex;justify-content:space-between;font-weight:bold;color:#e74c3c;">
            <span><i class="fa-solid fa-burst"></i> ${f.failure_mode}</span>
            <span>${f.failure_date}</span>
          </div>
          <div style="margin-top:4px;">Cause: ${f.root_cause}</div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">Downtime: ${f.downtime_hours} hrs | Loss: $${f.production_loss} | Repair: $${f.repair_cost}</div>
        `;
        list.appendChild(item);
      });
    } catch (err) {
      console.error("Failed to load motor failures.", err);
    }
  },

  async loadMotorAuditHistory(tag) {
    const list = document.getElementById('motor-audit-list');
    if (!list) return;
    try {
      const res = await fetch('/api/audit?limit=20');
      if (!res.ok) return;
      const logs = await res.json();
      const motorLogs = logs.filter(l => l.entity_id === tag);
      list.innerHTML = '';
      if (motorLogs.length === 0) {
        list.innerHTML = '<div style="font-size:12px;color:var(--text-muted);padding:10px;">No recent audit changes logged.</div>';
        return;
      }
      motorLogs.forEach(l => {
        const item = document.createElement('div');
        item.style.cssText = "border-bottom:1px solid var(--border-color);padding:8px 0;font-size:11px;";
        item.innerHTML = `
          <div style="display:flex;justify-content:space-between;color:var(--color-primary);">
            <span><strong>${l.action}</strong> by ${l.username}</span>
            <span style="color:var(--text-muted);">${l.timestamp}</span>
          </div>
        `;
        list.appendChild(item);
      });
    } catch (err) {
      console.error("Failed to load motor audit log.", err);
    }
  },

  drawFeedingPath(m) {
    const container = document.getElementById('feeding-path-svg-wrapper');
    if (!container) return;
    container.innerHTML = '';

    const isRunning = m.status === 'Running';
    const isFault = m.status === 'Fault';
    const flowColor = isRunning ? '#2ecc71' : (isFault ? '#e74c3c' : '#f39c12');
    
    const svgHTML = `
      <svg width="280" height="420" viewBox="0 0 280 420" xmlns="http://www.w3.org/2000/svg" style="background:#151518; border-radius:6px; border:1px solid var(--border-color);">
        <style>
          .flow-line { fill: none; stroke: #3e3e46; stroke-width: 3; }
          .flow-line.active { stroke: #2ecc71; stroke-dasharray: 8 6; animation: dash 1s linear infinite; }
          .flow-line.fault { stroke: #e74c3c; }
          @keyframes dash { to { stroke-dashoffset: -14; } }
          .node-box { fill: #252529; stroke: #3e3e46; stroke-width: 1.5; rx: 4; cursor: pointer; }
          .lbl-title { font-family: 'Source Code Pro', monospace; font-size: 11px; fill: #e1e7ed; font-weight: bold; }
          .lbl-val { font-family: 'Outfit', sans-serif; font-size: 9px; fill: #8e9ca8; }
        </style>

        <path class="flow-line ${isRunning ? 'active' : (isFault ? 'fault' : '')}" d="M140,40 L140,360" />
        
        <g transform="translate(40, 15)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">PLANT-01 (Main Grid)</text>
          <text class="lbl-val" x="10" y="34">Capacity: 120 MW Incomer</text>
        </g>

        <g transform="translate(40, 85)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.substation || 'Main Substation-1'}</text>
          <text class="lbl-val" x="10" y="34">Substation Step-down 33kV</text>
        </g>

        <g transform="translate(40, 155)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.pcc || 'PCC-1'}</text>
          <text class="lbl-val" x="10" y="34">Power Control Center Incomer</text>
        </g>

        <g transform="translate(40, 225)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.mcc || 'MCC-1'}</text>
          <text class="lbl-val" x="10" y="34">Motor Control Cabinet</text>
        </g>

        <g transform="translate(40, 295)">
          <rect class="node-box" x="0" y="0" width="200" height="40" />
          <text class="lbl-title" x="10" y="24">${m.feeder || 'Feeder-1'} (${m.starter_type || 'DOL'})</text>
          <text class="lbl-val" x="10" y="34">MPCB: ${m.breaker_details || 'Protected'}</text>
        </g>

        <g transform="translate(40, 365)">
          <rect class="node-box" x="0" y="0" width="200" height="40" style="stroke:${flowColor};" />
          <text class="lbl-title" x="10" y="24" fill="${flowColor}">${m.tag} - Motor</text>
          <text class="lbl-val" x="10" y="34">Rating: ${m.power_kw} kW | ${m.voltage} V</text>
        </g>
      </svg>
    `;
    container.innerHTML = svgHTML;
  },

  async loadMaintenanceHistory(tag) {
    try {
      const res = await fetch(`/api/motors/${tag}/maintenance`);
      if (!res.ok) return;
      const logs = await res.json();
      
      const timeline = document.getElementById('maintenance-timeline');
      if (!timeline) return;
      timeline.innerHTML = '';

      if (logs.length === 0) {
        timeline.innerHTML = '<div style="font-size:12px;color:var(--text-muted);text-align:center;padding:20px;">No historical maintenance logged.</div>';
        return;
      }

      logs.forEach(log => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
          <div class="timeline-card" style="background:var(--bg-card);border:1px solid var(--border-color);padding:10px;border-radius:6px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--color-primary);margin-bottom:4px;">
              <span>${log.log_date}</span>
              <span><i class="fa-solid fa-user-gear"></i> ${log.technician}</span>
            </div>
            <div style="font-weight:bold;font-size:12px;">${log.type}</div>
            <div style="font-size:12px;margin-top:4px;">${log.work_description || log.notes}</div>
          </div>
        `;
        timeline.appendChild(item);
      });
    } catch (err) {
      console.error("Failed to load maintenance timeline.", err);
    }
  }
};

function setupTabControls() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const targetPaneId = tab.getAttribute('data-tab');
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const targetPane = document.getElementById(targetPaneId);
      if (targetPane) targetPane.classList.add('active');
    });
  });
}

function setupMaintenanceLogger() {
  const modal = document.getElementById('modal-maintenance');
  const tagInput = document.getElementById('maint-tag');
  const dateInput = document.getElementById('maint-date');
  const saveBtn = document.getElementById('save-maintenance-btn');

  if (!modal || !saveBtn) return;

  saveBtn.addEventListener('click', async () => {
    const type = document.getElementById('maint-type').value;
    const tech = document.getElementById('maint-technician').value.trim();
    const notes = document.getElementById('maint-notes').value.trim();
    const dateVal = dateInput.value;

    if (!tech || !notes) {
      alert("Please provide the technician name and findings description.");
      return;
    }

    const payload = {
      type: type,
      technician: tech,
      notes: notes,
      log_date: dateVal
    };

    try {
      const res = await fetch(`/api/motors/${activeMotorTag}/maintenance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        modal.classList.remove('active');
        RightPanelComponent.loadMaintenanceHistory(activeMotorTag);
        loadData();
      } else {
        alert("Failed to save log.");
      }
    } catch (err) {
      alert("Error saving log.");
    }
  });
}

function setupWorkOrderCreator() {
  const woBtn = document.getElementById('add-wo-btn');
  if (!woBtn) return;
  woBtn.addEventListener('click', async () => {
    const title = prompt("Enter Work Order Title:", `Inspect ${activeMotorTag}`);
    if (!title) return;
    try {
      const res = await fetch('/api/work-orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ motor_tag: activeMotorTag, title: title, priority: "High" })
      });
      if (res.ok) {
        alert("Work Order created successfully!");
      }
    } catch (err) {
      alert("Error creating Work Order.");
    }
  });
}
