/* -------------------------------------------------------------
 * MOTO-TWIN CORE Orchestrator (app.js)
 * ES6 Module conducting global state, RBAC, modals & layout events
 * ------------------------------------------------------------- */

import { TreeComponent } from './components/TreeComponent.js';
import { CenterPanelComponent } from './components/CenterPanelComponent.js';
import { RightPanelComponent } from './components/RightPanelComponent.js';
import { DashboardComponent } from './components/DashboardComponent.js';

// Global Application State
export const state = {
  currentUser: null, // { id, username, full_name, email, role }
  role: 'Engineer', // Admin, Engineer
  theme: 'dark', // dark, light
  selectedNode: { id: 'plant', label: 'Industrial Plant', type: 'plant' },
  activeFilters: {
    area: '',
    voltage: '',
    make: '',
    status: '',
    criticality: ''
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
  setupModalTriggers();
  
  // Initialize subcomponents
  CenterPanelComponent.init();
  RightPanelComponent.init();
  
  // Initial load
  loadData();
});

// 1. Resizable Panels Splitter Setup (FLUID DRAGGING FIX)
function setupSplitters() {
  const splitterLeft = document.getElementById('splitter-left');
  const splitterRight = document.getElementById('splitter-right');
  const panelLeft = document.getElementById('panel-left');
  const panelRight = document.getElementById('panel-right');
  const workspace = document.querySelector('.app-workspace');

  if (splitterLeft && panelLeft) {
    splitterLeft.addEventListener('mousedown', (e) => {
      e.preventDefault();
      splitterLeft.classList.add('active');
      document.body.style.userSelect = 'none';
      document.body.style.cursor = 'col-resize';
      
      const onMouseMove = (moveEvent) => {
        const workspaceRect = workspace.getBoundingClientRect();
        const newWidth = moveEvent.clientX - workspaceRect.left;
        if (newWidth >= 200 && newWidth <= 550) {
          panelLeft.style.width = `${newWidth}px`;
        }
      };

      const onMouseUp = () => {
        splitterLeft.classList.remove('active');
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });
  }

  if (splitterRight && panelRight) {
    splitterRight.addEventListener('mousedown', (e) => {
      e.preventDefault();
      splitterRight.classList.add('active');
      document.body.style.userSelect = 'none';
      document.body.style.cursor = 'col-resize';

      const onMouseMove = (moveEvent) => {
        const workspaceRect = workspace.getBoundingClientRect();
        const newWidth = workspaceRect.right - moveEvent.clientX;
        if (newWidth >= 250 && newWidth <= 650) {
          panelRight.style.width = `${newWidth}px`;
        }
      };

      const onMouseUp = () => {
        splitterRight.classList.remove('active');
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
      };

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });
  }
}

// 2. Theme Setup
function setupTheme() {
  const toggle = document.getElementById('theme-toggle');
  document.body.className = 'dark-theme';

  if (toggle) {
    toggle.addEventListener('click', () => {
      if (state.theme === 'dark') {
        state.theme = 'light';
        document.body.className = 'light-theme';
      } else {
        state.theme = 'dark';
        document.body.className = 'dark-theme';
      }
    });
  }
}

// 3. User Authentication & Session Setup (LOGIN MODAL MANDATORY AT START)
function setupAuth() {
  const headerLoginBtn = document.getElementById('header-login-btn');
  const userProfileMenu = document.getElementById('user-profile-menu');
  const userAvatarBtn = document.getElementById('user-avatar-btn');
  const userDropdown = document.getElementById('user-dropdown');
  const userLogoutBtn = document.getElementById('user-logout-btn');
  const modalAuth = document.getElementById('modal-auth');
  const loginForm = document.getElementById('login-form');

  checkSession();

  if (headerLoginBtn && modalAuth) {
    headerLoginBtn.addEventListener('click', () => {
      modalAuth.classList.add('active');
    });
  }

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

  if (userLogoutBtn) {
    userLogoutBtn.addEventListener('click', async () => {
      try {
        await fetch('/api/auth/logout', { method: 'POST' });
      } catch (err) {
        console.warn("Logout request notice:", err);
      }
      state.currentUser = null;
      state.role = null;
      updateUserUI();
      // Instantly open login modal
      if (modalAuth) modalAuth.classList.add('active');
    });
  }

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('login-username').value.trim();
      const password = document.getElementById('login-password').value.trim();

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) {
          alert(data.error || 'Invalid credentials. Enter admin/admin or engineer/engineer.');
        } else {
          state.currentUser = data.user;
          state.role = data.user.role || 'Engineer';
          updateUserUI();
          if (modalAuth) modalAuth.classList.remove('active');
        }
      } catch (err) {
        alert('Unable to authenticate with backend server.');
      }
    });
  }
}

