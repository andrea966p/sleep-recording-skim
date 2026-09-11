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
  const sel = $('#preset');
  sel.innerHTML = '';
  for (const [name, p] of Object.entries(CFG.presets)) {
    const o = document.createElement('option');
    o.value = name;
    o.textContent = `${p.label} — ${p.slots.length} slots, ${p.total_channels} ch`;
    sel.appendChild(o);
  }
}

async function loadPreset(name) {
  PRESET = await api(`/api/presets/${name}`);
  const slots = $('#slots');
  slots.innerHTML = '';
  for (const [slot, info] of Object.entries(PRESET.slots)) {
    const chans = info.labels.map((l, i) =>
      info.roles[i] ? `${l} ${info.roles[i]}` : l).join(' · ');
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
    slots.appendChild(div);
  }
  $('#preset-note').textContent =
    `${Object.keys(PRESET.slots).length} slots, ${PRESET.all_labels.length} channels total`
    + (PRESET.with_gpio ? ', GPIO kept' : ', GPIO dropped');
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
            : !slots.length ? 'Enter at least one mouse ID.'
            : '';
  $('#btn-now').disabled = !!why;
  $('#btn-schedule').disabled = !!why;
  if (why) { $('#keep-note').textContent = why; return; }
  const labels = slots.flatMap(s => PRESET.slots[s].labels).sort();
  $('#keep-note').innerHTML =
    `<b>${labels.length} channels will be kept</b> for ${slots.length} `
    + `${slots.length === 1 ? 'mouse' : 'mice'} — going to `
    + `<span class="mono">03_Data_Mouse/${owner}/</span>: `
    + `<span class="mono">${labels.join(', ')}</span>`;
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
  const body = {owner: $('#owner').value, preset: $('#preset').value, slots};
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

$('#preset').onchange = e => loadPreset(e.target.value);
$('#owner').onchange = e => {
  SELECTED = e.target.value;
  if (!SELECTED) { renderKeepNote(); return; }
  const want = CFG.users[SELECTED].default_preset;
  if ($('#preset').value !== want) { $('#preset').value = want; loadPreset(want); }
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
  await loadPreset($('#preset').value);

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
