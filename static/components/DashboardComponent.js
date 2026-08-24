/* -------------------------------------------------------------
 * MOTO-TWIN Dashboard Component (DashboardComponent.js)
 * KPI telemetry tiles, Predictive Risk feed, and Chart.js analytics
 * ------------------------------------------------------------- */

let chartHealth = null;
let chartCriticality = null;
let chartPower = null;
let chartArea = null;

export const DashboardComponent = {
  
  render(data) {
    this.updateKPIs(data);
    this.renderHealthChart(data.health_dist || []);
    this.renderCriticalityChart(data.criticality_dist || []);
    this.renderPowerChart(data.power_dist || []);
    this.renderAreaChart(data.area_dist || []);
    this.loadPredictiveRiskFeed();
  },

  updateKPIs(data) {
    const counts = data.counts || {};
    document.getElementById('kpi-total-motors').textContent = counts.motors || 0;
    document.getElementById('kpi-running-motors').textContent = counts.running || 0;
    document.getElementById('kpi-standby-motors').textContent = counts.standby || 0;
    document.getElementById('kpi-fault-motors').textContent = counts.fault || 0;

    if (document.getElementById('kpi-avg-health')) {
      document.getElementById('kpi-avg-health').textContent = `${data.avg_health_score || 85}%`;
    }
    if (document.getElementById('kpi-active-alarms')) {
      document.getElementById('kpi-active-alarms').textContent = data.active_alarms_count || 0;
    }
    if (document.getElementById('kpi-overdue-maint')) {
      document.getElementById('kpi-overdue-maint').textContent = data.maintenance_overdue_count || 0;
    }
    if (document.getElementById('kpi-daily-energy')) {
      document.getElementById('kpi-daily-energy').textContent = `${(data.daily_energy_kwh || 0).toLocaleString()} kWh`;
    }
  },

  async loadPredictiveRiskFeed() {
    const feed = document.getElementById('predictive-feed');
    if (!feed) return;
    try {
      const res = await fetch('/api/motors');
      if (!res.ok) return;
      const motors = await res.json();
      
      const riskyMotors = motors.filter(m => (m.health_score < 75) || m.status === 'Fault');
      feed.innerHTML = '';

      if (riskyMotors.length === 0) {
        feed.innerHTML = '<span class="feed-item"><i class="fa-solid fa-circle-check" style="color:#2ecc71;"></i> All motors operating within normal health & telemetry bounds. Zero elevated risks detected.</span>';
        return;
      }

      riskyMotors.slice(0, 4).forEach(m => {
        const item = document.createElement('div');
        item.className = 'feed-item';
        item.innerHTML = `
          <i class="fa-solid fa-triangle-exclamation" style="color: ${m.status === 'Fault' ? '#e74c3c' : '#f39c12'};"></i>
          <strong>${m.tag} (${m.name})</strong> — Health: <span style="color:${m.health_score < 60 ? '#e74c3c' : '#f39c12'};font-weight:bold;">${m.health_score}% ${m.condition_status}</span> | Status: ${m.status} | MCC: ${m.mcc || 'MCC-1'}
        `;
        feed.appendChild(item);
      });
    } catch (err) {
      console.error("Failed to load predictive risk feed.", err);
    }
  },

  renderHealthChart(dist) {
    const el = document.getElementById('chart-health');
    if (!el) return;
    if (chartHealth) chartHealth.destroy();
    
    const ctx = el.getContext('2d');
    chartHealth = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: dist.map(d => d.category),
        datasets: [{
          data: dist.map(d => d.count),
          backgroundColor: ['#2ecc71', '#1abc9c', '#f39c12', '#e67e22', '#e74c3c'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#e1e7ed', font: { size: 10 } } }
        }
      }
    });
  },

  renderCriticalityChart(dist) {
    const el = document.getElementById('chart-criticality');
    if (!el) return;
    if (chartCriticality) chartCriticality.destroy();
    
    const ctx = el.getContext('2d');
    chartCriticality = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: dist.map(d => d.criticality),
        datasets: [{
          data: dist.map(d => d.count),
          backgroundColor: ['#e74c3c', '#3498db', '#95a5a6'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#e1e7ed', font: { size: 10 } } }
        }
      }
    });
  },

  renderPowerChart(dist) {
    const el = document.getElementById('chart-power');
    if (!el) return;
    if (chartPower) chartPower.destroy();
    
    const ctx = el.getContext('2d');
    chartPower = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: dist.map(d => d.range),
        datasets: [{
          label: 'Motors Count',
          data: dist.map(d => d.count),
          backgroundColor: 'rgba(0, 210, 211, 0.6)',
          borderColor: 'rgba(0, 210, 211, 1)',
          borderWidth: 1.5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#2f2f35' }, ticks: { color: '#e1e7ed' } },
          y: { grid: { color: '#2f2f35' }, ticks: { color: '#e1e7ed', precision: 0 } }
        }
      }
    });
  },

  renderAreaChart(dist) {
    const el = document.getElementById('chart-area');
    if (!el) return;
    if (chartArea) chartArea.destroy();
    
    const ctx = el.getContext('2d');
    chartArea = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: dist.map(d => d.area),
        datasets: [{
          label: 'Motors Count',
          data: dist.map(d => d.count),
          backgroundColor: 'rgba(155, 89, 182, 0.6)',
          borderColor: 'rgba(155, 89, 182, 1)',
          borderWidth: 1.5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#2f2f35' }, ticks: { color: '#e1e7ed' } },
          y: { grid: { color: '#2f2f35' }, ticks: { color: '#e1e7ed', precision: 0 } }
        }
      }
    });
  }
};
