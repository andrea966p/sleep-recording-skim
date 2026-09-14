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
  if (!r.ok) throw new Error(body.error || `HTTP ${r.status}`);
  return body;
};
const post = (p, b) => api(p, {
  method: 'POST', headers: {'Content-Type': 'application/json'},
  body: b ? JSON.stringify(b) : undefined,
});

let CFG = null, PRESET = null, STATE = null, SELECTED = 'andrea';
// What the operator says is physically on each port. A splitter puts TWO chips
// on a port: 64 enumerated channels, two animals. Without one, 32 and one animal.
let SPLIT = {A: true, B: true, C: true, D: true};

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
  else if (a.recording === 'R_ON') pill('#p-allego', 'live', `recording · ${a.sample_freq/1000} kHz`);
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
function renderPresetPicker() {
  const lsel = $('#layout');
  lsel.innerHTML = '';
  for (const [name, t] of Object.entries(CFG.layouts)) {
    const o = document.createElement('option');
    o.value = name; o.textContent = t.label;
    lsel.appendChild(o);
  }
  lsel.appendChild(Object.assign(document.createElement('option'),
                                 {value: 'custom', textContent: 'Custom'}));

  const ssel = $('#setting');
  ssel.innerHTML = '';
  for (const [name, st] of Object.entries(CFG.settings)) {
    const o = document.createElement('option');
    o.value = name;
    o.textContent = `${st.label} — ${st.channels_per_animal} ch/mouse`;
    ssel.appendChild(o);
  }
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
      + chk.problems.map(x => `<div style="color:var(--bad)">• ${x}</div>`).join('');
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
      <label class="sw"><input type="checkbox" data-k="split"> SPI splitter</label>
      <div class="derived" data-k="derived"></div>`;
    const cb = div.querySelector('[data-k=split]');
    cb.checked = !!SPLIT[port];
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
    PRESET = await post('/api/layout/resolve',
                        {setting: $('#setting').value, splitters: SPLIT});
  } catch (e) {
    $('#port-note').innerHTML = `<span style="color:var(--bad)">${e.message}</span>`;
    return;
  }
  syncLayoutSelect();
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
      <div class="hd"><span class="name">${slot}</span>
        <span class="ch">${chans}</span></div>
      <input placeholder="mouse ID" data-k="mouse" maxlength="32">
      <select data-k="type">${CFG.recording_types.map(
        t => `<option value="${t}">${t}</option>`).join('')}</select>`;
    const inp = div.querySelector('input');
    inp.addEventListener('input', () => {
      div.classList.toggle('on', !!inp.value.trim());
      renderKeepNote();
    });
    // The recording type is part of the NAS folder name (BSR/RSR/SDR), so a
    // change to it changes where the data lands. Without this the preview would
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
        ? ' \u2014 no QC criterion applies to this layout, so no QC bundle is produced'
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

function renderKeepNote() {
  if (!PRESET) return;
  const slots = Object.keys(gatherSlots());
  const owner = $('#owner').value;
  const why = !owner ? 'Choose who is recording first.'
            : (PRESET && PRESET.check && !PRESET.check.ok)
              ? 'The declared rig does not match what Allego sees.'
            : !slots.length ? 'Enter at least one mouse ID.'
            : '';
  $('#btn-now').disabled = !!why;
  $('#btn-schedule').disabled = !!why;
  if (why) { $('#keep-note').textContent = why; return; }
  const labels = slots.flatMap(s => PRESET.slot_channels[s]).sort();
  $('#keep-note').innerHTML =
    `<b>${labels.length} channels will be kept</b> for ${slots.length} `
    + `${slots.length === 1 ? 'mouse' : 'mice'} — going to `
    + `<span class="mono">03_Data_Mouse/${owner}/</span>: `
    + `<span class="mono">${labels.join(', ')}</span>`;
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
      '<span style="color:var(--faint)">No batch name: the folder keeps '
      + 'Allego\u2019s own name, as before.</span>';
    return;
  }
  const seq = ++nameSeq;
  try {
    const r = await post('/api/naming/preview', {
      owner, setting: $('#setting').value, splitters: SPLIT,
      slots: gatherSlots(),
      batch_name: batch, start_at: $('#start').value || null});
    if (seq !== nameSeq) return;          // a later keystroke already answered
    el.innerHTML = `Will arrive as <span class="mono">03_Data_Mouse/${owner}/`
      + `<b>${r.folder}</b>/</span> holding <span class="mono">${r.file_base}`
      + `_data.xdat</span>, <span class="mono">${r.file_base}_timestamp.xdat</span> `
      + `and <span class="mono">${r.file_base}.xdat.json</span>`
      // The folder is dated by the day the recording STARTS. After 09:00 the
      // pre-filled Start at is tomorrow, so the two buttons produce two
      // different dates and the preview must not silently show one of them.
      + (r.if_started_now
          ? ` — dated by the scheduled start. <b>Start now</b> instead and it `
            + `would be <span class="mono">${r.if_started_now}</span>.`
          : '');
  } catch (e) {
    if (seq !== nameSeq) return;
    el.innerHTML = `<span style="color:var(--bad)">${e.message}</span>`;
  }
}

