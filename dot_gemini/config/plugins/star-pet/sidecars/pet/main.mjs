// 星语 · Star Pet — Antigravity sidecar
//
// The host starts this process for the `star-pet` plugin and hands it everything needed:
//   ANTIGRAVITY_LS_ADDRESS       localhost:<http port> of the language server (gRPC-web gateway)
//   ANTIGRAVITY_CSRF_TOKEN       token for that gateway
//   AGY_BROWSER_ACTIVE_PORT_FILE path of the Chromium DevToolsActivePort file
//   ANTIGRAVITY_APP_DATA_DIR     ~/.gemini/antigravity (brain transcripts live here)
//   ANTIGRAVITY_EXECUTABLE_DATA_DIR  per-plugin data directory
//
// The companion layer itself is injected into the Antigravity renderer through its own local CDP
// endpoint. Nothing under /opt/Antigravity is read or written.

import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, renameSync, statSync, writeFileSync, openSync, readSync, closeSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { request } from 'node:http';
import { randomUUID } from 'node:crypto';
import { installStarPet } from './layer.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));

const env = process.env;
const dataDir = env.ANTIGRAVITY_EXECUTABLE_DATA_DIR || join(homedir(), '.antigravity-star-pet');
const appDataDir = env.ANTIGRAVITY_APP_DATA_DIR || join(homedir(), '.gemini/antigravity');
const portFile = env.AGY_BROWSER_ACTIVE_PORT_FILE || join(homedir(), '.config/Antigravity/DevToolsActivePort');
const lsAddress = env.ANTIGRAVITY_LS_ADDRESS || '';
const csrfToken = env.ANTIGRAVITY_CSRF_TOKEN || '';
const owner = `${process.pid}:${randomUUID()}`;

mkdirSync(dataDir, { recursive: true });
const LOG = join(dataDir, 'pet.log');
const SETTINGS = join(dataDir, 'settings.json');

// --- logging -----------------------------------------------------------------
function log(line) {
  try {
    const stat = existsSync(LOG) ? statSync(LOG) : null;
    if (stat && stat.size > 262144) renameSync(LOG, LOG + '.1');
    appendFileSync(LOG, `${new Date().toISOString()} ${line}\n`);
  } catch { /* logging must never crash the companion */ }
}

// --- settings ----------------------------------------------------------------
const DEFAULT_SETTINGS = { enabled: true, scale: 160, ttlMs: 5200, state: "auto" };
let settings = { ...DEFAULT_SETTINGS };
function readSettings() {
  try {
    const raw = JSON.parse(readFileSync(SETTINGS, 'utf8'));
    settings = {
      ...DEFAULT_SETTINGS,
      ...Object.fromEntries(Object.entries(raw || {}).filter(([k]) => k in DEFAULT_SETTINGS)),
    };
    settings.enabled = settings.enabled !== false;
    settings.scale = Math.max(120, Math.min(420, Number(settings.scale) || 220));
  } catch { settings = { ...DEFAULT_SETTINGS }; }
  return settings;
}
if (!existsSync(SETTINGS)) writeFileSync(SETTINGS, JSON.stringify(DEFAULT_SETTINGS, null, 2) + '\n', { mode: 0o600 });
readSettings();

// --- assets ------------------------------------------------------------------
function dataUrl(rel) {
  const body = readFileSync(join(HERE, rel));
  return `data:image/webp;base64,${body.toString('base64')}`;
}
const FRAMES = {};
for (const name of ['idle', 'blink', 'proud', 'sad']) {
  try { FRAMES[name] = dataUrl(`assets/frames/${name}.webp`); } catch (error) { log(`frame missing ${name}: ${error.message}`); }
}
let dialogue = { lines: {} };
try { dialogue = JSON.parse(readFileSync(join(HERE, 'assets/dialogue.json'), 'utf8')); } catch (error) { log(`dialogue load failed: ${error.message}`); }
const LINES = {
  idle: dialogue.lines?.idle || [],
  thinking: dialogue.lines?.thinking || [],
  success: dialogue.lines?.success || [],
  error: dialogue.lines?.error || [],
  offline: dialogue.lines?.offline || [],
  petting: dialogue.lines?.petting || [],
  dragged: dialogue.lines?.dragged || [],
  crying: dialogue.lines?.crying || [],
};
// The injected bubble only renders these buckets.
const BUBBLE_LINES = {
  idle: LINES.idle, thinking: LINES.thinking, success: LINES.success,
  error: LINES.error, petting: LINES.petting, dragged: LINES.dragged, crying: LINES.crying,
};

