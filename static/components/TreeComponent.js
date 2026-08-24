/* -------------------------------------------------------------
 * MOTO-TWIN Tree Component (TreeComponent.js)
 * Collapsible list-based digital twin hierarchy tree explorer
 * ------------------------------------------------------------- */

import { navigateToNode, state } from '../app.js';

export const TreeComponent = {
  containerId: 'distribution-tree',
  flatNodes: {}, // tag/id -> node data reference

  init(treeData) {
    this.flatNodes = {};
    const container = document.getElementById(this.containerId);
    container.innerHTML = '';
    
    // Render tree recursively
    const treeHTML = this.renderNodeHTML(treeData);
    container.appendChild(treeHTML);

    this.setupListeners();
  },

  renderNodeHTML(node) {
    // Map icons
    let iconClass = 'fa-solid ';
    if (node.type === 'plant') iconClass += 'fa-industry plant';
    else if (node.type === 'substation') iconClass += 'fa-server substation';
    else if (node.type === 'transformer') iconClass += 'fa-bolt-lightning transformer';
    else if (node.type === 'pcc') iconClass += 'fa-cubes pcc';
    else if (node.type === 'mcc') iconClass += 'fa-table-cells mcc';
    else if (node.type === 'feeder') iconClass += 'fa-toggle-on feeder';
    else if (node.type === 'motor') iconClass += 'fa-gears motor';
    
    const li = document.createElement('li');
    li.className = `tree-node ${node.type}`;
    li.setAttribute('data-id', node.id);
    li.setAttribute('data-type', node.type);
    li.setAttribute('data-label', node.label);

    const hasChildren = node.children && node.children.length > 0;
    if (hasChildren) {
      li.classList.add('parent-node');
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'tree-node-content';
    
    // Expand/Collapse arrow
    const toggleSpan = document.createElement('span');
    toggleSpan.className = 'tree-toggle';
    if (hasChildren) {
      toggleSpan.innerHTML = '<i class="fa-solid fa-chevron-down"></i>';
    }
    contentDiv.appendChild(toggleSpan);

    // Icon
    const icon = document.createElement('i');
    icon.className = `tree-node-icon ${iconClass}`;
    contentDiv.appendChild(icon);

    // Text Label
    const textSpan = document.createElement('span');
    textSpan.className = 'tree-node-label';
    textSpan.textContent = node.label;
    contentDiv.appendChild(textSpan);

    // Health Score Badge for motors
    if (node.type === 'motor' && node.health_score !== undefined) {
      const hBadge = document.createElement('span');
      hBadge.className = 'tree-health-badge';
      hBadge.style.fontSize = '9px';
      hBadge.style.padding = '1px 4px';
      hBadge.style.borderRadius = '8px';
      hBadge.style.marginLeft = '6px';
      hBadge.style.background = node.health_score >= 75 ? 'rgba(46,204,113,0.15)' : (node.health_score >= 60 ? 'rgba(243,156,18,0.15)' : 'rgba(231,76,60,0.15)');
      hBadge.style.color = node.health_score >= 75 ? '#2ecc71' : (node.health_score >= 60 ? '#f39c12' : '#e74c3c');
      hBadge.textContent = `${node.health_score}%`;
      contentDiv.appendChild(hBadge);
    }

    // Status indicator light (for motors or aggregates)
    if (node.status) {
      const statusDot = document.createElement('span');
      statusDot.className = `status-indicator ${node.status.toLowerCase()}`;
      statusDot.title = `Status: ${node.status}`;
      contentDiv.appendChild(statusDot);
    }

    li.appendChild(contentDiv);

    // Store in flat reference for easy traversal
    this.flatNodes[node.id] = {
      id: node.id,
      label: node.label,
      type: node.type,
      status: node.status,
      element: li,
      parent: null
    };

    if (hasChildren) {
      const ul = document.createElement('ul');
      ul.className = 'tree-children';
      node.children.forEach(child => {
        const childLI = this.renderNodeHTML(child);
        ul.appendChild(childLI);
      });
      li.appendChild(ul);
    }

    return li;
  },

  setupListeners() {
    const container = document.getElementById(this.containerId);
    
    container.addEventListener('click', (e) => {
      const content = e.target.closest('.tree-node-content');
      if (!content) return;

      const nodeLI = content.parentElement;
      const nodeId = nodeLI.getAttribute('data-id');
      const nodeType = nodeLI.getAttribute('data-type');
      const nodeLabel = nodeLI.getAttribute('data-label');
      
      // If clicked toggle arrow
      const toggle = e.target.closest('.tree-toggle');
      if (toggle && nodeLI.classList.contains('parent-node')) {
        e.stopPropagation();
        nodeLI.classList.toggle('collapsed');
        return;
      }

      // Navigate to node
      navigateToNode({ id: nodeId, label: nodeLabel, type: nodeType });
    });

    // Expand All / Collapse All actions
    document.getElementById('tree-expand-all').addEventListener('click', () => {
      document.querySelectorAll('.parent-node').forEach(node => {
        node.classList.remove('collapsed');
      });
    });

    document.getElementById('tree-collapse-all').addEventListener('click', () => {
      document.querySelectorAll('.parent-node').forEach(node => {
        if (node.getAttribute('data-type') !== 'plant') {
          node.classList.add('collapsed');
        }
      });
    });
  },

  selectNode(nodeId) {
    // Remove previous selection
    document.querySelectorAll('.tree-node').forEach(node => {
      node.classList.remove('selected');
    });

    const target = this.flatNodes[nodeId];
    if (target && target.element) {
      target.element.classList.add('selected');
      
      // Expand parents to make sure it's visible
      let parent = target.element.parentElement.closest('.parent-node');
      while (parent) {
        parent.classList.remove('collapsed');
        parent = parent.parentElement.closest('.parent-node');
      }

      // Auto scroll to target node
      target.element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  },

  // Instant filtering of tree nodes by query text
  filterTree(query) {
    const q = query.trim().toLowerCase();
    if (!q) {
      // Reset filter - show all nodes
      document.querySelectorAll('.tree-node').forEach(node => {
        node.style.display = 'block';
        node.classList.remove('match');
      });
      return;
    }

    // Process nodes bottom-up (hide by default, show if matches or child matches)
    const allLIs = document.querySelectorAll('.tree-node');
    allLIs.forEach(li => {
      const id = li.getAttribute('data-id').toLowerCase();
      const label = li.getAttribute('data-label').toLowerCase();
      const match = id.includes(q) || label.includes(q);
      
      if (match) {
        li.classList.add('match');
      } else {
        li.classList.remove('match');
      }
      li.style.display = 'none'; // hide initially
    });

    // For any match, display it and all its ancestor branches
    document.querySelectorAll('.tree-node.match').forEach(li => {
      li.style.display = 'block';
      
      // Expand and show all parents
      let parent = li.parentElement.closest('.parent-node');
      while (parent) {
        parent.style.display = 'block';
        parent.classList.remove('collapsed');
        parent = parent.parentElement.closest('.parent-node');
      }

      // Show all children of matching node
      li.querySelectorAll('.tree-node').forEach(child => {
        child.style.display = 'block';
      });
    });
  },

  // Trace the parent of a motor node
  findParentNodeId(motorTag) {
    if (!state.treeData) return null;
    
    // Tree search helper
    const search = (node, parent) => {
      if (node.id === motorTag) return parent;
      if (node.children) {
        for (const child of node.children) {
          const res = search(child, node);
          if (res) return res;
        }
      }
      return null;
    };

    return search(state.treeData, null);
  }
};