/* ---------- live panel ---------- */
let liveStart = null;
function renderLive(s) {
  const r = s.active_run;
  const on = r && ['STARTING','RECORDING','STOPPING'].includes(r.state);
  $('#live').classList.toggle('hide', !on);
  $('#setup').classList.toggle('hide', !!on);
  if (!on) { liveStart = null; return; }
  liveStart = r.actual_start ? new Date(r.actual_start) : null;
  $('#live-id').textContent = r.run_id;
  $('#live-owner').textContent = r.owner;
  $('#live-file').textContent = r.base_name || '…';
  $('#live-bytes').textContent = r.bytes_on_disk > 0 ? gb(r.bytes_on_disk) : '0 bytes';
  $('#live-stop').textContent = r.scheduled_stop ? local(r.scheduled_stop) : 'manual';
  $('#live-mice').innerHTML = Object.entries(r.slots)
    .map(([k, v]) => `<span class="tag">${k} · ${v.mouse_id} · ${v.recording_type}</span>`)
    .join(' ');
  const elapsed = liveStart ? (Date.now() - liveStart) / 1000 : 0;
  $('#live-elapsed').textContent = dur(elapsed);
  $('#live-lag').classList.toggle('hide', !(elapsed < 90 && !(r.bytes_on_disk > 0)));
  const g = (r.results || {}).growth;
  if (g && !g.growing) {
    $('#live-lag').className = 'badbox';
    $('#live-lag').innerHTML =
      `<b>The recorder says R_ON but no bytes landed in ${g.window_s} s.</b> ` +
      `This needs a person — the run is not producing data.`;
  }
}
setInterval(() => {
  if (liveStart) $('#live-elapsed').textContent = dur((Date.now() - liveStart) / 1000);
}, 1000);

/* ---------- history ---------- */
const STATE_CLASS = s =>
  s === 'DONE' ? 'ok' : s === 'RECORDING' ? 'live'
  : s.startsWith('FAILED') ? 'bad'
  : s === 'UPLOAD_PENDING' ? 'warn' : '';

