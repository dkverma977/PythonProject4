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
  currentUser: null, // { id, username, full_name, email, role }
  role: 'Viewer', // Admin, Engineer, Viewer
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
  setupAuth();
  setupGlobalEvents();
  setupMobileDrawers();
  
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

// 3. User Authentication & Session Setup
function setupAuth() {
  const headerLoginBtn = document.getElementById('header-login-btn');
  const userProfileMenu = document.getElementById('user-profile-menu');
  const userAvatarBtn = document.getElementById('user-avatar-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const userLogoutBtn = document.getElementById('user-logout-btn');

  const modalLogin = document.getElementById('modal-login');
  const closeLoginModal = document.getElementById('close-login-modal');
  const tabLoginBtn = document.getElementById('tab-login-btn');
  const tabRegisterBtn = document.getElementById('tab-register-btn');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const toggleLoginPwd = document.getElementById('toggle-login-pwd');

  // Check active session on startup
  checkSession();

  // Header login button opens modal
  if (headerLoginBtn) {
    headerLoginBtn.addEventListener('click', () => {
      showAuthAlert('');
      modalLogin.classList.add('active');
    });
  }

  // Close login modal
  if (closeLoginModal) {
    closeLoginModal.addEventListener('click', () => {
      modalLogin.classList.remove('active');
    });
  }

  // Toggle dropdown menu
  if (userAvatarBtn && userDropdown) {
    userAvatarBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });
    document.addEventListener('click', (e) => {
      if (!userDropdown.contains(e.target) && !userAvatarBtn.contains(e.target)) {
        userDropdown.classList.remove('show');
      }
    });
  }

  // Logout button
  if (userLogoutBtn) {
    userLogoutBtn.addEventListener('click', async () => {
      try {
        await fetch('/api/auth/logout', { method: 'POST' });
      } catch (err) {
        console.warn("Logout request failed:", err);
      }
      state.currentUser = null;
      state.role = 'Viewer';
      updateUserUI();
    });
  }

  // Password visibility toggle
  if (toggleLoginPwd) {
    toggleLoginPwd.addEventListener('click', () => {
      const pwdInput = document.getElementById('login-password');
      if (pwdInput.type === 'password') {
        pwdInput.type = 'text';
        toggleLoginPwd.className = 'fa-solid fa-eye-slash toggle-password';
      } else {
        pwdInput.type = 'password';
        toggleLoginPwd.className = 'fa-solid fa-eye toggle-password';
      }
    });
  }

  // Auth Modal Tabs (Sign In / Register)
  if (tabLoginBtn && tabRegisterBtn) {
    tabLoginBtn.addEventListener('click', () => {
      tabLoginBtn.classList.add('active');
      tabRegisterBtn.classList.remove('active');
      loginForm.style.display = 'block';
      registerForm.style.display = 'none';
      showAuthAlert('');
    });
    tabRegisterBtn.addEventListener('click', () => {
      tabRegisterBtn.classList.add('active');
      tabLoginBtn.classList.remove('active');
      registerForm.style.display = 'block';
      loginForm.style.display = 'none';
      showAuthAlert('');
    });
  }

  // Demo Preset Account Quick-Fill
  document.querySelectorAll('.demo-account-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const u = btn.getAttribute('data-user');
      const p = btn.getAttribute('data-pwd');
      document.getElementById('login-username').value = u;
      document.getElementById('login-password').value = p;
      showAuthAlert('');
    });
  });

  // Login Form Submit
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('login-username').value.trim();
      const password = document.getElementById('login-password').value.trim();

      const submitBtn = document.getElementById('login-submit-btn');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Authenticating...';

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) {
          showAuthAlert(data.error || 'Invalid credentials.');
        } else {
          state.currentUser = data.user;
          state.role = data.user.role || 'Viewer';
          updateUserUI();
          modalLogin.classList.remove('active');
        }
      } catch (err) {
        showAuthAlert('Network error. Unable to reach server.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> Sign In';
      }
    });
  }

  // Register Form Submit
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('reg-username').value.trim();
      const full_name = document.getElementById('reg-fullname').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value.trim();
      const role = document.getElementById('reg-role').value;

      const submitBtn = document.getElementById('register-submit-btn');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';

      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, full_name, email, password, role })
        });
        const data = await res.json();
        if (!res.ok) {
          showAuthAlert(data.error || 'Failed to create account.');
        } else {
          state.currentUser = data.user;
          state.role = data.user.role || 'Viewer';
          updateUserUI();
          modalLogin.classList.remove('active');
        }
      } catch (err) {
        showAuthAlert('Network error. Unable to reach server.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-user-check"></i> Create Account';
      }
    });
  }
}

