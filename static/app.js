/* -------------------------------------------------------------
 * MOTO-TWIN CORE Orchestrator (app.js)
 * ES6 Module conducting global state and layouts
 * ------------------------------------------------------------- */

import { TreeComponent } from './components/TreeComponent.js';
import { CenterPanelComponent } from './components/CenterPanelComponent.js';
import { RightPanelComponent } from './components/RightPanelComponent.js';
import { DashboardComponent } from './components/DashboardComponent.js';

// Global Application State
export const state = {
  role: 'Admin', // Admin, Engineer, Viewer
  theme: 'dark', // dark, light
  selectedNode: { id: 'plant', label: 'Industrial Plant', type: 'plant' },
  activeFilters: {
    area: '',
    voltage: '',
    make: '',
    status: '',
    critical: ''
  },
  searchQuery: '',
  treeData: null,
  motors: [],
  dashboardData: null
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  setupSplitters();
  setupTheme();
  setupRoleSwitcher();
  setupGlobalEvents();
  
  // Initialize subcomponents
  CenterPanelComponent.init();
  RightPanelComponent.init();
  
  // Initial load
  loadData();
});

// 1. Resizable Panels Splitter Setup
function setupSplitters() {
  const splitterLeft = document.getElementById('splitter-left');
  const splitterRight = document.getElementById('splitter-right');
  const panelLeft = document.getElementById('panel-left');
  const panelRight = document.getElementById('panel-right');
  const workspace = document.querySelector('.app-workspace');

  // Left Splitter Dragging
  splitterLeft.addEventListener('mousedown', (e) => {
    e.preventDefault();
    splitterLeft.classList.add('active');
    
    const onMouseMove = (moveEvent) => {
      const workspaceRect = workspace.getBoundingClientRect();
      const newWidth = moveEvent.clientX - workspaceRect.left;
      
      // Bounds checks
      if (newWidth >= 200 && newWidth <= 450) {
        panelLeft.style.width = `${newWidth}px`;
      }
    };

    const onMouseUp = () => {
      splitterLeft.classList.remove('active');
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  });

  // Right Splitter Dragging
  splitterRight.addEventListener('mousedown', (e) => {
    e.preventDefault();
    splitterRight.classList.add('active');
    
    const onMouseMove = (moveEvent) => {
      const workspaceRect = workspace.getBoundingClientRect();
      const newWidth = workspaceRect.right - moveEvent.clientX;
      
      // Bounds checks
      if (newWidth >= 250 && newWidth <= 500) {
        panelRight.style.width = `${newWidth}px`;
      }
    };

    const onMouseUp = () => {
      splitterRight.classList.remove('active');
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  });
}

// 2. Light/Dark Theme Setup
function setupTheme() {
  const toggle = document.getElementById('theme-toggle');
  
  // Set default theme
  document.body.className = 'dark-theme';

  toggle.addEventListener('click', () => {
    if (state.theme === 'dark') {
      state.theme = 'light';
      document.body.className = 'light-theme';
    } else {
      state.theme = 'dark';
      document.body.className = 'dark-theme';
    }
    // Update charts labels if loaded
    DashboardComponent.updateChartColors();
  });
}

// 3. Access Roles Setup
function setupRoleSwitcher() {
  const select = document.getElementById('role-select');
  select.addEventListener('change', (e) => {
    state.role = e.target.value;
    updateUIForRole();
  });
  
  updateUIForRole();
}

function updateUIForRole() {
  const importBtn = document.getElementById('import-btn');
  const addLogBtn = document.getElementById('add-log-btn');
  
  // Role based access logic
  if (state.role === 'Viewer') {
    if (importBtn) importBtn.style.display = 'none';
    if (addLogBtn) addLogBtn.style.display = 'none';
  } else if (state.role === 'Engineer') {
    if (importBtn) importBtn.style.display = 'none';
    if (addLogBtn) addLogBtn.style.display = 'inline-block';
  } else {
    // Admin
    if (importBtn) importBtn.style.display = 'flex';
    if (addLogBtn) addLogBtn.style.display = 'inline-block';
  }
}

// 4. Global Search, Filtering, and Print Events
function setupGlobalEvents() {
  const searchInput = document.getElementById('global-search');
  const clearBtn = document.getElementById('clear-search');
  
  // Debounce search
  let searchTimeout = null;
  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    clearBtn.style.display = state.searchQuery ? 'block' : 'none';
    
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      // Trigger instant tree search filter
      TreeComponent.filterTree(state.searchQuery);
      // Trigger motor list reload
      refreshCurrentView();
    }, 300);
  });

  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    state.searchQuery = '';
    clearBtn.style.display = 'none';
    TreeComponent.filterTree('');
    refreshCurrentView();
  });

  // Filter Selects
  const filterIds = [
    { id: 'filter-area', key: 'area' },
    { id: 'filter-voltage', key: 'voltage' },
    { id: 'filter-make', key: 'make' },
    { id: 'filter-status', key: 'status' },
    { id: 'filter-critical', key: 'critical' }
  ];

  filterIds.forEach(({ id, key }) => {
    const el = document.getElementById(id);
    el.addEventListener('change', (e) => {
      state.activeFilters[key] = e.target.value;
      refreshCurrentView();
    });
  });

  // Clear Filters
  document.getElementById('reset-filters').addEventListener('click', () => {
    filterIds.forEach(({ id, key }) => {
      const el = document.getElementById(id);
      el.value = '';
      state.activeFilters[key] = '';
    });
    refreshCurrentView();
  });

  // Dashboard Toggle
  const dbToggle = document.getElementById('dashboard-toggle');
  dbToggle.addEventListener('click', () => {
    navigateToNode({ id: 'plant', label: 'Industrial Plant', type: 'plant' });
  });

  // Modal Close Hooks
  const closeBtns = document.querySelectorAll('.close-modal');
  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
    });
  });

  // Clock Update
  setInterval(() => {
    const d = new Date();
    const formatted = `As of: ${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}:${String(d.getSeconds()).padStart(2,'0')}`;
    const clock = document.getElementById('live-time');
    if (clock) clock.textContent = formatted;
  }, 1000);
}

