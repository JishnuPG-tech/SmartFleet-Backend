import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Admin Web Dashboard"])

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
  <title>SmartFleet — Enterprise Command Portal</title>
  <meta name="description" content="Enterprise Fleet Telemetry & Zero-Redeploy OTA CMS Command Portal for Kerala NH-66 Operations" />
  <meta name="theme-color" content="#000000" />

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Typography: Instrument Serif, Plus Jakarta Sans, Inter, JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />

  <!-- Leaflet Map CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            ff: {
              bg: '#000000',
              'bg-raised': '#0A0A0A',
              surface: '#111111',
              'surface-strong': '#171717',
              'surface-glass': 'rgba(10, 10, 10, 0.85)',
              border: 'rgba(255, 255, 255, 0.08)',
              'border-strong': 'rgba(255, 255, 255, 0.16)',
              text: '#F4EDE2',
              'text-secondary': '#A1A1AA',
              'text-muted': '#71717A',
              accent: '#D97757',
              'accent-hover': '#E58A69',
              'accent-deep': '#B85F3A',
              'accent-soft': 'rgba(217, 119, 87, 0.12)',
              signal: '#D97757',
              'signal-soft': 'rgba(217, 119, 87, 0.08)',
              success: '#34D399',
              warning: '#FBBF24',
              danger: '#F87171',
              sky: '#38BDF8',
            }
          },
          fontFamily: {
            serif: ['"Instrument Serif"', 'Georgia', 'serif'],
            display: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
            sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }
        }
      }
    }
  </script>

  <style>
    :root {
      color-scheme: dark;
      --ff-bg: #000000;
      --ff-bg-raised: #0A0A0A;
      --ff-surface: #111111;
      --ff-surface-strong: #171717;
      --ff-border: rgba(255, 255, 255, 0.08);
      --ff-border-strong: rgba(255, 255, 255, 0.16);
      --ff-text: #F4EDE2;
      --ff-text-secondary: #A1A1AA;
      --ff-text-muted: #71717A;
      --ff-accent: #D97757;
      --ff-accent-hover: #E58A69;
      --ff-accent-soft: rgba(217, 119, 87, 0.12);
    }
    * { border-color: rgba(255, 255, 255, 0.08); }
    body {
      background-color: #000000;
      color: #F4EDE2;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      overflow-x: hidden;
      min-height: 100vh;
    }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb { background: #27272A; border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: #3F3F46; }

    /* MilkGlass Card & Folder Styles from FileToLink */
    .milkglass-card {
      position: relative;
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(20, 18, 16, 0.45) 0%, rgba(10, 9, 8, 0.85) 100%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .milkglass-card:hover {
      transform: translateY(-3px) scale(1.015);
      border-color: rgba(217, 119, 87, 0.35);
      box-shadow: 0 16px 36px -12px rgba(217, 119, 87, 0.18);
    }

    #fleetMap {
      height: 520px;
      width: 100%;
      border-radius: 16px;
      z-index: 10;
      background: #09090b;
    }
    .leaflet-popup-content-wrapper {
      background: #0A0A0A !important;
      color: #F4EDE2 !important;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 12px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.85);
      padding: 4px;
    }
    .leaflet-popup-tip { background: #0A0A0A !important; }
    .custom-truck-marker { transition: transform 0.4s ease-out; }
    .toast-animate { animation: toastIn 0.35s cubic-bezier(0.22, 1, 0.36, 1) forwards; }
    @keyframes toastIn { from { transform: translateY(-16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  </style>
</head>
<body class="bg-ff-bg text-ff-text antialiased selection:bg-ff-accent-soft selection:text-ff-accent select-none min-h-screen flex flex-col justify-between">

  <!-- Ambient background glow (Exact from FileToLink CaseStudiesPage) -->
  <div class="fixed top-1/3 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full blur-[200px] pointer-events-none opacity-15" style="background: radial-gradient(circle, #D97757 0%, rgba(217,119,87,0) 70%);"></div>

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed top-6 right-6 z-50 space-y-2 pointer-events-none"></div>

  <!-- MAIN APP CONTAINER -->
  <div class="relative z-10 w-full min-h-screen flex flex-col p-6 sm:p-10 lg:p-14 text-left max-w-[1600px] mx-auto">

    <!-- TOP APEX BRANDING & TELEMETRY STRIP -->
    <header class="pb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-white/[0.08] w-full">
      <div class="flex items-center gap-3.5">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#D97757] to-[#B85F3A] flex items-center justify-center text-white shadow-lg shadow-[#D97757]/20">
          <!-- Truck Icon -->
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8h4.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h4"/></svg>
        </div>
        <div>
          <div class="flex items-center gap-2.5">
            <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-white font-sans">
              SmartFleet
            </h1>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              Admin Authority
            </span>
          </div>
          <p class="text-xs text-neutral-400 font-mono tracking-tight">
            NH-66 / NH-544 Freight Mesh • Enterprise 2.0
          </p>
        </div>
      </div>

      <!-- Live Stream Status & Actions -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-xs font-mono">
          <span id="wsIndicator" class="size-2 rounded-full bg-[#D97757] animate-pulse"></span>
          <span class="text-neutral-400">Telemetry: <strong id="wsStatus" class="text-white font-semibold">Connected</strong></span>
          <span class="text-neutral-600">•</span>
          <span class="text-neutral-400" id="pingLatency">&lt; 1.5ms</span>
        </div>

        <button onclick="refreshAllData()" class="px-3 py-1.5 rounded-full bg-white/[0.04] hover:bg-white/[0.08] text-xs font-medium text-neutral-300 hover:text-white border border-white/[0.06] transition-all cursor-pointer flex items-center gap-1.5">
          <svg id="refreshIcon" class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>
          <span>Refresh</span>
        </button>

        <a href="/docs" target="_blank" class="px-3 py-1.5 rounded-full bg-white/[0.04] hover:bg-white/[0.08] text-xs font-medium text-neutral-300 hover:text-white border border-white/[0.06] transition-all flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          <span>API Docs</span>
        </a>
      </div>
    </header>

    <!-- MAIN DYNAMIC CONTENT AREA -->
    <main id="mainContentArea" class="pt-8 flex-1 w-full">
      <!-- Rendered dynamically via JavaScript -->
    </main>

    <!-- FOOTER (Exact FileToLink format) -->
    <footer class="pt-12 pb-6 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-500 font-mono gap-4 w-full">
      <div>
        SmartFleet 2.0 • Operating on 16 vCPU Container • Asia/Kolkata (UTC +5:30)
      </div>
      <div class="flex items-center gap-4">
        <span>Dual-Field OTP Verification</span>
        <span>•</span>
        <span>Zero-Redeploy OTA CMS</span>
        <span>•</span>
        <span>WebSocket Stream</span>
      </div>
    </footer>

  </div>

  <!-- SCRIPT ENGINE -->
  <script>
    const state = {
      activeView: 'overview',
      trucks: [],
      drivers: [],
      trips: [],
      config: null,
      alerts: [],
      metrics: {
        activeTrucks: 4,
        inTransit: 3,
        avgSpeed: 52,
        wsConnected: true,
      },
      ws: null,
      leafletMap: null,
      markers: {},
    };

    const SYSTEM_MODULES = [
      {
        id: 'radar',
        title: 'Fleet Radar',
        caption: 'Live GPS • Kerala NH-66',
        color: '#D97757',
        shimmer: ['#D97757', '#8A4F3D', '#C4927C'],
        cards: ['NH-66 Coastal Corridor', 'NH-544 Inland Route', 'NH-766 Wayanad Pass', 'Real-Time Breadcrumbs'],
        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><circle cx="12" cy="12" r="2"/><path stroke-linecap="round" stroke-linejoin="round" d="M16.24 7.76a6 6 0 010 8.49m-8.48-.01a6 6 0 010-8.49m11.31-2.82a10 10 0 010 14.14m-14.14 0a10 10 0 010-14.14"/></svg>'
      },
      {
        id: 'roster',
        title: 'Fleet Roster',
        caption: '4 Trucks • 3 Drivers',
        color: '#CF8A64',
        shimmer: ['#CF8A64', '#6A5045', '#A9B9C4'],
        cards: ['Commercial Fleet', 'Verified Drivers', 'Status Matrix', 'Direct Calling'],
        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path stroke-linecap="round" stroke-linejoin="round" d="M23 21v-2a4 4 0 00-3-3.87"/><path stroke-linecap="round" stroke-linejoin="round" d="M16 3.13a4 4 0 010 7.75"/></svg>'
      },
      {
        id: 'trips',
        title: 'Trips & POD',
        caption: '3 Active Trips • Dual-Field OTP',
        color: '#38BDF8',
        shimmer: ['#38BDF8', '#0369A1', '#BAE6FD'],
        cards: ['Dispatched Freight', 'Waybill Manifests', 'Delivery OTP Verification', 'Active Waypoints'],
        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>'
      },
      {
        id: 'cms',
        title: 'Zero-Redeploy CMS',
        caption: 'Live App Config • WebSocket Sync',
        color: '#34D399',
        shimmer: ['#34D399', '#065F46', '#A7F3D0'],
        cards: ['Emergency Hotlines', 'Speed Thresholds', 'Bata Allowances', 'Safety Broadcasts'],
        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>'
      },
      {
        id: 'server',
        title: 'Server Engine',
        caption: 'Operational • 16 vCPU Container',
        color: '#A78BFA',
        shimmer: ['#A78BFA', '#5B21B6', '#DDD6FE'],
        cards: ['FastAPI AsyncIO Mesh', 'SQLite & AsyncPG Engine', 'Telemetry Ingestion', 'Static CDN Pipeline'],
        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>'
      },
      {
        id: 'analytics',
        title: 'Analytics',
        caption: 'Insights & Performance',
        color: '#FBBF24',
        shimmer: ['#FBBF24', '#B45309', '#FDE68A'],
        cards: ['Route Distribution', 'Dispatch Velocity', 'SLA 98.4% On-Time', 'Corridor Speeds'],
        icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
      }
    ];

    function showToast(msg, type = 'info') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      toast.className = 'toast-animate px-4 py-3 rounded-2xl bg-[#0A0A0A]/95 border border-white/[0.12] shadow-2xl backdrop-blur-xl flex items-center gap-3 text-xs font-medium text-white pointer-events-auto';
      
      let iconSvg = '';
      if (type === 'success') {
        iconSvg = '<svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="m9 12 2 2 4-4"/></svg>';
      } else if (type === 'error') {
        iconSvg = '<svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
      } else {
        iconSvg = '<svg class="w-4 h-4 text-[#D97757]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
      }

      toast.innerHTML = `${iconSvg}<span>${msg}</span>`;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && state.activeView !== 'overview') {
        navigateTo('overview');
      }
    });

    function navigateTo(viewId) {
      state.activeView = viewId;
      renderCurrentView();
    }

    function renderCurrentView() {
      const main = document.getElementById('mainContentArea');
      if (state.activeView === 'overview') {
        main.innerHTML = renderOverviewHtml();
      } else if (state.activeView === 'radar') {
        main.innerHTML = renderRadarHtml();
        initFleetMap();
      } else if (state.activeView === 'roster') {
        main.innerHTML = renderRosterHtml();
      } else if (state.activeView === 'trips') {
        main.innerHTML = renderTripsHtml();
      } else if (state.activeView === 'cms') {
        main.innerHTML = renderCmsHtml();
      } else if (state.activeView === 'server') {
        main.innerHTML = renderServerHtml();
      } else if (state.activeView === 'analytics') {
        main.innerHTML = renderAnalyticsHtml();
      }
    }

    function renderOverviewHtml() {
      return `
        <div class="flex flex-col gap-8 animate-fade-in">
          
          <!-- Top KPI Strip -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.08] flex flex-col gap-1">
              <span class="text-[10px] font-mono uppercase text-neutral-500 tracking-wider">Active Fleet</span>
              <div class="flex items-baseline gap-2">
                <span class="text-2xl font-bold font-mono text-white">${state.trucks.length || 4}</span>
                <span class="text-xs text-emerald-400 font-mono">100% Online</span>
              </div>
            </div>

            <div class="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.08] flex flex-col gap-1">
              <span class="text-[10px] font-mono uppercase text-neutral-500 tracking-wider">In-Transit Freight</span>
              <div class="flex items-baseline gap-2">
                <span class="text-2xl font-bold font-mono text-white">${state.trips.filter(t => t.status === 'IN_TRANSIT').length || 3}</span>
                <span class="text-xs text-[#38BDF8] font-mono">NH Corridors</span>
              </div>
            </div>

            <div class="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.08] flex flex-col gap-1">
              <span class="text-[10px] font-mono uppercase text-neutral-500 tracking-wider">Corridor Avg Speed</span>
              <div class="flex items-baseline gap-2">
                <span class="text-2xl font-bold font-mono text-white">52</span>
                <span class="text-xs text-neutral-400 font-mono">km/h</span>
              </div>
            </div>

            <div class="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.08] flex flex-col gap-1">
              <span class="text-[10px] font-mono uppercase text-neutral-500 tracking-wider">Delayed Alerts</span>
              <div class="flex items-baseline gap-2">
                <span class="text-2xl font-bold font-mono text-white">${state.alerts.length || 0}</span>
                <span class="text-xs text-emerald-400 font-mono">Clear Flow</span>
              </div>
            </div>
          </div>

          <!-- Section Label -->
          <div class="flex items-center justify-between pb-2 border-b border-white/[0.06]">
            <div class="flex items-center gap-2">
              <span class="size-2 rounded-full bg-[#D97757]"></span>
              <h2 class="text-xs font-semibold uppercase tracking-wider text-neutral-300 font-mono">
                System Control Modules
              </h2>
            </div>
            <span class="text-xs text-neutral-500 font-mono">6 Operational Folders</span>
          </div>

          <!-- Linear Row-wise Folders (Aligned left to right) -->
          <div class="flex flex-wrap items-start justify-start gap-6 sm:gap-7 w-full py-1">
            ${SYSTEM_MODULES.map(m => `
              <div onclick="navigateTo('${m.id}')" class="milkglass-card w-[220px] sm:w-[240px] flex-shrink-0 cursor-pointer p-5 flex flex-col justify-between gap-6 group">
                <div class="flex items-start justify-between">
                  <div class="p-2.5 rounded-xl bg-white/[0.04] text-[${m.color}] border border-white/[0.06] group-hover:border-[${m.color}]/40 transition-colors">
                    ${m.icon}
                  </div>
                  <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.04] text-neutral-400 border border-white/[0.06]">
                    Module
                  </span>
                </div>

                <div class="flex flex-col gap-1.5 py-1">
                  <div class="h-1.5 w-full rounded-full bg-white/[0.06] overflow-hidden">
                    <div class="h-full rounded-full" style="width: 80%; background: linear-gradient(90deg, ${m.shimmer[0]}, ${m.shimmer[2]})"></div>
                  </div>
                  <span class="text-[11px] font-mono text-neutral-400 truncate">${m.cards[0]}</span>
                  <span class="text-[10px] font-mono text-neutral-500 truncate">${m.cards[1]}</span>
                </div>

                <div class="flex flex-col gap-0.5 pt-2 border-t border-white/[0.04]">
                  <h3 class="text-sm font-semibold text-white tracking-tight group-hover:text-[${m.color}] transition-colors">
                    ${m.title}
                  </h3>
                  <span class="text-[11px] font-mono text-neutral-400">
                    ${m.caption}
                  </span>
                </div>
              </div>
            `).join('')}
          </div>

        </div>
      `;
    }

    function renderRadarHtml() {
      return `
        <div class="flex flex-col gap-6 animate-fade-in">
          <div class="flex items-center justify-between pb-4 border-b border-white/[0.08] w-full">
            <button onclick="navigateTo('overview')" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-neutral-200 text-xs font-medium border border-white/[0.08] transition-all cursor-pointer group">
              <svg class="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
              <span>Back to Overview</span>
            </button>

            <div class="flex items-center gap-2">
              <span class="size-2 rounded-full bg-[#D97757]"></span>
              <span class="text-sm font-semibold tracking-tight text-white">Fleet Radar</span>
              <span class="text-xs text-neutral-500 font-mono">(Kerala NH-66 Corridor)</span>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 w-full">
            <div class="lg:col-span-3 rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-3 flex flex-col gap-3 shadow-2xl relative">
              <div id="fleetMap"></div>
              <div class="flex items-center justify-between px-2 text-xs font-mono text-neutral-400">
                <div class="flex items-center gap-3">
                  <span class="flex items-center gap-1.5"><span class="size-2 rounded-full bg-[#D97757]"></span> NH-66 (Calicut-Kochi)</span>
                  <span class="flex items-center gap-1.5"><span class="size-2 rounded-full bg-[#38BDF8]"></span> NH-544 (Kochi-Palakkad)</span>
                  <span class="flex items-center gap-1.5"><span class="size-2 rounded-full bg-[#34D399]"></span> NH-766 (Calicut-Wayanad)</span>
                </div>
                <span>Bearing & Speed Stream Active</span>
              </div>
            </div>

            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-5 flex flex-col gap-4 shadow-2xl">
              <div class="flex items-center justify-between pb-2 border-b border-white/[0.06]">
                <span class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Live GPS Stream</span>
                <span class="text-[10px] font-mono text-emerald-400">5s Pings</span>
              </div>

              <div id="telemetryPingsList" class="flex flex-col gap-2.5 overflow-y-auto max-h-[460px] pr-1">
                ${state.trucks.map(t => `
                  <div class="p-3 rounded-xl bg-white/[0.02] border border-white/[0.06] flex flex-col gap-1.5">
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-mono font-bold text-white">${t.plate_number}</span>
                      <span class="text-[10px] font-mono px-2 py-0.5 rounded-full ${t.status === 'IN_TRANSIT' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-white/[0.04] text-neutral-400 border border-white/[0.06]'}">
                        ${t.status}
                      </span>
                    </div>
                    <div class="flex items-center justify-between text-[11px] font-mono text-neutral-400">
                      <span>Speed: <strong class="text-[#D97757]">${t.current_speed || 48} km/h</strong></span>
                      <span>Heading: ${t.heading || 180}°</span>
                    </div>
                    <div class="text-[10px] font-mono text-neutral-500 truncate">
                      Loc: ${t.current_latitude?.toFixed(4) || 10.8505}, ${t.current_longitude?.toFixed(4) || 76.2711}
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
          </div>
        </div>
      `;
    }

    function initFleetMap() {
      if (state.leafletMap) {
        state.leafletMap.remove();
        state.leafletMap = null;
      }

      const mapElement = document.getElementById('fleetMap');
      if (!mapElement) return;

      const map = L.map('fleetMap', { zoomControl: false }).setView([10.5276, 76.2144], 8);
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CartoDB &copy; OpenStreetMap',
        maxZoom: 19
      }).addTo(map);

      state.leafletMap = map;

      const nh66Points = [
        [11.2588, 75.7804],
        [10.8505, 75.9224],
        [10.1915, 76.1661],
        [9.9816, 76.2999],
      ];
      L.polyline(nh66Points, { color: '#D97757', weight: 3, opacity: 0.75, dashArray: '6, 8' }).addTo(map);

      const nh544Points = [
        [9.9816, 76.2999],
        [10.5276, 76.2144],
        [10.7867, 76.6548],
      ];
      L.polyline(nh544Points, { color: '#38BDF8', weight: 3, opacity: 0.75, dashArray: '6, 8' }).addTo(map);

      state.trucks.forEach(t => {
        const lat = t.current_latitude || 10.5276;
        const lng = t.current_longitude || 76.2144;
        
        const iconHtml = `
          <div class="relative flex items-center justify-center">
            <div class="size-8 rounded-full bg-[#0A0A0A] border border-[#D97757] flex items-center justify-center text-[#D97757] shadow-xl shadow-[#D97757]/30">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8h4.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h4"/></svg>
            </div>
            <div class="absolute -top-1 -right-1 size-2.5 rounded-full bg-emerald-400 animate-ping"></div>
          </div>
        `;

        const customIcon = L.divIcon({
          html: iconHtml,
          className: 'custom-truck-marker',
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        });

        const marker = L.marker([lat, lng], { icon: customIcon }).addTo(map);
        marker.bindPopup(`
          <div class="p-2 flex flex-col gap-1 text-xs font-mono text-left">
            <span class="text-sm font-bold text-white">${t.plate_number}</span>
            <span class="text-neutral-400">Model: ${t.model || 'Commercial Carrier'}</span>
            <span class="text-[#D97757]">Speed: ${t.current_speed || 50} km/h</span>
            <span class="text-neutral-400">Status: ${t.status}</span>
          </div>
        `);
      });
    }

    function renderRosterHtml() {
      return `
        <div class="flex flex-col gap-6 animate-fade-in">
          <div class="flex items-center justify-between pb-4 border-b border-white/[0.08] w-full">
            <button onclick="navigateTo('overview')" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-neutral-200 text-xs font-medium border border-white/[0.08] transition-all cursor-pointer group">
              <svg class="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
              <span>Back to Overview</span>
            </button>

            <div class="flex items-center gap-2">
              <span class="size-2 rounded-full bg-[#CF8A64]"></span>
              <span class="text-sm font-semibold tracking-tight text-white">Fleet Roster</span>
              <span class="text-xs text-neutral-500 font-mono">(${state.trucks.length} Trucks • ${state.drivers.length} Drivers)</span>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
            
            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-5 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center justify-between pb-3 border-b border-white/[0.06]">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-[#CF8A64]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8h4.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h4"/></svg>
                  <h3 class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Commercial Trucks</h3>
                </div>
                <span class="text-xs font-mono text-neutral-500">${state.trucks.length} Registered</span>
              </div>

              <div class="flex flex-col gap-2.5">
                ${state.trucks.map(t => `
                  <div class="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] flex items-center justify-between">
                    <div class="flex flex-col gap-0.5">
                      <span class="text-sm font-bold font-mono text-white">${t.plate_number}</span>
                      <span class="text-xs text-neutral-400 font-sans">${t.model || 'Heavy Hauler'} • Capacity: ${t.capacity_tons || 16}T</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-mono px-2.5 py-1 rounded-full ${t.status === 'IN_TRANSIT' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-white/[0.04] text-neutral-400 border border-white/[0.06]'}">
                        ${t.status}
                      </span>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>

            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-5 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center justify-between pb-3 border-b border-white/[0.06]">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-[#CF8A64]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path stroke-linecap="round" stroke-linejoin="round" d="M23 21v-2a4 4 0 00-3-3.87"/><path stroke-linecap="round" stroke-linejoin="round" d="M16 3.13a4 4 0 010 7.75"/></svg>
                  <h3 class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Verified Drivers</h3>
                </div>
                <span class="text-xs font-mono text-neutral-500">${state.drivers.length} Drivers</span>
              </div>

              <div class="flex flex-col gap-2.5">
                ${state.drivers.map(d => `
                  <div class="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] flex items-center justify-between">
                    <div class="flex flex-col gap-0.5">
                      <span class="text-sm font-semibold text-white">${d.full_name}</span>
                      <span class="text-xs text-neutral-400 font-mono">${d.phone} • License: ${d.license_number || 'KL-2024-COMM'}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-mono px-2.5 py-1 rounded-full ${d.is_available ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-[#D97757]/10 text-[#D97757] border border-[#D97757]/20'}">
                        ${d.is_available ? 'Available' : 'Assigned'}
                      </span>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>

          </div>
        </div>
      `;
    }

    function renderTripsHtml() {
      return `
        <div class="flex flex-col gap-6 animate-fade-in">
          <div class="flex items-center justify-between pb-4 border-b border-white/[0.08] w-full">
            <button onclick="navigateTo('overview')" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-neutral-200 text-xs font-medium border border-white/[0.08] transition-all cursor-pointer group">
              <svg class="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
              <span>Back to Overview</span>
            </button>

            <div class="flex items-center gap-3">
              <button onclick="openOtpModal()" class="px-3.5 py-1.5 rounded-full bg-[#38BDF8]/10 hover:bg-[#38BDF8]/20 text-[#38BDF8] border border-[#38BDF8]/30 text-xs font-mono font-medium transition-all flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="m9 12 2 2 4-4"/></svg>
                <span>Verify POD OTP</span>
              </button>
            </div>
          </div>

          <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-6 flex flex-col gap-4 shadow-xl">
            <div class="flex items-center justify-between pb-3 border-b border-white/[0.06]">
              <span class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Active Waybills &amp; Consignments</span>
              <span class="text-xs font-mono text-neutral-500">${state.trips.length} Total</span>
            </div>

            <div class="flex flex-col gap-3">
              ${state.trips.map(trip => `
                <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-bold font-mono text-white">Trip #${trip.id}</span>
                      <span class="text-[10px] font-mono px-2 py-0.5 rounded-full ${trip.status === 'DELIVERED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-[#38BDF8]/10 text-[#38BDF8] border border-[#38BDF8]/20'}">
                        ${trip.status}
                      </span>
                    </div>
                    <span class="text-xs text-neutral-300 font-medium">
                      ${trip.origin || 'Calicut NH-66 Depot'} &rarr; ${trip.destination || 'Kochi Port Hub'}
                    </span>
                    <span class="text-[11px] font-mono text-neutral-500">
                      Cargo: ${trip.cargo_description || 'Electronics & Perishables'} (${trip.cargo_weight_tons || 12}T)
                    </span>
                  </div>

                  <div class="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
                    <button onclick="openOtpModal('${trip.id}')" class="px-3 py-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-xs font-mono text-white border border-white/[0.08] transition-all">
                      Verify Delivery
                    </button>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      `;
    }

    function renderCmsHtml() {
      const cfg = state.config || {
        emergency_hotline: '+91 484 2900 100',
        breakdown_sos_phone: '+91 98470 99999',
        highway_speed_limit_kmh: 65,
        driver_daily_bata_inr: 850,
        cargo_categories: ['Electronics', 'Perishables', 'FMCG', 'Industrial Parts', 'Spices & Tea'],
        safety_banner: 'Monsoon Advisory: Maintain safe braking distance on NH-66 and NH-766 ghats.'
      };

      return `
        <div class="flex flex-col gap-6 animate-fade-in">
          <div class="flex items-center justify-between pb-4 border-b border-white/[0.08] w-full">
            <button onclick="navigateTo('overview')" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-neutral-200 text-xs font-medium border border-white/[0.08] transition-all cursor-pointer group">
              <svg class="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
              <span>Back to Overview</span>
            </button>

            <div class="flex items-center gap-2">
              <span class="size-2 rounded-full bg-[#34D399]"></span>
              <span class="text-sm font-semibold tracking-tight text-white">Zero-Redeploy App CMS</span>
              <span class="text-xs text-neutral-500 font-mono">(Instant WebSocket Push)</span>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full">
            <div class="lg:col-span-2 rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-6 flex flex-col gap-5 shadow-xl">
              <div class="pb-2 border-b border-white/[0.06]">
                <h3 class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Fleet App Dynamic Settings</h3>
                <p class="text-xs text-neutral-400 mt-1 font-sans">
                  Updates save directly to the database and broadcast instantly to mobile APKs over WebSockets without rebuild or redeploy.
                </p>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div class="flex flex-col gap-1.5 text-left">
                  <label class="text-neutral-300 font-mono font-medium">Emergency Hotline</label>
                  <input id="cmsHotline" type="text" value="${cfg.emergency_hotline}" class="w-full h-10 px-3.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white font-mono outline-none focus:border-[#34D399] transition-colors" />
                </div>

                <div class="flex flex-col gap-1.5 text-left">
                  <label class="text-neutral-300 font-mono font-medium">Breakdown SOS Phone</label>
                  <input id="cmsSosPhone" type="text" value="${cfg.breakdown_sos_phone}" class="w-full h-10 px-3.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white font-mono outline-none focus:border-[#34D399] transition-colors" />
                </div>

                <div class="flex flex-col gap-1.5 text-left">
                  <label class="text-neutral-300 font-mono font-medium">Highway Speed Threshold (km/h)</label>
                  <input id="cmsSpeedLimit" type="number" value="${cfg.highway_speed_limit_kmh}" class="w-full h-10 px-3.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white font-mono outline-none focus:border-[#34D399] transition-colors" />
                </div>

                <div class="flex flex-col gap-1.5 text-left">
                  <label class="text-neutral-300 font-mono font-medium">Driver Daily Bata Allowance (INR)</label>
                  <input id="cmsBataRate" type="number" value="${cfg.driver_daily_bata_inr}" class="w-full h-10 px-3.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white font-mono outline-none focus:border-[#34D399] transition-colors" />
                </div>
              </div>

              <div class="flex flex-col gap-1.5 text-left text-xs">
                <label class="text-neutral-300 font-mono font-medium">Safety Banner Announcement</label>
                <textarea id="cmsBanner" rows="2" class="w-full p-3 rounded-xl bg-white/[0.04] border border-white/[0.1] text-white font-sans outline-none focus:border-[#34D399] transition-colors">${cfg.safety_banner}</textarea>
              </div>

              <div class="pt-2">
                <button onclick="saveAndBroadcastCms()" class="w-full h-11 rounded-xl bg-gradient-to-r from-[#34D399] to-[#059669] hover:opacity-95 text-midnight font-bold text-xs uppercase tracking-wider font-mono transition-all shadow-lg shadow-[#34D399]/20 cursor-pointer flex items-center justify-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="2"/><path stroke-linecap="round" stroke-linejoin="round" d="M16.24 7.76a6 6 0 010 8.49m-8.48-.01a6 6 0 010-8.49m11.31-2.82a10 10 0 010 14.14m-14.14 0a10 10 0 010-14.14"/></svg>
                  <span>Broadcast Updates to Fleet APKs</span>
                </button>
              </div>
            </div>

            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-6 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center justify-between pb-2 border-b border-white/[0.06]">
                <span class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Config Payload</span>
                <span class="text-[10px] font-mono text-emerald-400">v2.0 Sync</span>
              </div>
              <pre id="cmsJsonPreview" class="p-3.5 rounded-xl bg-black border border-white/[0.06] text-[11px] font-mono text-neutral-400 overflow-x-auto max-h-[300px]">${JSON.stringify(cfg, null, 2)}</pre>
            </div>
          </div>
        </div>
      `;
    }

    function renderServerHtml() {
      return `
        <div class="flex flex-col gap-6 animate-fade-in">
          <div class="flex items-center justify-between pb-4 border-b border-white/[0.08] w-full">
            <button onclick="navigateTo('overview')" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-neutral-200 text-xs font-medium border border-white/[0.08] transition-all cursor-pointer group">
              <svg class="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
              <span>Back to Overview</span>
            </button>

            <div class="flex items-center gap-2">
              <span class="size-2 rounded-full bg-[#A78BFA]"></span>
              <span class="text-sm font-semibold tracking-tight text-white">Server Engine</span>
              <span class="text-xs text-neutral-500 font-mono">(16 vCPU Container • Port 8000)</span>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 w-full">
            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-5 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center gap-2 pb-2 border-b border-white/[0.06]">
                <svg class="w-4 h-4 text-[#A78BFA]" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path stroke-linecap="round" stroke-linejoin="round" d="M9 1v3m6-3v3m-6 17v3m6-3v3M1 9h3m-3 6h3m17-6h3m-3 6h3"/></svg>
                <h3 class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Host Compute</h3>
              </div>
              <div class="flex flex-col gap-2.5 text-xs font-mono">
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">Capacity</span>
                  <span class="text-white font-medium">16 vCPU Container</span>
                </div>
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">Memory</span>
                  <span class="text-white font-medium">60 GB RAM</span>
                </div>
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">Platform</span>
                  <span class="text-white font-medium">Debian 12 Bookworm</span>
                </div>
                <div class="flex justify-between py-1">
                  <span class="text-neutral-400">Timezone</span>
                  <span class="text-emerald-400 font-medium">Asia/Kolkata (+5:30)</span>
                </div>
              </div>
            </div>

            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-5 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center gap-2 pb-2 border-b border-white/[0.06]">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                <h3 class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Microservice Mesh</h3>
              </div>
              <div class="flex flex-col gap-2.5 text-xs font-mono">
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">FastAPI Gateway</span>
                  <span class="text-emerald-400 font-medium">Port 8000 • Active</span>
                </div>
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">Telemetry WebSocket</span>
                  <span class="text-[#D97757] font-medium">/ws/v1/fleet • Open</span>
                </div>
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">Database</span>
                  <span class="text-white font-medium">SQLite AsyncIO Mesh</span>
                </div>
                <div class="flex justify-between py-1">
                  <span class="text-neutral-400">APK Distribution</span>
                  <span class="text-[#38BDF8] font-medium">/uploads/apks/</span>
                </div>
              </div>
            </div>

            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-5 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center gap-2 pb-2 border-b border-white/[0.06]">
                <svg class="w-4 h-4 text-[#FBBF24]" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="m9 12 2 2 4-4"/></svg>
                <h3 class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Health &amp; Uptime</h3>
              </div>
              <div class="flex flex-col gap-2.5 text-xs font-mono">
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">System Status</span>
                  <span class="text-emerald-400 font-medium">100% Operational</span>
                </div>
                <div class="flex justify-between py-1 border-b border-white/[0.04]">
                  <span class="text-neutral-400">Telemetry Lag</span>
                  <span class="text-white font-medium">&lt; 1.5ms</span>
                </div>
                <div class="flex justify-between py-1">
                  <span class="text-neutral-400">Dual Engine POD</span>
                  <span class="text-emerald-400 font-medium">Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    function renderAnalyticsHtml() {
      return `
        <div class="flex flex-col gap-6 animate-fade-in">
          <div class="flex items-center justify-between pb-4 border-b border-white/[0.08] w-full">
            <button onclick="navigateTo('overview')" class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/[0.06] hover:bg-white/[0.12] text-neutral-200 text-xs font-medium border border-white/[0.08] transition-all cursor-pointer group">
              <svg class="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
              <span>Back to Overview</span>
            </button>

            <div class="flex items-center gap-2">
              <span class="size-2 rounded-full bg-[#FBBF24]"></span>
              <span class="text-sm font-semibold tracking-tight text-white">Analytics &amp; Performance</span>
              <span class="text-xs text-neutral-500 font-mono">(Kerala Freight Insights)</span>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
            
            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-6 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center justify-between pb-3 border-b border-white/[0.06]">
                <span class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Corridor Route Distribution</span>
                <span class="text-[11px] font-mono text-neutral-500">Active Dispatches</span>
              </div>

              <div class="flex flex-col sm:flex-row items-center justify-around gap-6 py-4">
                <div class="relative w-36 h-36 flex items-center justify-center flex-shrink-0">
                  <svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="38" fill="transparent" stroke="#D97757" stroke-width="11" stroke-dasharray="138.5 239" stroke-dashoffset="0" stroke-linecap="round" />
                    <circle cx="50" cy="50" r="38" fill="transparent" stroke="#38BDF8" stroke-width="11" stroke-dasharray="66.8 239" stroke-dashoffset="-138.5" stroke-linecap="round" />
                    <circle cx="50" cy="50" r="38" fill="transparent" stroke="#34D399" stroke-width="11" stroke-dasharray="33.4 239" stroke-dashoffset="-205.3" stroke-linecap="round" />
                  </svg>
                  <div class="absolute inset-0 flex flex-col items-center justify-center text-center font-mono">
                    <span class="text-base font-bold text-white">100%</span>
                    <span class="text-[9px] uppercase text-neutral-400">Routed</span>
                  </div>
                </div>

                <div class="flex flex-col gap-3 text-xs w-full sm:w-auto font-mono">
                  <div class="flex items-center justify-between gap-6">
                    <div class="flex items-center gap-2">
                      <span class="size-2.5 rounded-full bg-[#D97757]"></span>
                      <span class="text-neutral-300">NH-66 Coastal</span>
                    </div>
                    <span class="text-white font-bold">58%</span>
                  </div>
                  <div class="flex items-center justify-between gap-6">
                    <div class="flex items-center gap-2">
                      <span class="size-2.5 rounded-full bg-[#38BDF8]"></span>
                      <span class="text-neutral-300">NH-544 Inland</span>
                    </div>
                    <span class="text-white font-bold">28%</span>
                  </div>
                  <div class="flex items-center justify-between gap-6">
                    <div class="flex items-center gap-2">
                      <span class="size-2.5 rounded-full bg-[#34D399]"></span>
                      <span class="text-neutral-300">NH-766 Ghats</span>
                    </div>
                    <span class="text-white font-bold">14%</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-2xl bg-[#0A0A0A] border border-white/[0.08] p-6 flex flex-col gap-4 shadow-xl">
              <div class="flex items-center justify-between pb-3 border-b border-white/[0.06]">
                <span class="text-xs font-semibold uppercase tracking-wider text-neutral-200 font-mono">Delivery SLA &amp; Compliance</span>
                <span class="text-[11px] font-mono text-emerald-400">98.4% On-Time</span>
              </div>
              <div class="flex flex-col gap-4 py-2 font-mono text-xs">
                <div>
                  <div class="flex justify-between text-neutral-300 mb-1.5">
                    <span>On-Time Arrival Rate</span>
                    <span class="text-white font-bold">98.4%</span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-white/[0.06] overflow-hidden">
                    <div class="h-full rounded-full bg-emerald-400" style="width: 98.4%"></div>
                  </div>
                </div>

                <div>
                  <div class="flex justify-between text-neutral-300 mb-1.5">
                    <span>Driver Check-in Rate</span>
                    <span class="text-white font-bold">100%</span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-white/[0.06] overflow-hidden">
                    <div class="h-full rounded-full bg-[#D97757]" style="width: 100%"></div>
                  </div>
                </div>

                <div>
                  <div class="flex justify-between text-neutral-300 mb-1.5">
                    <span>Safe Corridor Adherence</span>
                    <span class="text-white font-bold">96.8%</span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-white/[0.06] overflow-hidden">
                    <div class="h-full rounded-full bg-[#38BDF8]" style="width: 96.8%"></div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      `;
    }

    async function refreshAllData() {
      const icon = document.getElementById('refreshIcon');
      if (icon) icon.classList.add('animate-spin');

      try {
        const [trucksRes, driversRes, tripsRes, configRes, alertsRes] = await Promise.all([
          fetch('/api/v1/trucks'),
          fetch('/api/v1/drivers'),
          fetch('/api/v1/trips'),
          fetch('/api/v1/config/app'),
          fetch('/api/v1/alerts')
        ]);

        if (trucksRes.ok) state.trucks = await trucksRes.json();
        if (driversRes.ok) state.drivers = await driversRes.json();
        if (tripsRes.ok) state.trips = await tripsRes.json();
        if (configRes.ok) state.config = await configRes.json();
        if (alertsRes.ok) state.alerts = await alertsRes.json();

        renderCurrentView();
        showToast('Fleet data refreshed from server', 'success');
      } catch (err) {
        console.error('Refresh error:', err);
        showToast('Sync error with backend', 'error');
      } finally {
        if (icon) icon.classList.remove('animate-spin');
      }
    }

    async function saveAndBroadcastCms() {
      const payload = {
        emergency_hotline: document.getElementById('cmsHotline').value.trim(),
        breakdown_sos_phone: document.getElementById('cmsSosPhone').value.trim(),
        highway_speed_limit_kmh: parseInt(document.getElementById('cmsSpeedLimit').value) || 65,
        driver_daily_bata_inr: parseFloat(document.getElementById('cmsBataRate').value) || 850,
        cargo_categories: ['Electronics', 'Perishables', 'FMCG', 'Industrial Parts', 'Spices & Tea'],
        safety_banner: document.getElementById('cmsBanner').value.trim(),
        active_theme_default: 'lime_green'
      };

      try {
        const res = await fetch('/api/v1/config/app', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          state.config = await res.json();
          document.getElementById('cmsJsonPreview').innerText = JSON.stringify(state.config, null, 2);
          showToast('OTA config broadcasted to driver APKs over WebSockets!', 'success');
        } else {
          showToast('Failed to update config', 'error');
        }
      } catch (e) {
        showToast('Network error while saving config', 'error');
      }
    }

    function openOtpModal(defaultTripId = '') {
      const tripId = defaultTripId || (state.trips[0]?.id || 1);
      const code = prompt(`Enter 4-digit Customer Delivery OTP for Trip #${tripId}:`, '1234');
      if (!code) return;

      fetch(`/api/v1/pod/${tripId}/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ otp: code.trim(), otp_code: code.trim() })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success' || data.verified) {
          showToast(`Delivery confirmed for Trip #${tripId}! POD verified.`, 'success');
          refreshAllData();
        } else {
          showToast(`OTP Verification: ${data.detail || data.message || 'Invalid code'}`, 'error');
        }
      })
      .catch(() => showToast('POD OTP verification error', 'error'));
    }

    function initWebSocket() {
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${proto}//${window.location.host}/ws/v1/fleet`;

      try {
        const ws = new WebSocket(wsUrl);
        ws.onopen = () => {
          const ind = document.getElementById('wsIndicator');
          const stat = document.getElementById('wsStatus');
          if (ind) ind.className = 'size-2 rounded-full bg-emerald-400 animate-pulse';
          if (stat) {
            stat.innerText = 'Connected';
            stat.className = 'text-emerald-400 font-semibold';
          }
        };
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'telemetry') {
              const truck = state.trucks.find(t => t.plate_number === data.truck_id);
              if (truck) {
                truck.current_latitude = data.latitude;
                truck.current_longitude = data.longitude;
                truck.current_speed = data.speed_kmh;
                truck.heading = data.heading;
              }
            } else if (data.type === 'app_config_update') {
              showToast('OTA Broadcast received from fleet!', 'info');
            }
          } catch (e) {}
        };
        ws.onclose = () => {
          const ind = document.getElementById('wsIndicator');
          const stat = document.getElementById('wsStatus');
          if (ind) ind.className = 'size-2 rounded-full bg-[#D97757]';
          if (stat) {
            stat.innerText = 'Polling';
            stat.className = 'text-neutral-400 font-semibold';
          }
          setTimeout(initWebSocket, 4000);
        };
      } catch (err) {
        console.warn('WebSocket init note:', err);
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      renderCurrentView();
      refreshAllData();
      initWebSocket();
      setInterval(refreshAllData, 5000);
    });
  </script>
</body>
</html>
"""

@router.get("/admin", response_class=HTMLResponse)
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """
    Enterprise Fleet Management Command Portal matching FileToLink / Framer design system.
    """
    return HTMLResponse(content=HTML_CONTENT)