async function renderRuns() {
  const {runs} = await api('/api/runs?limit=40');
  const tb = $('#runs');
  if (!runs.length) {
    tb.innerHTML = '<tr><td colspan="8" class="note">No runs yet.</td></tr>';
    return;
  }
  tb.innerHTML = runs.map(r => {
    const mice = Object.entries(r.slots)
      .map(([k, v]) => `${k}:${v.mouse_id}`).join(' ');
    let d = '–';
    if (r.actual_start && r.actual_stop)
      d = dur((new Date(r.actual_stop) - new Date(r.actual_start)) / 1000);
    const strip = (r.results && r.results.strip) || null;
    const retry = r.state.startsWith('FAILED') || r.state === 'UPLOAD_PENDING'
      ? `<button class="ghost" style="padding:4px 10px;font-size:12px"
           onclick="retryRun('${r.run_id}','${r.state}')"
           title="${(r.error || '').replace(/"/g, '&quot;').slice(0, 300)}">retry</button>` : '';
    return `<tr>
      <td class="mono">${r.run_id}</td>
      <td>${r.owner}</td>
      <td class="mono" style="font-size:11px">${mice}</td>
      <td><span class="tag ${STATE_CLASS(r.state)}">${r.state}</span></td>
      <td class="mono">${local(r.actual_start || r.scheduled_start)}</td>
      <td class="mono">${d}</td>
      <td class="mono">${strip ? strip.saving_pct + '% smaller'
        : (r.results && r.results.qc_bundle_skipped) ? 'no QC bundle' : '–'}</td>
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

/* ---------- actions ---------- */
async function createRun(schedule) {
  const slots = gatherSlots();
  if (!Object.keys(slots).length) {
    toast('Enter at least one mouse ID first.', 'bad'); return null;
  }
  if (PRESET && PRESET.check && !PRESET.check.ok) {
    toast('The declared rig does not match what Allego sees.', 'bad'); return null;
  }
  const body = {owner: $('#owner').value, slots,
                layout: $('#layout').value,
                setting: $('#setting').value, splitters: SPLIT,
                batch_name: $('#batch').value.trim()};
  if (schedule) {
    if (!$('#start').value) { toast('Pick a start time.', 'bad'); return null; }
    body.start_at = $('#start').value;
    if ($('#stop').value) body.stop_at = $('#stop').value;
  }
  return post('/api/runs', body);
}

$('#btn-schedule').onclick = async () => {
  try {
    const r = await createRun(true);
    if (r) { toast(`Scheduled ${r.run_id} for ${local(r.scheduled_start)}`, 'ok'); refresh(); }
  } catch (e) { toast(e.message, 'bad'); }
};

$('#btn-now').onclick = async () => {
  const slots = gatherSlots();
  const n = Object.keys(slots).length;
  if (!confirm(`Start recording now with ${n} ${n === 1 ? 'mouse' : 'mice'}?\n\n`
      + Object.entries(slots).map(([k, v]) => `  ${k}  ${v.mouse_id}  ${v.recording_type}`).join('\n')
      + `\n\nThis records ALL channels; the selection only affects the stripped copy.`))
    return;
  try {
    const r = await createRun(false);
    if (!r) return;
    await post(`/api/runs/${r.run_id}/start`);
    toast(`Recording started (${r.run_id})`, 'ok');
    refresh();
  } catch (e) { toast(e.message, 'bad'); }
};

$('#btn-stop').onclick = async () => {
  const r = STATE && STATE.active_run;
  if (!r) return;
  if (!confirm(`Stop recording ${r.base_name || r.run_id}?\n\n`
    + `It will then be stripped to ${r.keep_labels.length} channels and uploaded `
    + `to ${r.owner}'s folder on the NAS.`)) return;
  try {
    await post(`/api/runs/${r.run_id}/stop`);
    toast('Stopped. Post-processing queued.', 'ok');
    refresh();
  } catch (e) { toast(e.message, 'bad'); }
};

// Debounced: one request per pause in typing, not one per keystroke.
let batchTimer = null;
$('#batch').addEventListener('input', () => {
  clearTimeout(batchTimer);
  batchTimer = setTimeout(renderNameNote, 250);
});
// The date in the folder name is the date the recording will CARRY, so changing
// the scheduled start changes it.
$('#start').addEventListener('change', renderNameNote);

$('#setting').onchange = () => loadLayout();
$('#layout').onchange = e => {
  const t = CFG.layouts[e.target.value];
  if (!t) return;                       // "Custom": keep whatever is set
  $('#setting').value = t.setting;
  SPLIT = Object.assign({}, t.splitters);
  renderPorts();
  loadLayout();
};
$('#owner').onchange = e => {
  SELECTED = e.target.value;
  if (!SELECTED) { renderKeepNote(); return; }
  const want = CFG.users[SELECTED].default_layout;
  const t = CFG.layouts[want];
  if (t) {
    $('#setting').value = t.setting;
    SPLIT = Object.assign({}, t.splitters);
    renderPorts();
    loadLayout();
    return;
  }
  renderKeepNote();
};

/* ---------- poll ---------- */
async function refresh() {
  try {
    STATE = await api('/api/state');
    $('#offline').classList.add('hide');
    renderPills(STATE);
    renderLive(STATE);
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
  setInterval(refresh, 2000);
})();