// 5. Load and refresh data from Backend
export async function loadData() {
  try {
    const API_BASE = 'http://127.0.0.1:8000';
    
    // 1. Fetch Tree
    const treeRes = await fetch(`${API_BASE}/api/tree`);
    state.treeData = await treeRes.json();
    TreeComponent.init(state.treeData);

    // 2. Fetch Motors (all)
    const motorsRes = await fetch(`${API_BASE}/api/motors`);
    state.motors = await motorsRes.json();
    populateFiltersLists();

    // 3. Fetch Dashboard Telemetry
    const dashRes = await fetch(`${API_BASE}/api/dashboard`);
    state.dashboardData = await dashRes.json();
    DashboardComponent.render(state.dashboardData);

    // Update views based on selection
    refreshCurrentView();
  } catch (err) {
    console.error("Failed to retrieve plant data from backend server.", err);
  }
}

// Populate drop-down filter menus from unique active records
function populateFiltersLists() {
  const areas = [...new Set(state.motors.map(m => m.area).filter(Boolean))].sort();
  const volts = [...new Set(state.motors.map(m => m.voltage).filter(Boolean))].sort((a,b) => a-b);
  const makes = [...new Set(state.motors.map(m => m.make).filter(Boolean))].sort();

  const areaSelect = document.getElementById('filter-area');
  const voltSelect = document.getElementById('filter-voltage');
  const makeSelect = document.getElementById('filter-make');

  // Keep first option
  areaSelect.innerHTML = '<option value="">All Areas</option>';
  voltSelect.innerHTML = '<option value="">All Voltages</option>';
  makeSelect.innerHTML = '<option value="">All Makes</option>';

  areas.forEach(a => areaSelect.add(new Option(a, a)));
  volts.forEach(v => {
    const label = v < 1000 ? `${v} V` : `${(v/1000).toFixed(1)} kV`;
    voltSelect.add(new Option(label, v));
  });
  makes.forEach(m => makeSelect.add(new Option(m, m)));
}

// Navigates and loads details for a node
export function navigateToNode(node) {
  state.selectedNode = node;
  
  // Update header breadcrumbs
  CenterPanelComponent.renderBreadcrumbs(node);

  const dbView = document.getElementById('dashboard-view');
  const eqView = document.getElementById('equipment-view');
  const dbToggle = document.getElementById('dashboard-toggle');
  
  if (node.type === 'plant') {
    // Show Dashboard
    dbView.classList.add('active');
    eqView.classList.remove('active');
    dbToggle.classList.add('active');
    RightPanelComponent.hideCard();
  } else if (node.type === 'motor') {
    // Highlight motor in tree, show detail card in right panel
    dbView.classList.remove('active');
    eqView.classList.add('active');
    dbToggle.classList.remove('active');
    
    // Fetch and show detailed specifications
    RightPanelComponent.loadMotor(node.id);
    
    // For Center Panel in motor selection: Display the list of sibling motors in the Feeder!
    const parentNodeId = TreeComponent.findParentNodeId(node.id);
    if (parentNodeId) {
      CenterPanelComponent.loadEquipmentList({ id: parentNodeId.id, label: parentNodeId.label, type: parentNodeId.type });
    }
  } else {
    // Substation, PCC, MCC, Feeder -> Show connected child list/grid
    dbView.classList.remove('active');
    eqView.classList.add('active');
    dbToggle.classList.remove('active');
    
    CenterPanelComponent.loadEquipmentList(node);
    
    // Hide details card, it belongs to motors
    RightPanelComponent.hideCard();
  }

  // Highlight active tree item
  TreeComponent.selectNode(node.id);
}

// Refresh the visible tables or dashboard elements when filters change
function refreshCurrentView() {
  // If dashboard is active, re-filter stats inside dashboard
  if (state.selectedNode.type === 'plant') {
    // Fetch dashboard info and render
    DashboardComponent.renderFiltered(state.motors, state.activeFilters, state.searchQuery);
  } else {
    // Reload equipment grids
    CenterPanelComponent.loadEquipmentList(state.selectedNode);
  }
}
