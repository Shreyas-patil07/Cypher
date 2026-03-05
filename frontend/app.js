/**
 * CYPHER HUD — Dashboard Controller
 * Real-time Threat Detection Powered by AI
 */

const API_BASE = ""; // same-origin

// ─── CypherHUD Class ─────────────────────────────────────────────
class CypherHUD {
  constructor() {
    // DOM refs
    this.statusDot = document.getElementById("status-dot");
    this.statusText = document.getElementById("status-text");
    this.statusPill = document.getElementById("status-pill");
    this.alertList = document.getElementById("alert-list");
    this.emptyState = document.getElementById("empty-state");
    this.alertCounter = document.getElementById("alert-counter");
    this.threatIndicator = document.getElementById("threat-indicator");
    this.threatValue = document.getElementById("threat-value");
    this.threatBarFill = document.getElementById("threat-bar-fill");

    // Stats elements
    this.elTotalThreats = document.getElementById("total-threats");
    this.elPerson = document.getElementById("person-count");
    this.elWeapon = document.getElementById("weapon-count");
    this.elFPS = document.getElementById("fps-value");
    this.elCameras = document.getElementById("camera-count");
    this.elUptime = document.getElementById("uptime");

    // Modal
    this.modalBackdrop = document.getElementById("modal-backdrop");
    this.modalImg = document.getElementById("modal-img");
    this.modalMeta = document.getElementById("modal-meta");

    // State
    this._alerts = [];
    this._highestRisk = "clear";

    this._bindEvents();
    this._startPolling();
  }

  // ─── Event binding ───────────────────────────────────────────
  _bindEvents() {
    document.getElementById("btn-start").addEventListener("click", () => this.startSurveillance());
    document.getElementById("btn-stop").addEventListener("click", () => this.stopSurveillance());
    document.getElementById("refresh-btn").addEventListener("click", () => this.refresh());
    document.getElementById("modal-close").addEventListener("click", () => this.closeModal());
    this.modalBackdrop.addEventListener("click", (e) => {
      if (e.target === this.modalBackdrop) this.closeModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.closeModal();
    });
  }

  // ─── Polling ─────────────────────────────────────────────────
  _startPolling() {
    this.refresh();
    setInterval(() => this.refresh(), 5000);
  }

  async refresh() {
    try {
      const [statusData, alertsData, statsData] = await Promise.all([
        this._fetch("/api/status"),
        this._fetch("/api/alerts"),
        this._fetch("/api/statistics"),
      ]);

      this._updateStatus(statusData);
      this._updateAlerts(alertsData.alerts || []);
      this._updateStatistics(statsData);
    } catch (err) {
      console.warn("Refresh failed:", err.message);
      this._setStatus("offline", "Offline");
    }
  }

  // ─── Status ──────────────────────────────────────────────────
  _updateStatus(data) {
    if (data.running) {
      this._setStatus("live", "Live");
    } else {
      this._setStatus("idle", "Idle");
    }
  }

  _setStatus(state, text) {
    this.statusText.textContent = text;
    this.statusDot.className = "dot";

    switch (state) {
      case "live":
        this.statusDot.classList.add("live");
        break;
      case "idle":
        // default yellow dot
        break;
      case "offline":
        this.statusDot.classList.add("danger");
        break;
    }
  }

  // ─── Statistics ──────────────────────────────────────────────
  _updateStatistics(data) {
    this._animateValue(this.elTotalThreats, data.total_threats || 0);
    this._animateValue(this.elPerson, data.threats_by_type?.person || 0);
    this._animateValue(this.elWeapon, data.threats_by_type?.weapon || 0);

    const fps = data.current_fps || 0;
    this.elFPS.textContent = fps > 0 ? fps.toFixed(1) : "—";
    this.elCameras.textContent = data.active_cameras || 0;

    const uptime = data.system_uptime_seconds || 0;
    this.elUptime.textContent = this._formatUptime(uptime);

    // Update threat level indicator
    this._updateThreatLevel(data);
  }

  _animateValue(el, newVal) {
    const current = parseInt(el.textContent) || 0;
    if (current !== newVal) {
      el.textContent = newVal;
      el.style.transform = "scale(1.2)";
      el.style.color = "#fff";
      setTimeout(() => {
        el.style.transform = "scale(1)";
        el.style.color = "";
      }, 300);
    }
  }

