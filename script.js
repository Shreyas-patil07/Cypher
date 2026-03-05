let incidents = [
  {
    id: 1,
    type: "conflict",
    alert: "Human Conflict Detected",
    location: "Sector 7 Market Street",
    zone: "Sector 7",
    time: "21:45",
    date: "05 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 2,
    type: "accident",
    alert: "Accident Detected",
    location: "Sector 5 Ring Road",
    zone: "Sector 5",
    time: "20:12",
    date: "05 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 3,
    type: "weapon",
    alert: "Weapon Detection Alert",
    location: "Transit Hub Gate 3",
    zone: "Transit Hub",
    time: "19:31",
    date: "05 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 4,
    type: "conflict",
    alert: "Human Conflict Detected",
    location: "Sector 5 Market Zone",
    zone: "Sector 5",
    time: "18:56",
    date: "05 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 5,
    type: "accident",
    alert: "Accident Detected",
    location: "Airport Connector",
    zone: "North Corridor",
    time: "18:04",
    date: "04 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 6,
    type: "conflict",
    alert: "Human Conflict Detected",
    location: "Sector 7 Bus Terminal",
    zone: "Sector 7",
    time: "17:27",
    date: "04 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 7,
    type: "weapon",
    alert: "Weapon Detection Alert",
    location: "Sector 3 Overpass",
    zone: "Sector 3",
    time: "16:42",
    date: "04 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 8,
    type: "conflict",
    alert: "Human Conflict Detected",
    location: "Sector 5 Market Zone",
    zone: "Sector 5",
    time: "15:16",
    date: "04 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 9,
    type: "accident",
    alert: "Accident Detected",
    location: "City Hospital Junction",
    zone: "Central Junction",
    time: "14:08",
    date: "03 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 10,
    type: "conflict",
    alert: "Human Conflict Detected",
    location: "Old Town Plaza",
    zone: "Old Town",
    time: "12:51",
    date: "03 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 11,
    type: "weapon",
    alert: "Weapon Detection Alert",
    location: "Industrial Gate 2",
    zone: "Industrial Belt",
    time: "11:33",
    date: "03 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 12,
    type: "conflict",
    alert: "Human Conflict Detected",
    location: "Sector 5 Market Zone",
    zone: "Sector 5",
    time: "10:19",
    date: "03 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 13,
    type: "accident",
    alert: "Accident Detected",
    location: "Riverfront Express Lane",
    zone: "Riverfront",
    time: "09:26",
    date: "02 Mar 2026",
    week: true,
    month: true
  },
  {
    id: 14,
    type: "conflict",
    alert: "Human Conflict Detected",
    location: "Sector 7 Market Street",
    zone: "Sector 7",
    time: "22:10",
    date: "26 Feb 2026",
    week: false,
    month: true
  },
  {
    id: 15,
    type: "accident",
    alert: "Accident Detected",
    location: "Central Junction",
    zone: "Central Junction",
    time: "08:20",
    date: "24 Feb 2026",
    week: false,
    month: true
  },
  {
    id: 16,
    type: "weapon",
    alert: "Weapon Detection Alert",
    location: "Sector 5 Metro Exit",
    zone: "Sector 5",
    time: "20:41",
    date: "21 Feb 2026",
    week: false,
    month: true
  }
];

let zoneCoordinates = {
  "Sector 5": { lat: 28.6135, lng: 77.2092 },
  "Sector 7": { lat: 28.6339, lng: 77.2192 },
  "Transit Hub": { lat: 28.6201, lng: 77.2422 },
  "North Corridor": { lat: 28.6525, lng: 77.2048 },
  "Sector 3": { lat: 28.6081, lng: 77.1824 },
  "Central Junction": { lat: 28.6248, lng: 77.2134 },
  "Old Town": { lat: 28.6416, lng: 77.2362 },
  "Industrial Belt": { lat: 28.5922, lng: 77.2451 },
  "Riverfront": { lat: 28.6025, lng: 77.228 }
};

const alertStream = document.getElementById("alertStream");
const filterButtons = document.querySelectorAll(".filter-btn");
const reportTabs = document.querySelectorAll(".report-tab");

const weeklyTotal = document.getElementById("weeklyTotal");
const weeklyAccidents = document.getElementById("weeklyAccidents");
const weeklyConflicts = document.getElementById("weeklyConflicts");
const weeklyWeapons = document.getElementById("weeklyWeapons");
const weeklyHotspot = document.getElementById("weeklyHotspot");