async function checkSession() {
  const modalAuth = document.getElementById('modal-auth');
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated && data.user) {
        state.currentUser = data.user;
        state.role = data.user.role || 'Engineer';
        if (modalAuth) modalAuth.classList.remove('active');
      } else {
        // Not authenticated -> Require immediate login modal
        if (modalAuth) modalAuth.classList.add('active');
      }
    } else {
      if (modalAuth) modalAuth.classList.add('active');
    }
  } catch (err) {
    if (modalAuth) modalAuth.classList.add('active');
  }
  updateUserUI();
}

function updateUserUI() {
  const headerLoginBtn = document.getElementById('header-login-btn');
  const userProfileMenu = document.getElementById('user-profile-menu');
  const userDropdown = document.getElementById('user-dropdown');

  if (userDropdown) userDropdown.classList.remove('show');

  if (state.currentUser) {
    if (headerLoginBtn) headerLoginBtn.style.display = 'none';
    if (userProfileMenu) userProfileMenu.style.display = 'flex';

    const names = (state.currentUser.full_name || state.currentUser.username).split(' ');
    const initials = names.length >= 2 ? (names[0][0] + names[1][0]).toUpperCase() : names[0].substring(0, 2).toUpperCase();
    if (document.getElementById('user-avatar-initials')) document.getElementById('user-avatar-initials').textContent = initials;
    if (document.getElementById('user-display-name')) document.getElementById('user-display-name').textContent = state.currentUser.full_name || state.currentUser.username;
    
    const roleBadge = document.getElementById('user-role-badge');
    if (roleBadge) {
      roleBadge.textContent = state.role;
      roleBadge.className = `user-role-badge role-${(state.role || 'engineer').toLowerCase()}`;
    }

    if (document.getElementById('dd-user-name')) document.getElementById('dd-user-name').textContent = state.currentUser.full_name || state.currentUser.username;
    if (document.getElementById('dd-user-email')) document.getElementById('dd-user-email').textContent = state.currentUser.email || `${state.currentUser.username}@mototwin.com`;
    if (document.getElementById('dd-user-role')) document.getElementById('dd-user-role').textContent = state.role;
  } else {
    if (headerLoginBtn) headerLoginBtn.style.display = 'flex';
    if (userProfileMenu) userProfileMenu.style.display = 'none';
  }

  // Update UI action controls according to Admin vs Engineer role
  updateUIForRole();
}

function updateUIForRole() {
  const importBtn = document.getElementById('btn-import-excel');
  const addMotorBtn = document.getElementById('add-motor-btn');
  const addLogBtn = document.getElementById('add-log-btn');
  const addWoBtn = document.getElementById('add-wo-btn');

  const isAdmin = state.role === 'Admin';

  // Admin can modify any field; Engineer is Read-Only across modify actions
  if (importBtn) importBtn.style.display = isAdmin ? 'flex' : 'none';
  if (addMotorBtn) addMotorBtn.style.display = isAdmin ? 'inline-block' : 'none';
  if (addLogBtn) addLogBtn.style.display = isAdmin ? 'inline-block' : 'none';
  if (addWoBtn) addWoBtn.style.display = isAdmin ? 'inline-block' : 'none';
}

