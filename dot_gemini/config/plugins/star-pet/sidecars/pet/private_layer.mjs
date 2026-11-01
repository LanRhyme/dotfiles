// Page-side companion layer. This function is serialized with Function.prototype.toString()
// and evaluated inside the Antigravity renderer through its local CDP endpoint, so it must stay
// fully self-contained: no imports, no references to module scope.

export function installStarPet(config) {
  const VERSION = 'star-pet/1';
  const KEY = '__starPet';
  const HOST_ID = 'star-pet-host';

  if (window[KEY] && window[KEY].version === VERSION) {
    window[KEY].update(config);
    return window[KEY].status();
  }
  try { window[KEY] && window[KEY].destroy(); } catch (e) { /* stale layer */ }
  const stale = document.getElementById(HOST_ID);
  if (stale) stale.remove();
  if (!document.body) return { installed: false, reason: 'no-body' };

  const cfg = Object.assign({
    scale: 220, state: 'idle', lines: {}, frames: {}, quota: null, usage: null, skin: null,
    ttlMs: 5200, owner: 'star-pet'
  }, config || {});

  const host = document.createElement('div');
  host.id = HOST_ID;
  host.style.cssText = 'position:fixed;inset:0;z-index:6000;pointer-events:none;contain:layout style;';
  const shadow = host.attachShadow({ mode: 'open' });

  shadow.innerHTML = `
<style>
  :host { all: initial; }
  *, *::before, *::after { box-sizing: border-box; }
  .wrap { position: absolute; left: 0; top: 0; width: 220px; pointer-events: none; }
  .cat { position: relative; width: 100%; aspect-ratio: 420 / 351; pointer-events: auto; cursor: grab; touch-action: none;
         user-select: none; -webkit-user-select: none; outline: none;
         transition: transform .2s cubic-bezier(.34,1.56,.64,1); }
  .cat { animation: star-breathe 6s ease-in-out infinite; transform-origin: 50% 100%; }
  .cat.dragging { cursor: grabbing; transform: scale(.97); }
  .cat.pressed { transform: scale(.94); }
  .frame { position: absolute; inset: 0; display: block; width: 100%; height: 100%; object-fit: contain;
           pointer-events: none; transform-origin: 50% 100%; transition: opacity .22s ease; }
  .frame.b { opacity: 0; }
  .glow { position: absolute; inset: -10%; border-radius: 50%; pointer-events: none; opacity: 0;
          background: radial-gradient(circle at 50% 62%, rgba(255,214,150,.30), rgba(255,214,150,0) 62%);
          transform: scale(.92); transition: opacity .4s ease, transform .5s ease; }
  .cat.cheer .glow { opacity: 1; transform: scale(1.04); }
  .dots { position: absolute; left: 50%; top: -6px; transform: translateX(-50%); display: none; gap: 5px; }
  .busy .dots { display: flex; }
  .dots i { width: 6px; height: 6px; border-radius: 50%; background: #c4b0ff; opacity: .35;
            animation: star-dot 1.15s ease-in-out infinite; }
  .dots i:nth-child(2) { animation-delay: .16s; }
  .dots i:nth-child(3) { animation-delay: .32s; }
  .bubble { position: absolute; right: 2px; bottom: calc(100% - 8px); width: 236px;
            padding: 10px 12px 9px; border-radius: 14px; opacity: 0; visibility: hidden;
            transform: translateY(7px) scale(.975); transform-origin: 88% 100%;
            transition: opacity .18s ease, transform .18s cubic-bezier(.34,1.4,.64,1), visibility .18s;
            background: rgba(27,23,38,.93); border: 1px solid rgba(180,150,255,.26);

            color: #efe9ff; font: 12.5px/1.45 "Noto Sans CJK SC", "Source Han Sans SC", system-ui, -apple-system, "Segoe UI", sans-serif;
            pointer-events: none; }
  .bubble.show { opacity: 1; visibility: visible; transform: translateY(0) scale(1); }

  .bubble .title { font-size: 12px; font-weight: 600; letter-spacing: .01em; color: #d9cbff; margin-bottom: 7px;
                   display: flex; justify-content: space-between; align-items: center; }
  .bubble .title em { font-style: normal; font-size: 10.5px; font-weight: 400; color: #9d90b8; }
  .row { display: flex; justify-content: space-between; align-items: baseline; font-size: 11.5px; color: #b6aacd; margin-top: 6px; }
  .row b { font-size: 12px; font-weight: 600; color: #f2ecff; font-variant-numeric: tabular-nums; }
  .bar { height: 4px; border-radius: 3px; background: rgba(255,255,255,.13); overflow: hidden; margin-top: 3px; }
  .bar i { display: block; height: 100%; width: 0; border-radius: 3px;
           background: linear-gradient(90deg, #b79cff, #8fd4ff); transition: width .35s ease; }
  .bar.warn i { background: linear-gradient(90deg, #ffc062, #ffa53d); }
  .bar.danger i { background: linear-gradient(90deg, #ff7fa8, #ff5c8a); }
  .line { margin-top: 9px; padding-top: 8px; border-top: 1px dashed rgba(180,150,255,.22);
          font-size: 12px; color: #efe6ff; }
  .usage { margin-top: 6px; font-size: 10.5px; color: #9d90b8; display: none; }
  .usage.on { display: block; }
  .meta { margin-top: 4px; font-size: 10px; color: #857a9c; }
  @keyframes star-breathe { 0%, 100% { transform: scale(1) translateY(0); } 50% { transform: scale(1.012) translateY(-2px); } }
  @keyframes star-dot { 0%, 100% { opacity: .22; transform: translateY(0); } 50% { opacity: .95; transform: translateY(-3px); } }
  @media (prefers-reduced-motion: reduce) { .frame { animation: none; } .dots i { animation: none; opacity: .6; } }
</style>
<div class="wrap">
  <div class="bubble" role="status" aria-live="polite">
    <div class="title"><span>Gemini Models</span><em class="stamp"></em></div>
    <div class="row"><span>5 小时</span><b class="five">—</b></div>
    <div class="bar five-bar"><i></i></div>
    <div class="row"><span>1 周</span><b class="week">—</b></div>
    <div class="bar week-bar"><i></i></div>
    <div class="line"></div>
    <div class="usage"></div>
    <div class="meta">本机读取 · 缓存不等于实时额度</div>
  </div>
  <div class="cat" tabindex="0" role="button" aria-label="星语 Gemini 猫娘">
    <div class="glow"></div>
    <div class="dots"><i></i><i></i><i></i></div>
    <img class="frame a" alt="" draggable="false">
    <img class="frame b" alt="" draggable="false">
  </div>
</div>`;

  document.body.appendChild(host);
  const wrap = shadow.querySelector('.wrap');
  const cat = shadow.querySelector('.cat');
  const fa = shadow.querySelector('.frame.a');
  const fb = shadow.querySelector('.frame.b');
  const bubble = shadow.querySelector('.bubble');
  const elFive = shadow.querySelector('.five');
  const elWeek = shadow.querySelector('.week');
  const barFive = shadow.querySelector('.five-bar');
  const barWeek = shadow.querySelector('.week-bar');
  const elLine = shadow.querySelector('.line');
  const elStamp = shadow.querySelector('.stamp');
  const elUsage = shadow.querySelector('.usage');

  const store = {
    get(k, d) { try { const v = localStorage.getItem('star-pet:' + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem('star-pet:' + k, JSON.stringify(v)); } catch (e) { /* private mode */ } },
  };

  let scale = Math.max(120, Math.min(420, Number(cfg.scale) || 220));
  let pos = store.get('pos', null);
  let frameName = '';
  let front = fa;
  let back = fb;
  let lineIndex = 0;
  let lineTimer = 0;
  let blinkTimer = 0;
  let hover = false;
  let dragging = null;
  let alive = true;
  let textShown = '';

  const linesOf = (kind) => {
    const all = cfg.lines || {};
    const list = all[kind] && all[kind].length ? all[kind] : (all.idle || []);
    return Array.isArray(list) && list.length ? list : ['喵？'];
  };
  function clamp(next) {
    const w = wrap.offsetWidth || scale;
    const h = wrap.offsetHeight || scale;
    const maxX = Math.max(0, innerWidth - w - 4);
    const maxY = Math.max(0, innerHeight - h - 4);
    return { x: Math.max(4, Math.min(maxX, next.x)), y: Math.max(4, Math.min(maxY, next.y)) };
  }

  function applyPosition(next, persist) {
    pos = clamp(next);
    wrap.style.left = pos.x + 'px';
    wrap.style.top = pos.y + 'px';
    if (persist) store.set('pos', pos);
  }

  function defaultPosition() {
    const w = wrap.offsetWidth || scale;
    const h = wrap.offsetHeight || scale;
    return { x: Math.max(8, innerWidth - w - 22), y: Math.max(8, innerHeight - h - 70) };
  }

  function setFrame(name) {
    const src = cfg.frames && cfg.frames[name];
    if (!src || frameName === name) return;
    frameName = name;
    // 已经显示同一张图就不做动画，否则每次配置推送都会闪一次
    if (front.getAttribute('src') === src && front.style.opacity === '1') return;
    const next = back;
    next.src = src;
    const swap = () => {
      if (!alive || next !== back) return;
      next.style.opacity = '1';
      front.style.opacity = '0';
      const previous = front;
      front = next;
      back = previous;
    };
    if (next.decode) next.decode().then(swap, swap);
    else swap();
  }

  function baseFrame() {
    // 只保留「报错委屈」这一种换脸；成功用暖光提示，表情不再随每步来回切
    return cfg.state === 'error' ? 'sad' : 'idle';
  }

  // 上游 blink.png 是另一次渲染（整张脸位置不同），切过去就是闪一下，故不做眨眼
  function scheduleBlink() { /* 保留呼吸动画，不切帧 */ }

  function bar(track, value) {
    track.classList.remove('warn', 'danger');
    const fill = track.querySelector('i');
    if (!fill) return '—';
    if (typeof value !== 'number' || !isFinite(value)) { fill.style.width = '0%'; return '—'; }
    const pct = Math.max(0, Math.min(100, value * 100));
    fill.style.width = pct.toFixed(1) + '%';
    if (pct <= 10) track.classList.add('danger');
    else if (pct <= 30) track.classList.add('warn');
    return Math.round(pct) + '%';
  }

  function renderQuota() {
    const q = cfg.quota;
    elFive.textContent = bar(barFive, q && typeof q.fiveHour === 'number' ? q.fiveHour : null);
    elWeek.textContent = bar(barWeek, q && typeof q.weekly === 'number' ? q.weekly : null);
    if (q && q.stale) elStamp.textContent = '待更新';
    else if (q && q.at) {
      const mins = Math.max(0, Math.round((Date.now() - q.at) / 60000));
      elStamp.textContent = mins < 1 ? '刚刚' : mins + ' 分钟前';
    } else elStamp.textContent = '未知';
  }

  function renderUsage() {
    const u = cfg.usage;
    if (!u || !u.steps) { elUsage.classList.remove('on'); elUsage.textContent = ''; return; }
    const tokens = Number(u.outputTokens) || 0;
    if (tokens > 0) {
      const short = tokens >= 1000 ? (tokens / 1000).toFixed(1).replace(/\.0$/, '') + 'k' : String(tokens);
      elUsage.textContent = `今日 ${u.steps} 步 · 输出 ${short} tokens`;
    } else {
      elUsage.textContent = `今日 ${u.steps} 步`;
    }
    elUsage.classList.add('on');
  }

  function renderLine(kind) {
    const list = linesOf(kind);
    const text = list[lineIndex % list.length];
    lineIndex += 1;
    textShown = text;
    elLine.textContent = text;
    return text;
  }

  function showBubble(kind, ttl) {
    renderQuota();
    renderUsage();
    if (kind) renderLine(kind);
    bubble.classList.add('show');
    clearTimeout(lineTimer);
    const hold = typeof ttl === 'number' ? ttl : cfg.ttlMs;
    if (hold > 0 && !hover) lineTimer = setTimeout(() => hideBubble(), hold);
  }

  function hideBubble() {
    clearTimeout(lineTimer);
    bubble.classList.remove('show');
  }

  function applyState() {
    cat.classList.toggle('busy', cfg.state === 'thinking');
    cat.classList.toggle('cheer', cfg.state === 'success');
    setFrame(baseFrame());
  }

  function update(next) {
    if (!alive) return { installed: false };
    next = next || {};
    const framesChanged = Boolean(next.frames && next.frames.idle && next.frames.idle !== (cfg.frames && cfg.frames.idle));
    const previousScale = scale;
    Object.assign(cfg, next);
    if (framesChanged) frameName = '';
    if (typeof next.scale === 'number') scale = Math.max(120, Math.min(420, next.scale));
    if (scale !== previousScale) {
      wrap.style.width = scale + 'px';
      bubble.style.width = Math.max(184, Math.min(262, Math.round(scale * 1.06))) + 'px';
      applyPosition(pos || defaultPosition(), false);
    }
    applyState();
    applySkin(cfg.skin);
    if (bubble.classList.contains('show')) { renderQuota(); renderUsage(); }
    return status();
  }

  function status() {
    return {
      installed: alive && host.isConnected, version: VERSION, owner: cfg.owner, state: cfg.state,
      scale, pos: pos ? { x: Math.round(pos.x), y: Math.round(pos.y) } : null,
      bubble: bubble.classList.contains('show'), line: textShown,
      skin: !!document.getElementById('star-skin-style'),
      quota: cfg.quota || null, viewport: [innerWidth, innerHeight],
    };
  }

  // Morandi palette injected as one stylesheet. The vars come from morandi-gen.py so the IDE
  // follows the wallpaper instead of a fixed sky-blue theme.
  let backdropEl = null;

  function applySkin(skin) {
    const existing = document.getElementById('star-skin-style');
    let backdrop = backdropEl || document.getElementById('star-skin-backdrop');
    if (!skin || (!skin.wallpaper && (!skin.vars || !Object.keys(skin.vars).length))) {
      if (existing) existing.remove();
      if (backdrop) { backdrop.remove(); backdropEl = null; }
      return false;
    }
    if (skin.wallpaper) {
      if (!backdrop) { backdrop = document.createElement('div'); backdrop.id = 'star-skin-backdrop'; }
      backdropEl = backdrop;
      if (!backdrop.isConnected) (document.body || document.documentElement).prepend(backdrop);
      const url = `url("${skin.wallpaper}")`;
      if (backdrop.style.backgroundImage !== url) backdrop.style.backgroundImage = url;
    }
    let el = existing;
    if (!el) { el = document.createElement('style'); el.id = 'star-skin-style'; (document.head || document.documentElement).appendChild(el); }
    // 只把壁纸铺到最底层，并把宿主自带的不透明底色放开；配色、字体、圆角、面板一律不动
    const scrim = typeof skin.scrim === 'number' ? skin.scrim : 0.35;
    const vars = skin.vars && Object.keys(skin.vars).length
      ? `:root,html{${Object.keys(skin.vars).map((key) => `${key}:${skin.vars[key]}!important;`).join('')}}`
      : '';
    const css = `
${vars}
#root{position:relative!important;z-index:1!important}
#star-skin-backdrop{position:fixed!important;inset:0!important;z-index:0!important;pointer-events:none!important;
  background-repeat:no-repeat!important;background-size:cover!important;background-position:center!important}
#star-skin-backdrop::before{content:'';position:absolute;inset:0;background:rgba(8,6,14,${scrim})}
body,[class~="bg-background"]{background-color:transparent!important;background-image:none!important}
`;
    if (el.textContent !== css) el.textContent = css;
    return true;
  }

  // 标记输入框外壳，供上面的玻璃规则命中；宿主 DOM 没有稳定 class，只能按几何与样式找
  function markComposer() {
    try {
      const editable = document.querySelector('[contenteditable="true"]');
      if (!editable) return;
      let el = editable;
      for (let i = 0; i < 12 && el && el !== document.body; i++, el = el.parentElement) {
        const cs = getComputedStyle(el);
        const radius = parseFloat(cs.borderTopLeftRadius) || 0;
        const border = parseFloat(cs.borderTopWidth) || 0;
        const rect = el.getBoundingClientRect();
        if (radius >= 10 && rect.width >= 280 && (border > 0 || cs.backgroundColor !== 'rgba(0, 0, 0, 0)')) {
          el.setAttribute('data-star-composer', '');
          return;
        }
      }
    } catch (error) { /* 标记失败不影响桌宠 */ }
  }

  // The host rewrites document.body while booting and after some navigations, which detaches
  // the layer even though window.__starPet survives. Re-attach cheaply instead of re-injecting.
  const keepAlive = setInterval(() => {
    if (!alive) { clearInterval(keepAlive); return; }
    if (!host.isConnected && document.body) document.body.appendChild(host);
    if (cfg.skin) {
      if (!document.getElementById('star-skin-style')) applySkin(cfg.skin);
      else if (backdropEl && !backdropEl.isConnected && document.body) document.body.prepend(backdropEl);
      markComposer();
    }
  }, 1000);

  function destroy() {
    alive = false;
    clearInterval(keepAlive);
    clearTimeout(lineTimer);
    clearTimeout(blinkTimer);
    removeListeners();
    host.remove();
    const skin = document.getElementById('star-skin-style');
    if (skin) skin.remove();
    const backdrop = document.getElementById('star-skin-backdrop');
    if (backdrop) backdrop.remove();
    for (const el of document.querySelectorAll('[data-star-composer]')) el.removeAttribute('data-star-composer');
    try { delete window[KEY]; } catch (e) { window[KEY] = undefined; }
    return { removed: true };
  }

  // -- interaction ---------------------------------------------------------
  function onPointerDown(event) {
    if (event.button !== 0 && event.pointerType === 'mouse') return;
    event.stopPropagation();
    event.preventDefault();
    cat.setPointerCapture?.(event.pointerId);
    dragging = {
      pointerId: event.pointerId, moved: false,
      startX: event.clientX, startY: event.clientY,
      originX: pos.x, originY: pos.y,
    };
    cat.classList.add('pressed');
    hideBubble();
  }

  function onPointerMove(event) {
    if (!dragging || event.pointerId !== dragging.pointerId) return;
    event.stopPropagation();
    const dx = event.clientX - dragging.startX;
    const dy = event.clientY - dragging.startY;
    if (!dragging.moved && Math.hypot(dx, dy) < 4) return;
    dragging.moved = true;
    cat.classList.add('dragging');
    applyPosition({ x: dragging.originX + dx, y: dragging.originY + dy }, false);
  }

  function onPointerUp(event) {
    if (!dragging || event.pointerId !== dragging.pointerId) return;
    event.stopPropagation();
    const moved = dragging.moved;
    dragging = null;
    cat.classList.remove('dragging');
    cat.classList.remove('pressed');
    if (moved) {
      applyPosition(pos || defaultPosition(), true);
      showBubble('dragged', 2200);
    } else {
      showBubble(cfg.state === 'error' ? 'crying' : 'petting');
    }
  }

  function onPointerEnter() { hover = true; showBubble(null, 0); }
  function onPointerLeave() { hover = false; showBubble(null, 900); }

  function onKey(event) {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    event.preventDefault();
    showBubble('petting');
  }

  function onResize() { if (pos) applyPosition(pos, true); }

  function removeListeners() {
    cat.removeEventListener('pointerdown', onPointerDown);
    cat.removeEventListener('pointermove', onPointerMove);
    cat.removeEventListener('pointerup', onPointerUp);
    cat.removeEventListener('pointercancel', onPointerUp);
    cat.removeEventListener('pointerenter', onPointerEnter);
    cat.removeEventListener('pointerleave', onPointerLeave);
    cat.removeEventListener('keydown', onKey);
    window.removeEventListener('resize', onResize);
  }

  cat.addEventListener('pointerdown', onPointerDown);
  cat.addEventListener('pointermove', onPointerMove);
  cat.addEventListener('pointerup', onPointerUp);
  cat.addEventListener('pointercancel', onPointerUp);
  cat.addEventListener('pointerenter', onPointerEnter);
  cat.addEventListener('pointerleave', onPointerLeave);
  cat.addEventListener('keydown', onKey);
  window.addEventListener('resize', onResize);

  wrap.style.width = scale + 'px';
  bubble.style.width = Math.max(184, Math.min(262, Math.round(scale * 1.06))) + 'px';
  applyPosition(pos || defaultPosition(), false);
  applyState();
  applySkin(cfg.skin);
  setFrame(baseFrame());
  scheduleBlink();
  renderQuota();
  renderLine('idle');

  window[KEY] = { version: VERSION, update, status, destroy, owner: cfg.owner, get config() { return cfg; } };
  return status();
}
