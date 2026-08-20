/* -------------------------------------------------------------
 * MOTO-TWIN Center Panel Component (CenterPanelComponent.js)
 * Breadcrumbs, Child Equipment Lists, & Filtered Asset Directory Grid
 * ------------------------------------------------------------- */

import { navigateToNode, state } from '../app.js';
import { TreeComponent } from './TreeComponent.js';
import { RightPanelComponent } from './RightPanelComponent.js';

export const CenterPanelComponent = {
  init() {
    setupExportButtons();
  },

  // Generates and renders breadcrumb trails based on the selected node
  renderBreadcrumbs(node) {
    const container = document.getElementById('header-breadcrumb');
    if (!container) return;
    container.innerHTML = '';

    // Always start with plant
    const plantCrumb = createCrumb('Plant Network', 'plant');
    container.appendChild(plantCrumb);

    if (node.type === 'plant') return;

    let pathParts = [];
    
    if (node.type === 'motor') {
      const parentFeeder = TreeComponent.findParentNodeId(node.id);
      if (parentFeeder) {
        pathParts = parentFeeder.id.split('|');
      }
      pathParts.push(node.id);
    } else {
      pathParts = node.id.split('|');
    }

    let currentId = '';
    pathParts.forEach((part, index) => {
      container.appendChild(createSeparator());
      
      const isLast = index === pathParts.length - 1;
      let label = part;
      let type = 'substation';
      
      if (index === 0) {
        currentId = part;
        type = 'substation';
      } else if (index === 1) {
        currentId += `|${part}`;
        type = 'pcc';
      } else if (index === 2) {
        currentId += `|${part}`;
        type = 'mcc';
      } else if (index === 3) {
        currentId += `|${part}`;
        type = 'feeder';
      } else {
        currentId = part;
        type = 'motor';
      }

      const crumb = createCrumb(label, currentId, type, isLast);
      container.appendChild(crumb);
    });
  },

  // Renders the child list of the selected node
  loadEquipmentList(node) {
    const title = document.getElementById('equipment-title');
    const summary = document.getElementById('equipment-summary');
    const table = document.getElementById('equipment-table');
    
    if (title) title.textContent = `Connected Assets: ${node.label}`;
    if (summary) summary.innerHTML = '';
    if (table) table.innerHTML = '';

    const treeNode = findNodeInTree(node.id, state.treeData);
    if (!treeNode || !treeNode.children || treeNode.children.length === 0) {
      if (table) table.innerHTML = '<tbody><tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-muted);">No child equipment connected to this node.</td></tr></tbody>';
      return;
    }

    const children = treeNode.children;
    const totalCount = children.length;
    const runningCount = children.filter(c => (c.status || '').toLowerCase() === 'running').length;
    const standbyCount = children.filter(c => (c.status || '').toLowerCase() === 'standby').length;
    const faultCount = children.filter(c => (c.status || '').toLowerCase() === 'fault').length;

    if (summary) {
      summary.innerHTML = `
        <div class="summary-item"><span class="lbl">Total Nodes:</span><span class="val">${totalCount}</span></div>
        <div class="summary-item"><span class="lbl" style="color:var(--color-success);">Running:</span><span class="val">${runningCount}</span></div>
        <div class="summary-item"><span class="lbl" style="color:var(--color-warning);">Standby:</span><span class="val">${standbyCount}</span></div>
        <div class="summary-item"><span class="lbl" style="color:var(--color-danger);">Fault:</span><span class="val">${faultCount}</span></div>
      `;
    }

    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    if (node.type === 'feeder' || (children[0] && children[0].type === 'motor')) {
      thead.innerHTML = `
        <tr>
          <th>Motor Tag</th>
          <th>Description / Name</th>
          <th>Health Score</th>
          <th>Criticality</th>
          <th>Rating (kW)</th>
          <th>Voltage (V)</th>
          <th>Status</th>
        </tr>
      `;

      children.forEach(m => {
        const tr = document.createElement('tr');
        const hVal = m.health_score !== undefined ? m.health_score : 85;
        const hColor = hVal >= 75 ? '#2ecc71' : (hVal >= 60 ? '#f39c12' : '#e74c3c');
        tr.innerHTML = `
          <td class="font-mono text-highlight bold">${m.id}</td>
          <td>${m.label.split(' - ')[1] || m.label}</td>
          <td><span style="font-weight:bold;color:${hColor}">${hVal}% ${m.condition || 'GOOD'}</span></td>
          <td><span class="badge ${m.criticality && m.criticality.startsWith('A') ? 'critical' : ''}">${m.criticality || 'B - Important'}</span></td>
          <td>${m.power || 'N/A'}</td>
          <td>${m.voltage || 'N/A'}</td>
          <td class="status-cell">
            <span class="status-indicator ${(m.status || 'Running').toLowerCase()}"></span>
            <span>${m.status || 'Running'}</span>
          </td>
        `;
        
        tr.addEventListener('click', () => {
          document.querySelectorAll('#equipment-table tbody tr').forEach(r => r.classList.remove('selected-row'));
          tr.classList.add('selected-row');
          RightPanelComponent.loadMotor(m.id);
        });
        tbody.appendChild(tr);
      });
    } else {
      thead.innerHTML = `
        <tr>
          <th>Node Tag</th>
          <th>Equipment Type</th>
          <th>Sub-Feeders Count</th>
          <th>Operating Status</th>
        </tr>
      `;

      children.forEach(child => {
        const tr = document.createElement('tr');
        const childCount = child.children ? child.children.length : 0;
        let typeLabel = child.type.toUpperCase();
        if (child.type === 'pcc') typeLabel = 'Power Control Center (PCC)';
        if (child.type === 'mcc') typeLabel = 'Motor Control Center (MCC)';
        if (child.type === 'feeder') typeLabel = 'Feeder Switch';

        tr.innerHTML = `
          <td class="bold">${child.label}</td>
          <td>${typeLabel}</td>
          <td>${childCount}</td>
          <td class="status-cell">
            <span class="status-indicator ${(child.status || 'Running').toLowerCase()}"></span>
            <span>${child.status || 'Running'}</span>
          </td>
        `;
        
        tr.addEventListener('click', () => {
          navigateToNode({ id: child.id, label: child.label, type: child.type });
        });
        tbody.appendChild(tr);
      });
    }

    table.appendChild(thead);
    table.appendChild(tbody);
  },

  // Renders full filtered Asset Directory Grid across all motor records
  renderFilteredAssetGrid(motors) {
    const title = document.getElementById('equipment-title');
    const summary = document.getElementById('equipment-summary');
    const table = document.getElementById('equipment-table');

    if (title) title.textContent = "Industrial Motor Asset Directory";
    if (!table) return;

    table.innerHTML = '';
    
    // Apply filters
    const q = (state.searchQuery || '').trim().toLowerCase();
    const filtered = motors.filter(m => {
      if (q) {
        const match = (m.tag || '').toLowerCase().includes(q) ||
                      (m.name || '').toLowerCase().includes(q) ||
                      (m.make || '').toLowerCase().includes(q) ||
                      (m.area || '').toLowerCase().includes(q) ||
                      (m.mcc || '').toLowerCase().includes(q);
        if (!match) return false;
      }
      if (state.activeFilters.area && m.area !== state.activeFilters.area) return false;
      if (state.activeFilters.voltage && String(m.voltage) !== String(state.activeFilters.voltage)) return false;
      if (state.activeFilters.make && m.make !== state.activeFilters.make) return false;
      if (state.activeFilters.status && m.status !== state.activeFilters.status) return false;
      if (state.activeFilters.criticality && m.criticality !== state.activeFilters.criticality) return false;
      return true;
    });

    // Summary tiles
    if (summary) {
      const total = filtered.length;
      const run = filtered.filter(m => m.status === 'Running').length;
      const std = filtered.filter(m => m.status === 'Standby').length;
      const flt = filtered.filter(m => m.status === 'Fault').length;
      summary.innerHTML = `
        <div class="summary-item"><span class="lbl">Filtered Motors:</span><span class="val">${total}</span></div>
        <div class="summary-item"><span class="lbl" style="color:var(--color-success);">Running:</span><span class="val">${run}</span></div>
        <div class="summary-item"><span class="lbl" style="color:var(--color-warning);">Standby:</span><span class="val">${std}</span></div>
        <div class="summary-item"><span class="lbl" style="color:var(--color-danger);">Fault:</span><span class="val">${flt}</span></div>
      `;
    }

    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    thead.innerHTML = `
      <tr>
        <th>Motor Tag</th>
        <th>Asset Description</th>
        <th>Plant Area</th>
        <th>Substation</th>
        <th>MCC</th>
        <th>Feeder</th>
        <th>Rating (kW)</th>
        <th>Voltage (V)</th>
        <th>Health Score</th>
        <th>Criticality</th>
        <th>Status</th>
      </tr>
    `;

    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;padding:25px;color:var(--text-muted);">No electric motors match the selected filter criteria.</td></tr>';
    } else {
      filtered.forEach(m => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        const hVal = m.health_score !== undefined ? m.health_score : 85;
        const hColor = hVal >= 75 ? '#2ecc71' : (hVal >= 60 ? '#f39c12' : '#e74c3c');
        const isCrit = m.criticality && m.criticality.startsWith('A');

        tr.innerHTML = `
          <td class="font-mono text-highlight bold">${m.tag}</td>
          <td>${m.name}</td>
          <td>${m.area || '-'}</td>
          <td>${m.substation || '-'}</td>
          <td>${m.mcc || '-'}</td>
          <td>${m.feeder || '-'}</td>
          <td class="font-mono">${m.power_kw} kW</td>
          <td class="font-mono">${m.voltage} V</td>
          <td><span style="font-weight:bold;color:${hColor}">${hVal}% ${m.condition_status || 'GOOD'}</span></td>
          <td><span class="badge ${isCrit ? 'critical' : ''}">${m.criticality || 'B - Important'}</span></td>
          <td class="status-cell">
            <span class="status-indicator ${(m.status || 'Running').toLowerCase()}"></span>
            <span>${m.status}</span>
          </td>
        `;

        tr.addEventListener('click', () => {
          document.querySelectorAll('#equipment-table tbody tr').forEach(r => r.style.background = '');
          tr.style.background = 'rgba(0, 210, 211, 0.12)';
          RightPanelComponent.loadMotor(m.tag);
        });
        tbody.appendChild(tr);
      });
    }

    table.appendChild(thead);
    table.appendChild(tbody);
  }
};

