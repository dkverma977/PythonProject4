/* -------------------------------------------------------------
 * MOTO-TWIN Dashboard Component (DashboardComponent.js)
 * KPI telemetry tiles and Chart.js aggregation and rendering
 * ------------------------------------------------------------- */

let chartPower = null;
let chartArea = null;
let chartVoltage = null;
let chartMake = null;

export const DashboardComponent = {
  
  // Render full dashboard stats fetched from backend API
  render(data) {
    this.updateKPIs(data.counts);
    this.renderPowerChart(data.power_dist);
    this.renderAreaChart(data.area_dist);
    this.renderVoltageChart(data.voltage_dist);
    this.renderMakeChart(data.make_dist);
  },

  // Update card elements
  updateKPIs(counts) {
    document.getElementById('kpi-total-motors').textContent = counts.motors;
    document.getElementById('kpi-running-motors').textContent = counts.running;
    document.getElementById('kpi-standby-motors').textContent = counts.standby;
    document.getElementById('kpi-fault-motors').textContent = counts.fault;

    document.getElementById('kpi-total-subs').textContent = counts.substations;
    document.getElementById('kpi-total-pccs').textContent = counts.pccs;
    document.getElementById('kpi-total-mccs').textContent = counts.mccs;
    document.getElementById('kpi-total-feeders').textContent = counts.feeders;
  },

  // Perform Client-Side filtering and re-aggregation
  renderFiltered(motors, filters, search) {
    const q = search.trim().toLowerCase();
    
    // Apply filters
    const filtered = motors.filter(m => {
      // 1. Search Query
      if (q) {
        const matches = 
          m.tag.toLowerCase().includes(q) ||
          m.name.toLowerCase().includes(q) ||
          m.make.toLowerCase().includes(q) ||
          m.location.toLowerCase().includes(q) ||
          m.mcc.toLowerCase().includes(q) ||
          m.feeder.toLowerCase().includes(q);
        if (!matches) return false;
      }
      // 2. Dropdown Filters
      if (filters.area && m.area !== filters.area) return false;
      if (filters.voltage && m.voltage !== parseInt(filters.voltage)) return false;
      if (filters.make && m.make !== filters.make) return false;
      if (filters.status && m.status !== filters.status) return false;
      if (filters.critical) {
        const isCrit = filters.critical === 'critical';
        if (m.is_critical !== isCrit) return false;
      }
      return true;
    });

    // Re-Aggregate Counts
    const counts = {
      motors: filtered.length,
      running: filtered.filter(m => m.status === 'Running').length,
      standby: filtered.filter(m => m.status === 'Standby').length,
      fault: filtered.filter(m => m.status === 'Fault').length,
      substations: new Set(filtered.map(m => m.substation).filter(Boolean)).size,
      pccs: new Set(filtered.map(m => `${m.substation}|${m.pcc}`).filter(Boolean)).size,
      mccs: new Set(filtered.map(m => `${m.substation}|${m.pcc}|${m.mcc}`).filter(Boolean)).size,
      feeders: new Set(filtered.map(m => `${m.substation}|${m.pcc}|${m.mcc}|${m.feeder}`).filter(Boolean)).size
    };
    
    this.updateKPIs(counts);

    // Re-Aggregate Chart data
    // 1. Power
    const power_ranges = {"<15 kW": 0, "15-55 kW": 0, "55-150 kW": 0, ">150 kW": 0};
    filtered.forEach(m => {
      const kw = m.power_kw || 0;
      if (kw < 15) power_ranges["<15 kW"] += 1;
      else if (kw <= 55) power_ranges["15-55 kW"] += 1;
      else if (kw <= 150) power_ranges["55-150 kW"] += 1;
      else power_ranges[">150 kW"] += 1;
    });
    const powerData = Object.entries(power_ranges).map(([k, v]) => ({ range: k, count: v }));

    // 2. Area
    const areas = {};
    filtered.forEach(m => { areas[m.area] = (areas[m.area] || 0) + 1; });
    const areaData = Object.entries(areas).map(([k, v]) => ({ area: k, count: v }));

    // 3. Voltage
    const voltages = {};
    filtered.forEach(m => {
      const v_str = m.voltage < 1000 ? `${m.voltage} V` : `${(m.voltage/1000).toFixed(1)} kV`;
      voltages[v_str] = (voltages[v_str] || 0) + 1;
    });
    const voltageData = Object.entries(voltages).map(([k, v]) => ({ voltage: k, count: v }));

    // 4. Make
    const makes = {};
    filtered.forEach(m => { makes[m.make] = (makes[m.make] || 0) + 1; });
    const makeData = Object.entries(makes).map(([k, v]) => ({ make: k, count: v }));

    // Update charts data dynamically
    this.updateChartData(chartPower, powerData.map(d => d.range), powerData.map(d => d.count));
    this.updateChartData(chartArea, areaData.map(d => d.area), areaData.map(d => d.count));
    this.updateChartData(chartVoltage, voltageData.map(d => d.voltage), voltageData.map(d => d.count));
    this.updateChartData(chartMake, makeData.map(d => d.make), makeData.map(d => d.count));
  },

  updateChartData(chart, labels, data) {
    if (!chart) return;
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update();
  },

  // Chart setups
  renderPowerChart(dist) {
    if (chartPower) chartPower.destroy();
    
    const ctx = document.getElementById('chart-power').getContext('2d');
    const colors = getThemeColors();

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
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { color: colors.grid }, ticks: { color: colors.text } },
          y: { grid: { color: colors.grid }, ticks: { color: colors.text, precision: 0 } }
        }
      }
    });
  },

  renderAreaChart(dist) {
    if (chartArea) chartArea.destroy();
    
    const ctx = document.getElementById('chart-area').getContext('2d');
    const colors = getThemeColors();

    chartArea = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: dist.map(d => d.area),
        datasets: [{
          label: 'Motors Count',
          data: dist.map(d => d.count),
          backgroundColor: 'rgba(52, 152, 219, 0.6)',
          borderColor: 'rgba(52, 152, 219, 1)',
          borderWidth: 1.5
        }]
      },
      options: {
        indexAxis: 'y', // horizontal bar chart
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { color: colors.grid }, ticks: { color: colors.text, precision: 0 } },
          y: { grid: { color: colors.grid }, ticks: { color: colors.text } }
        }
      }
    });
  },

  renderVoltageChart(dist) {
    if (chartVoltage) chartVoltage.destroy();
    
    const ctx = document.getElementById('chart-voltage').getContext('2d');
    const colors = getThemeColors();

    chartVoltage = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: dist.map(d => d.voltage),
        datasets: [{
          data: dist.map(d => d.count),
          backgroundColor: [
            'rgba(46, 204, 113, 0.7)',
            'rgba(241, 196, 15, 0.7)',
            'rgba(155, 89, 182, 0.7)',
            'rgba(231, 76, 60, 0.7)'
          ],
          borderColor: colors.border,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: colors.text, font: { family: 'Outfit' } }
          }
        }
      }
    });
  },

  renderMakeChart(dist) {
    if (chartMake) chartMake.destroy();
    
    const ctx = document.getElementById('chart-make').getContext('2d');
    const colors = getThemeColors();

    chartMake = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: dist.map(d => d.make),
        datasets: [{
          data: dist.map(d => d.count),
          backgroundColor: [
            'rgba(26, 188, 156, 0.7)',
            'rgba(230, 126, 34, 0.7)',
            'rgba(52, 73, 94, 0.7)',
            'rgba(243, 156, 18, 0.7)'
          ],
          borderColor: colors.border,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: colors.text, font: { family: 'Outfit' } }
          }
        }
      }
    });
  },

  // Refresh charts colors when theme switches (Light vs Dark mode grid lines / text colors)
  updateChartColors() {
    const colors = getThemeColors();
    const charts = [chartPower, chartArea, chartVoltage, chartMake];
    
    charts.forEach(chart => {
      if (!chart) return;
      
      // Update Legend text
      if (chart.options.plugins && chart.options.plugins.legend) {
        chart.options.plugins.legend.labels.color = colors.text;
      }
      
      // Update Scales ticks/grids
      if (chart.options.scales) {
        if (chart.options.scales.x) {
          chart.options.scales.x.grid.color = colors.grid;
          chart.options.scales.x.ticks.color = colors.text;
        }
        if (chart.options.scales.y) {
          chart.options.scales.y.grid.color = colors.grid;
          chart.options.scales.y.ticks.color = colors.text;
        }
      }
      
      // Update Doughnut / Pie borders
      if (chart.data.datasets && chart.data.datasets[0] && chart.config.type !== 'bar') {
        chart.data.datasets[0].borderColor = colors.border;
      }
      
      chart.update();
    });
  }
};

// Retrieve HSL color values relative to theme state
function getThemeColors() {
  const isLight = document.body.classList.contains('light-theme');
  return {
    text: isLight ? '#2f3640' : '#e1e7ed',
    grid: isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.06)',
    border: isLight ? '#ffffff' : '#1e1e1e'
  };
}
