// ============================================================
// PLANNER — upload, results grid, drag-and-drop, re-run solver
// ============================================================

// ── State ──────────────────────────────────────────────────
let currentRunId      = null;
let forcedAssignments = {};   // { "Morceau": "LUN_05_14:00-16:00" }
let lastParams        = null; // form parameters saved for re-plan
let lastPlanData      = null; // full JSON from last plan response
let currentWeek       = null;
let draggedPiece      = null; // { name, fromSlot|null }

// ── Drag-and-drop helpers ───────────────────────────────────

function makeDraggable(el, pieceName, fromSlot) {
  el.draggable = true;
  el.addEventListener('dragstart', e => {
    draggedPiece = { name: pieceName, fromSlot };
    el.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', pieceName);
  });
  el.addEventListener('dragend', () => {
    el.classList.remove('dragging');
    draggedPiece = null;
  });
  el.addEventListener('contextmenu', e => {
    e.preventDefault();
    showContextMenu(e.clientX, e.clientY, pieceName, fromSlot);
  });
}

function setupDropZone(el, slotKey) {
  el.addEventListener('dragover', e => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    el.classList.add('drag-over');
  });
  el.addEventListener('dragleave', () => el.classList.remove('drag-over'));
  el.addEventListener('drop', e => {
    e.preventDefault();
    el.classList.remove('drag-over');
    if (!draggedPiece) return;
    forcedAssignments[draggedPiece.name] = slotKey;
    replan();
  });
}

// ── Context menu ────────────────────────────────────────────

function showContextMenu(x, y, pieceName, slotKey) {
  const menu = document.getElementById('chip-context-menu');
  if (!menu) return;
  menu.style.left = x + 'px';
  menu.style.top  = y + 'px';
  menu.classList.add('visible');
  menu.dataset.piece = pieceName;
  menu.dataset.slot  = slotKey || '';
}

function hideContextMenu() {
  document.getElementById('chip-context-menu')?.classList.remove('visible');
}

document.addEventListener('click', hideContextMenu);

function releaseChip() {
  const menu = document.getElementById('chip-context-menu');
  if (!menu) return;
  const piece = menu.dataset.piece;
  if (piece) {
    delete forcedAssignments[piece];
    replan();
  }
  hideContextMenu();
}

window.releaseChip = releaseChip;

// ── Weekly grid renderer ────────────────────────────────────

function buildSlotKey(jour, heures) {
  // Convert "Lundi 05" + "14:00-16:00" → "LUN_05_14:00-16:00"
  const DAY = { lundi:'LUN', mardi:'MAR', mercredi:'MER', jeudi:'JEU', vendredi:'VEN', samedi:'SAM', dimanche:'DIM' };
  const parts = (jour || '').toLowerCase().split(' ');
  const dayCode = DAY[parts[0]] || parts[0].toUpperCase().slice(0,3);
  const date = (parts[1] || '00').padStart(2, '0');
  return `${dayCode}_${date}_${heures}`;
}