// 4. Modal Triggers & Excel Validation Hook
function setupModalTriggers() {
  // Modal Close buttons
  document.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', () => {
      // Don't close login modal if unauthenticated!
      if (!state.currentUser) return;
      document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.remove('active'));
    });
  });

  // Import Excel Modal
  const btnImport = document.getElementById('btn-import-excel');
  const modalImport = document.getElementById('modal-import-excel');
  if (btnImport && modalImport) {
    btnImport.addEventListener('click', () => {
      if (state.role !== 'Admin') {
        alert("Admin role required for Excel batch import.");
        return;
      }
      modalImport.classList.add('active');
    });
  }

  // Validate Excel
  const btnValExcel = document.getElementById('btn-validate-excel');
  if (btnValExcel) {
    btnValExcel.addEventListener('click', async () => {
      const fileInput = document.getElementById('excel-file-input');
      if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please select an Excel .xlsx spreadsheet file.");
        return;
      }
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);

      btnValExcel.disabled = true;
      btnValExcel.textContent = "Validating...";

      try {
        const res = await fetch('/api/import/excel/validate', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (!res.ok) {
          alert(data.error || "Validation failed.");
        } else {
          document.getElementById('import-step-upload').style.display = 'none';
          document.getElementById('import-step-preview').style.display = 'block';

          const summaryBox = document.getElementById('val-summary-box');
          summaryBox.innerHTML = `
            <strong>Validation Results:</strong> Total Rows: ${data.total_rows} | Valid Rows: ${data.valid_rows_count} | Errors: ${data.errors_count}
          `;

          const tbody = document.querySelector('#import-preview-table tbody');
          tbody.innerHTML = '';
          data.preview.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${r.tag}</td><td>${r.name}</td><td>${r.area}</td><td>${r.power_kw} kW</td><td>${r.voltage} V</td><td>${r.current_amp} A</td><td>${r.mcc}</td>`;
            tbody.appendChild(tr);
          });

          // Confirm batch import hook
          document.getElementById('btn-confirm-import').onclick = async () => {
            const cRes = await fetch('/api/import/excel/confirm', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ rows: data.preview })
            });
            if (cRes.ok) {
              alert("Batch import completed successfully!");
              modalImport.classList.remove('active');
              loadData();
            }
          };
        }
      } catch (err) {
        alert("Error uploading Excel file.");
      } finally {
        btnValExcel.disabled = false;
        btnValExcel.textContent = "Validate Spreadsheet";
      }
    });
  }

  const btnCancelImport = document.getElementById('btn-cancel-import');
  if (btnCancelImport) {
    btnCancelImport.addEventListener('click', () => {
      document.getElementById('import-step-upload').style.display = 'block';
      document.getElementById('import-step-preview').style.display = 'none';
    });
  }

  // Data Quality Modal
  const btnDQ = document.getElementById('btn-data-quality');
  const modalDQ = document.getElementById('modal-data-quality');
  if (btnDQ && modalDQ) {
    btnDQ.addEventListener('click', async () => {
      modalDQ.classList.add('active');
      const body = document.getElementById('dq-modal-body');
      body.innerHTML = '<p>Auditing asset database integrity...</p>';
      try {
        const res = await fetch('/api/data-quality');
        const report = await res.json();
        body.innerHTML = `
          <div class="validation-summary-box">
            <h4>Data Quality Index</h4>
            Total Assets Audited: <strong>${report.total}</strong><br>
            Complete Records: <strong style="color:#2ecc71;">${report.complete}</strong><br>
            Incomplete Fields: <strong style="color:#f39c12;">${report.incomplete}</strong><br>
            Invalid Ratings: <strong style="color:#e74c3c;">${report.invalid}</strong><br>
            Orphaned Assets: <strong style="color:#e74c3c;">${report.orphaned}</strong>
          </div>
        `;
      } catch (err) {
        body.innerHTML = '<p style="color:#e74c3c;">Failed to run data quality audit.</p>';
      }
    });
  }

  // Audit Logs Modal
  const btnAudit = document.getElementById('btn-audit-logs');
  const modalAudit = document.getElementById('modal-audit-logs');
  if (btnAudit && modalAudit) {
    btnAudit.addEventListener('click', async () => {
      modalAudit.classList.add('active');
      const tbody = document.querySelector('#audit-logs-table tbody');
      tbody.innerHTML = '<tr><td colspan="6">Loading system audit trail...</td></tr>';
      try {
        const res = await fetch('/api/audit?limit=50');
        const logs = await res.json();
        tbody.innerHTML = '';
        if (logs.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No audit events recorded.</td></tr>';
          return;
        }
        logs.forEach(l => {
          const tr = document.createElement('tr');
          tr.innerHTML = `<td>${l.timestamp}</td><td><strong>${l.username}</strong></td><td>${l.action}</td><td>${l.entity || '-'}</td><td>${l.entity_id || '-'}</td><td>${l.new_value || '-'}</td>`;
          tbody.appendChild(tr);
        });
      } catch (err) {
        tbody.innerHTML = '<tr><td colspan="6" style="color:#e74c3c;">Failed to load audit logs.</td></tr>';
      }
    });
  }

  // Add Motor Asset Modal
  const addBtn = document.getElementById('add-motor-btn');
  const modalAdd = document.getElementById('modal-add-motor');
  const addForm = document.getElementById('add-motor-form');

  if (addBtn && modalAdd) {
    addBtn.addEventListener('click', () => {
      if (state.role !== 'Admin') {
        alert("Admin role required to add new motor assets.");
        return;
      }
      modalAdd.classList.add('active');
    });
  }

  if (addForm) {
    addForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        tag: document.getElementById('add-tag').value.trim(),
        name: document.getElementById('add-name').value.trim(),
        area: document.getElementById('add-area').value.trim(),
        make: document.getElementById('add-make').value.trim(),
        power_kw: parseFloat(document.getElementById('add-power').value),
        voltage: parseInt(document.getElementById('add-voltage').value),
        current_amp: parseFloat(document.getElementById('add-current').value),
        substation: document.getElementById('add-substation').value.trim(),
        pcc: document.getElementById('add-pcc').value.trim(),
        mcc: document.getElementById('add-mcc').value.trim(),
        feeder: document.getElementById('add-feeder').value.trim(),
        criticality: document.getElementById('add-criticality').value,
        status: document.getElementById('add-status').value
      };

      try {
        const res = await fetch('/api/motors', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
          alert(data.error || "Failed to create motor.");
        } else {
          alert(`Motor ${payload.tag} added successfully!`);
          modalAdd.classList.remove('active');
          loadData();
        }
      } catch (err) {
        alert("Network error adding motor.");
      }
    });
  }
}

// 5. Global Search, Filter, and View Toggles Setup
function setupGlobalEvents() {
  const searchInput = document.getElementById('global-search');
  const clearBtn = document.getElementById('clear-search');
  
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      if (clearBtn) clearBtn.style.display = state.searchQuery ? 'block' : 'none';
      
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        refreshCurrentView();
      }, 300);
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      state.searchQuery = '';
      clearBtn.style.display = 'none';
      refreshCurrentView();
    });
  }

  const filterIds = [
    { id: 'filter-area', key: 'area' },
    { id: 'filter-voltage', key: 'voltage' },
    { id: 'filter-make', key: 'make' },
    { id: 'filter-status', key: 'status' },
    { id: 'filter-criticality', key: 'criticality' }
  ];

  filterIds.forEach(({ id, key }) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', (e) => {
        state.activeFilters[key] = e.target.value;
        refreshCurrentView();
      });
    }
  });

  const resetBtn = document.getElementById('reset-filters');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      filterIds.forEach(({ id, key }) => {
        const el = document.getElementById(id);
        if (el) el.value = '';
        state.activeFilters[key] = '';
      });
      refreshCurrentView();
    });
  }

  // Dashboard View Toggle
  const dbToggle = document.getElementById('dashboard-toggle');
  const eqToggle = document.getElementById('equipment-toggle');
  const dbView = document.getElementById('dashboard-view');
  const eqView = document.getElementById('equipment-view');

  if (dbToggle && eqToggle) {
    dbToggle.addEventListener('click', () => {
      dbToggle.classList.add('active');
      eqToggle.classList.remove('active');
      if (dbView) dbView.classList.add('active');
      if (eqView) eqView.classList.remove('active');
      state.selectedNode = { id: 'plant', label: 'Industrial Plant', type: 'plant' };
      CenterPanelComponent.renderBreadcrumbs(state.selectedNode);
    });

    eqToggle.addEventListener('click', () => {
      eqToggle.classList.add('active');
      dbToggle.classList.remove('active');
      if (eqView) eqView.classList.add('active');
      if (dbView) dbView.classList.remove('active');
      refreshCurrentView();
    });
  }
}

// 6. Mobile Drawer Setup
function setupMobileDrawers() {
  const treeToggle = document.getElementById('mobile-tree-toggle');
  const detailsToggle = document.getElementById('mobile-details-toggle');
  const panelLeft = document.getElementById('panel-left');
  const panelRight = document.getElementById('panel-right');

  if (treeToggle && panelLeft) {
    treeToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      panelLeft.classList.toggle('drawer-open');
    });
  }

  if (detailsToggle && panelRight) {
    detailsToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      panelRight.classList.toggle('drawer-open');
    });
  }
}

// 7. Data Loader & State Refresh
export async function loadData() {
  try {
    const treeRes = await fetch('/api/tree');
    state.treeData = await treeRes.json();
    TreeComponent.init(state.treeData);

    const motorsRes = await fetch('/api/motors');
    state.motors = await motorsRes.json();

    const dashRes = await fetch('/api/dashboard');
    state.dashboardData = await dashRes.json();
    DashboardComponent.render(state.dashboardData);

    refreshCurrentView();
  } catch (err) {
    console.error("Failed to load plant data from server.", err);
  }
}

export function navigateToNode(node) {
  state.selectedNode = node;
  CenterPanelComponent.renderBreadcrumbs(node);

  const dbView = document.getElementById('dashboard-view');
  const eqView = document.getElementById('equipment-view');
  const dbToggle = document.getElementById('dashboard-toggle');
  const eqToggle = document.getElementById('equipment-toggle');

  if (node.type === 'plant') {
    if (dbView) dbView.classList.add('active');
    if (eqView) eqView.classList.remove('active');
    if (dbToggle) dbToggle.classList.add('active');
    if (eqToggle) eqToggle.classList.remove('active');
    RightPanelComponent.hideCard();
  } else if (node.type === 'motor') {
    if (dbView) dbView.classList.remove('active');
    if (eqView) eqView.classList.add('active');
    if (dbToggle) dbToggle.classList.remove('active');
    if (eqToggle) eqToggle.classList.add('active');

    RightPanelComponent.loadMotor(node.id);
  } else {
    if (dbView) dbView.classList.remove('active');
    if (eqView) eqView.classList.add('active');
    if (dbToggle) dbToggle.classList.remove('active');
    if (eqToggle) eqToggle.classList.add('active');

    CenterPanelComponent.loadEquipmentList(node);
    RightPanelComponent.hideCard();
  }
}

function refreshCurrentView() {
  const dbView = document.getElementById('dashboard-view');
  if (dbView && dbView.classList.contains('active')) {
    DashboardComponent.render(state.dashboardData);
  } else {
    CenterPanelComponent.renderFilteredAssetGrid(state.motors);
  }
}