// --- CDP client --------------------------------------------------------------
// The host ships a Node runtime with a global WebSocket (verified on Antigravity 2.17 / node 24)
let WSImpl = typeof globalThis.WebSocket === 'function' ? globalThis.WebSocket : null;
if (!WSImpl) log('host runtime has no global WebSocket; the companion cannot attach');

class Cdp {
  constructor(url) {
    this.url = url;
    this.id = 0;
    this.pending = new Map();
    this.closed = false;
    this.socket = new WSImpl(url);
    this.ready = new Promise((resolve, reject) => {
      const done = () => { clearTimeout(this.handshakeTimer); resolve(); };
      const fail = (error) => { clearTimeout(this.handshakeTimer); reject(error); };
      this.handshakeTimer = setTimeout(() => fail(new Error('CDP handshake timeout')), 5000);
      if (typeof this.socket.on === 'function') {
        this.socket.on('open', done);
        this.socket.on('error', fail);
      } else {
        this.socket.addEventListener('open', done, { once: true });
        this.socket.addEventListener('error', fail, { once: true });
      }
    });
    this.ready.catch(() => {});
    const onMessage = (event) => {
      const raw = event && event.data !== undefined ? event.data : event;
      let msg;
      try { msg = JSON.parse(typeof raw === 'string' ? raw : String(raw)); } catch { return; }
      const waiter = this.pending.get(msg.id);
      if (!waiter) return;
      this.pending.delete(msg.id);
      clearTimeout(waiter.timer);
      msg.error ? waiter.reject(new Error(msg.error.message || 'CDP error')) : waiter.resolve(msg.result);
    };
    if (typeof this.socket.on === 'function') this.socket.on('message', onMessage);
    else this.socket.addEventListener('message', onMessage);
    const onClose = () => {
      this.closed = true;
      for (const waiter of this.pending.values()) { clearTimeout(waiter.timer); waiter.reject(new Error('host detached')); }
      this.pending.clear();
    };
    if (typeof this.socket.on === 'function') this.socket.on('close', onClose);
    else this.socket.addEventListener('close', onClose);
  }
  async send(method, params = {}) {
    await this.ready;
    if (this.closed) throw new Error('CDP closed');
    return new Promise((resolve, reject) => {
      const id = ++this.id;
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`${method} timeout`)); }, 12000);
      this.pending.set(id, { resolve, reject, timer });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }
  async evaluate(expression) {
    const out = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (out.exceptionDetails) {
      throw new Error(out.exceptionDetails.exception?.description || out.exceptionDetails.text || 'evaluate failed');
    }
    return out.result?.value;
  }
  close() {
    this.closed = true;
    try { this.socket.close(); } catch { /* already gone */ }
  }
}