function renderWeekGrid(weekData, weekKey) {
  // weekData: array of { Jour, Heures, Morceau?, ...musicians }
  const repart = lastPlanData?.repartition?.[weekKey] || [];

  // Collect unique days and time slots
  const daysSet   = new Set();
  const slotsSet  = new Set();
  const slotMap   = {}; // "JOU_DD_HH:MM-HH:MM" → { Morceau?, participants[] }

  for (const row of repart) {
    daysSet.add(row['Jour']);
    slotsSet.add(row['Heures']);
    const key = buildSlotKey(row['Jour'], row['Heures']);
    if (!slotMap[key]) slotMap[key] = { jour: row['Jour'], heures: row['Heures'], songs: [] };
    if (row['Morceau']) {
      slotMap[key].songs.push({ name: row['Morceau'], forced: !!forcedAssignments[row['Morceau']] });
    }
  }

  const days  = Array.from(daysSet);
  const slots = Array.from(slotsSet).sort();

  if (!days.length) {
    return '<p style="color:#666;padding:20px">Aucun créneau pour cette semaine.</p>';
  }

  // Build grid: rows = time slots, columns = days
  let html = `<div class="week-grid-wrapper">
    <div class="grid-time-labels">
      <div class="grid-time-label" style="height:44px"></div><!-- header row spacer -->`;
  for (const slot of slots) {
    html += `<div class="grid-time-label">${slot}</div>`;
  }
  html += `</div><!-- .grid-time-labels -->
    <div class="grid-days">
      <div class="grid-day-columns">`;

  for (const jour of days) {
    html += `<div class="grid-day-column">
      <div class="grid-day-header">${jour}</div>`;
    for (const heures of slots) {
      const key = buildSlotKey(jour, heures);
      const cell = slotMap[key];
      const songs = cell?.songs || [];
      const chipHtml = songs.map(s => `
        <span class="song-chip ${s.forced ? 'forced' : ''}"
              data-piece="${escHtml(s.name)}"
              data-slot="${escHtml(key)}"
              id="chip-${escHtml(s.name.replace(/[^a-z0-9]/gi,'_'))}">
          ${escHtml(s.name)}
        </span>`).join('');
      html += `<div class="grid-slot ${songs.length ? '' : 'empty'}"
                    data-slot="${escHtml(key)}" data-jour="${escHtml(jour)}" data-heures="${escHtml(heures)}">
                ${chipHtml}
              </div>`;
    }
    html += `</div>`;
  }

  html += `</div></div></div><!-- .week-grid-wrapper -->`;
  return html;
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderResults(data) {
  lastPlanData = data;

  // Stats
  const statsEl = document.getElementById('result-stats');
  if (statsEl) {
    statsEl.innerHTML = `
      <span class="stat-assigned"><i class="fa fa-check-circle"></i> ${data.assigned} assigné${data.assigned > 1 ? 's' : ''}</span>
      <span class="stat-unassigned"><i class="fa fa-exclamation-circle"></i> ${data.notassigned?.length || 0} non assigné${(data.notassigned?.length||0) > 1 ? 's' : ''}</span>`;
  }

  // Build week tabs
  const tabs = document.getElementById('week-tabs');
  const gridContainer = document.getElementById('week-grid-container');
  if (!tabs || !gridContainer) return;

  const weeks = Object.keys(data.repartition || {}).sort();
  if (!weeks.length) {
    gridContainer.innerHTML = '<p style="color:#666;padding:20px">Aucun résultat à afficher.</p>';
    return;
  }

  tabs.innerHTML = weeks.map(w => `
    <button class="week-tab" data-week="${w}">${w.replace('SEMAINE_', 'Sem. ')}</button>`).join('');

  // Select first week
  selectWeek(weeks[0]);

  tabs.querySelectorAll('.week-tab').forEach(btn => {
    btn.addEventListener('click', () => selectWeek(btn.dataset.week));
  });

  // Pool of unassigned songs
  renderPool(data.notassigned || []);

  // Show results section
  document.getElementById('results-section')?.classList.remove('hidden');
  document.getElementById('upload-section')?.classList.add('compact');

  // Update download link
  const dlBtn = document.getElementById('download-btn');
  if (dlBtn && currentRunId) {
    dlBtn.href = `/api/download?run_id=${encodeURIComponent(currentRunId)}`;
    dlBtn.style.display = '';
  }
}

function selectWeek(weekKey) {
  currentWeek = weekKey;
  document.querySelectorAll('.week-tab').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.week === weekKey);
  });
  const container = document.getElementById('week-grid-container');
  if (container) {
    container.innerHTML = renderWeekGrid(null, weekKey);
    // Attach drag listeners to chips and drop zones
    container.querySelectorAll('.song-chip').forEach(chip => {
      makeDraggable(chip, chip.dataset.piece, chip.dataset.slot);
    });
    container.querySelectorAll('.grid-slot').forEach(slot => {
      setupDropZone(slot, slot.dataset.slot);
    });
  }
}

function renderPool(unassigned) {
  const pool = document.getElementById('pool-list');
  if (!pool) return;
  const count = document.getElementById('pool-count');
  if (count) count.textContent = unassigned.length;

  if (!unassigned.length) {
    pool.innerHTML = '<p style="color:#666;font-size:13px">Tous les morceaux sont planifiés !</p>';
    return;
  }
  pool.innerHTML = unassigned.map(name => `
    <span class="pool-chip" draggable="true" data-piece="${escHtml(name)}">${escHtml(name)}</span>`
  ).join('');

  pool.querySelectorAll('.pool-chip').forEach(chip => {
    chip.addEventListener('dragstart', e => {
      draggedPiece = { name: chip.dataset.piece, fromSlot: null };
      chip.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    });
    chip.addEventListener('dragend', () => {
      chip.classList.remove('dragging');
      draggedPiece = null;
    });
  });
}

// ── API calls ───────────────────────────────────────────────

