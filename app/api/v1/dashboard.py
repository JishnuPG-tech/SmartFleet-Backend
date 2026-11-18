from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Admin Web Dashboard"])

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SmartFleet 2.0 — Business Owner Command Portal</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            midnight: '#080A08',
            surface: '#111411',
            surfaceElevated: '#191D18',
            borderDark: '#292E28',
            brand: '#C6FF00',
            brandHover: '#B2E600',
            textPrimary: '#FFFFFF',
            textSecondary: '#B4BBB0',
            statusDanger: '#FF6565',
            statusWarning: '#FFB547',
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #080A08; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .toast-animate { animation: slideIn 0.3s ease-out forwards; }
    @keyframes slideIn { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- TOP HEADER -->
  <header class="border-b border-borderDark bg-surface sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-brand flex items-center justify-center text-midnight font-extrabold text-xl shadow-lg shadow-brand/20">
          SF
        </div>
        <div>
          <h1 class="text-lg font-bold text-textPrimary tracking-tight">SmartFleet <span class="text-brand">Command Portal</span></h1>
          <p class="text-xs text-textSecondary">Realtime Business Config & Remote App Controls</p>
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2 bg-surfaceElevated px-3 py-1.5 rounded-full border border-borderDark text-xs font-medium">
          <span class="w-2 h-2 rounded-full bg-brand animate-pulse"></span>
          <span class="text-textSecondary">Sync: <strong class="text-brand" id="syncStatus">Connected</strong></span>
        </div>
        <button onclick="refreshData()" class="p-2 rounded-lg bg-surfaceElevated hover:bg-borderDark text-textSecondary hover:text-white transition" title="Refresh">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
        </button>
      </div>
    </div>
  </header>

  <!-- TOAST CONTAINER -->
  <div id="toastContainer" class="fixed top-20 right-6 z-50 space-y-2 pointer-events-none"></div>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">

    <!-- OVERVIEW STATS -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Active Cargos</div>
        <div class="text-2xl font-bold text-textPrimary mt-1" id="statCargos">--</div>
        <div class="text-xs text-brand mt-1">Live in driver app</div>
      </div>
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Payload Tiers</div>
        <div class="text-2xl font-bold text-textPrimary mt-1" id="statWeights">--</div>
        <div class="text-xs text-textSecondary mt-1">Preset options</div>
      </div>
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Logistics Hubs</div>
        <div class="text-2xl font-bold text-textPrimary mt-1" id="statHubs">--</div>
        <div class="text-xs text-textSecondary mt-1">Kerala gateways</div>
      </div>
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Trip Allowance</div>
        <div class="text-2xl font-bold text-brand mt-1" id="statAllowance">₹1,500</div>
        <div class="text-xs text-textSecondary mt-1">Base driver bata</div>
      </div>
    </div>

    <!-- TABS NAVIGATION -->
    <div class="border-b border-borderDark mb-6 flex space-x-2 overflow-x-auto pb-1">
      <button onclick="switchTab('cargos')" id="tab-cargos" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-brand text-brand bg-surfaceElevated transition">
        📦 Cargo Categories
      </button>
      <button onclick="switchTab('weights')" id="tab-weights" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        ⚖️ Payload Weights
      </button>
      <button onclick="switchTab('hubs')" id="tab-hubs" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        📍 Kerala Hubs
      </button>
      <button onclick="switchTab('broadcast')" id="tab-broadcast" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        📢 Driver Emergency Broadcast
      </button>
      <button onclick="switchTab('rates')" id="tab-rates" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        💰 Allowance & Settings
      </button>
    </div>

    <!-- TAB 1: CARGO CATEGORIES -->
    <section id="panel-cargos" class="tab-panel space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 class="text-lg font-bold text-textPrimary">Manage Cargo Types</h2>
            <p class="text-sm text-textSecondary">These options appear instantly inside the driver and owner "New Trip" dropdown.</p>
          </div>
          <!-- Add Cargo Form -->
          <form onsubmit="handleAddCargo(event)" class="flex gap-2">
            <input id="newCargoInput" type="text" placeholder="e.g. Rubber Sheets / Raw Cashew" required
                   class="bg-surfaceElevated border border-borderDark rounded-lg px-4 py-2.5 text-sm text-white placeholder-textSecondary focus:outline-none focus:border-brand w-64 sm:w-80">
            <button type="submit" class="bg-brand text-midnight font-bold px-4 py-2.5 rounded-lg text-sm hover:bg-brandHover transition flex items-center space-x-1 shadow-md shadow-brand/10">
              <span>+ Add Cargo</span>
            </button>
          </form>
        </div>

        <!-- Cargo Chips Grid -->
        <div id="cargosList" class="flex flex-wrap gap-2.5 pt-2">
          <div class="text-sm text-textSecondary py-4">Loading active cargo categories...</div>
        </div>
      </div>
    </section>

    <!-- TAB 2: PAYLOAD WEIGHTS -->
    <section id="panel-weights" class="tab-panel hidden space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 class="text-lg font-bold text-textPrimary">Standard Payload Weights</h2>
            <p class="text-sm text-textSecondary">Configure common multi-axle and tipper payload weights in metric tons.</p>
          </div>
          <!-- Add Weight Form -->
          <form onsubmit="handleAddWeight(event)" class="flex gap-2">
            <input id="newWeightTons" type="number" step="0.5" min="1" max="60" placeholder="Tons (e.g. 26.5)" required
                   class="bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-brand w-28">
            <input id="newWeightLabel" type="text" placeholder="Vehicle Class (e.g. 12-Wheel Medium)" required
                   class="bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-brand w-56">
            <button type="submit" class="bg-brand text-midnight font-bold px-4 py-2.5 rounded-lg text-sm hover:bg-brandHover transition">
              + Add Tier
            </button>
          </form>
        </div>

        <div id="weightsGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div class="text-sm text-textSecondary py-4">Loading payload weight tiers...</div>
        </div>
      </div>
    </section>

    <!-- TAB 3: KERALA HUBS -->
    <section id="panel-hubs" class="tab-panel hidden space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 class="text-lg font-bold text-textPrimary">Logistics Hubs & Depots</h2>
            <p class="text-sm text-textSecondary">Origin and destination checkpoints available for trip dispatch.</p>
          </div>
          <!-- Add Hub Button / Trigger -->
          <button onclick="toggleAddHubModal(true)" class="bg-brand text-midnight font-bold px-4 py-2.5 rounded-lg text-sm hover:bg-brandHover transition">
            + Register New Hub
          </button>
        </div>

        <div id="hubsTable" class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-surfaceElevated text-textSecondary uppercase text-xs">
              <tr>
                <th class="px-4 py-3 rounded-l-lg">Code</th>
                <th class="px-4 py-3">City</th>
                <th class="px-4 py-3">Hub Name & Location</th>
                <th class="px-4 py-3">Coordinates (Lat, Lng)</th>
                <th class="px-4 py-3 text-right rounded-r-lg">Action</th>
              </tr>
            </thead>
            <tbody id="hubsTableBody" class="divide-y divide-borderDark">
              <tr><td colspan="5" class="px-4 py-6 text-center text-textSecondary">Loading registered hubs...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 4: DRIVER BROADCAST & NOTICES -->
    <section id="panel-broadcast" class="tab-panel hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Composer -->
        <div class="bg-surface border border-borderDark rounded-xl p-6">
          <h2 class="text-lg font-bold text-textPrimary mb-1">Broadcast Live Notice</h2>
          <p class="text-sm text-textSecondary mb-6">Instantly flashes a high-visibility alert banner on all active driver phones.</p>

          <form onsubmit="handlePostBroadcast(event)" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold uppercase text-textSecondary mb-1.5">Alert Severity</label>
              <select id="broadcastSeverity" class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand">
                <option value="warning">⚠️ Warning (Amber - Delays / Diversions)</option>
                <option value="critical">🚨 Critical (Red - Road Block / Strike / Hazard)</option>
                <option value="info">ℹ️ Information (Blue - Policy / Bonus updates)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase text-textSecondary mb-1.5">Notice Headline</label>
              <input id="broadcastTitle" type="text" placeholder="e.g. NH 66 Edappally Bypass Congestion" required
                     class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand">
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase text-textSecondary mb-1.5">Detailed Message</label>
              <textarea id="broadcastMessage" rows="3" placeholder="e.g. Heavy pipeline work near Lulu Mall; expect 30 mins delay. Take Kalamassery route if possible." required
                        class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand"></textarea>
            </div>

            <div class="flex items-center space-x-3 pt-2">
              <button type="submit" class="flex-1 bg-brand text-midnight font-bold py-3 rounded-lg text-sm hover:bg-brandHover transition shadow-lg shadow-brand/20">
                🚀 Send Broadcast to Drivers
              </button>
              <button type="button" onclick="handleClearBroadcast()" class="px-4 py-3 bg-surfaceElevated border border-borderDark hover:bg-borderDark text-statusDanger rounded-lg text-sm font-semibold transition">
                Clear Active Banner
              </button>
            </div>
          </form>
        </div>

        <!-- Live Preview -->
        <div class="bg-surface border border-borderDark rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h3 class="text-sm font-bold uppercase tracking-wider text-textSecondary mb-4">Driver Phone Preview</h3>
            <div id="bannerPreviewBox" class="border border-borderDark rounded-xl p-4 bg-surfaceElevated space-y-2">
              <div class="flex items-center space-x-2">
                <span id="previewBadge" class="text-xs px-2 py-0.5 rounded font-bold uppercase bg-statusWarning/20 text-statusWarning">WARNING</span>
                <span class="text-xs text-textSecondary">Just now</span>
              </div>
              <h4 id="previewTitle" class="font-bold text-sm text-white">No active broadcast</h4>
              <p id="previewText" class="text-xs text-textSecondary">When an alert is sent, it will appear pinned here and on every driver cockpit screen.</p>
            </div>
          </div>
          <div class="text-xs text-textSecondary mt-6 pt-4 border-t border-borderDark">
            Active banners persist across driver app restarts until manually cleared.
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 5: RATES & ALLOWANCE -->
    <section id="panel-rates" class="tab-panel hidden space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6 max-w-xl">
        <h2 class="text-lg font-bold text-textPrimary mb-1">Driver Trip Allowance</h2>
        <p class="text-sm text-textSecondary mb-6">Default daily bata/allowance auto-credited for newly dispatched trips.</p>

        <form onsubmit="handleUpdateAllowance(event)" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold uppercase text-textSecondary mb-1.5">Default Bata (₹ INR)</label>
            <div class="relative">
              <span class="absolute left-4 top-3 text-textSecondary font-bold">₹</span>
              <input id="inputAllowance" type="number" step="50" min="500" max="10000" required
                     class="w-full bg-surfaceElevated border border-borderDark rounded-lg pl-8 pr-4 py-2.5 text-sm text-white font-bold text-lg focus:outline-none focus:border-brand">
            </div>
          </div>
          <button type="submit" class="bg-brand text-midnight font-bold px-6 py-2.5 rounded-lg text-sm hover:bg-brandHover transition">
            Save Allowance Rate
          </button>
        </form>
      </div>
    </section>

  </main>

  <!-- ADD HUB MODAL -->
  <div id="addHubModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-surface border border-borderDark rounded-xl max-w-md w-full p-6 space-y-4">
      <h3 class="text-lg font-bold text-white">Register New Logistics Hub</h3>
      <form onsubmit="handleAddHub(event)" class="space-y-3">
        <div>
          <label class="block text-xs uppercase text-textSecondary mb-1">City Name</label>
          <input id="hubCity" type="text" placeholder="e.g. Alappuzha" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-sm text-white">
        </div>
        <div>
          <label class="block text-xs uppercase text-textSecondary mb-1">City Code (3 Letters)</label>
          <input id="hubCode" type="text" placeholder="e.g. ALP" maxlength="4" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-sm text-white uppercase">
        </div>
        <div>
          <label class="block text-xs uppercase text-textSecondary mb-1">Hub Name / Landmark</label>
          <input id="hubName" type="text" placeholder="e.g. Coir Industrial Development Zone" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-sm text-white">
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-xs uppercase text-textSecondary mb-1">Latitude</label>
            <input id="hubLat" type="number" step="0.0001" placeholder="9.4981" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-sm text-white">
          </div>
          <div>
            <label class="block text-xs uppercase text-textSecondary mb-1">Longitude</label>
            <input id="hubLng" type="number" step="0.0001" placeholder="76.3388" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-sm text-white">
          </div>
        </div>
        <div class="flex justify-end space-x-2 pt-3">
          <button type="button" onclick="toggleAddHubModal(false)" class="px-4 py-2 bg-surfaceElevated hover:bg-borderDark text-textSecondary rounded-lg text-sm">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-brand text-midnight font-bold rounded-lg text-sm hover:bg-brandHover">Save Hub</button>
        </div>
      </form>
    </div>
  </div>

  <!-- SCRIPT -->
  <script>
    let currentConfig = null;

    async function loadData() {
      try {
        const res = await fetch('/api/v1/config/metadata');
        if (!res.ok) throw new Error('API error');
        currentConfig = await res.json();
        render();
        document.getElementById('syncStatus').innerText = 'Connected';
        document.getElementById('syncStatus').className = 'text-brand';
      } catch (e) {
        console.error(e);
        document.getElementById('syncStatus').innerText = 'Offline/Reconnecting';
        document.getElementById('syncStatus').className = 'text-statusDanger';
      }
    }

    function render() {
      if (!currentConfig) return;

      // Stats
      document.getElementById('statCargos').innerText = (currentConfig.cargos || []).length;
      document.getElementById('statWeights').innerText = (currentConfig.weights || []).length;
      document.getElementById('statHubs').innerText = (currentConfig.hubs || []).length;
      document.getElementById('statAllowance').innerText = '₹' + (currentConfig.driver_allowance_default || 1500).toLocaleString();
      document.getElementById('inputAllowance').value = currentConfig.driver_allowance_default || 1500;

      // Cargos list
      const cList = document.getElementById('cargosList');
      cList.innerHTML = '';
      (currentConfig.cargos || []).forEach(cargo => {
        const div = document.createElement('div');
        div.className = 'flex items-center space-x-2 bg-surfaceElevated border border-borderDark px-3 py-1.5 rounded-lg text-sm text-white hover:border-brand/40 transition';
        div.innerHTML = `
          <span>${cargo}</span>
          <button onclick="handleDeleteCargo('${cargo.replace(/'/g, "\\'")}')" class="text-textSecondary hover:text-statusDanger transition ml-1 font-bold text-xs" title="Delete">✕</button>
        `;
        cList.appendChild(div);
      });

      // Weights grid
      const wGrid = document.getElementById('weightsGrid');
      wGrid.innerHTML = '';
      (currentConfig.weights || []).forEach(w => {
        const card = document.createElement('div');
        card.className = 'flex items-center justify-between p-3.5 bg-surfaceElevated border border-borderDark rounded-lg';
        card.innerHTML = `
          <div>
            <div class="text-brand font-bold text-base">${parseFloat(w.val).toFixed(1)} Tons</div>
            <div class="text-xs text-textSecondary">${w.label}</div>
          </div>
          <button onclick="handleDeleteWeight(${w.val})" class="text-textSecondary hover:text-statusDanger p-1 text-sm font-bold" title="Delete">✕</button>
        `;
        wGrid.appendChild(card);
      });

      // Hubs table
      const hBody = document.getElementById('hubsTableBody');
      hBody.innerHTML = '';
      (currentConfig.hubs || []).forEach(h => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-surfaceElevated/50 transition';
        tr.innerHTML = `
          <td class="px-4 py-3 font-bold text-brand">${h.code}</td>
          <td class="px-4 py-3 font-semibold text-white">${h.city}</td>
          <td class="px-4 py-3 text-textSecondary">${h.name}</td>
          <td class="px-4 py-3 text-xs font-mono text-textSecondary">${h.lat.toFixed(4)}, ${h.lng.toFixed(4)}</td>
          <td class="px-4 py-3 text-right">
            <button onclick="handleDeleteHub('${h.code}')" class="text-textSecondary hover:text-statusDanger font-bold text-xs">Remove</button>
          </td>
        `;
        hBody.appendChild(tr);
      });

      // Broadcast preview
      const banner = currentConfig.notice_banner;
      const bBox = document.getElementById('bannerPreviewBox');
      const bBadge = document.getElementById('previewBadge');
      const bTitle = document.getElementById('previewTitle');
      const bText = document.getElementById('previewText');

      if (banner && banner.active) {
        bBox.className = 'border border-statusWarning/50 rounded-xl p-4 bg-statusWarning/10 space-y-2';
        bBadge.innerText = (banner.severity || 'WARNING').toUpperCase();
        bBadge.className = 'text-xs px-2 py-0.5 rounded font-bold uppercase bg-statusWarning text-midnight';
        bTitle.innerText = banner.title;
        bText.innerText = banner.message;
      } else {
        bBox.className = 'border border-borderDark rounded-xl p-4 bg-surfaceElevated space-y-2';
        bBadge.innerText = 'INACTIVE';
        bBadge.className = 'text-xs px-2 py-0.5 rounded font-bold uppercase bg-borderDark text-textSecondary';
        bTitle.innerText = 'No active broadcast';
        bText.innerText = 'When an alert is sent, it will appear pinned here and on every driver cockpit screen.';
      }
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.className = 'tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition';
      });
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));

      document.getElementById('tab-' + tabId).className = 'tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-brand text-brand bg-surfaceElevated transition';
      document.getElementById('panel-' + tabId).classList.remove('hidden');
    }

    function showToast(msg, isSuccess = true) {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      toast.className = `toast-animate px-4 py-3 rounded-lg text-sm font-semibold text-white flex items-center space-x-2 shadow-xl border ${isSuccess ? 'bg-surface border-brand text-brand' : 'bg-surface border-statusDanger text-statusDanger'}`;
      toast.innerHTML = `<span>${isSuccess ? '✓' : '⚠️'}</span><span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => toast.remove(), 3500);
    }

    // ACTIONS
    async function handleAddCargo(e) {
      e.preventDefault();
      const input = document.getElementById('newCargoInput');
      const name = input.value.trim();
      if (!name) return;

      const res = await fetch('/api/v1/config/cargo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
      });
      if (res.ok) {
        input.value = '';
        showToast(`Added cargo "${name}"`);
        loadData();
      }
    }

    async function handleDeleteCargo(name) {
      if (!confirm(`Remove "${name}" from active cargo categories?`)) return;
      const res = await fetch(`/api/v1/config/cargo/${encodeURIComponent(name)}`, {method: 'DELETE'});
      if (res.ok) {
        showToast(`Removed "${name}"`);
        loadData();
      }
    }

    async function handleAddWeight(e) {
      e.preventDefault();
      const tons = parseFloat(document.getElementById('newWeightTons').value);
      const label = document.getElementById('newWeightLabel').value.trim();

      const res = await fetch('/api/v1/config/weight', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({val: tons, label})
      });
      if (res.ok) {
        document.getElementById('newWeightTons').value = '';
        document.getElementById('newWeightLabel').value = '';
        showToast(`Added ${tons}T payload tier`);
        loadData();
      }
    }

    async function handleDeleteWeight(val) {
      if (!confirm(`Remove ${val}T payload tier?`)) return;
      const res = await fetch(`/api/v1/config/weight/${val}`, {method: 'DELETE'});
      if (res.ok) {
        showToast(`Removed ${val}T tier`);
        loadData();
      }
    }

    async function handleAddHub(e) {
      e.preventDefault();
      const payload = {
        city: document.getElementById('hubCity').value.trim(),
        code: document.getElementById('hubCode').value.trim().toUpperCase(),
        name: document.getElementById('hubName').value.trim(),
        lat: parseFloat(document.getElementById('hubLat').value),
        lng: parseFloat(document.getElementById('hubLng').value),
      };

      const res = await fetch('/api/v1/config/hub', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        toggleAddHubModal(false);
        showToast(`Registered hub "${payload.city} (${payload.code})"`);
        loadData();
      }
    }

    async function handleDeleteHub(code) {
      if (!confirm(`Delete hub ${code}?`)) return;
      const res = await fetch(`/api/v1/config/hub/${encodeURIComponent(code)}`, {method: 'DELETE'});
      if (res.ok) {
        showToast(`Deleted hub ${code}`);
        loadData();
      }
    }

    async function handlePostBroadcast(e) {
      e.preventDefault();
      const payload = {
        severity: document.getElementById('broadcastSeverity').value,
        title: document.getElementById('broadcastTitle').value.trim(),
        message: document.getElementById('broadcastMessage').value.trim(),
      };

      const res = await fetch('/api/v1/config/broadcast', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast('Broadcast sent to all driver cockpits!');
        loadData();
      }
    }

    async function handleClearBroadcast() {
      const res = await fetch('/api/v1/config/broadcast', {method: 'DELETE'});
      if (res.ok) {
        showToast('Active broadcast cleared');
        loadData();
      }
    }

    async function handleUpdateAllowance(e) {
      e.preventDefault();
      const amount = parseInt(document.getElementById('inputAllowance').value);
      const res = await fetch(`/api/v1/config/allowance?amount=${amount}`, {method: 'POST'});
      if (res.ok) {
        showToast(`Default trip allowance updated to ₹${amount.toLocaleString()}`);
        loadData();
      }
    }

    function toggleAddHubModal(show) {
      document.getElementById('addHubModal').classList.toggle('hidden', !show);
    }

    function refreshData() {
      loadData();
      showToast('Refreshed latest configuration');
    }

    // Initialize
    loadData();
  </script>
</body>
</html>
"""

@router.get("/admin", response_class=HTMLResponse)
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_portal():
    """Pure-User Command Portal for business owners to manage fleet dropdowns, weights, hubs, and notices."""
    return HTMLResponse(content=HTML_CONTENT, status_code=200)
