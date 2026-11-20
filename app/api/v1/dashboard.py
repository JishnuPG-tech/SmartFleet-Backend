import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Admin Web Dashboard"])

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SmartFleet 2.0 — Enterprise Fleet Command Portal</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  
  <!-- Leaflet CSS & JS for Live Radar Map -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            midnight: '#08090D',
            surface: '#11131B',
            surfaceElevated: '#171A23',
            borderDark: 'rgba(248, 250, 252, 0.08)',
            borderStrong: 'rgba(248, 250, 252, 0.16)',
            brand: '#C6FF00',
            brandHover: '#B2E600',
            brandSky: '#38BDF8',
            brandClaude: '#D97757',
            textPrimary: '#F8FAFC',
            textSecondary: '#B5BCC9',
            textMuted: '#7F899B',
            statusDanger: '#FF647C',
            statusWarning: '#F6C56B',
            statusSuccess: '#48D6A0',
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #08090D; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .toast-animate { animation: slideIn 0.3s ease-out forwards; }
    @keyframes slideIn { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    #fleetMap { height: 560px; width: 100%; border-radius: 0.75rem; z-index: 10; }
    .leaflet-popup-content-wrapper { background: #11131B !important; color: #F8FAFC !important; border: 1px solid rgba(248, 250, 252, 0.16); border-radius: 0.5rem; }
    .leaflet-popup-tip { background: #11131B !important; }
    .truck-marker-icon { transition: transform 0.4s ease-out; }
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
          <h1 class="text-base font-bold text-textPrimary tracking-tight flex items-center gap-2">
            SmartFleet <span class="text-brand">Command Portal</span>
            <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-brand/10 text-brand border border-brand/20">Enterprise 2.0</span>
          </h1>
          <p class="text-xs text-textSecondary">Real-Time Mobile GPS Telemetry & Zero-Redeploy App CMS</p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2 bg-surfaceElevated px-3 py-1.5 rounded-full border border-borderDark text-xs font-medium">
          <span id="syncDot" class="w-2 h-2 rounded-full bg-brand animate-pulse"></span>
          <span class="text-textSecondary">Telemetry WS: <strong class="text-brand font-mono" id="syncStatus">Connected</strong></span>
        </div>
        <button onclick="refreshData()" class="p-2 rounded-lg bg-surfaceElevated hover:bg-borderStrong text-textSecondary hover:text-white transition" title="Refresh">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
        </button>
      </div>
    </div>
  </header>

  <!-- TOAST CONTAINER -->
  <div id="toastContainer" class="fixed top-20 right-6 z-50 space-y-2 pointer-events-none"></div>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full">

    <!-- KPI SUMMARY CARDS -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Active Trucks</div>
        <div class="text-2xl font-bold text-textPrimary mt-1" id="statTrucks">--</div>
        <div class="text-xs text-brand mt-1 flex items-center gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-brand animate-ping"></span> Live GPS Streaming
        </div>
      </div>
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Trips in Transit</div>
        <div class="text-2xl font-bold text-textPrimary mt-1" id="statTrips">--</div>
        <div class="text-xs text-brandSky mt-1">Kerala NH-66 Corridor</div>
      </div>
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Registered Drivers</div>
        <div class="text-2xl font-bold text-textPrimary mt-1" id="statDrivers">--</div>
        <div class="text-xs text-textSecondary mt-1">Commercial DL Verified</div>
      </div>
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="text-xs text-textSecondary uppercase tracking-wider font-semibold">Daily Bata Standard</div>
        <div class="text-2xl font-bold text-brand mt-1" id="statAllowance">₹1,500</div>
        <div class="text-xs text-textSecondary mt-1">OTA Controlled Allowance</div>
      </div>
    </div>

    <!-- TABS NAVIGATION -->
    <div class="border-b border-borderDark mb-6 flex space-x-2 overflow-x-auto pb-1">
      <button onclick="switchTab('radar')" id="tab-radar" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-brand text-brand bg-surfaceElevated transition">
        🗺️ Live Radar Map
      </button>
      <button onclick="switchTab('trips')" id="tab-trips" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        📋 Trips & Waybills
      </button>
      <button onclick="switchTab('cms')" id="tab-cms" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        📱 App CMS & Hotlines
      </button>
      <button onclick="switchTab('cargos')" id="tab-cargos" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        📦 Cargo Categories
      </button>
      <button onclick="switchTab('hubs')" id="tab-hubs" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        📍 Kerala Hubs
      </button>
      <button onclick="switchTab('broadcast')" id="tab-broadcast" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        📢 Driver Broadcast
      </button>
      <button onclick="switchTab('updates')" id="tab-updates" class="tab-btn px-4 py-2.5 rounded-lg text-sm font-semibold border-b-2 border-transparent text-textSecondary hover:text-white transition">
        🚀 APK Auto-Updater
      </button>
    </div>

    <!-- TAB 1: LIVE RADAR MAP -->
    <section id="panel-radar" class="tab-panel space-y-4">
      <div class="bg-surface border border-borderDark rounded-xl p-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div>
            <h2 class="text-base font-bold text-textPrimary flex items-center gap-2">
              Kerala Highway Live Operations Map
              <span class="text-xs font-normal text-textSecondary font-mono">(NH-66 / MC Road / National Corridor)</span>
            </h2>
            <p class="text-xs text-textSecondary">Real-time driver mobile phone GPS breadcrumbs updating with continuous bearing interpolation.</p>
          </div>
          <div class="flex items-center gap-2 text-xs">
            <span class="px-2.5 py-1 rounded bg-surfaceElevated border border-borderDark flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-statusSuccess"></span> Moving / Active
            </span>
            <span class="px-2.5 py-1 rounded bg-surfaceElevated border border-borderDark flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-statusWarning"></span> Idle / Terminal
            </span>
            <span class="px-2.5 py-1 rounded bg-surfaceElevated border border-borderDark flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-statusDanger"></span> Breakdown SOS
            </span>
          </div>
        </div>

        <!-- Leaflet Map Container -->
        <div id="fleetMap" class="border border-borderDark shadow-inner"></div>
      </div>
    </section>

    <!-- TAB 2: TRIPS & WAYBILLS -->
    <section id="panel-trips" class="tab-panel hidden space-y-4">
      <div class="bg-surface border border-borderDark rounded-xl p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-base font-bold text-textPrimary">Active & Historical Freight Trips</h2>
            <p class="text-xs text-textSecondary">Real-time dispatch state machine: Waiting ➔ Accepted ➔ Running ➔ Delivered.</p>
          </div>
          <button onclick="refreshData()" class="px-3 py-1.5 bg-surfaceElevated border border-borderDark hover:border-brand text-xs font-semibold rounded-lg text-textPrimary transition">
            Refresh Trips
          </button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-textSecondary">
            <thead class="bg-surfaceElevated uppercase tracking-wider text-[11px] font-bold text-textPrimary border-b border-borderDark">
              <tr>
                <th class="px-4 py-3">Trip ID</th>
                <th class="px-4 py-3">Route Corridor</th>
                <th class="px-4 py-3">Truck & Driver</th>
                <th class="px-4 py-3">Cargo & Weight</th>
                <th class="px-4 py-3">Progress</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">POD Proof</th>
              </tr>
            </thead>
            <tbody id="tripsTableBody" class="divide-y divide-borderDark font-medium">
              <tr><td colspan="7" class="px-4 py-6 text-center text-textMuted">Loading active trips...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 3: APP CMS & HOTLINES (ZERO REDEPLOY) -->
    <section id="panel-cms" class="tab-panel hidden space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6">
        <div class="mb-6">
          <div class="flex items-center gap-2">
            <h2 class="text-lg font-bold text-textPrimary">Zero-Redeploy App CMS & Remote Config</h2>
            <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-brand/10 text-brand border border-brand/20">Instant Live Sync</span>
          </div>
          <p class="text-xs text-textSecondary mt-1">Changes saved here are broadcast over WebSockets and instantly update the mobile app without requiring a code push or APK recompilation.</p>
        </div>

        <form id="cmsForm" onsubmit="handleSaveCms(event)" class="space-y-6">
          <!-- Emergency Contacts Section -->
          <div class="border border-borderDark rounded-xl p-4 bg-surfaceElevated/50 space-y-4">
            <h3 class="text-sm font-bold text-textPrimary flex items-center gap-2">
              📞 Emergency Hotlines & Dispatch Numbers
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <label class="block font-semibold text-textSecondary mb-1">Kerala Highway Police Patrol</label>
                <input id="cmsHighwayPolice" type="text" class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand font-mono">
              </div>
              <div>
                <label class="block font-semibold text-textSecondary mb-1">Head Office Dispatch Line</label>
                <input id="cmsOfficeDispatch" type="text" class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand font-mono">
              </div>
              <div>
                <label class="block font-semibold text-textSecondary mb-1">Heavy Breakdown / Towing Service</label>
                <input id="cmsBreakdown" type="text" class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand font-mono">
              </div>
            </div>
          </div>

          <!-- Theme Palette Section -->
          <div class="border border-borderDark rounded-xl p-4 bg-surfaceElevated/50 space-y-4">
            <h3 class="text-sm font-bold text-textPrimary flex items-center gap-2">
              🎨 Default App Theme Palette
            </h3>
            <p class="text-xs text-textSecondary">Select the default accent color delivered to all fresh driver app installs. Drivers can also toggle this inside their app settings.</p>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label class="flex items-center gap-3 p-3.5 rounded-lg border border-borderDark bg-surface hover:border-brand cursor-pointer">
                <input type="radio" name="default_palette" value="lime_green" id="themeLime">
                <div>
                  <div class="text-xs font-bold text-brand flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full bg-brand"></span> Lime Green (Acid)
                  </div>
                  <div class="text-[11px] text-textSecondary">High-visibility Kerala sunlight default</div>
                </div>
              </label>
              <label class="flex items-center gap-3 p-3.5 rounded-lg border border-borderDark bg-surface hover:border-brandSky cursor-pointer">
                <input type="radio" name="default_palette" value="sky_blue" id="themeSky">
                <div>
                  <div class="text-xs font-bold text-brandSky flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full bg-brandSky"></span> Sky Blue
                  </div>
                  <div class="text-[11px] text-textSecondary">Precision telematics cool tone</div>
                </div>
              </label>
              <label class="flex items-center gap-3 p-3.5 rounded-lg border border-borderDark bg-surface hover:border-brandClaude cursor-pointer">
                <input type="radio" name="default_palette" value="claude_orange" id="themeClaude">
                <div>
                  <div class="text-xs font-bold text-brandClaude flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full bg-brandClaude"></span> Claude Orange
                  </div>
                  <div class="text-[11px] text-textSecondary">Editorial low-fatigue warm tone</div>
                </div>
              </label>
            </div>
          </div>

          <!-- Base Bata Allowance -->
          <div class="border border-borderDark rounded-xl p-4 bg-surfaceElevated/50 space-y-4">
            <h3 class="text-sm font-bold text-textPrimary flex items-center gap-2">
              💰 Driver Daily Bata Allowance
            </h3>
            <div class="flex items-center gap-4 text-xs">
              <div class="w-48">
                <label class="block font-semibold text-textSecondary mb-1">Standard Daily Allowance (₹)</label>
                <input id="cmsAllowance" type="number" step="50" min="500" max="5000" class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand font-mono font-bold text-brand">
              </div>
              <div class="text-textSecondary pt-5">
                Automatically applied as the base fare allowance for new trip calculations.
              </div>
            </div>
          </div>

          <div class="flex justify-end">
            <button type="submit" id="btnSaveCms" class="bg-brand text-midnight font-bold px-6 py-2.5 rounded-lg text-sm hover:bg-brandHover transition flex items-center gap-2 shadow-lg shadow-brand/20">
              <span>💾 Save & Broadcast Live to Fleet</span>
            </button>
          </div>
        </form>
      </div>
    </section>

    <!-- TAB 4: CARGO CATEGORIES -->
    <section id="panel-cargos" class="tab-panel hidden space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 class="text-base font-bold text-textPrimary">Manage Freight Cargo Types</h2>
            <p class="text-xs text-textSecondary">These categories populate the dispatch wizard and driver waybill pickers in real-time.</p>
          </div>
          <form onsubmit="handleAddCargo(event)" class="flex gap-2">
            <input id="newCargoInput" type="text" placeholder="e.g. Rubber Sheets / Raw Cashew" required
                   class="bg-surfaceElevated border border-borderDark rounded-lg px-3.5 py-2 text-xs text-white placeholder-textSecondary focus:outline-none focus:border-brand w-64">
            <button type="submit" class="bg-brand text-midnight font-bold px-4 py-2 rounded-lg text-xs hover:bg-brandHover transition">
              + Add Cargo
            </button>
          </form>
        </div>
        <div id="cargosList" class="flex flex-wrap gap-2.5 pt-2">
          <div class="text-xs text-textSecondary py-4">Loading active cargo categories...</div>
        </div>
      </div>
    </section>

    <!-- TAB 5: KERALA HUBS -->
    <section id="panel-hubs" class="tab-panel hidden space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 class="text-base font-bold text-textPrimary">Logistics Hubs & Waypoint Terminals</h2>
            <p class="text-xs text-textSecondary">Geofenced loading yards across Kerala used for route distance computation.</p>
          </div>
          <button onclick="toggleAddHubModal(true)" class="bg-brand text-midnight font-bold px-4 py-2 rounded-lg text-xs hover:bg-brandHover transition">
            + New Hub Terminal
          </button>
        </div>
        <div id="hubsGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="text-xs text-textSecondary py-4">Loading logistics hubs...</div>
        </div>
      </div>
    </section>

    <!-- TAB 6: BROADCAST -->
    <section id="panel-broadcast" class="tab-panel hidden space-y-6">
      <div class="bg-surface border border-borderDark rounded-xl p-6">
        <div class="mb-6">
          <h2 class="text-base font-bold text-textPrimary">Driver Emergency & Safety Broadcast</h2>
          <p class="text-xs text-textSecondary">Instant banner push to all driver mobile cockpits (e.g., Ghat road landslides, monsoon flood warnings).</p>
        </div>

        <div id="activeBroadcastCard" class="mb-6 p-4 rounded-xl border border-borderDark bg-surfaceElevated flex items-start justify-between">
          <div>
            <div class="flex items-center space-x-2 mb-1">
              <span id="activeBroadcastBadge" class="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-brand/10 text-brand border border-brand/20">Active Broadcast</span>
              <span id="activeBroadcastTitle" class="text-sm font-bold text-textPrimary">No active broadcast</span>
            </div>
            <p id="activeBroadcastMsg" class="text-xs text-textSecondary">All clear. Normal traffic on NH-66 corridor.</p>
          </div>
          <button id="btnClearBroadcast" onclick="handleClearBroadcast()" class="text-xs text-statusDanger hover:underline ml-4 hidden font-semibold">
            Clear Notice
          </button>
        </div>

        <form onsubmit="handlePostBroadcast(event)" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-textSecondary mb-1">Notice Headline</label>
              <input id="broadcastTitle" type="text" placeholder="e.g. Heavy Rain Alert: Thamarassery Churam" required
                     class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand">
            </div>
            <div>
              <label class="block text-xs font-semibold text-textSecondary mb-1">Severity Level</label>
              <select id="broadcastSeverity" class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand">
                <option value="info">🔵 Information (Normal)</option>
                <option value="warning">🟡 Operational Delay Warning</option>
                <option value="critical">🔴 Critical Road Block / Danger</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-textSecondary mb-1">Detailed Driver Instructions</label>
            <textarea id="broadcastMessage" rows="3" placeholder="e.g. Caution: Heavy fog and slippery road on Wayanad Ghat stretch. Limit speed to 30 km/h." required
                      class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand"></textarea>
          </div>
          <div class="flex justify-end">
            <button type="submit" class="bg-brand text-midnight font-bold px-5 py-2.5 rounded-lg text-xs hover:bg-brandHover transition">
              📢 Dispatch Urgent Broadcast
            </button>
          </div>
        </form>
      </div>
    </section>

    <!-- TAB 7: APK AUTO-UPDATER -->
    <section id="panel-updates" class="tab-panel hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-surface border border-borderDark rounded-xl p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-textPrimary">In-App APK Channel</h2>
            <span id="updateMandatoryBadge" class="px-2.5 py-0.5 text-xs font-bold rounded bg-brand/10 text-brand border border-brand/30">Active Channel</span>
          </div>
          <div class="space-y-3 text-xs">
            <div class="flex justify-between py-2 border-b border-borderDark">
              <span class="text-textSecondary">Latest Version:</span>
              <span id="liveVersionName" class="font-bold text-white font-mono">--</span>
            </div>
            <div class="flex justify-between py-2 border-b border-borderDark">
              <span class="text-textSecondary">Build Code:</span>
              <span id="liveVersionCode" class="font-bold text-white font-mono">--</span>
            </div>
            <div class="flex justify-between py-2 border-b border-borderDark">
              <span class="text-textSecondary">Package Size:</span>
              <span id="liveApkSize" class="font-bold text-white font-mono">--</span>
            </div>
            <div class="flex justify-between py-2 border-b border-borderDark">
              <span class="text-textSecondary">Published Date:</span>
              <span id="livePublishedAt" class="font-bold text-white font-mono">--</span>
            </div>
            <div class="pt-2">
              <span class="text-textSecondary block mb-1">Release Highlights:</span>
              <ul id="liveReleaseNotes" class="list-disc list-inside text-textSecondary space-y-1"></ul>
            </div>
          </div>
        </div>

        <div class="bg-surface border border-borderDark rounded-xl p-6">
          <h2 class="text-base font-bold text-textPrimary mb-4">Publish Release Build</h2>
          <form id="publishUpdateForm" onsubmit="handlePublishUpdate(event)" class="space-y-4">
            <div class="grid grid-cols-2 gap-4 text-xs">
              <div>
                <label class="block font-semibold text-textSecondary mb-1">Version Name</label>
                <input id="inputVersionName" name="version_name" type="text" placeholder="2.3.0" required
                       class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand font-mono">
              </div>
              <div>
                <label class="block font-semibold text-textSecondary mb-1">Version Code</label>
                <input id="inputVersionCode" name="version_code" type="number" placeholder="3" required
                       class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand font-mono">
              </div>
            </div>
            <div class="text-xs">
              <label class="block font-semibold text-textSecondary mb-1">Release Notes (1 per line)</label>
              <textarea id="inputNotes" name="release_notes_raw" rows="3" placeholder="Real-time mobile hardware GPS tracking&#10;Zero-redeploy OTA config support" required
                        class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand"></textarea>
            </div>
            <div class="text-xs">
              <label class="block font-semibold text-textSecondary mb-1">Upload Android APK Binary (.apk)</label>
              <input type="file" name="apk_file" accept=".apk" required
                     class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-textSecondary focus:outline-none focus:border-brand file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-brand file:text-midnight hover:file:bg-brandHover">
            </div>
            <button id="btnPublishSubmit" type="submit" class="w-full bg-brand text-midnight font-bold py-2.5 rounded-lg text-xs hover:bg-brandHover transition">
              Deploy Release APK to Channel
            </button>
          </form>
        </div>
      </div>
    </section>

  </main>

  <!-- ADD HUB MODAL -->
  <div id="addHubModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-surface border border-borderDark rounded-xl max-w-md w-full p-6 shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-base font-bold text-white">Add Logistics Hub</h3>
        <button onclick="toggleAddHubModal(false)" class="text-textSecondary hover:text-white">&times;</button>
      </div>
      <form onsubmit="handleCreateHub(event)" class="space-y-3 text-xs">
        <div>
          <label class="block text-textSecondary mb-1">City / Region</label>
          <input id="hubCity" type="text" placeholder="e.g. Kottayam" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand">
        </div>
        <div>
          <label class="block text-textSecondary mb-1">Hub Code (3-4 Letters)</label>
          <input id="hubCode" type="text" placeholder="KTM" required maxlength="5" class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand uppercase font-mono">
        </div>
        <div>
          <label class="block text-textSecondary mb-1">Full Terminal Name</label>
          <input id="hubName" type="text" placeholder="Rubber Board Industrial Depot" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand">
        </div>
        <div class="grid grid-cols-2 gap-3 font-mono">
          <div>
            <label class="block text-textSecondary mb-1 font-sans">Latitude</label>
            <input id="hubLat" type="number" step="0.0001" placeholder="9.5915" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand">
          </div>
          <div>
            <label class="block text-textSecondary mb-1 font-sans">Longitude</label>
            <input id="hubLng" type="number" step="0.0001" placeholder="76.5221" required class="w-full bg-surfaceElevated border border-borderDark rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand">
          </div>
        </div>
        <div class="flex justify-end gap-2 pt-3">
          <button type="button" onclick="toggleAddHubModal(false)" class="px-4 py-2 bg-surfaceElevated border border-borderDark rounded-lg text-textSecondary hover:text-white">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-brand text-midnight font-bold rounded-lg hover:bg-brandHover">Save Hub</button>
        </div>
      </form>
    </div>
  </div>

  <!-- JAVASCRIPT LOGIC -->
  <script>
    let appConfig = null;
    let fleetMap = null;
    let truckMarkers = {};
    let ws = null;

    function showToast(msg, isError = false) {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      toast.className = `px-4 py-3 rounded-lg shadow-xl border text-xs font-semibold flex items-center space-x-2 toast-animate ${
        isError ? 'bg-statusDanger/20 border-statusDanger text-statusDanger' : 'bg-surfaceElevated border-borderStrong text-textPrimary'
      }`;
      toast.innerHTML = `<span>${isError ? '❌' : '✅'}</span><span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => { toast.remove(); }, 4000);
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('border-brand', 'text-brand', 'bg-surfaceElevated');
        b.classList.add('border-transparent', 'text-textSecondary');
      });
      document.getElementById(`panel-${tabId}`).classList.remove('hidden');
      const activeBtn = document.getElementById(`tab-${tabId}`);
      activeBtn.classList.remove('border-transparent', 'text-textSecondary');
      activeBtn.classList.add('border-brand', 'text-brand', 'bg-surfaceElevated');

      if (tabId === 'radar' && fleetMap) {
        setTimeout(() => { fleetMap.invalidateSize(); }, 200);
      }
    }

    // Initialize Leaflet Map
    function initMap() {
      if (fleetMap) return;
      fleetMap = L.map('fleetMap').setView([10.15, 76.45], 8);

      // CartoDB Dark Matter tiles for ultra-modern dark look
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(fleetMap);
    }

    function createTruckSvgIcon(heading = 0, status = 'available') {
      const color = status === 'breakdown' ? '#FF647C' : (status === 'on_trip' ? '#C6FF00' : '#38BDF8');
      const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36" style="transform: rotate(${heading}deg);">
          <circle cx="18" cy="18" r="16" fill="#11131B" stroke="${color}" stroke-width="2.5" />
          <path d="M18 7 L25 24 L18 20 L11 24 Z" fill="${color}" />
        </svg>
      `;
      return L.divIcon({
        className: 'truck-marker-icon',
        html: svg,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -18]
      });
    }

    // Connect WebSocket
    function connectTelemetryWebSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/v1/fleet`;

      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        document.getElementById('syncStatus').textContent = 'Connected';
        document.getElementById('syncDot').className = 'w-2 h-2 rounded-full bg-brand animate-pulse';
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          handleWebSocketMessage(msg);
        } catch (e) {
          console.error('WS parse error', e);
        }
      };

      ws.onclose = () => {
        document.getElementById('syncStatus').textContent = 'Reconnecting...';
        document.getElementById('syncDot').className = 'w-2 h-2 rounded-full bg-statusWarning animate-pulse';
        setTimeout(connectTelemetryWebSocket, 3000);
      };
    }

    function handleWebSocketMessage(msg) {
      if (msg.type === 'telemetry_update') {
        const { truck_plate, latitude, longitude, heading, speed_kmh } = msg;
        updateTruckOnMap(truck_plate, latitude, longitude, heading, speed_kmh, 'on_trip');
      } else if (msg.type === 'trip_created' || msg.type === 'trip_status_changed' || msg.type === 'trip_delivered') {
        loadTrips();
        loadKPIs();
      } else if (msg.type === 'config_updated') {
        loadData();
        showToast('App CMS Configuration updated OTA');
      }
    }

    function updateTruckOnMap(plate, lat, lng, heading = 0, speed = 0, status = 'available', driverName = 'Driver') {
      if (!fleetMap || !lat || !lng) return;

      const icon = createTruckSvgIcon(heading, status);

      if (truckMarkers[plate]) {
        truckMarkers[plate].setLatLng([lat, lng]);
        truckMarkers[plate].setIcon(icon);
      } else {
        const marker = L.marker([lat, lng], { icon: icon }).addTo(fleetMap);
        truckMarkers[plate] = marker;
      }

      truckMarkers[plate].bindPopup(`
        <div class="text-xs p-1 space-y-1">
          <div class="font-bold text-sm text-brand font-mono">${plate}</div>
          <div class="text-textSecondary">Driver: <strong class="text-white">${driverName}</strong></div>
          <div class="text-textSecondary">Status: <span class="capitalize text-white">${status.replace('_', ' ')}</span></div>
          <div class="text-textSecondary font-mono">Speed: ${speed ? speed.toFixed(1) : 0} km/h • Bearing: ${heading || 0}°</div>
          <div class="text-[10px] text-textMuted pt-1">Live Mobile GPS Telemetry Active</div>
        </div>
      `);
    }

    // Fetch and render trucks on map
    async function loadTrucks() {
      try {
        const res = await fetch('/api/v1/trucks');
        if (res.ok) {
          const trucks = await res.json();
          document.getElementById('statTrucks').textContent = trucks.length;
          trucks.forEach(t => {
            if (t.last_latitude && t.last_longitude) {
              updateTruckOnMap(t.plate, t.last_latitude, t.last_longitude, t.last_heading, t.last_speed_kmh, t.status, t.assigned_driver_id || 'Assigned');
            }
          });
        }
      } catch (err) {
        console.error('Failed loading trucks', err);
      }
    }

    // Fetch and render trips
    async function loadTrips() {
      try {
        const res = await fetch('/api/v1/trips');
        if (res.ok) {
          const trips = await res.json();
          const inTransit = trips.filter(t => t.status === 'running' || t.status === 'accepted').length;
          document.getElementById('statTrips').textContent = inTransit;

          const tbody = document.getElementById('tripsTableBody');
          tbody.innerHTML = '';
          if (trips.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="px-4 py-6 text-center text-textMuted">No trips found.</td></tr>';
            return;
          }

          trips.forEach(t => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-surfaceElevated/50 transition';

            let statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-brandSky/10 text-brandSky border border-brandSky/30">Waiting</span>';
            if (t.status === 'running') statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-brand/10 text-brand border border-brand/30 animate-pulse">Running</span>';
            if (t.status === 'delivered') statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-statusSuccess/10 text-statusSuccess border border-statusSuccess/30">Delivered</span>';
            if (t.status === 'breakdown') statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-statusDanger/10 text-statusDanger border border-statusDanger/30">Breakdown</span>';

            const pct = Math.min(100, Math.round((t.distance_done_km / (t.total_distance_km || 1)) * 100));

            tr.innerHTML = `
              <td class="px-4 py-3 font-mono font-bold text-white">${t.id}</td>
              <td class="px-4 py-3 font-semibold text-white">${t.origin_city} ➔ ${t.dest_city}</td>
              <td class="px-4 py-3 font-mono">${t.truck_plate}<div class="text-[10px] text-textMuted">${t.driver_id}</div></td>
              <td class="px-4 py-3">${t.cargo_title}<div class="text-[10px] text-textMuted">${t.weight_tons} Tons</div></td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-16 bg-surfaceElevated rounded-full h-1.5 overflow-hidden">
                    <div class="bg-brand h-1.5 rounded-full" style="width: ${pct}%"></div>
                  </div>
                  <span class="text-[10px] font-mono text-textMuted">${pct}%</span>
                </div>
              </td>
              <td class="px-4 py-3">${statusBadge}</td>
              <td class="px-4 py-3">
                ${t.pod ? `<a href="${t.pod.photo_url}" target="_blank" class="text-brand hover:underline text-[11px] font-semibold">View POD Photo</a>` : '<span class="text-textMuted">—</span>'}
              </td>
            `;
            tbody.appendChild(tr);
          });
        }
      } catch (err) {
        console.error('Failed loading trips', err);
      }
    }

    // Fetch and render Drivers count
    async function loadKPIs() {
      try {
        const dRes = await fetch('/api/v1/drivers');
        if (dRes.ok) {
          const drivers = await dRes.json();
          document.getElementById('statDrivers').textContent = drivers.length;
        }
      } catch (err) {}
    }

    // Load App CMS Configuration
    async function loadData() {
      try {
        const res = await fetch('/api/v1/config/app');
        if (res.ok) {
          appConfig = await res.json();
          
          // Populate Emergency Contacts
          if (appConfig.emergency_contacts) {
            document.getElementById('cmsHighwayPolice').value = appConfig.emergency_contacts.highway_police || '';
            document.getElementById('cmsOfficeDispatch').value = appConfig.emergency_contacts.office_dispatch || '';
            document.getElementById('cmsBreakdown').value = appConfig.emergency_contacts.breakdown_service || '';
          }

          // Populate Theme Palette
          if (appConfig.theme && appConfig.theme.default_palette) {
            const p = appConfig.theme.default_palette;
            if (p === 'sky_blue') document.getElementById('themeSky').checked = true;
            else if (p === 'claude_orange') document.getElementById('themeClaude').checked = true;
            else document.getElementById('themeLime').checked = true;
          }

          // Allowance
          if (appConfig.driver_allowance_default) {
            document.getElementById('cmsAllowance').value = appConfig.driver_allowance_default;
            document.getElementById('statAllowance').textContent = '₹' + appConfig.driver_allowance_default.toLocaleString();
          }

          // Cargos
          renderCargos(appConfig.cargos || []);

          // Hubs
          renderHubs(appConfig.hubs || []);

          // Notice Banner
          renderBroadcast(appConfig.notice_banner);
        }
      } catch (err) {
        console.error('Failed loading app config', err);
      }

      loadTrucks();
      loadTrips();
      loadKPIs();
    }

    function renderCargos(cargos) {
      const container = document.getElementById('cargosList');
      container.innerHTML = '';
      cargos.forEach(cargo => {
        const chip = document.createElement('div');
        chip.className = 'inline-flex items-center space-x-2 bg-surfaceElevated border border-borderDark px-3 py-1.5 rounded-lg text-xs font-semibold text-textPrimary hover:border-brand transition';
        chip.innerHTML = `
          <span>📦 ${cargo}</span>
          <button onclick="handleDeleteCargo('${cargo.replace(/'/g, "\\\\'")}')" class="text-textSecondary hover:text-statusDanger font-bold ml-1 text-sm">&times;</button>
        `;
        container.appendChild(chip);
      });
    }

    function renderHubs(hubs) {
      const container = document.getElementById('hubsGrid');
      container.innerHTML = '';
      hubs.forEach(h => {
        const card = document.createElement('div');
        card.className = 'bg-surfaceElevated border border-borderDark rounded-xl p-4 text-xs';
        card.innerHTML = `
          <div class="flex items-center justify-between mb-1">
            <span class="font-bold text-white text-sm">${h.city}</span>
            <span class="px-2 py-0.5 rounded bg-brand/10 text-brand font-mono font-bold">${h.code}</span>
          </div>
          <div class="text-textSecondary text-[11px] mb-2">${h.name}</div>
          <div class="text-textMuted font-mono text-[10px] flex justify-between items-center">
            <span>Lat: ${h.lat.toFixed(4)}, Lng: ${h.lng.toFixed(4)}</span>
            <button onclick="handleDeleteHub('${h.code}')" class="text-statusDanger hover:underline font-semibold font-sans">Delete</button>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function renderBroadcast(banner) {
      const card = document.getElementById('activeBroadcastCard');
      const badge = document.getElementById('activeBroadcastBadge');
      const title = document.getElementById('activeBroadcastTitle');
      const msg = document.getElementById('activeBroadcastMsg');
      const clearBtn = document.getElementById('btnClearBroadcast');

      if (banner && banner.active) {
        badge.textContent = banner.severity.toUpperCase();
        title.textContent = banner.title;
        msg.textContent = banner.message;
        clearBtn.classList.remove('hidden');
      } else {
        badge.textContent = 'NO ACTIVE NOTICE';
        title.textContent = 'Operational Alert Clear';
        msg.textContent = 'No weather or road alerts currently broadcast to field drivers.';
        clearBtn.classList.add('hidden');
      }
    }

    // Save CMS Form
    async function handleSaveCms(e) {
      e.preventDefault();
      const btn = document.getElementById('btnSaveCms');
      btn.disabled = true;

      const selectedPalette = document.querySelector('input[name="default_palette"]:checked')?.value || 'lime_green';

      const payload = {
        emergency_contacts: {
          highway_police: document.getElementById('cmsHighwayPolice').value.trim(),
          police: '112',
          ambulance: '108',
          office_dispatch: document.getElementById('cmsOfficeDispatch').value.trim(),
          breakdown_service: document.getElementById('cmsBreakdown').value.trim()
        },
        theme: {
          default_palette: selectedPalette,
          allowed_palettes: ['lime_green', 'sky_blue', 'claude_orange'],
          allow_driver_override: true
        },
        driver_allowance_default: parseInt(document.getElementById('cmsAllowance').value) || 1500
      };

      try {
        const res = await fetch('/api/v1/config/app', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          showToast('App CMS & Remote Config broadcasted live to all phones!');
          loadData();
        } else {
          showToast('Failed saving CMS configuration', true);
        }
      } catch (err) {
        showToast('Network error saving CMS', true);
      } finally {
        btn.disabled = false;
      }
    }

    async function handleAddCargo(e) {
      e.preventDefault();
      const name = document.getElementById('newCargoInput').value.trim();
      if (!name) return;
      const res = await fetch('/api/v1/config/cargo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      if (res.ok) {
        document.getElementById('newCargoInput').value = '';
        showToast(`Added cargo category "${name}"`);
        loadData();
      }
    }

    async function handleDeleteCargo(name) {
      if (!confirm(`Delete cargo type "${name}"?`)) return;
      const res = await fetch(`/api/v1/config/cargo/${encodeURIComponent(name)}`, { method: 'DELETE' });
      if (res.ok) {
        showToast(`Removed cargo category "${name}"`);
        loadData();
      }
    }

    async function handleCreateHub(e) {
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        toggleAddHubModal(false);
        showToast(`Created hub "${payload.city} (${payload.code})"`);
        loadData();
      }
    }

    async function handleDeleteHub(code) {
      if (!confirm(`Delete hub ${code}?`)) return;
      const res = await fetch(`/api/v1/config/hub/${encodeURIComponent(code)}`, { method: 'DELETE' });
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
        message: document.getElementById('broadcastMessage').value.trim()
      };
      const res = await fetch('/api/v1/config/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        showToast('Urgent broadcast transmitted to all driver apps!');
        loadData();
      }
    }

    async function handleClearBroadcast() {
      const res = await fetch('/api/v1/config/broadcast', { method: 'DELETE' });
      if (res.ok) {
        showToast('Active broadcast cleared');
        loadData();
      }
    }

    function toggleAddHubModal(show) {
      document.getElementById('addHubModal').classList.toggle('hidden', !show);
    }

    function refreshData() {
      loadData();
      showToast('Synced latest fleet coordinates & configuration');
    }

    async function loadUpdateInfo() {
      try {
        const res = await fetch('/api/v1/app/check-update?current_version_code=0');
        if (res.ok) {
          const u = await res.json();
          document.getElementById('liveVersionName').textContent = 'v' + u.latest_version_name;
          document.getElementById('liveVersionCode').textContent = u.latest_version_code;
          document.getElementById('liveApkSize').textContent = (u.apk_size_bytes / (1024*1024)).toFixed(1) + ' MB';
          document.getElementById('livePublishedAt').textContent = new Date(u.published_at).toLocaleString();
          
          const notesList = document.getElementById('liveReleaseNotes');
          notesList.innerHTML = '';
          (u.release_notes || []).forEach(n => {
            const li = document.createElement('li');
            li.textContent = n;
            notesList.appendChild(li);
          });
          document.getElementById('inputVersionCode').value = u.latest_version_code + 1;
        }
      } catch (err) {}
    }

    async function handlePublishUpdate(e) {
      e.preventDefault();
      const btn = document.getElementById('btnPublishSubmit');
      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = 'Uploading & Publishing Release...';

      const form = document.getElementById('publishUpdateForm');
      const formData = new FormData(form);

      try {
        const res = await fetch('/api/v1/app/publish-update', {
          method: 'POST',
          body: formData
        });
        if (res.ok) {
          showToast('Release APK published to driver in-app channel!');
          loadUpdateInfo();
          form.reset();
        } else {
          showToast('Failed to publish update', true);
        }
      } catch (err) {
        showToast('Network error publishing update', true);
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }

    // Startup
    window.addEventListener('DOMContentLoaded', () => {
      initMap();
      loadData();
      connectTelemetryWebSocket();
      loadUpdateInfo();
    });
  </script>
</body>
</html>
"""

@router.api_route("/admin", methods=["GET", "HEAD"], response_class=HTMLResponse)
@router.api_route("/admin/dashboard", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def admin_portal():
    """Enterprise Fleet Operations & Zero-Redeploy App CMS Web Portal."""
    return HTMLResponse(content=HTML_CONTENT, status_code=200)