async function replan() {
  if (!currentRunId || !lastParams) return;
  showOverlay(true);

  const body = new FormData();
  body.append('run_id', currentRunId);
  body.append('forced_assignments', JSON.stringify(forcedAssignments));
  for (const [k, v] of Object.entries(lastParams)) body.append(k, v);

  try {
    const res = await fetch('/api/replan', { method: 'POST', body });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    renderResults(data);
    if (currentWeek) selectWeek(currentWeek);
  } catch (err) {
    alert('Erreur lors du recalcul : ' + err.message);
  } finally {
    showOverlay(false);
  }
}

function showOverlay(show) {
  document.getElementById('solver-overlay')?.classList.toggle('active', show);
}

// ── Form submission ─────────────────────────────────────────

function collectParams() {
  const params = {};
  ['maybe_penalty','max_load','load_penalty','group_bonus','seuil_absence','timeout_limit'].forEach(id => {
    const el = document.getElementById(id);
    if (el) params[id] = el.value;
  });
  params.mode_absence = document.getElementById('mode_absence')?.value || 'flexible';
  const creneaux = [];
  document.querySelectorAll('.creneau-item').forEach(item => {
    const text = item.querySelector('.creneau-item-text')?.textContent?.trim();
    if (text) creneaux.push(text);
  });
  params.creneaux_speciaux = JSON.stringify(creneaux);
  params.seuil_absence_creneau_special = document.getElementById('seuil_absence_creneau_special')?.value || '5';
  return params;
}

async function submitForm(e) {
  e.preventDefault();
  const dispoFile  = document.getElementById('file-dispo')?.files[0];
  const rePartFile = document.getElementById('file-repart')?.files[0];

  if (!dispoFile || !rePartFile) {
    alert('Veuillez déposer les deux fichiers Excel.');
    return;
  }

  forcedAssignments = {};
  lastParams = collectParams();
  showOverlay(true);

  const body = new FormData();
  body.append('disponibilites', dispoFile);
  body.append('repartition', rePartFile);
  for (const [k, v] of Object.entries(lastParams)) body.append(k, v);

  try {
    const res = await fetch('/api/upload', { method: 'POST', body });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    currentRunId = data.run_id;
    renderResults(data);
  } catch (err) {
    alert('Erreur : ' + err.message);
  } finally {
    showOverlay(false);
  }
}

// ── File drop zones ─────────────────────────────────────────

function setupDropZoneInput(zoneId, inputId) {
  const zone  = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;

  zone.addEventListener('click', () => input.click());
  input.addEventListener('change', () => updateZone(zone, input));

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) {
      const dt = new DataTransfer();
      dt.items.add(files[0]);
      input.files = dt.files;
      updateZone(zone, input);
    }
  });
}

function updateZone(zone, input) {
  const file = input.files[0];
  if (!file) return;
  zone.classList.add('has-file');
  const label = zone.querySelector('.file-label');
  if (label) label.textContent = file.name;
}

// ── Créneau spéciaux management ─────────────────────────────

window.addCreneau = function() {
  const jour = document.getElementById('creneau-jour')?.value;
  const date = document.getElementById('creneau-date')?.value;
  const h1   = document.getElementById('creneau-h1')?.value;
  const h2   = document.getElementById('creneau-h2')?.value;
  if (!jour || !date || !h1 || !h2) return;

  const text = `${jour}_${String(date).padStart(2,'0')}_${h1}-${h2}`;
  const list = document.getElementById('creneaux-list');
  if (!list) return;

  const item = document.createElement('div');
  item.className = 'creneau-item';
  item.innerHTML = `
    <span class="creneau-item-text">${escHtml(text)}</span>
    <button class="btn-remove-creneau" onclick="this.closest('.creneau-item').remove()">
      <i class="fa fa-times"></i>
    </button>`;
  list.appendChild(item);
};

// ── Bootstrap ───────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('planner-form')?.addEventListener('submit', submitForm);
  setupDropZoneInput('drop-zone-dispo',  'file-dispo');
  setupDropZoneInput('drop-zone-repart', 'file-repart');

  // Open/close parameters modal
  document.getElementById('params-toggle')?.addEventListener('click', () => {
    document.getElementById('params-modal')?.classList.add('active');
  });
  document.getElementById('params-close')?.addEventListener('click', () => {
    document.getElementById('params-modal')?.classList.remove('active');
  });
  document.getElementById('params-modal')?.addEventListener('click', e => {
    if (e.target === document.getElementById('params-modal')) {
      document.getElementById('params-modal')?.classList.remove('active');
    }
  });

  // Pool toggle
  document.getElementById('pool-toggle')?.addEventListener('click', () => {
    document.getElementById('pool-panel')?.classList.toggle('open');
  });

  // Context menu
  document.getElementById('ctx-release')?.addEventListener('click', releaseChip);
});