const monthlyTotal = document.getElementById("monthlyTotal");
const monthlyAccidents = document.getElementById("monthlyAccidents");
const monthlyConflicts = document.getElementById("monthlyConflicts");
const monthlyAccidentConflict = document.getElementById("monthlyAccidentConflict");
const monthlyWeapons = document.getElementById("monthlyWeapons");
const monthlyTrend = document.getElementById("monthlyTrend");
const monthlyZone = document.getElementById("monthlyZone");

const weeklyLocationRows = document.getElementById("weeklyLocationRows");
const monthlyLocationRows = document.getElementById("monthlyLocationRows");

const weeklyAccidentBar = document.getElementById("weeklyAccidentBar");
const weeklyConflictBar = document.getElementById("weeklyConflictBar");
const weeklyWeaponBar = document.getElementById("weeklyWeaponBar");
const monthlyAccidentBar = document.getElementById("monthlyAccidentBar");
const monthlyConflictBar = document.getElementById("monthlyConflictBar");
const monthlyWeaponBar = document.getElementById("monthlyWeaponBar");
const loadNearbyAlertsBtn = document.getElementById("loadNearbyAlertsBtn");
const heatmapStatus = document.getElementById("heatmapStatus");

const zoneMapElement = document.getElementById("zoneMap");

let zoneMap = null;
let heatLayers = [];
let zoneLayerLookup = {};
let selectedZone = null;
let selectedIncidentId = null;
let mapSelectionHandlerBound = false;
let userLocationCenter = null;

let activeFilter = "all";

const defaultIncidents = incidents.slice();
const defaultZoneCoordinates = { ...zoneCoordinates };
const nearbyZones = ["North Block", "South Block", "East Block", "West Block", "Central Block", "Market Block"];
const nearbyRoads = ["Main Road", "Station Lane", "Market Street", "Hospital Road", "Transit Point", "Ring Link"];

function applyFilter(data) {
  if (activeFilter === "all") return data;
  return data.filter((item) => item.type === activeFilter);
}

function getAlertTimestamp(item) {
  const parsed = Date.parse(`${item.date} ${item.time}`);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function getLatestIncidentByZone(data, zone) {
  return data
    .filter((item) => item.zone === zone)
    .slice()
    .sort((a, b) => {
      const timeDiff = getAlertTimestamp(b) - getAlertTimestamp(a);
      if (timeDiff !== 0) return timeDiff;
      return b.id - a.id;
    })[0] || null;
}

function clearMapSelection() {
  selectedZone = null;
  selectedIncidentId = null;
  renderAlerts(applyFilter(incidents));
  highlightSelectedMapZone();
}

function renderAlerts(filtered) {
  alertStream.innerHTML = "";

  const zoneFiltered = selectedZone
    ? filtered.filter((item) => item.zone === selectedZone)
    : filtered;

  const alertsToShow = selectedIncidentId
    ? zoneFiltered.filter((item) => item.id === selectedIncidentId)
    : zoneFiltered;

  if (!alertsToShow.length) {
    alertStream.innerHTML = "<p class='alert-meta'>No alerts found for this filter.</p>";
    return;
  }

  if (!selectedIncidentId && selectedZone) {
    const focusNote = document.createElement("p");
    focusNote.className = "alert-meta";
    focusNote.textContent = `Map Selection: ${selectedZone} (click anywhere to clear)`;
    alertStream.appendChild(focusNote);
  }

  alertsToShow
    .slice()
    .sort((a, b) => {
      const timeDiff = getAlertTimestamp(b) - getAlertTimestamp(a);
      if (timeDiff !== 0) return timeDiff;
      return b.id - a.id;
    })
    .forEach((item) => {
      const card = document.createElement("article");
      card.className = "alert-card";
      card.dataset.type = item.type;
      card.tabIndex = 0;

      card.innerHTML = `
        <div class="alert-top">
          <span class="alert-title">SYSTEM: CYPHER VISION</span>
        </div>
        <div class="alert-type">ALERT: ${item.alert}</div>
        <div class="alert-meta">
          Location: ${item.location}<br>
          Time: ${item.time} | Date: ${item.date}
        </div>
        ${selectedIncidentId === item.id ? '<div class="alert-meta alert-clear-hint">click anywhere to clear</div>' : ""}
      `;

      const applyCardSelection = () => {
        selectedZone = item.zone;
        selectedIncidentId = item.id;
        renderAlerts(applyFilter(incidents));
        highlightSelectedMapZone();
      };

      card.addEventListener("click", applyCardSelection);
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          applyCardSelection();
        }
      });

      alertStream.appendChild(card);
    });
}

