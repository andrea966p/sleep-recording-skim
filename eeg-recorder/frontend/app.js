/* eeg-recorder console.
 *
 * One page, no framework, no build step. It polls /api/state and renders; every
 * mutation is a POST followed by an immediate re-poll, so what is on screen is
 * always what the service actually believes rather than what this file guessed.
 *
 * Two things here exist because of measurements on the rig, not taste:
 *   - The "0 bytes is normal" notice. Allego does not update the .xdat file size
 *     for ~30 s after a perfectly healthy start, so a live panel that showed
 *     0 bytes with no explanation would make every user think the rig had failed.
 *   - The slot grid follows the PRESET, not a fixed eight. unipolar_lfp is four
 *     animals, one per port; rendering eight slots for it would invite someone to
 *     type a mouse id into a slot that does not exist.
 */
const $ = s => document.querySelector(s);
const api = async (path, opts) => {
  const r = await fetch(path, opts);
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(body.error || `HTTP ${r.status}`),
                                 {status: r.status});
  return body;
};
const post = (p, b) => api(p, {
  method: 'POST', headers: {'Content-Type': 'application/json'},
  body: b ? JSON.stringify(b) : undefined,
});
const remove = (p) => api(p, {method: 'DELETE'});

let CFG = null, PRESET = null, STATE = null, SELECTED = 'andrea';
// What the operator says is physically on each port. A splitter puts TWO chips
// on a port: 64 enumerated channels, two animals. Without one, 32 and one animal.
let SPLIT = {A: true, B: true, C: true, D: true};
// Which ports are part of this run at all. A port with no headstage plugged in
// enumerates 0, and with no way to say "I am not using it" the console refused
// to start and offered no way out -- the backend had ports_used all along and
// the page never sent it. Found 2026-09-14 while listing what to bench test.
let USED = {A: true, B: true, C: true, D: true};
// A channel selection made for ONE run and not saved to the config. It goes
// through the same validator as a saved setting (presets.make_setting), so an
// inline choice cannot be looser than a stored one.
const CUSTOM_SETTING = '__custom__';
// The setting in use before switching to Custom. "Custom channels" then starts
// as a COPY of what the rig is already set to, which is what someone means by
// customising -- and it removes a bad default: the picker used to seed from
// whichever headstage sorted first alphabetically, which is the exotic unipolar
// one, silently giving the wrong expected channel count and the wrong floor.
let LAST_SETTING = null;
function customPayload() {
  if ($('#setting').value !== CUSTOM_SETTING) return null;
  const roles = {};
  document.querySelectorAll('#cs-roles .row').forEach(d => {
    const r = d.querySelector('[data-k=role]').value.trim();
    const v = d.querySelector('[data-k=site]').value.trim();
    if (r && v) roles[r] = parseInt(v, 10);
  });
  // Contiguity is decided HERE, from what is typed, not from the server's
  // answer. Inferring it from the response was a dead end: a non-contiguous
  // selection makes the request fail, the failure says "declare qc: none with a
  // reason", and the reason box only appeared on a successful response. The
  // server remains the authority -- it refuses an empty reason.
  const sites = Object.values(roles).sort((a, b) => a - b);
  const contiguous = sites.length > 0 && sites.every((v, i) => v === i + 1);
  $('#cs-qcbox').classList.toggle('hide', contiguous);
  return {headstage: $('#cs-hs').value, roles,
          qc: contiguous ? 'auto' : 'none',
          qc_reason: $('#cs-reason').value.trim(),
          label: 'Custom channels'};
}

/* ---------- toast ---------- */
function toast(msg, kind) {
  const d = document.createElement('div');
  if (kind) d.className = kind;
  d.textContent = msg;
  $('#toast').appendChild(d);
  setTimeout(() => d.remove(), kind === 'bad' ? 12000 : 6000);
}