// Helper crumb builders
function createCrumb(label, nodeId, type = 'plant', isActive = false) {
  const span = document.createElement('span');
  span.className = 'crumb';
  if (isActive) span.classList.add('active');
  span.textContent = label;
  
  if (!isActive) {
    span.addEventListener('click', () => {
      navigateToNode({ id: nodeId, label: label, type: type });
    });
  }
  return span;
}

function createSeparator() {
  const span = document.createElement('span');
  span.className = 'separator';
  span.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
  return span;
}

function findNodeInTree(id, node) {
  if (!node) return null;
  if (node.id === id) return node;
  if (node.children) {
    for (const child of node.children) {
      const match = findNodeInTree(id, child);
      if (match) return match;
    }
  }
  return null;
}

function setupExportButtons() {
  const exportBtn = document.getElementById('export-excel-btn');
  const printBtn = document.getElementById('print-filtered-btn');

  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const params = new URLSearchParams();
      if (state.searchQuery) params.append('search', state.searchQuery);
      if (state.activeFilters.area) params.append('area', state.activeFilters.area);
      if (state.activeFilters.voltage) params.append('voltage', state.activeFilters.voltage);
      if (state.activeFilters.make) params.append('make', state.activeFilters.make);
      if (state.activeFilters.status) params.append('status', state.activeFilters.status);
      if (state.activeFilters.criticality) params.append('criticality', state.activeFilters.criticality);
      
      window.location.href = `/api/export?${params.toString()}`;
    });
  }

  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }
}