function zoneAggregation(data) {
  return data.reduce((acc, item) => {
    acc[item.zone] = (acc[item.zone] || 0) + 1;
    return acc;
  }, {});
}

function levelFromCount(count) {
  if (count >= 3) return "high";
  if (count === 2) return "medium";
  return "low";
}

function coreColor(level) {
  if (level === "high") return "#d1392c";
  if (level === "medium") return "#e78021";
  return "#ff8a00";
}

function updateHeatmapStatus(message) {
  if (heatmapStatus) {
    heatmapStatus.textContent = message;
  }
}

function highlightSelectedMapZone() {
  if (!zoneMap) return;

  Object.entries(zoneLayerLookup).forEach(([zone, layerInfo]) => {
    const isSelected = selectedZone === zone;

    layerInfo.zoneCircle.setStyle({
      color: layerInfo.color,
      fillColor: layerInfo.color,
      fillOpacity: isSelected ? 0.46 : 0.32,
      weight: isSelected ? 2 : 1
    });

    layerInfo.coreMarker.setStyle({
      color: isSelected ? "#ffffff" : "#f4f7fa",
      fillColor: layerInfo.color,
      fillOpacity: 0.95,
      radius: isSelected ? 11 : layerInfo.baseRadius,
      weight: isSelected ? 2 : 1
    });
  });

  if (selectedZone && zoneLayerLookup[selectedZone]) {
    const selected = zoneLayerLookup[selectedZone];
    zoneMap.setView(selected.coordinates, Math.max(zoneMap.getZoom(), 13));
    selected.coreMarker.openTooltip();
  }
}

function createOffset(base, spread) {
  return base + (Math.random() - 0.5) * spread;
}

function randomTime() {
  const hour = Math.floor(Math.random() * 24);
  const minute = Math.floor(Math.random() * 60);
  return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
}

function formatDate(dateValue) {
  const day = String(dateValue.getDate()).padStart(2, "0");
  const month = dateValue.toLocaleString("en-US", { month: "short" });
  const year = dateValue.getFullYear();
  return `${day} ${month} ${year}`;
}

function nearbyType(index) {
  const pool = ["conflict", "accident", "weapon", "conflict", "accident", "conflict"];
  return pool[index % pool.length];
}

function alertLabel(type) {
  if (type === "accident") return "Accident Detected";
  if (type === "weapon") return "Weapon Detection Alert";
  return "Human Conflict Detected";
}

function buildNearbyDataset(centerLat, centerLng) {
  const generatedZoneCoordinates = {};

  nearbyZones.forEach((zone) => {
    generatedZoneCoordinates[zone] = {
      lat: createOffset(centerLat, 0.06),
      lng: createOffset(centerLng, 0.06)
    };
  });

  const now = new Date();
  const generatedIncidents = Array.from({ length: 16 }, (_, index) => {
    const zone = nearbyZones[index % nearbyZones.length];
    const type = nearbyType(index);
    const daysAgo = index;
    const dateValue = new Date(now);
    dateValue.setDate(now.getDate() - daysAgo);

    return {
      id: index + 1,
      type,
      alert: alertLabel(type),
      location: `${zone} ${nearbyRoads[index % nearbyRoads.length]}`,
      zone,
      time: randomTime(),
      date: formatDate(dateValue),
      week: daysAgo <= 6,
      month: daysAgo <= 30
    };
  });

  return {
    incidents: generatedIncidents,
    coordinates: generatedZoneCoordinates
  };
}