/* ---------- formatting ---------- */
const gb = b => (b == null ? '–' : (b / 1e9).toFixed(b < 1e10 ? 2 : 1) + ' GB');
function dur(sec) {
  if (sec == null || sec < 0) return '–';
  const h = Math.floor(sec / 3600), m = Math.floor(sec % 3600 / 60),
        s = Math.floor(sec % 60);
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}
const esc = t => String(t ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Allego 4 states are "ON"/"OFF"; the old client sent "R_ON"/"S_ON". Accept both.
const isOn = v => v === 'ON' || v === 'R_ON' || v === 'S_ON' || v === true;
// measured_utc may come without a zone suffix; it is UTC either way.
const utcLocal = iso => iso ? local(/[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : iso + 'Z') : '–';
const local = iso => iso ? new Date(iso).toLocaleString([], {
  month:'short', day:'numeric', hour:'2-digit', minute:'2-digit', hour12:false}) : '–';

/* Lights are 09:00 ON / 21:00 OFF KST, so ZT0 = 09:00. People schedule against
   this, not against the wall clock, so showing it removes an arithmetic step
   that is easy to get wrong at 3am. */
function ztNow(d) {
  const h = d.getHours() + d.getMinutes() / 60;
  const zt = (h - 9 + 24) % 24;
  const phase = zt < 12 ? 'light' : 'dark';
  return `ZT ${zt.toFixed(1)} · ${phase} phase`;
}

/* ---------- clock ---------- */
setInterval(() => {
  const d = new Date();
  $('#clock').textContent = d.toLocaleTimeString([], {hour12: false});
  $('#date').textContent = d.toLocaleDateString([], {
    weekday:'long', year:'numeric', month:'long', day:'numeric'});
  $('#zt').textContent = ztNow(d);
}, 1000);

/* ---------- pills ---------- */
function pill(el, cls, text) {
  const p = $(el);
  p.querySelector('.dot').className = 'dot ' + cls;
  p.querySelector('span').textContent = text;
}

function renderPills(s) {
  const a = s.allego;
  if (!a.reachable)      pill('#p-allego', 'bad', 'unreachable');
  else if (!a.server_running) pill('#p-allego', 'bad', 'server down');
  else if (a.problems && a.problems.length) pill('#p-allego', 'warn', a.problems[0].slice(0, 44));
  else if (isOn(a.recording)) pill('#p-allego', 'live', `recording · ${a.sample_freq/1000} kHz`);
  else pill('#p-allego', 'ok', `ready · ${a.system_mode} · ${a.sample_freq/1000} kHz`);

  const st = s.storage;
  pill('#p-disk', st.level === 'ok' ? 'ok' : st.level === 'warn' ? 'warn' : 'bad',
       `${gb(st.free_bytes)} free · ${st.hours_remaining} h at ${st.gb_per_hour} GB/h`);

  const n = s.nas;
  if (!n.mounted)         pill('#p-nas', 'bad', 'not mounted');
  else if (!n.sentinel_ok) pill('#p-nas', 'bad', 'sentinel missing');
  else pill('#p-nas', 'ok', `${gb(n.free_bytes)} free`);
}

/* ---------- setup form ---------- */
/* Re-read the configuration and rebuild the pickers. The settings panel calls
   this after adding or deleting something; init() is an IIFE and cannot be. */
async function reloadConfig() {
  CFG = await api('/api/users');
  renderPresetPicker();
  LAST_SETTING = $('#setting').value;
  await loadLayout();
}

function renderPresetPicker() {
  const lsel = $('#layout');
  lsel.innerHTML = '';
  for (const [name, t] of Object.entries(CFG.layouts)) {
    const o = document.createElement('option');
    o.value = name; o.textContent = t.label;
    lsel.appendChild(o);
  }
  // Shown when the ports match no saved layout. DISABLED: it is a description
  // of the current state, not an action. As a selectable option it did nothing,
  // which read as a broken control -- reported 2026-09-14.
  lsel.appendChild(Object.assign(document.createElement('option'),
    {value: 'custom', textContent: 'Custom (ports match no saved layout)',
     disabled: true}));

  const ssel = $('#setting');
  ssel.innerHTML = '';
  for (const [name, st] of Object.entries(CFG.settings)) {
    const o = document.createElement('option');
    o.value = name;
    o.textContent = `${st.label} — ${st.channels_per_animal} ch/mouse`;
    ssel.appendChild(o);
  }
  ssel.appendChild(Object.assign(document.createElement('option'),
    {value: CUSTOM_SETTING, textContent: '＋ Custom channels for this run…'}));

  const chs = $('#cs-hs');
  chs.innerHTML = Object.entries(CFG.headstages).map(([n, h]) =>
    `<option value="${esc(n)}">${esc(h.label)}</option>`).join('');
  renderPorts();
}

/* THE TEMPLATE SELECT IS A VIEW, NOT A SOURCE OF TRUTH.
   The declaration is (setting + SPLIT). A template is just a name for one
   combination of those, so the select shows whichever template matches, or
   "Custom". Keeping it as independent state is how it came to read
   "4 mice, unipolar LFP" over a rig declared as 8-mouse EEG/EMG: functionally
   harmless, and exactly the kind of label someone later believes. */
function syncLayoutSelect() {
  const setting = $('#setting').value;
  const match = Object.entries(CFG.layouts).find(([, t]) =>
    t.setting === setting && CFG.ports.every(p => !!t.splitters[p] === !!SPLIT[p]));
  $('#layout').value = match ? match[0] : 'custom';
}

/* The declaration versus what Allego actually enumerated. A disagreement means
   the strip would keep the wrong channels, discovered after the animals are
   done -- so it disables the buttons rather than warning. */
function renderPortCheck() {
  const chk = PRESET.check || {ok: true, ports: {}, problems: []};
  for (const div of document.querySelectorAll('.port')) {
    const p = div.dataset.port, row = chk.ports[p] || {};
    div.querySelector('[data-k=ch]').textContent =
      row.used === false ? 'not in use'
        : `${row.enumerated ?? '?'} ch, expects ${row.expected ?? '?'}`;
    div.querySelector('[data-k=derived]').textContent =
      (PRESET.slots || []).filter(s => s[0] === p).join(' · ') || '—';
    div.classList.toggle('bad', row.ok === false);
    div.classList.toggle('off', row.used === false);
  }
  $('#port-note').innerHTML = chk.ok
    ? '<span style="color:var(--ok)">The declared rig matches what Allego sees.</span>'
    : '<b style="color:var(--bad)">Cannot record:</b> '
      + chk.problems.map(x => `<div style="color:var(--bad)">• ${esc(x)}</div>`).join('');
  renderKeepNote();
}

/* ---------- the four ports ---------- */
function renderPorts() {
  const box = $('#ports');
  box.innerHTML = '';
  for (const port of CFG.ports) {
    const div = document.createElement('div');
    div.className = 'port';
    div.dataset.port = port;
    div.innerHTML = `
      <div class="hd"><span class="name">Port ${port}</span>
        <span class="ch" data-k="ch"></span></div>
      <label class="sw"><input type="checkbox" data-k="used"> In use</label>
      <label class="sw"><input type="checkbox" data-k="split"> SPI splitter</label>
      <div class="derived" data-k="derived"></div>`;
    const use = div.querySelector('[data-k=used]');
    const cb = div.querySelector('[data-k=split]');
    use.checked = !!USED[port];
    cb.checked = !!SPLIT[port];
    cb.disabled = !USED[port];
    use.addEventListener('change', () => {
      USED[port] = use.checked;
      cb.disabled = !use.checked;
      loadLayout();
    });
    cb.addEventListener('change', () => {
      SPLIT[port] = cb.checked;
      loadLayout();          // syncLayoutSelect() runs inside
    });
    box.appendChild(div);
  }
}

/* Resolve the declaration server-side: slots, channels, roles and the
   enumeration check all come from ONE call, so the page never reimplements the
   slot rule or the expected channel count. A second copy of either would drift
   from the one that actually decides what gets recorded. */
async function loadLayout() {
  try {
    const custom = customPayload();
    $('#custom-box').classList.toggle('hide', !custom);
    if (custom && !Object.keys(custom.roles).length) {
      $('#cs-preview').textContent = 'Add at least one signal.';
      $('#port-note').textContent = '';
      $('#slots').innerHTML = ''; $('#keep-note').textContent = '';
      $('#btn-now').disabled = $('#btn-schedule').disabled = true;
      return;
    }
    PRESET = await post('/api/layout/resolve',
                        {setting: custom ? '' : $('#setting').value,
                         splitters: SPLIT, custom,
                         ports_used: CFG.ports.filter(p => USED[p])});
  } catch (e) {
    // A channel problem belongs in the channel box, not in the port row, and
    // the old preview must go -- showing a valid-looking line that contradicts
    // what is typed is worse than showing nothing.
    const where = customPayload() ? '#cs-preview' : '#port-note';
    const sp = Object.assign(document.createElement('span'), {textContent: e.message});
    sp.style.color = 'var(--bad)';
    $(where).replaceChildren(sp);
    if (where === '#cs-preview') $('#port-note').textContent = '';
    $('#slots').innerHTML = '';
    $('#keep-note').textContent = '';
    $('#btn-now').disabled = $('#btn-schedule').disabled = true;
    return;
  }
  syncLayoutSelect();
  if (customPayload()) renderCustomPreview();
  renderPortCheck();
  const slots = $('#slots');
  slots.innerHTML = '';
  for (const slot of PRESET.slots) {
    const labels = PRESET.slot_channels[slot], roles = PRESET.roles[slot];
    const chans = labels.map((l, i) => roles[i] ? `${l} ${roles[i]}` : l).join(' · ');
    const div = document.createElement('div');
    div.className = 'slot';
    div.dataset.slot = slot;
    div.innerHTML = `
      <div class="hd"><span class="name">${esc(slot)}</span>
        <span class="ch">${esc(chans)}</span></div>
      <input placeholder="mouse ID" data-k="mouse" maxlength="32">
      <select data-k="type">${CFG.recording_types.map(
        t => `<option value="${esc(t)}">${esc((CFG.recording_type_labels || {})[t] || t)}</option>`).join('')}</select>`;
    const inp = div.querySelector('input');
    inp.addEventListener('input', () => {
      div.classList.toggle('on', !!inp.value.trim());
      renderKeepNote();
    });
    // The recording type picks the mouse's NAS folder (Baseline/Recovery) and
    // its code (B/R), so a change to it changes where the data lands. Without this the preview would
    // keep showing the previous condition, which is worse than showing none.
    div.querySelector('select').addEventListener('change', renderKeepNote);
    slots.appendChild(div);
  }
  $('#preset-note').textContent =
    `${PRESET.slots.length} slots, ${PRESET.all_labels.length} channels total`
    // Said BEFORE the run, not in a failure afterwards. This layout has no
    // wire-free floor under core/criteria.py, so no QC bundle will be made and
    // the strip cannot be re-judged from the original later. Last in the line
    // because it is the sentence, not a modifier on the channel count.
    + (PRESET.qc === 'none'
        ? ' \u2014 QC not applicable: no QC bundle is produced. '
          + (PRESET.qc_reason || '').trim()
        : '');
  renderKeepNote();
}

function gatherSlots() {
  const out = {};
  document.querySelectorAll('.slot').forEach(d => {
    const mouse = d.querySelector('[data-k=mouse]').value.trim();
    if (!mouse) return;
    out[d.dataset.slot] = {mouse_id: mouse,
                           recording_type: d.querySelector('[data-k=type]').value};
  });
  return out;
}

/* The ports this run will occupy: slot[0] is the port. Start now is also held
   back while one of them records or the rig is busy; Schedule is not, because a
   future window on a busy port is checked by the server (409 on overlap). */
let FORM_WHY = '';
const formPorts = () => [...new Set(Object.keys(gatherSlots()).map(k => k[0]))].sort();
function applyGate() {
  const a = (STATE && STATE.allego) || {};
  const up = !!(STATE && a.reachable);     // not before the first poll, not with Allego down
  const taken = formPorts().filter(p => ((a.ports || {})[p] || {}).recording);
  const busy = STATE && STATE.rig_busy && STATE.rig_busy.busy;
  $('#btn-schedule').disabled = !!FORM_WHY;
  $('#btn-now').disabled = !!FORM_WHY || !up || taken.length > 0 || !!busy || !!IMP_RUNNING || RESTARTING;
  const fp = formPorts();
  $('#run-ports').innerHTML = !fp.length ? '' : `This run will occupy port${fp.length > 1 ? 's' : ''} `
    + `<b>${fp.join(', ')}</b>; Stop affects only these.`
    + (taken.length ? `<div style="color:var(--bad)">Port ${taken.join(', ')} is recording now: `
        + `Start now is disabled (Schedule books a later window).</div>` : '')
    + (busy ? `<div style="color:var(--warn)">Rig busy: ${esc(STATE.rig_busy.reason || '')}. Start now is disabled.</div>` : '');
}

function renderKeepNote() {
  if (!PRESET) return;
  const slots = Object.keys(gatherSlots());
  const owner = $('#owner').value;
  // Two slots cannot hold the same animal. Said HERE, while the form is on
  // screen, because the alternative is finding out seven minutes after the
  // recording stopped: the cohort schema refuses duplicate ids, so no QC bundle
  // can be computed, so the run holds at FAILED_QC. Reported 2026-09-14.
  const filled = gatherSlots();
  // Case-folded: "HLBSSL31" and "hlbssl31" are one animal to everyone except a
  // string comparison, and two cards for one mouse is exactly what this guards.
  const seen = {};
  Object.entries(filled).forEach(([k, v]) =>
    (seen[v.mouse_id.toLowerCase()] ||= []).push(k));
  const dupes = Object.entries(seen).filter(([, ss]) => ss.length > 1);

  const why = !owner ? 'Choose who is recording first.'
            : !$('#batch').value.trim()
              ? 'Enter a recording batch name (e.g. HLBSSL, or SCREEN for a test): '
                + 'it is the NAS folder the mice are filed under.'
            : (PRESET && PRESET.check && !PRESET.check.ok)
              ? 'The declared rig does not match what Allego sees.'
            : !slots.length ? 'Enter at least one mouse ID.'
            : dupes.length
              ? 'The same mouse ID is in more than one slot: '
                + dupes.map(([, ss]) => ss.map(k => `${k} (${filled[k].mouse_id})`)
                    .join(' and ')).join('; ')
                + '. Each animal needs its own ID.'
            : '';
  const clashing = new Set(dupes.flatMap(([, ss]) => ss));
  document.querySelectorAll('.slot').forEach(d =>
    d.classList.toggle('dupe', clashing.has(d.dataset.slot)));

  FORM_WHY = why;
  applyGate();
  if (why) { $('#keep-note').textContent = why; return; }
  const labels = slots.flatMap(s => PRESET.slot_channels[s]).sort();
  $('#keep-note').innerHTML =
    `<b>${labels.length} channels will be kept</b> for ${slots.length} `
    + `${slots.length === 1 ? 'mouse' : 'mice'}, exported as one CSV per mouse: `
    + `<span class="mono">${esc(labels.join(', '))}</span>`;
  renderNameNote();
}

/* The folder and file names this run will carry on the NAS, shown BEFORE it
   starts. Asked of the server rather than rebuilt here: one rule, one place. A
   second copy of a naming rule in the UI would drift from the one that actually
   writes the folder, and the drift would only show up on the NAS. */
let nameSeq = 0;
async function renderNameNote() {
  const el = $('#name-note');
  const batch = $('#batch').value.trim();
  const owner = $('#owner').value;
  if (!batch || !owner || !PRESET) {
    el.innerHTML = batch ? '' :
      '<span style="color:var(--bad)">A batch name is required: each mouse is filed '
      + `under <span class="mono">${esc((CFG && CFG.nas_root) || '02_Data_Sleep')}/&lt;user&gt;/`
      + '&lt;batch&gt;/Baseline|Recovery/</span>.</span>';
    return;
  }
  const seq = ++nameSeq;
  try {
    const r = await post('/api/naming/preview', {
      owner, setting: customPayload() ? '' : $('#setting').value,
      custom: customPayload(), splitters: SPLIT,
      ports_used: CFG.ports.filter(p => USED[p]),
      slots: gatherSlots(),
      batch_name: batch, start_at: $('#start').value || null});
    if (seq !== nameSeq) return;          // a later keystroke already answered
    if (!r.mice.length) { el.innerHTML = ''; return; }
    el.innerHTML = `Each mouse arrives as one CSV + info.json in `
      + `<span class="mono">${esc(r.root)}/</span>:<br>`
      + r.mice.map(m => `<span class="mono">&nbsp;&nbsp;${esc(m.slot)}&nbsp;&nbsp;`
          + `${esc(m.batch)}/${esc(m.condition_dir)}/<b>${esc(m.folder)}</b>/${esc(m.file_base)}.csv</span>`)
          .join('<br>')
      // The folders are dated by the day the recording STARTS. After 09:00 the
      // pre-filled Start at is tomorrow, so the two buttons produce two
      // different dates and the preview must not silently show one of them.
      + (r.if_started_now
          ? `<br>Dated by the scheduled start. <b>Start now</b> instead and they `
            + `would be dated <span class="mono">${esc(r.today)}</span>.`
          : '');
  } catch (e) {
    if (seq !== nameSeq) return;
    el.innerHTML = `<span style="color:var(--bad)">${esc(e.message)}</span>`;
  }
}

/* ---------- live panel ---------- */
/* Several runs can record at once now (one run per set of ports), so this lists
   every active run, each with its own Stop. Stop affects only that run's ports. */
const activeRuns = s => (Array.isArray(s.active_runs) ? s.active_runs
    : s.active_run ? [s.active_run] : [])
  .filter(r => ['STARTING','RECORDING','STOPPING'].includes(r.state));
// Ports of a run: the new field, else derived from the slots (slot[0] is the port).
const runPorts = r => r.ports && r.ports.length ? r.ports
  : [...new Set((r.occupied || Object.keys(r.slots || {})).map(k => k[0]))].sort();
// Per-port files. Old runs have one combined file in base_name/data_path.
function runFiles(r) {
  const live = (STATE && STATE.allego && STATE.allego.ports) || {};
  const bob = r.bytes_on_disk;
  const pf = r.port_files && Object.keys(r.port_files).length ? r.port_files : null;
  if (!pf) return [{port: runPorts(r).join(''), name: r.base_name,
                    bytes: typeof bob === 'number' ? bob : null}];
  return Object.entries(pf).map(([p, f]) => ({port: p, name: f.base_name,
    bytes: (bob && typeof bob === 'object' ? bob[p] : null) ?? (live[p] || {}).bytes ?? null}));
}
const bytesTxt = b => b > 0 ? (b < 1e9 ? (b / 1e6).toFixed(1) + ' MB' : gb(b)) : '0 bytes';
let liveHtml = '';
function renderLive(s) {
  const runs = activeRuns(s);
  $('#live').classList.toggle('hide', !runs.length);
  if (!runs.length) { liveHtml = ''; $('#live-runs').innerHTML = ''; return; }
  const html = runs.map(r => {
    const files = runFiles(r);
    const growth = (r.results || {}).growth;
    return `<div class="livecard" data-run="${esc(r.run_id)}" style="margin-bottom:14px">
      <div class="row" style="gap:26px">
        <div><label>Run</label><div class="mono">${esc(r.run_id)}</div></div>
        <div><label>Owner</label><div>${esc(r.owner)}</div></div>
        <div><label>Batch</label><div>${esc(r.batch_name)}</div></div>
        <div><label>State</label><div>${esc(r.state)}</div></div>
        <div><label>Ports</label><div class="mono">${esc(runPorts(r).join(' '))}</div></div>
        <div><label>Elapsed</label><div class="mono elapsed"
          data-start="${esc(r.actual_start || '')}">–</div></div>
        <div><label>Stops at</label><div class="mono">${r.scheduled_stop ? local(r.scheduled_stop) : 'manual'}</div></div>
        <div style="margin-left:auto"><button class="danger" data-stop="${esc(r.run_id)}">Stop this run</button></div>
      </div>
      <table style="margin-top:6px"><thead><tr><th>Port</th><th>File</th><th>On disk</th></tr></thead><tbody>
        ${files.map(f => `<tr><td class="mono">${esc(f.port)}</td>
          <td class="mono">${esc(f.name || '…')}</td>
          <td class="mono">${f.bytes == null ? '–' : bytesTxt(f.bytes)}</td></tr>`).join('')}
      </tbody></table>
      <div class="note">${Object.entries(r.slots || {}).map(([k, v]) =>
        `<span class="tag">${esc(k)} · ${esc(v.mouse_id)} · ${esc(v.recording_type)}</span>`).join(' ')}</div>
      ${growth && !growth.growing
        ? `<div class="badbox"><b>The recorder says ON but no bytes landed in ${esc(growth.window_s)} s.</b> `
          + `This needs a person — the run is not producing data.</div>`
        : `<div class="warnbox lag" data-start="${esc(r.actual_start || '')}"
             data-bytes="${files.reduce((n, f) => n + (f.bytes || 0), 0)}">
             The file size does not move for about 30 seconds after a healthy start —
             Allego flushes it in blocks. <b>0 bytes here is normal at first</b> and is not
             evidence that anything is wrong.</div>`}
    </div>`;
  }).join('');
  if (html !== liveHtml) { liveHtml = html; $('#live-runs').innerHTML = html; }
  tickLive();
}
function tickLive() {
  document.querySelectorAll('#live-runs .elapsed').forEach(el => {
    el.textContent = el.dataset.start ? dur((Date.now() - new Date(el.dataset.start)) / 1000) : '–';
  });
  document.querySelectorAll('#live-runs .lag').forEach(el => {
    const t = el.dataset.start ? (Date.now() - new Date(el.dataset.start)) / 1000 : 0;
    el.classList.toggle('hide', !(t < 90 && !(+el.dataset.bytes > 0)));
  });
}
setInterval(tickLive, 1000);

/* ---------- history ---------- */
const STATE_CLASS = s =>
  s === 'DONE' ? 'ok' : s === 'RECORDING' ? 'live'
  : s.startsWith('FAILED') ? 'bad'
  : (s === 'UPLOAD_PENDING' || s === 'EXPORTED') ? 'warn' : '';

let RUNS = [];
async function renderRuns() {
  const {runs} = await api('/api/runs?limit=40');
  RUNS = runs;
  const tb = $('#runs');
  if (!runs.length) {
    tb.innerHTML = '<tr><td colspan="9" class="note">No runs yet.</td></tr>';
    return;
  }
  tb.innerHTML = runs.map(r => {
    const mice = Object.entries(r.slots)
      .map(([k, v]) => `${esc(k)}:${esc(v.mouse_id)}`).join(' ');
    let d = '–';
    if (r.actual_start && r.actual_stop)
      d = dur((new Date(r.actual_stop) - new Date(r.actual_start)) / 1000);
    const strip = (r.results && r.results.strip) || null;
    const exp = (r.results && r.results.export) || null;
    const up = (r.results && r.results.upload && r.results.upload.mice) ? r.results.upload : null;
    const retry = r.state.startsWith('FAILED') || r.state === 'UPLOAD_PENDING'
      ? `<button class="ghost" style="padding:4px 10px;font-size:12px"
           onclick="retryRun('${r.run_id}','${r.state}')"
           title="${esc((r.error || '').slice(0, 300))}">retry</button>`
      // A reservation made by mistake (a wrong date, 2026-10-14) could only be
      // removed through the API. /abort already refuses anything that has started.
      : (r.state === 'SCHEDULED' || r.state === 'DRAFT')
      ? `<button class="ghost" style="padding:4px 10px;font-size:12px"
           onclick="cancelRun('${r.run_id}')">cancel</button>` : '';
    const ports = esc(runPorts(r).join(' ')) || '–';
    const files = r.port_files && Object.keys(r.port_files).length
      ? Object.entries(r.port_files).map(([p, f]) => `${esc(p)}: ${esc(f.base_name)}`).join('<br>')
      : esc(r.base_name || '');
    return `<tr>
      <td class="mono">${esc(r.run_id)}</td>
      <td>${esc(r.owner)}</td>
      <td class="mono" style="font-size:11px"><b>${ports}</b><br>${files}</td>
      <td class="mono" style="font-size:11px">${mice}</td>
      <td><span class="tag ${STATE_CLASS(r.state)}">${esc(r.state)}</span>${
        (r.results && r.results.start_warning)
          ? ` <span class="tag bad" title="${esc(r.results.start_warning)}">port missing at start</span>`
          : ''}</td>
      <td class="mono">${local(r.actual_start || r.scheduled_start)}</td>
      <td class="mono">${d}</td>
      <td class="mono">${up ? `${up.mice.length} mice on NAS`
        : exp ? `${exp.n_mice} CSVs, ${(exp.bytes / 1e9).toFixed(1)} GB`
        : strip ? strip.saving_pct + '% smaller'
        : (r.results && r.results.qc_bundle_skipped) ? 'no QC bundle'
        : (r.results && r.results.qc_not_applicable) ? 'QC n/a' : '–'}</td>
      <td>${retry}</td></tr>`;
  }).join('');
}

window.retryRun = async (id, state) => {
  let body;
  if (state === 'FAILED_QC') {
    // Retrying FAILED_QC unchanged just fails again the same way, so the button
    // would be a dead end. Offer the only two real options, and make the
    // destructive one state exactly what is lost before it is chosen.
    const skip = confirm(
      'This run has no QC bundle.\n\n' +
      'Stripping removes the wire-free channels that this project measures every ' +
      'other channel against, so once stripped the recording can NEVER be quality-' +
      'checked again. The cached features are the only surviving record of them.\n\n' +
      'OK  = strip it anyway, without a QC bundle (fine for a test recording)\n' +
      'Cancel = leave it alone; compute the bundle first with cards/ladder.py\n\n' +
      'The choice is recorded on this run either way.');
    if (!skip) {
      toast('Left alone. Compute the QC bundle, then press retry again.', 'ok');
      return;
    }
    body = {skip_qc_bundle: true};
  }
  try {
    await post(`/api/runs/${id}/postprocess`, body);
    toast(body ? `${id} queued, stripping WITHOUT a QC bundle` : `queued ${id}`, 'ok');
  } catch (e) { toast(e.message, 'bad'); }
  renderRuns();
};

window.cancelRun = async id => {
  const {runs} = await api('/api/runs?limit=40');
  const r = runs.find(x => x.run_id === id);
  if (!r || !confirm(`Cancel this reservation?\n\n${id} · ${r.owner} · batch ${r.batch_name}\n` +
                     `start ${local(r.scheduled_start)}  stop ${local(r.scheduled_stop)}\n\n` +
                     'Nothing has been recorded for it. It stays in the list as ABORTED.')) return;
  try {
    await post(`/api/runs/${id}/abort`);
    toast(`cancelled ${id}`, 'ok');
  } catch (e) { toast(e.message, 'bad'); }
  renderRuns();
};

/* ---------- actions ---------- */
async function createRun(schedule) {
  const slots = gatherSlots();
  if (!Object.keys(slots).length) {
    toast('Enter at least one mouse ID first.', 'bad'); return null;
  }
  if (PRESET && PRESET.check && !PRESET.check.ok) {
    toast('The declared rig does not match what Allego sees.', 'bad'); return null;
  }
  const custom = customPayload();
  const body = {owner: $('#owner').value, slots,
                layout: custom ? 'custom' : $('#layout').value,
                setting: custom ? '' : $('#setting').value,
                custom, splitters: SPLIT,
                ports_used: CFG.ports.filter(p => USED[p]),
                batch_name: $('#batch').value.trim()};
  if (schedule) {
    if (!$('#start').value) { toast('Pick a start time.', 'bad'); return null; }
    body.start_at = $('#start').value;
    if ($('#stop').value) body.stop_at = $('#stop').value;
  }
  $('#form-error').classList.add('hide');
  return post('/api/runs', body);
}

/* A refused booking (409 on port overlap) is shown verbatim and stays on screen,
   with the conflicting run looked up from the run list when its id is in the text. */
function formError(e) {
  toast(e.message, 'bad');
  const hit = RUNS.find(r => e.message.includes(r.run_id));
  const box = $('#form-error');
  box.textContent = e.message + (hit ? `\nConflicting run: ${hit.run_id} · ${hit.owner} · `
    + `ports ${runPorts(hit).join(' ')} · ${hit.state} · ${local(hit.scheduled_start)} to ${local(hit.scheduled_stop)}` : '');
  box.classList.remove('hide');
}

$('#btn-schedule').onclick = async () => {
  try {
    const r = await createRun(true);
    if (r) { toast(`Scheduled ${r.run_id} for ${local(r.scheduled_start)}`, 'ok'); refresh(); }
  } catch (e) { formError(e); }
};

$('#btn-now').onclick = async () => {
  const slots = gatherSlots();
  const n = Object.keys(slots).length;
  if (!confirm(`Start recording now with ${n} ${n === 1 ? 'mouse' : 'mice'} on port ${formPorts().join(', ')}?\n\n`
      + Object.entries(slots).map(([k, v]) => `  ${k}  ${v.mouse_id}  ${v.recording_type}`).join('\n')
      + `\n\nThis records ALL channels; the selection only affects the stripped copy `
      + `and the per-mouse CSVs.`))
    return;
  try {
    const r = await createRun(false);
    if (!r) return;
    await post(`/api/runs/${r.run_id}/start`);
    toast(`Recording started (${r.run_id})`, 'ok');
    refresh();
  } catch (e) { formError(e); }
};

$('#live-runs').onclick = async e => {
  const id = e.target.dataset && e.target.dataset.stop;
  const r = id && activeRuns(STATE).find(x => x.run_id === id);
  if (!r) return;
  const ports = runPorts(r).join(', ');
  if (!confirm(`Stop recording ${r.base_name || r.run_id}?\n\n`
    + `This stops only this run's ports (${ports}). Any other run that is recording keeps recording.\n\n`
    + `It will then be stripped to ${r.keep_labels.length} channels, exported as `
    + `one CSV per mouse and uploaded to ${r.owner}'s folder on the NAS.`)) return;
  try {
    await post(`/api/runs/${r.run_id}/stop`);
    toast('Stopped. Post-processing queued.', 'ok');
    refresh();
  } catch (err) { toast(err.message, 'bad'); }
};

// Debounced: one request per pause in typing, not one per keystroke.
let batchTimer = null;
$('#batch').addEventListener('input', () => {
  clearTimeout(batchTimer);
  // renderKeepNote gates the buttons on a batch name, then calls renderNameNote
  batchTimer = setTimeout(renderKeepNote, 250);
});
// The date in the folder name is the date the recording will CARRY, so changing
// the scheduled start changes it.
$('#start').addEventListener('change', renderNameNote);

$('#setting').onchange = (e) => {
  if (e.target.value === CUSTOM_SETTING) seedCustomFrom(LAST_SETTING);
  else LAST_SETTING = e.target.value;
  loadLayout();
};

/* Start Custom as a copy of the setting already in use, so the headstage and
   the sites are the rig's, not an arbitrary first entry. */
function seedCustomFrom(name) {
  const st = (CFG.settings || {})[name] || (CFG.settings || {})[LAST_SETTING]
           || Object.values(CFG.settings || {})[0];
  if (!st) return;
  $('#cs-hs').value = st.headstage;
  $('#cs-roles').innerHTML = '';
  Object.entries(st.roles).sort((a, b) => a[1] - b[1])
    .forEach(([r, o]) => addCustomRole(r, o));
}
$('#layout').onchange = e => {
  const t = CFG.layouts[e.target.value];
  if (!t) return;                       // "Custom": keep whatever is set
  $('#setting').value = t.setting;
  SPLIT = Object.assign({}, t.splitters);
  renderPorts();              // USED is deliberately left alone: whether a port
  loadLayout();               // is plugged in is a fact about the rig, not a
                              // property of the layout you picked.
};
$('#owner').onchange = e => {
  SELECTED = e.target.value;
  if (!SELECTED) { renderKeepNote(); return; }
  const want = CFG.users[SELECTED].default_layout;
  const t = CFG.layouts[want];
  if (t) {
    $('#setting').value = t.setting;
    SPLIT = Object.assign({}, t.splitters);
    // Choosing a person is the start of a fresh setup, so every port comes back
    // into use; a port left switched off from someone else's session would
    // silently drop animals from this one.
    USED = Object.fromEntries(CFG.ports.map(p => [p, true]));
    renderPorts();
    loadLayout();
    return;
  }
  renderKeepNote();
};

/* ====================================================================== */
/* RIG, PORTS, IMPEDANCE, RESTART (per-port recording on Allego 4, 2026-10-28)  */
/*                                                                         */
/* Rig-wide actions (impedance, restart) need the WHOLE rig idle: Allego     */
/* refuses impedance while streaming and a restart resets the rate. The      */
/* buttons are disabled otherwise and the server refuses with 409 as well.   */
/* Every field read here is optional so an old backend still renders.        */
/* ====================================================================== */
let PORTS_API = null, PORTS_TICK = 0, IMP_RUNNING = null, RESTARTING = false;
const IMP = {};                       // port -> last saved/measured result or null
const PORT_LETTERS = () => (CFG && CFG.ports) || ['A', 'B', 'C', 'D'];

async function loadPortsApi() {
  try { PORTS_API = await api('/api/ports'); } catch (e) { PORTS_API = null; }
}
// Merge /api/state (fresh) over /api/ports (reservations); old backends send a bare count.
function portInfo(p) {
  const raw = ((STATE.allego || {}).ports || {})[p];
  const base = raw && typeof raw === 'object' ? raw : {channels: raw || 0, legacy: typeof raw === 'number'};
  return {...(((PORTS_API || {}).ports || {})[p] || {}), ...base};
}
// '' when the rig is idle, else the reason it is not.
function rigIdle() {
  if (!STATE) return 'Waiting for the first state poll.';
  const a = STATE.allego || {};
  if (!a.reachable) return 'Allego is not reachable.';
  if (PORT_LETTERS().some(p => portInfo(p).legacy)) return 'This backend does not support rig operations.';
  if (IMP_RUNNING || RESTARTING) return 'A rig operation is running.';
  if (STATE.rig_busy && STATE.rig_busy.busy) return `Rig busy: ${STATE.rig_busy.reason || ''}`;
  if (isOn(a.recording) || PORT_LETTERS().some(p => portInfo(p).recording)) return 'A port is recording.';
  if (activeRuns(STATE).length) return 'A run is active.';
  return '';
}

function renderRig(s) {
  const a = s.allego || {};
  const hz = a.sample_freq;
  let m = a.measured_rate;
  // measured_rate may be a ratio to the nominal rate or Hz; show a ratio either way.
  const ratio = m == null ? null : (m > 20 && hz ? m / hz : m);
  const kv = (k, v, cls) => `<div><label>${k}</label><div class="mono"${cls ? ` style="color:var(--${cls})"` : ''}>${v}</div></div>`;
  $('#rig-kv').innerHTML =
      kv('Mode', esc(a.system_mode ?? '–'))
    + kv('Sample rate', hz ? `${hz} Hz` : '–')
    + kv('Measured rate', ratio == null ? '–' : `${ratio.toFixed(2)}x`
        + (Math.abs(ratio - 1) > 0.1 ? ' (NOT 1.0x: do not record)' : ''),
        ratio != null && Math.abs(ratio - 1) > 0.1 ? 'bad' : '')
    + kv('Streaming', isOn(a.streaming) ? 'ON' : 'OFF')
    + kv('Recording', isOn(a.recording) ? 'ON' : 'OFF')
    + (a.split_files_by_port == null ? '' : kv('Split files by port', a.split_files_by_port ? 'true' : 'false (one combined file)',
        a.split_files_by_port ? '' : 'warn'))
    + (a.server_version ? kv('Allego', esc(a.server_version)) : '');
  $('#rig-problems').innerHTML = (a.problems || []).map(x => `<div class="warnbox">${esc(x)}</div>`).join('')
    + (a.error ? `<div class="badbox">${esc(a.error)}</div>` : '');
  const busy = s.rig_busy && s.rig_busy.busy;
  $('#busy-banner').classList.toggle('hide', !busy);
  if (busy) $('#busy-banner').innerHTML = `<b>Rig busy:</b> ${esc(s.rig_busy.reason || 'a rig operation is running')}. Recording and rig changes are refused until it ends.`;
  const why = rigIdle();
  $('#btn-restart').disabled = !!why;
  $('#restart-why').textContent = why;
}

function renderCards() {
  const runs = activeRuns(STATE);
  $('#pcards').innerHTML = PORT_LETTERS().map(p => {
    const i = portInfo(p), n = i.channels || 0, rs = i.next_reservation;
    const mins = rs && rs.start ? (new Date(rs.start) - Date.now()) / 60000 : null;
    const soon = mins != null && mins <= 60;
    const [cls, tag] = i.recording ? ['rec', 'recording'] : !n ? ['none', 'no headstage']
      : soon ? ['soon', `reserved in ${Math.max(0, Math.round(mins))} min`] : ['', 'idle'];
    const run = runs.find(r => r.run_id === i.run_id);
    const why = rigIdle() || (!n ? 'No headstage on this port.' : '');
    return `<div class="pcard ${cls}">
      <div class="hd"><b>Port ${p}</b><span class="tag ${i.recording ? 'live' : soon ? 'warn' : !n ? '' : 'ok'}">${tag}</span></div>
      <div>${n} channels${i.selected_channels != null ? `, ${i.selected_channels} selected` : ''}</div>
      ${i.legacy ? '' : `<div>Recording: <b>${i.recording ? 'ON' : 'OFF'}</b></div>`}
      ${i.recording ? `<div>Run: <span class="mono">${esc(i.run_id || '?')}</span> · ${esc((run && run.owner) || i.owner || '?')}${run ? ` · ${esc(run.batch_name)}` : ''}</div>
        <div class="mono" style="word-break:break-all">${esc(i.file || '…')}</div>
        <div class="mono">${i.bytes == null ? '–' : bytesTxt(i.bytes)}</div>` : ''}
      <div>Next: ${rs ? `${esc(rs.owner)} · ${local(rs.start)} to ${local(rs.stop)} <span class="mono">${esc(rs.run_id)}</span>` : 'none'}</div>
      <button class="ghost" data-imp="${p}" ${why ? 'disabled' : ''} title="${esc(why)}">${IMP_RUNNING === p ? 'Measuring…' : 'Impedance'}</button>
    </div>`;
  }).join('');
}

$('#pcards').onclick = async e => {
  const p = e.target.dataset && e.target.dataset.imp;
  if (!p || rigIdle()) return;
  if (!confirm(`Measure impedance on port ${p}?\n\n`
    + `This STOPS data streaming for about 30 seconds (Allego refuses the measurement while streaming). `
    + `It cannot run while anyone is recording, and nobody can start a recording until it finishes.`)) return;
  IMP_RUNNING = p; renderCards(); renderRig(STATE);
  try {
    IMP[p] = await post(`/api/ports/${p}/impedance`);
    toast(`Impedance measured on port ${p}`, 'ok');
  } catch (err) { toast(err.message, 'bad'); }
  IMP_RUNNING = null;
  renderImpedance(); refresh();
};

async function loadImpedance() {
  for (const p of PORT_LETTERS()) {
    try { IMP[p] = await api(`/api/ports/${p}/impedance`); } catch (e) { IMP[p] = IMP[p] || null; }
  }
  renderImpedance();
}

// Canonical bipolar channels are /1 /2 /33 /34 on every port.
const CANON = /\/(1|2|33|34)$/;
function renderImpedance() {
  $('#imp-panel').innerHTML = PORT_LETTERS().filter(p => IMP[p]).map(p => {
    const r = IMP[p];
    return `<details style="margin-top:10px" open><summary><b>Port ${p} impedance</b> · saved ${utcLocal(r.measured_utc)}
        · ${r.channels.length} channels${r.duration_s != null ? ` · ${Math.round(r.duration_s)} s` : ''}</summary>
      <table style="max-width:420px"><thead><tr><th>Label</th><th>kΩ</th><th>Phase</th></tr></thead><tbody>
      ${r.channels.map(c => `<tr class="${CANON.test(c.label) ? 'canon' : ''}"><td class="mono">${esc(c.label)}</td>
        <td class="mono">${Number(c.kohm).toFixed(1)}</td><td class="mono">${Number(c.phase_deg).toFixed(1)}°</td></tr>`).join('')}
      </tbody></table>
      <div class="note">Highlighted: canonical bipolar channels /1 /2 /33 /34.</div></details>`;
  }).join('');
}

function stateBrief(x) {
  if (!x) return '–';
  const ch = x.ports ? Object.entries(x.ports).map(([p, v]) => `${p}:${v && typeof v === 'object' ? v.channels : v}`).join(' ') : null;
  return [x.system_mode, x.sample_freq != null ? `${x.sample_freq} Hz` : null,
          x.streaming != null ? `streaming ${x.streaming}` : null,
          x.split_files_by_port != null ? `split ${x.split_files_by_port}` : null,
          ch && `channels ${ch}`].filter(Boolean).join(' · ') || JSON.stringify(x);
}
$('#btn-restart').onclick = async () => {
  if (rigIdle()) return;
  if (!confirm('Restart Allego (same mode)?\n\n'
    + 'It re-enumerates the headstages, resets the sample rate (the console restores 1000 Hz afterwards) '
    + 'and takes about 15 seconds. It cannot run while anyone is recording, and nobody can start a recording '
    + 'until it finishes.')) return;
  RESTARTING = true; renderRig(STATE); renderCards();
  $('#restart-result').textContent = 'Restarting… (about 15 s)';
  try {
    const r = await post('/api/allego/restart');
    $('#restart-result').innerHTML = `Restarted in ${Math.round(r.duration_s)} s.<br>Before: ${esc(stateBrief(r.before))}<br>After: ${esc(stateBrief(r.after))}`;
    toast('Allego restarted', 'ok');
  } catch (err) { $('#restart-result').textContent = ''; toast(err.message, 'bad'); }
  RESTARTING = false;
  refresh();
};

/* ---------- poll ---------- */
async function refresh() {
  try {
    STATE = await api('/api/state');
    $('#offline').classList.add('hide');
    renderPills(STATE);
    renderRig(STATE);
    if (PORTS_TICK++ % 5 === 0) await loadPortsApi();   // reservations change slowly
    renderCards();
    renderLive(STATE);
    applyGate();
    await renderRuns();
  } catch (e) {
    $('#offline').classList.remove('hide');
  }
}

(async function init() {
  try {
    CFG = await api('/api/users');
  } catch (e) {
    $('#offline').classList.remove('hide'); return;
  }
  const os = $('#owner');
  // NO DEFAULT OWNER, deliberately. The API returns users alphabetically, so a
  // default would silently pre-select whoever sorts first -- which on a shared
  // rig is precisely how one person's run ends up in another person's NAS
  // folder. Choosing a name has to be a deliberate act.
  const ph = document.createElement('option');
  ph.value = ''; ph.textContent = '— choose —'; ph.disabled = true; ph.selected = true;
  os.appendChild(ph);
  for (const u of Object.keys(CFG.users)) {
    const o = document.createElement('option');
    o.value = u; o.textContent = u; os.appendChild(o);
  }
  renderPresetPicker();
  await loadLayout();

  // default: next 09:00 (ZT0), running 24 h -- the shape almost every run here has
  const d = new Date(); d.setSeconds(0, 0);
  d.setHours(9, 0, 0, 0); if (d <= new Date()) d.setDate(d.getDate() + 1);
  const fmt = x => new Date(x - x.getTimezoneOffset() * 60000)
    .toISOString().slice(0, 19);
  $('#start').value = fmt(d);
  const e = new Date(d); e.setDate(e.getDate() + 1);
  $('#stop').value = fmt(e);
  $('#start-hint').textContent = '(local time · ZT0 is 09:00)';

  await refresh();
  loadImpedance();
  setInterval(refresh, 2000);
})();

/* ====================================================================== */
/* RIG SETTINGS                                                            */
/*                                                                         */
/* Collapsed by default: it is not part of the daily path, and the daily    */
/* path should not have to scroll past it.                                  */
/* ====================================================================== */
let SETTINGS = null;

$('#settings-head').onclick = async () => {
  const body = $('#settings-body'), shown = !body.classList.contains('hide');
  body.classList.toggle('hide', shown);
  $('#settings-caret').textContent = shown ? '▸ show' : '▾ hide';
  if (!shown) await loadSettings();
};

async function loadSettings() {
  SETTINGS = await api('/api/settings');

  $('#set-list').innerHTML = Object.entries(SETTINGS.settings).map(([n, s]) => {
    const sites = Object.entries(s.roles)
      .sort((a, b) => a[1] - b[1]).map(([r, o]) => `${esc(r)}=/${o}`).join(', ');
    // "no QC criterion" is a property of the layout, not a failure of the run,
    // and it is said here as well as before a run so nobody meets it first in
    // an error message.
    const qc = s.qc === 'none'
      ? ` <span style="color:var(--warn)">no QC criterion</span>` : '';
    const del = s.editable
      ? ` <a href="#" data-del-set="${esc(n)}" style="color:var(--bad)">delete</a>`
      : ` <span style="color:var(--faint)">curated</span>`;
    return `<div><span class="mono">${esc(n)}</span> — ${esc(s.label)}: `
         + `<span class="mono">${sites}</span>${qc}${del}`
         + (s.seen_in ? `<br><span style="color:var(--faint)">seen in ${esc(s.seen_in)}</span>` : '')
         + `</div>`;
  }).join('');

  $('#lay-list').innerHTML = Object.entries(SETTINGS.layouts).map(([n, t]) => {
    const split = esc(CFG.ports.filter(p => t.splitters[p]).join(', ')) || 'none';
    const del = t.editable
      ? ` <a href="#" data-del-lay="${esc(n)}" style="color:var(--bad)">delete</a>`
      : ` <span style="color:var(--faint)">curated</span>`;
    return `<div><span class="mono">${esc(n)}</span> — ${esc(t.label)}: `
         + `${esc(t.setting)}, splitters on ${split}${del}</div>`;
  }).join('');

  $('#hs-list').innerHTML = Object.entries(SETTINGS.headstages).map(([n, h]) =>
    `<div><span class="mono">${esc(n)}</span> — ${esc(h.label)}: ${esc(h.slots_per_chip)} slots, `
    + `${esc(h.real_channels)} real, ${h.bipolar_in_hardware ? 'bipolar' : 'unipolar'}`
    + (h.splitter_verified ? '' : ', <span style="color:var(--warn)">splitter unverified</span>')
    + (h.source ? `<br><span style="color:var(--faint)">${esc(h.source)}</span>` : '')
    + `</div>`).join('');

  $('#audit-list').innerHTML = (SETTINGS.history || []).length
    ? SETTINGS.history.map(h =>
        `<div><span class="mono">${esc(h.utc)}</span> ${esc(h.action)} `
        + `<b>${esc(h.name || '')}</b>${h.who ? ' by ' + esc(h.who) : ''}</div>`).join('')
    : '<span style="color:var(--faint)">nothing changed yet</span>';

  const hs = $('#ns-hs');
  hs.innerHTML = Object.entries(SETTINGS.headstages).map(([n, h]) =>
    `<option value="${esc(n)}">${esc(h.label)}</option>`).join('');
  if (!$('#ns-roles').children.length) { addRoleRow(); addRoleRow(); }
  previewSetting();

  document.querySelectorAll('[data-del-set]').forEach(a => a.onclick = async e => {
    e.preventDefault();
    const n = a.dataset.delSet;
    if (!confirm(`Delete the recording setting "${n}"?`)) return;
    try { await remove(`/api/settings/recording/${n}`); toast(`deleted ${n}`, 'ok'); }
    catch (err) { toast(err.message, 'bad'); }
    await loadSettings(); await reloadConfig();
  });
  document.querySelectorAll('[data-del-lay]').forEach(a => a.onclick = async e => {
    e.preventDefault();
    const n = a.dataset.delLay;
    if (!confirm(`Delete the layout "${n}"?`)) return;
    try { await remove(`/api/settings/layout/${n}`); toast(`deleted ${n}`, 'ok'); }
    catch (err) { toast(err.message, 'bad'); }
    await loadSettings(); await reloadConfig();
  });
}

function addRoleRow(role = '', site = '') {
  const div = document.createElement('div');
  div.className = 'row';
  div.style.marginTop = '6px';
  div.innerHTML =
    `<div><input data-k="role" placeholder="signal name, e.g. eeg" maxlength="24" value="${esc(role)}"></div>`
  + `<div><input data-k="site" type="number" min="1" max="64" placeholder="site" value="${esc(site)}" style="width:90px"></div>`
  + `<div><button class="ghost" data-k="drop">−</button></div>`;
  div.querySelector('[data-k=drop]').onclick = () => { div.remove(); previewSetting(); };
  div.querySelectorAll('input').forEach(i => i.addEventListener('input', previewSetting));
  $('#ns-roles').appendChild(div);
}
$('#ns-addrole').onclick = () => { addRoleRow(); previewSetting(); };
$('#ns-hs').onchange = previewSetting;

function gatherRoles() {
  const out = {};
  document.querySelectorAll('#ns-roles .row').forEach(d => {
    const r = d.querySelector('[data-k=role]').value.trim();
    const s = d.querySelector('[data-k=site]').value.trim();
    if (r && s) out[r] = parseInt(s, 10);
  });
  return out;
}

/* Show the exact sites the strip would keep, and whether a QC floor exists,
   BEFORE the setting is saved. The floor rule derives base+n..base+real, which
   only describes sites running 1..n; anything else has no criterion and must
   say why. Telling someone that at save time is far better than at 09:00. */
function previewSetting() {
  const roles = gatherRoles();
  const hs = SETTINGS && SETTINGS.headstages[$('#ns-hs').value];
  const el = $('#ns-preview'), qcbox = $('#ns-qcbox');
  if (!hs || !Object.keys(roles).length) {
    el.textContent = 'Add at least one signal.'; qcbox.classList.add('hide'); return;
  }
  const sites = Object.values(roles).sort((a, b) => a - b);
  const over = sites.filter(s => s > hs.real_channels);
  const dup = sites.length !== new Set(sites).size;
  const contiguous = sites.every((s, i) => s === i + 1);
  qcbox.classList.toggle('hide', contiguous);

  const slot1 = Object.entries(roles).sort((a, b) => a[1] - b[1])
    .map(([r, o]) => `A/${o} ${esc(r)}`).join(' · ');
  const slot2 = Object.entries(roles).sort((a, b) => a[1] - b[1])
    .map(([, o]) => `A/${o + 32}`).join(' · ');
  let msg = `<b>${sites.length} channels per mouse.</b> First animal on port A: `
          + `<span class="mono">${slot1}</span>. Second animal on a split port: `
          + `<span class="mono">${slot2}</span>.`;
  if (dup) msg += `<div style="color:var(--bad)">Two signals share a site number.</div>`;
  if (over.length) msg += `<div style="color:var(--bad)">Site(s) ${over.join(', ')} `
    + `are beyond this headstage's ${hs.real_channels} real channels — nothing is wired there.</div>`;
  msg += contiguous
    ? `<div style="color:var(--ok)">QC applies: the wire-free floor is /${sites.length + 1}–/${hs.real_channels} on each chip.</div>`
    : `<div style="color:var(--warn)">No QC criterion: the floor rule does not describe these sites, so no QC bundle will ever be produced for this layout. Say why below.</div>`;
  el.innerHTML = msg;
}

$('#ns-save').onclick = async () => {
  try {
    await post('/api/settings/recording', {
      name: $('#ns-name').value.trim(),
      label: $('#ns-label').value.trim(),
      headstage: $('#ns-hs').value,
      roles: gatherRoles(),
      qc: $('#ns-qcbox').classList.contains('hide') ? 'auto' : 'none',
      qc_reason: $('#ns-reason').value.trim(),
      who: $('#owner').value || '',
    });
    toast('recording setting saved', 'ok');
    $('#ns-name').value = ''; $('#ns-label').value = ''; $('#ns-reason').value = '';
    $('#ns-roles').innerHTML = ''; addRoleRow(); addRoleRow();
    await loadSettings(); await reloadConfig();
  } catch (e) { toast(e.message, 'bad'); }
};

$('#nl-save').onclick = async () => {
  try {
    await post('/api/settings/layout', {
      name: $('#nl-name').value.trim(),
      label: $('#nl-label').value.trim(),
      setting: $('#setting').value,
      splitters: SPLIT,
      who: $('#owner').value || '',
    });
    toast('layout saved', 'ok');
    $('#nl-name').value = ''; $('#nl-label').value = '';
    await loadSettings(); await reloadConfig();
  } catch (e) { toast(e.message, 'bad'); }
};

/* ====================================================================== */
/* CUSTOM CHANNELS FOR ONE RUN                                             */
/*                                                                         */
/* The same picker the settings panel has, but scoped to this run and not  */
/* written to the config. Validation is the server's -- one rule, one       */
/* place -- so this cannot be looser than a saved setting.                 */
/* ====================================================================== */
function addCustomRole(role = '', site = '') {
  const div = document.createElement('div');
  div.className = 'row';
  div.style.marginTop = '6px';
  div.innerHTML =
    `<div><input data-k="role" placeholder="signal name, e.g. eeg" maxlength="24" value="${esc(role)}"></div>`
  + `<div><input data-k="site" type="number" min="1" max="64" placeholder="site" value="${esc(site)}" style="width:90px"></div>`
  + `<div><button class="ghost" data-k="drop">−</button></div>`;
  div.querySelector('[data-k=drop]').onclick = () => { div.remove(); loadLayout(); };
  div.querySelectorAll('input').forEach(i =>
    i.addEventListener('input', () => { clearTimeout(window.__csT);
      window.__csT = setTimeout(loadLayout, 350); }));
  $('#cs-roles').appendChild(div);
}

function renderCustomPreview() {
  if (!PRESET) return;
  const roles = PRESET.roles[PRESET.slots[0]] || [];
  const first = PRESET.slot_channels[PRESET.slots[0]] || [];
  const second = PRESET.slots.length > 1 ? PRESET.slot_channels[PRESET.slots[1]] : null;
  const hs = (CFG.headstages || {})[$('#cs-hs').value] || {};
  const n = first.length;
  const contiguous = PRESET.qc !== 'none';
  // The floor is the in-file control every verdict is judged against. Saying
  // whether one will exist -- and which sites it is -- belongs here, before the
  // run, not in a failure afterwards.
  $('#cs-preview').innerHTML =
      `<b>${n} channel${n === 1 ? '' : 's'} per mouse.</b> `
    + `First animal on port ${PRESET.slots[0][0]}: `
    + `<span class="mono">${first.map((l, i) => esc(`${l} ${roles[i] || ''}`)).join(' · ')}</span>`
    + (second ? `<br>Second animal on that port: <span class="mono">${esc(second.join(' · '))}</span>` : '')
    + (contiguous
        ? `<div style="color:var(--ok)">QC applies: the wire-free floor is `
          + `/${n + 1}–/${hs.real_channels || 16} on each chip.</div>`
        : `<div style="color:var(--warn)">No QC criterion: the floor rule does not `
          + `describe these sites, so no QC bundle will ever be produced for this `
          + `run. Say why below.</div>`);
}

$('#cs-addrole').onclick = () => { addCustomRole(); loadLayout(); };
$('#cs-hs').onchange = loadLayout;
$('#cs-reason').addEventListener('input', () => {
  clearTimeout(window.__csR); window.__csR = setTimeout(loadLayout, 400);
});

/* Turn the current selection into a reusable named setting. Same endpoint and
   same guards as the settings panel -- this is a shortcut, not a second door. */
$('#cs-save').onclick = async () => {
  const c = customPayload();
  if (!c || !Object.keys(c.roles).length) { toast('Add at least one signal first.', 'bad'); return; }
  const name = prompt('Save as a recording setting.\n\nKey (lower-case, digits, underscore):');
  if (!name) return;
  const label = prompt('Shown as:', name) || name;
  try {
    await post('/api/settings/recording', {...c, name: name.trim(), label, who: $('#owner').value || ''});
    await reloadConfig();
    $('#setting').value = name.trim();
    await loadLayout();
    toast(`saved "${name.trim()}" — now in the dropdown`, 'ok');
  } catch (e) { toast(e.message, 'bad'); }
};