async function checkSession() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated && data.user) {
        state.currentUser = data.user;
        state.role = data.user.role || 'Viewer';
      }
    }
  } catch (err) {
    console.warn("Unable to verify user session on launch:", err);
  }
  updateUserUI();
}

function showAuthAlert(msg) {
  const alertEl = document.getElementById('auth-alert');
  const msgEl = document.getElementById('auth-alert-msg');
  if (!alertEl) return;
  if (!msg) {
    alertEl.style.display = 'none';
  } else {
    msgEl.textContent = msg;
    alertEl.style.display = 'flex';
  }
}

function updateUserUI() {
  const headerLoginBtn = document.getElementById('header-login-btn');
  const userProfileMenu = document.getElementById('user-profile-menu');
  const userDropdown = document.getElementById('user-dropdown');

  if (userDropdown) userDropdown.classList.remove('show');

  if (state.currentUser) {
    if (headerLoginBtn) headerLoginBtn.style.display = 'none';
    if (userProfileMenu) userProfileMenu.style.display = 'flex';

    // Initials
    const names = (state.currentUser.full_name || state.currentUser.username).split(' ');
    const initials = names.length >= 2 ? (names[0][0] + names[1][0]).toUpperCase() : names[0].substring(0, 2).toUpperCase();
    document.getElementById('user-avatar-initials').textContent = initials;
    document.getElementById('user-display-name').textContent = state.currentUser.full_name || state.currentUser.username;
    
    const roleBadge = document.getElementById('user-role-badge');
    roleBadge.textContent = state.role;
    roleBadge.className = `user-role-badge role-${state.role.toLowerCase()}`;

    // Dropdown details
    document.getElementById('dd-user-name').textContent = state.currentUser.full_name || state.currentUser.username;
    document.getElementById('dd-user-email').textContent = state.currentUser.email || `${state.currentUser.username}@mototwin.com`;
    document.getElementById('dd-user-role').textContent = state.role;
  } else {
    if (headerLoginBtn) headerLoginBtn.style.display = 'flex';
    if (userProfileMenu) userProfileMenu.style.display = 'none';
  }

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

// 5. Mobile Drawer Controls
function setupMobileDrawers() {
  const treeToggle = document.getElementById('mobile-tree-toggle');
  const detailsToggle = document.getElementById('mobile-details-toggle');
  const backdrop = document.getElementById('drawer-backdrop');
  const panelLeft = document.getElementById('panel-left');
  const panelRight = document.getElementById('panel-right');

  const closeDrawers = () => {
    if (panelLeft) panelLeft.classList.remove('drawer-open');
    if (panelRight) panelRight.classList.remove('drawer-open');
    if (backdrop) backdrop.classList.remove('active');
  };

  const openLeftDrawer = () => {
    closeDrawers();
    if (panelLeft) panelLeft.classList.add('drawer-open');
    if (backdrop) backdrop.classList.add('active');
  };

  const openRightDrawer = () => {
    closeDrawers();
    if (panelRight) panelRight.classList.add('drawer-open');
    if (backdrop) backdrop.classList.add('active');
  };

  if (treeToggle && panelLeft) {
    treeToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = panelLeft.classList.contains('drawer-open');
      if (isOpen) {
        closeDrawers();
      } else {
        openLeftDrawer();
      }
    });
  }

  if (detailsToggle && panelRight) {
    detailsToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = panelRight.classList.contains('drawer-open');
      if (isOpen) {
        closeDrawers();
      } else {
        openRightDrawer();
      }
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', closeDrawers);
  }

  // Handle window resize back to desktop (>1024px)
  window.addEventListener('resize', () => {
    if (window.innerWidth > 1024) {
      closeDrawers();
    }
  });

  // Attach global helpers for component navigation
  window.closeMobileDrawers = closeDrawers;
  window.openMobileRightDrawer = openRightDrawer;
}

// 6. Load and refresh data from Backend
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
    if (window.closeMobileDrawers) window.closeMobileDrawers();
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
    
    // On small screens (<1024px), automatically slide open right drawer for motor details
    if (window.innerWidth <= 1024 && window.openMobileRightDrawer) {
      window.openMobileRightDrawer();
    }
  } else {
    // Substation, PCC, MCC, Feeder -> Show connected child list/grid
    dbView.classList.remove('active');
    eqView.classList.add('active');
    dbToggle.classList.remove('active');
    
    CenterPanelComponent.loadEquipmentList(node);
    
    // Hide details card, it belongs to motors
    RightPanelComponent.hideCard();
    if (window.closeMobileDrawers) window.closeMobileDrawers();
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