function initZoneMap() {
  if (zoneMap || typeof L === "undefined") return;

  const initialCenter = userLocationCenter || { lat: 28.622, lng: 77.218 };

  zoneMap = L.map(zoneMapElement, {
    zoomControl: true,
    attributionControl: true
  }).setView([initialCenter.lat, initialCenter.lng], 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(zoneMap);

  if (!mapSelectionHandlerBound) {
    zoneMap.on("click", () => {
      clearMapSelection();
    });
    mapSelectionHandlerBound = true;
  }
}

function clearHeatLayers() {
  heatLayers.forEach((layer) => {
    zoneMap.removeLayer(layer);
  });
  heatLayers = [];
  zoneLayerLookup = {};
}

function renderHeatmap(filtered) {
  initZoneMap();
  if (!zoneMap) return;

  const counts = zoneAggregation(filtered);
  clearHeatLayers();

  const bounds = [];

  Object.entries(zoneCoordinates).forEach(([zone, point]) => {
    const total = counts[zone] || 0;
    if (total === 0) return;
    const representativeAlert = getLatestIncidentByZone(filtered, zone);

    const level = levelFromCount(total);
    const color = coreColor(level);

    const zoneCircle = L.circle([point.lat, point.lng], {
      radius: 140 + total * 110,
      color,
      fillColor: color,
      fillOpacity: 0.32,
      weight: 1,
      bubblingMouseEvents: false
    }).bindTooltip(`${zone}: ${total} incidents`, {
      direction: "top"
    });

    const coreMarker = L.circleMarker([point.lat, point.lng], {
      radius: 5 + Math.min(total * 1.6, 8),
      color: "#f4f7fa",
      weight: 1,
      fillColor: color,
      fillOpacity: 0.95,
      bubblingMouseEvents: false
    });

    zoneCircle.addTo(zoneMap);
    coreMarker.addTo(zoneMap);

    zoneLayerLookup[zone] = {
      zoneCircle,
      coreMarker,
      color,
      baseRadius: 5 + Math.min(total * 1.6, 8),
      coordinates: [point.lat, point.lng]
    };

    zoneCircle.on("click", (event) => {
      L.DomEvent.stopPropagation(event);
      selectedZone = zone;
      selectedIncidentId = representativeAlert ? representativeAlert.id : null;
      renderAlerts(applyFilter(incidents));
      highlightSelectedMapZone();
    });

    coreMarker.on("click", (event) => {
      L.DomEvent.stopPropagation(event);
      selectedZone = zone;
      selectedIncidentId = representativeAlert ? representativeAlert.id : null;
      renderAlerts(applyFilter(incidents));
      highlightSelectedMapZone();
    });

    heatLayers.push(zoneCircle, coreMarker);
    bounds.push([point.lat, point.lng]);
  });

  if (bounds.length > 0) {
    if (!selectedZone || !zoneLayerLookup[selectedZone]) {
      zoneMap.fitBounds(bounds, { padding: [30, 30] });
    }
  }

  highlightSelectedMapZone();
}

function countByType(data, type) {
  return data.filter((item) => item.type === type).length;
}

function getTopZone(data) {
  const zones = Object.entries(zoneAggregation(data));
  if (!zones.length) return "-";
  return zones.sort((a, b) => b[1] - a[1])[0][0];
}

function getTopZones(data, limit) {
  const zones = Object.entries(zoneAggregation(data)).sort((a, b) => b[1] - a[1]);
  return zones.slice(0, limit);
}

function computeTrend(monthData) {
  if (monthData.length < 4) return "Insufficient Data";

  const recent = monthData.slice().sort((a, b) => b.id - a.id).slice(0, 4);
  const highSeverity = countByType(recent, "conflict") + countByType(recent, "weapon");

  if (highSeverity >= 3) return "Escalating";
  if (highSeverity <= 1) return "Declining";
  return "Stable";
}

function widthFromCount(count, total) {
  if (total === 0) return "0%";
  return `${Math.max(8, (count / total) * 100)}%`;
}

function fillRows(container, rows, emptyLabel) {
  container.innerHTML = "";

  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${emptyLabel}</td><td>0</td>`;
    container.appendChild(tr);
    return;
  }

  rows.forEach(([name, count]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${name}</td><td>${count}</td>`;
    container.appendChild(tr);
  });
}

function renderReports(filtered) {
  const weekly = filtered.filter((item) => item.week);
  const monthly = filtered.filter((item) => item.month);

  const weekAccidents = countByType(weekly, "accident");
  const weekConflicts = countByType(weekly, "conflict");
  const weekWeapons = countByType(weekly, "weapon");

  weeklyTotal.textContent = weekly.length;
  weeklyAccidents.textContent = weekAccidents;
  weeklyConflicts.textContent = weekConflicts;
  weeklyWeapons.textContent = weekWeapons;
  weeklyHotspot.textContent = getTopZone(weekly);

  weeklyAccidentBar.style.width = widthFromCount(weekAccidents, weekly.length);
  weeklyConflictBar.style.width = widthFromCount(weekConflicts, weekly.length);
  weeklyWeaponBar.style.width = widthFromCount(weekWeapons, weekly.length);
  fillRows(weeklyLocationRows, getTopZones(weekly, 5), "No weekly data");

  const monthAccidents = countByType(monthly, "accident");
  const monthConflicts = countByType(monthly, "conflict");
  const monthWeapons = countByType(monthly, "weapon");

  monthlyTotal.textContent = monthly.length;
  monthlyAccidents.textContent = monthAccidents;
  monthlyConflicts.textContent = monthConflicts;
  monthlyWeapons.textContent = monthWeapons;
  monthlyAccidentConflict.textContent = `${monthAccidents} : ${monthConflicts}`;
  monthlyTrend.textContent = computeTrend(monthly);
  monthlyZone.textContent = getTopZone(monthly);

  monthlyAccidentBar.style.width = widthFromCount(monthAccidents, monthly.length);
  monthlyConflictBar.style.width = widthFromCount(monthConflicts, monthly.length);
  monthlyWeaponBar.style.width = widthFromCount(monthWeapons, monthly.length);
  fillRows(monthlyLocationRows, getTopZones(monthly, 5), "No monthly data");
}