  _formatUptime(seconds) {
    if (seconds < 60) return `${Math.floor(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
  }

  _updateThreatLevel(data) {
    const weaponCount = data.threats_by_type?.weapon || 0;
    const personCount = data.threats_by_type?.person || 0;
    const total = data.total_threats || 0;

    let level = "clear";
    let barWidth = 0;

    if (weaponCount > 0 && data.last_alert_timestamp) {
      // Check how recent the last alert was
      level = "critical";
      barWidth = 100;
    } else if (personCount > 5) {
      level = "high";
      barWidth = 70;
    } else if (personCount > 0) {
      level = "medium";
      barWidth = 40;
    } else if (total > 0) {
      level = "medium";
      barWidth = 20;
    }

    this.threatIndicator.className = "panel threat-indicator";
    if (level !== "clear") {
      this.threatIndicator.classList.add(`level-${level}`);
    }
    this.threatValue.textContent = level.toUpperCase();
    this.threatBarFill.style.width = `${barWidth}%`;
  }

  // ─── Alerts ──────────────────────────────────────────────────
  _updateAlerts(alerts) {
    this._alerts = alerts;
    this.alertCounter.textContent = `${alerts.length} alert${alerts.length !== 1 ? "s" : ""}`;

    if (alerts.length === 0) {
      this.alertList.innerHTML = "";
      this.alertList.appendChild(this.emptyState);
      this.emptyState.style.display = "flex";
      return;
    }

    this.emptyState.style.display = "none";
    this.alertList.innerHTML = "";

    alerts.forEach((alert) => {
      const card = this._createAlertCard(alert);
      this.alertList.appendChild(card);
    });
  }

  _createAlertCard(alert) {
    const card = document.createElement("div");
    card.className = `alert-card ${alert.risk_level.toLowerCase()}-border`;

    // Thumbnail
    if (alert.image_url) {
      const img = document.createElement("img");
      img.className = "alert-thumb";
      img.src = alert.image_url;
      img.alt = "Incident";
      img.loading = "lazy";
      card.appendChild(img);
    } else {
      const placeholder = document.createElement("div");
      placeholder.className = "alert-thumb-placeholder";
      placeholder.innerHTML = "📷";
      card.appendChild(placeholder);
    }

    // Info
    const info = document.createElement("div");
    info.className = "alert-info";

    const type = document.createElement("div");
    type.className = "alert-type";
    type.textContent = alert.event_type;
    info.appendChild(type);

    const meta = document.createElement("div");
    meta.className = "alert-meta";
    const ts = new Date(alert.timestamp);
    const timeStr = ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    meta.textContent = `${alert.camera_id} • ${timeStr} • ${(alert.confidence * 100).toFixed(0)}%`;
    info.appendChild(meta);

    card.appendChild(info);

    // Badge
    const badge = document.createElement("span");
    badge.className = `alert-badge ${alert.risk_level.toLowerCase()}`;
    badge.textContent = alert.risk_level.toUpperCase();
    card.appendChild(badge);

    // Click to open modal
    if (alert.image_url) {
      card.addEventListener("click", () => this.openModal(alert));
    }

    return card;
  }

  // ─── Modal ───────────────────────────────────────────────────
  openModal(alert) {
    if (!alert.image_url) return;
    this.modalImg.src = alert.image_url;
    this.modalMeta.innerHTML = `
      <span>📌 ${alert.event_type}</span>
      <span>🏷️ ${alert.risk_level.toUpperCase()}</span>
      <span>📹 ${alert.camera_id}</span>
      <span>⏱ ${new Date(alert.timestamp).toLocaleString()}</span>
      <span>🎯 ${(alert.confidence * 100).toFixed(1)}% confidence</span>
    `;
    this.modalBackdrop.hidden = false;
  }

  closeModal() {
    this.modalBackdrop.hidden = true;
    this.modalImg.src = "";
  }

  // ─── Surveillance controls ───────────────────────────────────
  async startSurveillance() {
    try {
      await this._fetch("/api/start", { method: "POST", body: JSON.stringify({}) });
      this._setStatus("live", "Starting…");
      setTimeout(() => this.refresh(), 1000);
    } catch (err) {
      console.error("Start failed:", err);
    }
  }

  async stopSurveillance() {
    try {
      await this._fetch("/api/stop", { method: "POST" });
      this._setStatus("idle", "Stopped");
      setTimeout(() => this.refresh(), 500);
    } catch (err) {
      console.error("Stop failed:", err);
    }
  }

  // ─── Fetch helper ────────────────────────────────────────────
  async _fetch(path, options = {}) {
    const defaults = {
      headers: { "Content-Type": "application/json" },
    };
    const res = await fetch(`${API_BASE}${path}`, { ...defaults, ...options });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
}

// ─── Initialize ────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  window.cypherHUD = new CypherHUD();
});