function httpJson({ port, path, method = 'GET', headers = {}, body = null, timeout = 4000 }) {
  return new Promise((resolve, reject) => {
    const payload = body === null ? null : Buffer.from(JSON.stringify(body));
    const req = request({
      hostname: '127.0.0.1', port, path, method,
      headers: { ...headers, ...(payload ? { 'Content-Length': payload.length } : {}) },
    }, (res) => {
      let data = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => { data += chunk; if (data.length > 4 * 1024 * 1024) req.destroy(new Error('response too large')); });
      res.on('end', () => {
        if (res.statusCode !== 200) return reject(new Error(`HTTP ${res.statusCode}`));
        try { resolve(JSON.parse(data)); } catch (error) { reject(error); }
      });
    });
    req.setTimeout(timeout, () => req.destroy(new Error('timeout')));
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

function readPortFile() {
  const port = Number(readFileSync(portFile, 'utf8').split('\n')[0].trim());
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('invalid DevTools port');
  return port;
}

async function discoverPage() {
  const port = readPortFile();
  const targets = await httpJson({ port, path: '/json/list', timeout: 3000 });
  const page = (targets || []).find((t) => t.type === 'page' && /^https?:\/\/(127\.0\.0\.1|localhost):\d+\//.test(t.url || ''));
  if (!page || !/^ws:\/\/(127\.0\.0\.1|localhost):\d+\//.test(page.webSocketDebuggerUrl || '')) return null;
  return { port, page };
}

// --- quota -------------------------------------------------------------------
const quotaState = { value: null, at: 0, error: null };
async function refreshQuota() {
  if (!lsAddress || !csrfToken) { quotaState.error = 'no language server credentials'; return; }
  const [, portText] = lsAddress.replace(/^https?:\/\//, '').split(':');
  const port = Number(portText);
  if (!Number.isInteger(port) || port < 1) { quotaState.error = 'bad LS address'; return; }
  try {
    const payload = await httpJson({
      port, path: '/exa.language_server_pb.LanguageServerService/RetrieveUserQuotaSummary', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Connect-Protocol-Version': '1', 'x-codeium-csrf-token': csrfToken },
      body: {}, timeout: 8000,
    });
    const root = payload?.response || payload;
    const groups = Array.isArray(root?.groups) ? root.groups : [];
    const group = groups.find((g) => /gemini/i.test(g?.displayName || '')) || groups[0];
    if (!group) throw new Error('no quota groups');
    const pick = (suffix) => (group.buckets || []).find((b) => b.bucketId === `gemini-${suffix}` || b.window === suffix);
    const fraction = (bucket) => {
      const value = Number(bucket?.remainingFraction);
      return Number.isFinite(value) && value >= 0 && value <= 1 ? value : null;
    };
    const five = pick('5h');
    const week = pick('weekly');
    quotaState.at = Date.now();
    quotaState.value = {
      group: group.displayName || 'Gemini Models',
      fiveHour: fraction(five), weekly: fraction(week),
      resetFive: five?.resetTime || null, resetWeek: week?.resetTime || null,
      at: quotaState.at, stale: false,
    };
    quotaState.error = null;
  } catch (error) {
    quotaState.error = error.message;
    if (quotaState.value) quotaState.value = { ...quotaState.value, stale: Date.now() - quotaState.at > 300000 };
  }
}

// --- transcripts -------------------------------------------------------------
const startOfDay = (() => { const d = new Date(); d.setHours(0, 0, 0, 0); return d.getTime(); })();
let usage = null;

function transcriptFiles() {
  const brain = join(appDataDir, 'brain');
  const out = [];
  let dirs = [];
  try { dirs = readdirSync(brain, { withFileTypes: true }); } catch { return out; }
  for (const entry of dirs) {
    if (!entry.isDirectory()) continue;
    const file = join(brain, entry.name, '.system_generated/logs/transcript_full.jsonl');
    try { out.push({ file, session: entry.name, mtime: statSync(file).mtimeMs }); } catch { /* not every session logs */ }
  }
  return out.sort((a, b) => b.mtime - a.mtime);
}

function readTail(file, maxBytes = 262144) {
  const stat = statSync(file);
  const start = Math.max(0, stat.size - maxBytes);
  const fd = openSync(file, 'r');
  try {
    const buffer = Buffer.alloc(Math.max(0, Math.min(maxBytes, stat.size - start)));
    readSync(fd, buffer, 0, buffer.length, start);
    return buffer.toString('utf8');
  } finally { closeSync(fd); }
}

function parseSteps(file, session, since, budget = 262144) {
  let text;
  try { text = readTail(file, budget); } catch { return []; }
  const steps = [];
  for (const line of text.split('\n')) {
    if (!line || line.length > 4194304) continue;
    let step;
    try { step = JSON.parse(line); } catch { continue; }
    if (step.source !== 'MODEL' || step.type !== 'PLANNER_RESPONSE') continue;
    if (!Number.isSafeInteger(step.step_index)) continue;
    const created = Date.parse(step.created_at || '');
    if (Number.isFinite(created) && created < since) continue;
    steps.push({ ...step, session });
  }
  return steps;
}

// Cheap state probe: newest transcript only, tiny tail, cached for 2.5 s.
let lastStepCache = { at: 0, value: null, newest: null };
function newestStep() {
  const now = Date.now();
  if (now - lastStepCache.at < 2500) return lastStepCache;
  const files = transcriptFiles();
  if (!files.length) { lastStepCache = { at: now, value: null, newest: null, online: false }; return lastStepCache; }
  const newest = files[0];
  const steps = parseSteps(newest.file, newest.session, 0, 131072);
  const last = steps.length ? steps[steps.length - 1] : null;
  lastStepCache = { at: now, value: last, newest, online: true };
  return lastStepCache;
}

// Token accounting for the bubble: today's files, cached for 30 s.
let usageCache = { at: 0, value: null };
function usageToday() {
  const now = Date.now();
  if (now - usageCache.at < 30000) return usageCache.value;
  const files = transcriptFiles().filter((f) => f.mtime >= startOfDay).slice(0, 12);
  let steps = 0;
  let output = 0;
  const seen = new Set();
  for (const entry of files) {
    for (const step of parseSteps(entry.file, entry.session, startOfDay)) {
      const key = `${entry.session}:${step.step_index}`;
      if (seen.has(key)) continue;
      seen.add(key);
      steps += 1;
      if (Number.isFinite(step.output_tokens)) output += step.output_tokens;
    }
  }
  usageCache = { at: now, value: { steps, outputTokens: output, sessions: files.length } };
  usage = usageCache.value;
  return usage;
}

let lastState = 'idle';
let lastStateAt = 0;

function deriveState() {
  const now = Date.now();
  let result = 'idle';
  try {
    const probe = newestStep();
    if (probe.online === false) result = 'offline';
    else if (probe.value) {
      const status = String(probe.value.status || '');
      if (status === 'RUNNING') result = 'thinking';
      else if (status === 'ERROR') result = 'error';
      else if (status === 'DONE') {
        const created = Date.parse(probe.value.created_at || '');
        if (Number.isFinite(created) && now - created < 8000) result = 'success';
      }
    }
  } catch (error) { log(`state probe failed: ${error.message}`); }
  if (result !== lastState) { lastState = result; lastStateAt = now; }
  return result;
}

// --- session -----------------------------------------------------------------
let client = null;
let lastQuotaAt = 0;
let stopRequested = false;

function injectionConfig(state) {
  const quota = quotaState.value;
  return {
    owner,
    scale: settings.scale,
    ttlMs: settings.ttlMs,
    state,
    frames: FRAMES,
    lines: BUBBLE_LINES,
    quota: quota ? { fiveHour: quota.fiveHour, weekly: quota.weekly, at: quotaState.at, stale: quota.stale } : null,
    usage: usageToday(),
  };
}

async function ensureClient() {
  if (client && !client.closed) return client;
  client?.close();
  client = null;
  const found = await discoverPage();
  if (!found) return null;
  client = new Cdp(found.page.webSocketDebuggerUrl);
  log(`attached to page ${found.page.url}`);
  return client;
}

async function injectIfNeeded(state) {
  const alive = await client.evaluate('typeof window.__starPet === "object" && window.__starPet !== null');
  if (alive) return false;
  const source = `(${installStarPet.toString()})(${JSON.stringify(injectionConfig(state))})`;
  const result = await client.evaluate(source);
  log(`injected layer ${JSON.stringify(result)}`);
  return true;
}

async function tick() {
  if (stopRequested) return;
  readSettings();
  if (!settings.enabled) {
    if (client && !client.closed) {
      try { await client.evaluate('window.__starPet && window.__starPet.destroy()'); } catch { /* detached */ }
      client.close();
      client = null;
    }
    return;
  }

  const now = Date.now();
  if (now - lastQuotaAt > 60000) { lastQuotaAt = now; refreshQuota().catch(() => {}); }
  const state = settings.state !== 'auto' ? settings.state : deriveState();

  try {
    const active = await ensureClient();
    if (!active) return;
    const injected = await injectIfNeeded(state);
    if (!injected) {
      await active.evaluate(`window.__starPet.update(${JSON.stringify(injectionConfig(state))})`);
    }
  } catch (error) {
    log(`tick failed: ${error.message}`);
    client?.close();
    client = null;
  }
}

// --- lifecycle ---------------------------------------------------------------
function shutdown() {
  stopRequested = true;
  client?.close();
  clearInterval(timer);
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
process.on('uncaughtException', (error) => log(`uncaught: ${error.stack || error.message}`));
process.on('unhandledRejection', (error) => log(`unhandled: ${error?.stack || error}`));

log(`sidecar start pid=${process.pid} node=${process.version} ws=${typeof globalThis.WebSocket} data=${dataDir} ls=${lsAddress || '(none)'}`);
tick().catch(() => {});
const timer = setInterval(() => { tick().catch(() => {}); }, 2000);