function refreshDashboard() {
  const filtered = applyFilter(incidents);
  renderAlerts(filtered);
  renderHeatmap(filtered);
  renderReports(filtered);
}

function applyLocationBasedAlerts(latitude, longitude) {
  userLocationCenter = { lat: latitude, lng: longitude };
  const dataset = buildNearbyDataset(latitude, longitude);
  incidents = dataset.incidents;
  zoneCoordinates = dataset.coordinates;
  selectedZone = null;
  selectedIncidentId = null;
  activeFilter = "all";

  filterButtons.forEach((btn) => {
    const shouldBeActive = btn.dataset.filter === "all";
    btn.classList.toggle("active", shouldBeActive);
    btn.setAttribute("aria-selected", shouldBeActive ? "true" : "false");
  });

  if (zoneMap) {
    zoneMap.setView([latitude, longitude], 13);
  }

  refreshDashboard();
}

function requestLocationAndLoadAlerts() {
  if (!navigator.geolocation) {
    updateHeatmapStatus("Geolocation is not supported in this browser.");
    return;
  }

  if (loadNearbyAlertsBtn) loadNearbyAlertsBtn.disabled = true;
  updateHeatmapStatus("Requesting your location permission...");

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      updateHeatmapStatus("Location received. Scanning nearby area...");

      setTimeout(() => {
        applyLocationBasedAlerts(latitude, longitude);
        updateHeatmapStatus(`Loaded nearby alerts around ${latitude.toFixed(4)}, ${longitude.toFixed(4)}.`);
        if (loadNearbyAlertsBtn) loadNearbyAlertsBtn.disabled = false;
      }, 2200);
    },
    () => {
      incidents = defaultIncidents.slice();
      zoneCoordinates = { ...defaultZoneCoordinates };
      refreshDashboard();
      updateHeatmapStatus("Unable to access location. Please allow permission and try again.");
      if (loadNearbyAlertsBtn) loadNearbyAlertsBtn.disabled = false;
    },
    {
      enableHighAccuracy: true,
      timeout: 12000,
      maximumAge: 0
    }
  );
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((btn) => {
      btn.classList.remove("active");
      btn.setAttribute("aria-selected", "false");
    });

    button.classList.add("active");
    button.setAttribute("aria-selected", "true");
    activeFilter = button.dataset.filter;
    selectedZone = null;
    selectedIncidentId = null;
    refreshDashboard();
  });
});

reportTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    reportTabs.forEach((btn) => {
      btn.classList.remove("active");
      btn.setAttribute("aria-selected", "false");
    });

    tab.classList.add("active");
    tab.setAttribute("aria-selected", "true");

    const showWeekly = tab.dataset.reportTab === "weekly";
    document.getElementById("weeklyPanel").classList.toggle("active", showWeekly);
    document.getElementById("monthlyPanel").classList.toggle("active", !showWeekly);
    document.getElementById("weeklyPanel").hidden = !showWeekly;
    document.getElementById("monthlyPanel").hidden = showWeekly;
  });
});

if (loadNearbyAlertsBtn) {
  loadNearbyAlertsBtn.addEventListener("click", requestLocationAndLoadAlerts);
}

document.addEventListener("click", (event) => {
  if (!selectedIncidentId && !selectedZone) return;

  const target = event.target;
  if (!(target instanceof Element)) return;

  // Keep selection when user interacts with map layers or alert cards.
  if (target.closest("#zoneMap") || target.closest(".alert-card")) return;

  clearMapSelection();
});

refreshDashboard();
