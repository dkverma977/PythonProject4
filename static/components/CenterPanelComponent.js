/* -------------------------------------------------------------
 * MOTO-TWIN Center Panel Component (CenterPanelComponent.js)
 * Breadcrumbs and dynamically generated lists of child equipment
 * ------------------------------------------------------------- */

import { navigateToNode, state } from '../app.js';
import { TreeComponent } from './TreeComponent.js';

export const CenterPanelComponent = {
  init() {
    setupExportButtons();
  },

  // Generates and renders breadcrumb trails based on the selected node
  renderBreadcrumbs(node) {
    const container = document.getElementById('header-breadcrumb');
    container.innerHTML = '';

    // Always start with plant
    const plantCrumb = createCrumb('Plant Network', 'plant');
    container.appendChild(plantCrumb);

    if (node.type === 'plant') return;

    let pathParts = [];
    
    if (node.type === 'motor') {
      // Find parent of motor
      const parentFeeder = TreeComponent.findParentNodeId(node.id);
      if (parentFeeder) {
        // ID is Substation|PCC|MCC|Feeder
        pathParts = parentFeeder.id.split('|');
      }
      pathParts.push(node.id); // Add motor itself
    } else {
      pathParts = node.id.split('|');
    }

    // Build intermediate crumb elements
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
        currentId = part; // Motor Tag
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
    
    title.textContent = `Connected Assets: ${node.label}`;
    
    // Clear list
    summary.innerHTML = '';
    table.innerHTML = '';

    // Find node details in tree structure
    const treeNode = findNodeInTree(node.id, state.treeData);
    if (!treeNode || !treeNode.children || treeNode.children.length === 0) {
      table.innerHTML = '<tbody><tr><td style="text-align:center;padding:20px;color:var(--text-muted);">No child equipment connected to this node.</td></tr></tbody>';
      return;
    }

    const children = treeNode.children;

    // Build Stats Summary
    const totalCount = children.length;
    const runningCount = children.filter(c => c.status === 'Running' || c.status === 'running').length;
    const standbyCount = children.filter(c => c.status === 'Standby' || c.status === 'standby').length;
    const faultCount = children.filter(c => c.status === 'Fault' || c.status === 'fault').length;

    summary.innerHTML = `
      <div class="summary-item"><span class="lbl">Total Nodes:</span><span class="val">${totalCount}</span></div>
      <div class="summary-item"><span class="lbl" style="color:var(--color-success);">Running:</span><span class="val">${runningCount}</span></div>
      <div class="summary-item"><span class="lbl" style="color:var(--color-warning);">Standby:</span><span class="val">${standbyCount}</span></div>
      <div class="summary-item"><span class="lbl" style="color:var(--color-danger);">Fault:</span><span class="val">${faultCount}</span></div>
    `;

    // Build Child Table based on Node Type
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    if (node.type === 'feeder' || children[0].type === 'motor') {
      // Renders Table of Motors
      thead.innerHTML = `
        <tr>
          <th>Motor Tag</th>
          <th>Description / Name</th>
          <th>Rating (kW)</th>
          <th>Voltage (V)</th>
          <th>Status</th>
        </tr>
      `;

      children.forEach(m => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="font-mono text-highlight bold">${m.id}</td>
          <td>${m.label.split(' - ')[1] || m.label}</td>
          <td>${m.power || 'N/A'}</td>
          <td>${m.voltage || 'N/A'}</td>
          <td class="status-cell">
            <span class="status-indicator ${m.status.toLowerCase()}"></span>
            <span>${m.status}</span>
          </td>
        `;
        
        tr.addEventListener('click', () => {
          navigateToNode({ id: m.id, label: m.label, type: 'motor' });
        });
        tbody.appendChild(tr);
      });
    } else {
      // Renders generic Intermediate nodes (Substation / PCC / MCC)
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
            <span class="status-indicator ${child.status.toLowerCase()}"></span>
            <span>${child.status}</span>
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

// Find a node inside the hierarchical tree object
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

// Export excel and print actions hooks
function setupExportButtons() {
  const exportBtn = document.getElementById('export-excel-btn');
  const printBtn = document.getElementById('print-filtered-btn');

  exportBtn.addEventListener('click', () => {
    // Builds query string based on active filter state
    const params = new URLSearchParams();
    if (state.searchQuery) params.append('search', state.searchQuery);
    if (state.activeFilters.area) params.append('area', state.activeFilters.area);
    if (state.activeFilters.department) params.append('department', state.activeFilters.department);
    if (state.activeFilters.voltage) params.append('voltage', state.activeFilters.voltage);
    if (state.activeFilters.make) params.append('make', state.activeFilters.make);
    if (state.activeFilters.status) params.append('status', state.activeFilters.status);
    if (state.activeFilters.critical) {
      params.append('is_critical', state.activeFilters.critical === 'critical' ? 'true' : 'false');
    }
    
    // Redirect browser to stream downloadable file
    window.location.href = `/api/export?${params.toString()}`;
  });

  printBtn.addEventListener('click', () => {
    window.print();
  });
}
