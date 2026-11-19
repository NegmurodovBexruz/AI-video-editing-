"use strict";
/* Montaj studiyasi — client UI (2026-11-10 redesign). Hash routes: #bosh #videolar #video=<id> #uslublar #yangi #uslub-yarat.
   Same API as before: /api/health /api/styles /api/levels /api/jobs /api/style-jobs, uploads via PUT. */

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const STATE = { draft: ["", "Qoralama"], queued: ["warn", "Navbatda"], running: ["run", "Ishlayapti"], done: ["ok", "Tayyor"], failed: ["bad", "Xato"], cancelled: ["", "To'xtatilgan"] };
const DOC_EXT = [".md", ".txt"];
const VIDEO_EXT = [".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm", ".mxf", ".mts"];
const FB_EXT = [...VIDEO_EXT, ...DOC_EXT, ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".mp3", ".wav", ".m4a", ".aac", ".srt", ".json"];
const FB_STATES = ["done", "failed", "cancelled"];
const SOURCE_UZ = { plugin: "plagindan", "plugin+reference": "plagin + referens", reference: "referensdan", web: "internetdan", own: "AI o'zi yaratgan" };
const REF_USE = [["all", "Hammasi (ko'rinish)", "Titr, rang, harakat, o'tishlar va ritm referensdan olinadi"], ["rhythm", "Ritm va o'tishlar", "Kesim ritmi va o'tishlar referensdan; ko'rinish uslubdan"], ["captions", "Faqat titrlar", "Titr tizimi referensdan; qolgani uslubdan"], ["inspire", "Ilhom", "Uslub saqlanadi, referensdan 1–2 g'oya olinadi"]];
const AUTO_DEF = "AI videoga mos uslubni o'zi tanlaydi";
const LEVEL_POINTS = {
  min: ["Titrlar va kesimlar", "Rang va ovoz tozalanadi", "Grafika va AI kadrlar yo'q"],
  std: ["Minimaldagi hammasi", "Gapga mos grafika: raqamlar, kartalar, ikonkalar", "Musiqa va effekt tovushlari"],
  rich: ["Standartdagi hammasi", "AI yaratgan video kadrlar", "Murakkab sahnalar va o'tishlar"],
};
const KIND = { pod_glow: "twotier", talk_ahead: "counter", in_scene_type: "behind", holo_scene: "holo", ui_cascade: "icons", brand_stage: "stage", case_reel: "counter", spotlight_word: "word", editorial_showcase: "cards" };
const ICON = {
  up: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 16V4M7 9l5-5 5 5M4 20h16"/></svg>',
  clock: '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M9 2h6"/></svg>',
  x: '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
};

let styles = [], jobs = [], health = null, companies = [];
const seenStyleJobs = new Set();
let styleMessage = "";
let curCo = ""; try { curCo = localStorage.getItem("ms-co") || ""; } catch (_) {}   // "" = all, "_none" = no company
let LV = { rate: 18, levels: [], default: "std", max_usd: 500, formats: [], default_format: "9:16", est: { base: 10, per_sec: 0.6, level_add: {}, revision: 12 }, low_balance: 60, min_short_side: 720 };
const files = { raw: [], material: [], refdoc: [], refvideo: [], stylevideo: [] };
const matInfo = new WeakMap();   // File -> {note, required} for extra materials
const IMAGE_EXT = [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"];
const meta = new WeakMap();      // File -> {w, h, duration} read in the browser before upload
const draft = { refLike: "", style: "auto", level: null, usd: "", title: "", text: "", sTitle: "", sText: "", company: null, sCompany: null, format: null };
const fb = { job: null, text: "", files: [] };
let route = { name: "bosh", id: null };
let vstate = { ver: null, tab: "done", sig: "" };
let listSig = "", vFilter = { s: "", mode: "grid" }, sFilter = "all", query = "";

/* ---------- utils ---------- */
function esc(s) { return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function size(n) { if (n == null) return ""; const u = ["B", "KB", "MB", "GB"]; let i = 0; while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; } return (i ? n.toFixed(n < 10 ? 1 : 0) : n) + " " + u[i]; }
function when(iso) { if (!iso) return "—"; const d = new Date(iso), p = x => String(x).padStart(2, "0"); return `${p(d.getDate())}.${p(d.getMonth() + 1)} ${p(d.getHours())}:${p(d.getMinutes())}`; }
function dur(a, b) { if (!a) return "—"; const s = Math.max(0, Math.round(((b ? new Date(b) : new Date()) - new Date(a)) / 1000)); const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), r = s % 60; return h ? `${h} soat ${m} daq` : m ? `${m} daq ${r} s` : `${r} s`; }
function ext(n) { const i = n.lastIndexOf("."); return i < 0 ? "" : n.slice(i).toLowerCase(); }
function tc(sec) { const m = Math.floor(sec / 60), s = sec - m * 60; return `${m}:${s.toFixed(1).padStart(4, "0")}`; }
function money(x) { return "$" + (Number(x) || 0).toFixed(2); }
function usd(kr) { const d = (Number(kr) || 0) / LV.rate; return "$" + (d < 10 ? d.toFixed(2) : d.toFixed(0)); }
function chip(state) { const s = STATE[state] || ["", state]; return `<span class="chip ${s[0]}">${s[1]}</span>`; }
function fileUrl(id, p, dl) { return `/api/jobs/${encodeURIComponent(id)}/file?path=${encodeURIComponent(p)}${dl ? "&dl=1" : ""}`; }
function lvById(id) { return LV.levels.find(l => l.id === id); }
function styleTitle(n) {
  if (!n || n === "auto") return "Avtomatik";
  if (n.startsWith("custom:")) return "Yangi uslub: " + n.slice(7).replace(/_/g, " ");
  return (styles.find(s => s.name === n) || {}).title || n;
}
function jobStyle(j) {
  if (j.kind === "style") return j.new_style ? `Yangi uslub → ${j.new_style_title || j.new_style}` : "Uslub yaratish";
  if (j.style === "auto") return j.style_used ? `Avtomatik → ${styleTitle(j.style_used)}${SOURCE_UZ[j.style_source] ? ` (${SOURCE_UZ[j.style_source]})` : ""}` : "Avtomatik";
  return styleTitle(j.style);
}
function jobName(j) { return j.title || (j.raw && j.raw[0]) || (j.kind === "style" ? "Yangi uslub" : j.id); }
function jobCredits(j) { return (j.versions || []).reduce((a, v) => a + (Number(v.credits_spent) || 0), 0) + (Number(j.credits_spent) || 0); }
function nVersions(j) { return (j.versions || []).length + (j.video ? 1 : 0); }
function fmtById(id) { return (LV.formats || []).find(f => f.id === id); }
function estMinutes(sec, level) { const e = LV.est; return Math.max(5, Math.round(e.base + e.per_sec * sec + ((e.level_add || {})[level] || 0))); }
function minLeft(j) {
  if (!j.est_minutes) return null;
  if (j.state === "queued") return j.est_minutes;
  if (j.state === "running" && j.started) return Math.max(1, Math.round(j.est_minutes - (Date.now() - new Date(j.started)) / 60000));
  return null;
}
function queueAhead(exceptId) {   // minutes until the worker is free (running job's remainder + queued jobs)
  return jobs.filter(j => (j.state === "running" || j.state === "queued") && j.id !== exceptId && !j.archived)
    .reduce((a, j) => a + (minLeft(j) || (j.state === "running" ? 10 : LV.est.base)), 0);
}
function balanceNote(needKr) {
  const b = health && health.balance;
  if (!b) return "";
  if (needKr != null && needKr > b.kr) return `<div class="box err">Higgsfield balansi yetmasligi mumkin: oxirgi ma'lum balans <b>${b.kr} kr</b> (${when(b.at)}), belgilangan limit esa ${needKr} kr. Kredit to'ldiring yoki limitni pasaytiring.</div>`;
  if (b.low) return `<div class="box warn-box">Higgsfield balansi kam: <b>${b.kr} kr</b> (~${usd(b.kr)}), ${when(b.at)} holatiga ko'ra. ${b.threshold} kr dan kam qoldi. Kredit to'ldirishni unutmang.</div>`;
  return "";
}

/* ---------- companies ---------- */
function coById(id) { return companies.find(c => c.id === id); }
function coName(id) { const c = coById(id); return c ? c.name : "Kompaniyasiz"; }
function avatar(c, cls = "") { return c ? `<span class="av ${cls}" style="background:${esc(c.color)}" aria-hidden="true">${esc(c.initials)}</span>` : `<span class="av all ${cls}" aria-hidden="true">—</span>`; }
function coFilter(j) { return !curCo || (curCo === "_none" ? !j.company : j.company === curCo); }
function coLabel() { return !curCo ? "Barcha kompaniyalar" : curCo === "_none" ? "Kompaniyasiz" : coName(curCo); }
function coOptions(sel) { return `<option value="">Kompaniyasiz</option>` + companies.filter(c => !c.archived).map(c => `<option value="${esc(c.id)}"${c.id === sel ? " selected" : ""}>${esc(c.name)}</option>`).join(""); }
function defaultCo() { return curCo && curCo !== "_none" && !(coById(curCo) || {}).archived ? curCo : ""; }
async function loadCompanies() {
  try { companies = await api("/api/companies"); } catch (_) { companies = []; }
  if (curCo && curCo !== "_none" && !coById(curCo)) curCo = "";
  renderSwitcher();
}
function setCo(id) {
  curCo = id; try { localStorage.setItem("ms-co", id); } catch (_) {}
  renderSwitcher(); listSig = ""; loadJobs(); render();
}
function renderSwitcher(open) {
  const c = curCo && curCo !== "_none" ? coById(curCo) : null;
  const vis = jobs.filter(j => j.state !== "draft");
  const count = id => vis.filter(j => (id === "_none" ? !j.company : j.company === id)).length;
  const item = (id, label, av, n) => `<button type="button" class="coitem" data-co="${esc(id)}" aria-current="${curCo === id}">${av}<span class="nm">${esc(label)}</span><span class="n">${n}</span></button>`;
  const live = companies.filter(x => !x.archived), arch = companies.filter(x => x.archived);
  $("#cosw").innerHTML = `<button type="button" class="cobtn" id="cobtn" aria-haspopup="true" aria-expanded="${!!open}">${c ? avatar(c) : `<span class="av all" aria-hidden="true">${curCo === "_none" ? "—" : "∗"}</span>`}
      <span class="t"><small>Kompaniya${c && c.archived ? " · arxivda" : ""}</small><b>${esc(coLabel())}</b></span><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 10l5-5 5 5M7 14l5 5 5-5"/></svg></button>
    <div class="comenu" id="comenu" ${open ? "" : "hidden"}>
      ${item("", "Barcha kompaniyalar", `<span class="av all sm" aria-hidden="true">∗</span>`, vis.length)}
      ${live.length ? `<div class="lbl2">Kompaniyalar</div>` + live.map(x => item(x.id, x.name, avatar(x, "sm"), count(x.id))).join("") : ""}
      ${count("_none") ? item("_none", "Kompaniyasiz", `<span class="av all sm" aria-hidden="true">—</span>`, count("_none")) : ""}
      ${arch.length ? `<details class="coarch"><summary class="lbl2">Arxiv (${arch.length})</summary>${arch.map(x => `<div class="corow">${item(x.id, x.name, avatar(x, "sm"), count(x.id))}<button type="button" class="btn" data-unarch="${esc(x.id)}">Qaytarish</button></div>`).join("")}</details>` : ""}
      ${c && !c.archived ? `<hr><button type="button" class="coitem" data-arch="${esc(c.id)}"><span class="av all sm" aria-hidden="true">⤓</span><span class="nm">"${esc(c.name)}" ni arxivlash</span></button><p class="note" style="margin:0 10px 6px">Arxivlangan kompaniya o'chmaydi: videolari saqlanadi, uni qaytarish mumkin.</p>` : ""}
      <hr><form class="coadd" id="coadd" novalidate><input class="f" id="coName" maxlength="80" placeholder="Yangi kompaniya nomi" aria-label="Yangi kompaniya nomi"><button type="submit" class="btn pri">+ Qo'shish</button></form>
      <p class="note msg" id="coMsg" style="margin:0 10px 6px"></p></div>`;
}

async function api(path, opts = {}) {
  const o = { ...opts, headers: { "X-Dash": "1", ...(opts.headers || {}) } };
  if (o.json !== undefined) { o.body = JSON.stringify(o.json); o.headers["Content-Type"] = "application/json"; delete o.json; }
  const r = await fetch(path, o);
  const data = await r.json().catch(() => ({}));
  if (r.status === 401 && data.login) { location.href = "/login"; throw new Error("Avval tizimga kiring"); }
  if (!r.ok) throw new Error(data.error || `HTTP ${r.status}`);
  return data;
}
function put(url, file, onProgress) {
  return new Promise((resolve, reject) => {
    const x = new XMLHttpRequest();
    x.open("PUT", url); x.setRequestHeader("X-Dash", "1");
    x.upload.onprogress = e => onProgress(e.loaded);
    x.onload = () => { let d = {}; try { d = JSON.parse(x.responseText); } catch (_) {} if (x.status === 401) location.href = "/login"; x.status < 300 ? resolve(d) : reject(new Error(d.error || `HTTP ${x.status}`)); };
    x.onerror = () => reject(new Error("Tarmoq xatosi"));
    x.send(file);
  });
}
let me = { auth: false, user: null };
async function loadMe() { try { me = await api("/api/me"); } catch (_) {} sidefoot(); }

/* ---------- generated style previews ---------- */
function paint(cv, hue, kind, seed) {
  const w = cv.width = 480, h = cv.height = 300, x = cv.getContext("2d");
  const g = x.createLinearGradient(0, 0, w, h);
  g.addColorStop(0, `hsl(${hue},28%,26%)`); g.addColorStop(1, `hsl(${(hue + 30) % 360},24%,9%)`);
  x.fillStyle = g; x.fillRect(0, 0, w, h);
  const sx = w * (0.42 + (seed % 3) * 0.06), acc = `hsl(${hue},80%,62%)`, F = "'Fira Sans', sans-serif";
  x.textAlign = "center";
  if (kind === "behind") { x.fillStyle = acc; x.font = `900 104px ${F}`; x.fillText("KATTA", w / 2, h * .5); }
  x.fillStyle = kind === "behind" ? `hsl(${hue},20%,22%)` : "rgba(255,255,255,.14)";
  x.beginPath(); x.arc(sx, h * .38, 42, 0, 7); x.fill();
  x.beginPath(); x.moveTo(sx - 95, h); x.quadraticCurveTo(sx, h * .46, sx + 95, h); x.fill();
  if (kind === "twotier") { x.fillStyle = "#fff"; x.font = `italic 600 18px ${F}`; x.fillText("har kuni", w / 2, h * .66); x.fillStyle = acc; x.font = `italic 800 34px ${F}`; x.fillText("ASOSIY G'OYA", w / 2, h * .79); }
  else if (kind === "counter") { x.fillStyle = acc; x.fillRect(w * .6, h * .3, 150, 64); x.fillStyle = "#fff"; x.font = `800 44px ${F}`; x.textAlign = "left"; x.fillText("30%", w * .6 + 14, h * .3 + 50); }
  else if (kind === "holo") { x.strokeStyle = "rgba(90,230,255,.85)"; x.lineWidth = 2; for (let i = 0; i < 4; i++) x.strokeRect(w * .62 + i * 6, h * .2 + i * 6, 120, 80); }
  else if (kind === "icons") { ["#c000e6", acc, "#ffffff"].forEach((c, j) => { x.fillStyle = c; x.fillRect(w * .3 + j * 70, h * .1, 56, 56); }); }
  else if (kind === "stage") { x.fillStyle = acc; x.fillRect(w * .55, 0, w * .45, h); x.fillStyle = "#fff"; x.font = `700 22px ${F}`; x.fillText("Brend", w * .775, h * .52); }
  else if (kind === "word") { x.fillStyle = "#ffd400"; x.font = `900 54px ${F}`; x.fillText("SO'Z", w / 2, h * .8); }
  else if (kind === "cards") { for (let k = 0; k < 3; k++) { x.save(); x.translate(w * .7, h * .62); x.rotate((k - 1) * .18); x.fillStyle = k === 1 ? "#fff" : "rgba(255,255,255,.75)"; x.fillRect(-48, -66, 96, 128); x.restore(); } }
}
function paintAll(root) { $$("canvas[data-hue]", root).forEach(c => paint(c, +c.dataset.hue, c.dataset.kind, +(c.dataset.seed || 0))); }

/* ---------- loaders ---------- */
async function loadStyles() {
  styles = await api("/api/styles"); $("#cntS").textContent = styles.length;
  if (draft.style !== "auto" && !styles.some(s => s.name === draft.style)) draft.style = "auto";
}
async function loadLevels() { LV = { ...LV, ...(await api("/api/levels")) }; if (!draft.level && draft.usd === "") draft.level = LV.default; if (!draft.format) draft.format = LV.default_format; }
async function loadHealth() { try { health = await api("/api/health"); } catch (_) { health = null; } sidefoot(); }
async function loadJobs() {
  try { jobs = (await api("/api/jobs")).filter(j => !j.archived); } catch (_) { return; }
  const vis = jobs.filter(j => j.state !== "draft");
  $("#cntV").textContent = vis.filter(coFilter).length;
  const completedStyles = vis.filter(j => j.kind === "style" && j.state === "done" && j.new_style && !seenStyleJobs.has(j.id));
  if (completedStyles.length) {
    try { await loadStyles(); completedStyles.forEach(j => seenStyleJobs.add(j.id)); } catch (_) {}
  }
  sidefoot();
  const sig = vis.map(j => [j.id, j.state, j.revision || 0, j.video || "", (j.versions || []).length, j.company || ""].join(":")).join("|");
  if (sig !== listSig) { listSig = sig; if (!$("#comenu") || $("#comenu").hidden) renderSwitcher(); if (["bosh", "videolar", "uslublar"].includes(route.name)) render(); }
}
function sidefoot() {
  const rows = [], b = health && health.balance;
  if (b) {
    rows.push(`<div class="row"><span>${b.low ? `<span class="dot warn"></span>` : ""}Higgsfield balansi</span><b class="num" style="${b.low ? "color:#fbbf24" : ""}">${b.kr} kr</b></div>`);
    rows.push(`<div class="row"><span>≈ dollarda · ${when(b.at)}</span><b class="num">${usd(b.kr)}</b></div>`);
    if (b.low) rows.push(`<div class="row"><span style="color:#fbbf24">Balans kam: ${b.threshold} kr dan kam</span></div>`);
  } else rows.push(`<div class="row"><span>Higgsfield balansi</span><b>—</b></div>`);
  if (!health) rows.push(`<div class="row"><span><span class="dot bad"></span>Server bilan aloqa yo'q</span></div>`);
  else {
    if (health.dry_run) rows.push(`<div class="row"><span><span class="dot warn"></span>DRY RUN: soxta agent</span></div>`);
    const apiMode = health.claude_auth && health.claude_auth.mode === "api";
    const ready = health.claude && health.claude_login !== false;
    const agentStatus = health.dry_run ? "Sinov agenti tayyor" : !health.claude ? "Claude Code topilmadi" : apiMode ? (ready ? "Claude API sozlangan" : "Claude API kaliti kiritilmagan") : (ready ? "Claude Code tayyor" : "Claude ulanishi sozlanmagan");
    rows.push(`<div class="row"><span><span class="dot ${ready ? "" : "bad"}"></span>${agentStatus}</span><b>${health.current ? "ishlayapti: 1" : "bo'sh"}</b></div>`);
    if (!health.dry_run && health.higgsfield_mcp) rows.push(`<div class="row"><span><span class="dot ${health.higgsfield_mcp.configured ? "warn" : "bad"}"></span>${health.higgsfield_mcp.configured ? "Higgsfield: kirishni tekshiring" : "Higgsfield ulanishi sozlanmagan"}</span></div>`);
    if (health.worker_disabled) rows.push(`<div class="row"><span><span class="dot bad"></span>Ishchi o'chiq: boshqa dashbord xizmat qilyapti</span></div>`);
  }
  if (me.auth && me.user) rows.push(`<div class="row user"><span>👤 ${esc(me.user)}</span><span><button type="button" class="sfbtn" id="pwOpen">Parol</button><button type="button" class="sfbtn" id="logout">Chiqish</button></span></div>`);
  $("#sidefoot").innerHTML = rows.join("");
}

/* ---------- shared pieces ---------- */
function thumb(j) {
  let inner;
  if (j.video) inner = `<video muted playsinline preload="metadata" src="${fileUrl(j.id, j.video)}#t=1" aria-hidden="true" tabindex="-1"></video>`;
  else if (j.kind === "style") inner = `<span class="ph">${j.state === "done" ? "Yangi uslub ro'yxatga qo'shildi" : "Videolar tahlil qilinmoqda"}</span>`;
  else if (j.expired) inner = `<span class="ph">Saqlash muddati tugadi: video o'chirilgan</span>`;
  else inner = `<span class="ph">${j.state === "queued" ? "Navbatda turibdi" : j.state === "running" ? "Video tayyorlanmoqda" : j.state === "failed" ? "Video chiqmadi" : "Video yo'q"}</span>`;
  const nv = nVersions(j);
  return `<div class="thumb">${inner}<span class="tl">${chip(j.state)}${expiryChip(j)}</span>${nv > 1 ? `<span class="tr">v${nv}</span>` : ""}</div>`;
}
function daysLeft(j) {
  if (!j.expires_at) return null;
  return Math.max(0, Math.ceil((new Date(j.expires_at) - Date.now()) / 86400000));
}
function expiryChip(j) {
  if (j.expired) return ` <span class="chip">muddati tugadi</span>`;
  const d = daysLeft(j);
  return d === null ? "" : ` <span class="chip ${d <= 2 ? "warn" : ""}" title="Shu muddatdan keyin videolar serverdan o'chadi">${d ? d + " kun qoldi" : "bugun o'chadi"}</span>`;
}
function saveStyleCard(j) {
  if (j.saved_style_job) return `<div class="box info">Bu videoning uslubi saqlanmoqda yoki saqlangan: <a href="#video=${encodeURIComponent(j.saved_style_job)}">uslub yaratish ishini ochish</a>.</div>`;
  const nref = (j.refs || []).filter(r => VIDEO_EXT.includes(ext(r))).length;
  if (!nref) return "";
  return `<div class="card pad"><h2 style="font-size:16px;margin-bottom:6px">Shu uslubni saqlash</h2>
    <p class="sub" style="margin:0 0 10px">Yoqqan bo'lsa, bu ko'rinishni uslublar ro'yxatiga qo'shing: keyingi videolarni shu uslubda tez va arzonroq qilish mumkin bo'ladi. Namunalar: ${nref} ta referens + shu natija video + uslub kartasi. Alohida ish bo'lib bajariladi (~1–2 soat, kredit sarflanmaydi, Claude xarajati bor).</p>
    <div class="filters"><input class="f" id="ssName" maxlength="120" placeholder="Uslub nomi, masalan: Qizil nuqta promo" style="flex:1 1 220px"><button type="button" class="btn pri" data-savestyle="${esc(j.id)}">Uslubni saqlash</button></div>
    <p class="note msg" id="ssMsg" role="status"></p></div>`;
}
function vcard(j) {
  const kr = jobCredits(j), lv = lvById(j.level);
  return `<a class="card vcard" href="#video=${encodeURIComponent(j.id)}">${thumb(j)}<div class="vbody"><h3>${esc(jobName(j))}</h3>
    <div class="meta">${!curCo && j.company ? `${avatar(coById(j.company), "sm")}<span>${esc(coName(j.company))}</span><span>·</span>` : ""}<span>${esc(jobStyle(j))}</span>${lv ? `<span>·</span><span>${esc(lv.title)}</span>` : ""}${j.format ? `<span>·</span><span>${esc(j.format)}</span>` : ""}<span>·</span><span>${when(j.created)}</span>${j.qa && j.qa.total ? `<span class="chip ${j.qa.fails.length ? "bad" : j.qa.warns.length ? "warn" : "ok"}">QA ${j.qa.passed}/${j.qa.total}</span>` : ""}</div>
    ${j.state === "failed" && j.error ? `<p>${esc(j.error.slice(0, 120))}</p>` : ""}
    <div class="costline"><span title="Higgsfield"><i style="background:var(--hf)"></i>${usd(kr)}</span><span title="Claude: statistika keyingi bosqichda"><i style="background:var(--cl)"></i>—</span><b>${kr ? kr.toFixed(1).replace(/\.0$/, "") + " kr" : "0 kr"}</b></div></div></a>`;
}
function empty(title, text, action) { return `<div class="card empty"><b>${title}</b><span>${text}</span>${action || ""}</div>`; }

/* ---------- views ---------- */
const VIEWS = {
  bosh: { title: "Bosh sahifa", crumb: [], render() {
    const vis = jobs.filter(j => j.state !== "draft" && coFilter(j)), vids = vis.filter(j => j.kind !== "style");
    const done = vids.filter(j => j.state === "done").length, active = vis.filter(j => j.state === "running" || j.state === "queued");
    const kr = vids.reduce((a, j) => a + jobCredits(j), 0);
    const recent = vids.filter(j => j.video).sort((a, b) => (b.finished || b.created || "").localeCompare(a.finished || a.created || "")).slice(0, 6);
    return `${balanceNote()}<div class="kpis">
      <div class="card kpi"><div class="l">Videolar</div><div class="v">${done} / ${vids.length}</div><div class="s">tayyor / jami</div></div>
      <div class="card kpi"><div class="l">Jarayonda</div><div class="v">${active.length}</div><div class="s">${active.length ? "navbatda yoki ishlayapti" : "hozir hech narsa ishlamayapti"}</div></div>
      <div class="card kpi"><div class="l"><i style="background:var(--hf)"></i>Higgsfield</div><div class="v">${usd(kr)}</div><div class="s">${kr.toFixed(1)} kr · barcha versiyalar</div></div>
      <div class="card kpi"><div class="l"><i style="background:var(--cl)"></i>Claude</div><div class="v dim">—</div><div class="s">statistika keyingi bosqichda</div></div></div>
    <div class="grid2">
      <div class="card pad"><div class="chead"><h2>Jarayonda</h2><span class="sub">${active.length} ta</span></div>
        ${active.length ? active.map(j => { const ml = minLeft(j); return `<a class="qrow" href="#video=${encodeURIComponent(j.id)}"><div><b>${esc(jobName(j))}</b><small>${esc(jobStyle(j))} · ${j.state === "running" ? "ishlayapti " + dur(j.started) : "boshlanishini kutyapti"}${ml ? ` · taxminan ${ml} daq qoldi` : ""}${j.revision ? " · tuzatish " + j.revision : ""}</small></div>${chip(j.state)}</a>`; }).join("")
          : `<p class="sub" style="margin:0">Hozir hech narsa ishlamayapti. Yangi video qo'shsangiz shu yerda ko'rinadi.</p>`}</div>
      <div class="card pad"><div class="chead"><h2>Tezkor harakatlar</h2></div><div class="filters">
        <a class="btn pri" href="#yangi">+ Yangi video</a><a class="btn" href="#uslub-yarat">Uslub yaratish</a><a class="btn" href="#uslublar">Uslublar katalogi</a></div>
        <p class="note">Montaj to'liq avtomatik: tasdiq so'ralmaydi, natija "Videolar"da chiqadi.</p></div>
    </div>
    <div><div class="chead"><h2>Oxirgi videolar</h2><a class="btn" href="#videolar">Hammasi →</a></div>
      ${recent.length ? `<div class="cgrid">${recent.map(vcard).join("")}</div>` : empty("Hali tayyor video yo'q", "Birinchi videoni yuklang, AI o'zi montaj qiladi.", `<a class="btn pri" href="#yangi">+ Yangi video</a>`)}</div>`;
  } },

  videolar: { title: "Videolar", crumb: [], render() {
    const qq = query.toLowerCase();
    const list = jobs.filter(j => j.state !== "draft" && coFilter(j))
      .filter(j => !vFilter.s || (vFilter.s === "active" ? ["queued", "running"].includes(j.state) : j.state === vFilter.s))
      .filter(j => !qq || (jobName(j) + " " + jobStyle(j) + " " + (j.raw || []).join(" ")).toLowerCase().includes(qq));
    const seg = [["", "Hammasi"], ["done", "Tayyor"], ["active", "Jarayonda"], ["failed", "Xato"]].map(([v, t]) => `<button type="button" data-fs="${v}" aria-pressed="${vFilter.s === v}">${t}</button>`).join("");
    const head = `<div class="filters"><div class="seg" role="group" aria-label="Holat">${seg}</div>
      <span class="seg" role="group" aria-label="Ko'rinish" style="margin-left:auto"><button type="button" data-fm="grid" aria-pressed="${vFilter.mode === "grid"}">Katalog</button><button type="button" data-fm="list" aria-pressed="${vFilter.mode === "list"}">Jadval</button></span></div>`;
    if (!list.length) return head + empty(query || vFilter.s ? "Hech narsa topilmadi" : "Hali video yo'q", query || vFilter.s ? "Filtr yoki qidiruvni o'zgartiring." : "Birinchi videoni yuklang.", `<a class="btn pri" href="#yangi">+ Yangi video</a>`);
    if (vFilter.mode === "grid") return head + `<div class="cgrid">${list.map(vcard).join("")}</div>`;
    return head + `<div class="card"><div class="tbl"><table><thead><tr><th>Video</th><th>Uslub</th><th>Daraja</th><th>Holat</th><th class="n">Versiya</th><th class="n">Higgsfield</th><th>Yaratilgan</th></tr></thead><tbody>${list.map(j => {
      const kr = jobCredits(j), lv = lvById(j.level);
      return `<tr data-go="#video=${encodeURIComponent(j.id)}" tabindex="0"><td><b>${esc(jobName(j))}</b></td><td>${esc(jobStyle(j))}</td><td>${lv ? esc(lv.title) : "—"}</td><td>${chip(j.state)}</td><td class="n">${nVersions(j) || "—"}</td><td class="n">${usd(kr)} · ${kr.toFixed(1)} kr</td><td>${when(j.created)}</td></tr>`;
    }).join("")}</tbody></table></div></div>`;
  } },

  uslublar: { title: "Uslublar katalogi", crumb: [], render() {
    const qq = query.toLowerCase();
    const used = n => jobs.filter(j => j.style === n || j.style_used === n).length;
    const list = styles.filter(s => sFilter === "all" || (sFilter === "ag") === !!s.agency).filter(s => !qq || (s.title + " " + s.def).toLowerCase().includes(qq));
    const seg = [["all", "Hammasi"], ["base", "Umumiy"], ["ag", "Agentlik uslublari"]].map(([v, t]) => `<button type="button" data-sf="${v}" aria-pressed="${sFilter === v}">${t}</button>`).join("");
    const cards = list.map((s, i) => `<div class="card scard"><div class="thumb"><canvas data-hue="${(styles.indexOf(s) * 37 + 18) % 360}" data-kind="${KIND[s.name] || "cards"}" data-seed="${i}" aria-hidden="true"></canvas>${s.agency ? `<span class="tl"><span class="chip amb">Agentlik</span></span>` : ""}</div>
      <div class="vbody"><h3>${esc(s.title)}</h3><p>${esc(s.def || s.fits)}</p>${s.agency && s.from_company ? `<div class="meta">${avatar(coById(s.from_company), "sm")}<span>${esc(coName(s.from_company))} referenslaridan</span></div>` : ""}</div>
      <div class="foot"><span class="sub">${used(s.name)} ta videoda</span><div class="style-actions"><button type="button" class="btn danger" data-delete-style="${esc(s.name)}" aria-label="${esc(s.title)} uslubini o'chirish">O'chirish</button><a class="btn" href="#yangi" data-pick="${esc(s.name)}">Tanlash →</a></div></div></div>`).join("");
    return `<p class="note" id="styleMessage" role="status">${esc(styleMessage)}</p><div class="filters"><div class="seg" role="group" aria-label="Guruh">${seg}</div><a class="btn" style="margin-left:auto" href="#uslub-yarat">+ Uslub yaratish</a></div>` +
      (list.length ? `<div class="cgrid">${cards}</div>` : empty(sFilter === "ag" ? "Hali agentlik uslubi yo'q" : "Hech narsa topilmadi", sFilter === "ag" ? "Yoqqan uslubdagi 2 ta videodan yangi uslub yarating." : "Qidiruvni o'zgartiring.", `<a class="btn pri" href="#uslub-yarat">Uslub yaratish</a>`));
  } },

  yangi: { title: "Yangi video", crumb: ["videolar"], render() {
    const base = styles.filter(s => !s.agency), ag = styles.filter(s => s.agency);
    const srow = (v, t, d) => `<label class="srow"><input type="radio" name="style" value="${esc(v)}"${v === draft.style ? " checked" : ""}><div><b>${esc(t)}</b><span>${esc(d)}</span></div></label>`;
    const cur = draft.style === "auto" ? ["Avtomatik", AUTO_DEF] : [styleTitle(draft.style), (styles.find(s => s.name === draft.style) || {}).def || ""];
    return `<div class="wizard"><form class="card" id="newForm" novalidate>
      <div class="sec"><h3><span class="n">1</span>Kompaniya</h3>
        <select class="f" id="newCo" aria-label="Kompaniya">${coOptions(draft.company ?? defaultCo())}</select>
        <p class="note" style="margin-top:6px">Yangi kompaniyani chapdagi kompaniya menyusidan qo'shing.</p></div>
      <div class="sec"><h3><span class="n">2</span>Video</h3>
        <div class="drop" data-kind="raw" tabindex="0" role="button"><input type="file" multiple accept="video/*,.mkv,.mxf,.mts" hidden>${ICON.up}<b>Videoni shu yerga tashlang</b><span>yoki bosib tanlang · bir nechta fayl bo'lishi mumkin · imkoni bo'lsa 4K / 1440p</span></div>
        <ul class="files" data-list="raw"></ul>
        <div class="matbox"><span class="lbl" style="margin-top:14px">Qo'shimcha materiallar <em class="sub">ixtiyoriy · rasm, video, logo</em></span>
          <div class="drop small" data-kind="material" tabindex="0" role="button"><input type="file" multiple accept="image/*,.svg,video/*,.mkv,.mxf,.mts" hidden><b>Rasm va videolarni tashlang</b><span>AI ularni montajga qo'shadi: mahsulot, ofis, jarayon, logo</span></div>
          <ul class="files mats" data-list="material"></ul></div>
        <label style="display:block;margin-top:12px"><span class="lbl">Nomi (ixtiyoriy)</span><input class="f" id="title" maxlength="120" value="${esc(draft.title)}" placeholder="Masalan: Noyabr aksiyasi, 30 s"></label></div>
      <div class="sec"><h3><span class="n">3</span>Format</h3><div class="fmts" role="radiogroup" aria-label="Format">${(LV.formats || []).map(f => {
          const k = 46 / Math.max(f.w, f.h);
          return `<label class="fmt"><input type="radio" name="fmt" value="${esc(f.id)}"${f.id === draft.format ? " checked" : ""}><span class="shape" style="width:${Math.round(f.w * k)}px;height:${Math.round(f.h * k)}px" aria-hidden="true"></span><b>${esc(f.title)}</b><span>${esc(f.use)}</span><small>${f.w}×${f.h}</small></label>`;
        }).join("")}</div></div>
      <div class="sec"><h3><span class="n">4</span>Uslub</h3>
        <div class="cur"><div><b id="curName">${esc(cur[0])}</b><p id="curDef">${esc(cur[1])}</p></div><button type="button" class="btn" id="tgl" aria-expanded="false" aria-controls="slist">Uslubni o'zgartirish</button></div>
        <div class="slist" id="slist" role="radiogroup" aria-label="Uslub" hidden><div class="sgroup">Umumiy uslublar</div>${srow("auto", "Avtomatik", AUTO_DEF)}${base.map(s => srow(s.name, s.title, s.def || s.fits)).join("")}
          ${ag.length ? `<div class="sgroup">Agentlik uslublari</div>${ag.map(s => srow(s.name, s.title, s.def || s.fits)).join("")}` : ""}</div></div>
      <div class="sec"><h3><span class="n">5</span>Montaj uchun limit</h3><p class="note" style="margin:0 0 12px">Darajani tanlang yoki pastda limitni o'zingiz yozing.</p><div class="levels" role="radiogroup" aria-label="Montaj darajasi">${LV.levels.map(l => `<label class="lvl"><input type="radio" name="lvl" value="${l.id}"${l.id === draft.level ? " checked" : ""}><b>${esc(l.title)}</b>
          <ul>${(LEVEL_POINTS[l.id] || []).map(p => `<li>${esc(p)}</li>`).join("")}</ul>
          <div class="p">Higgsfield: <b>${l.min === l.max ? l.max : l.min + "–" + l.max} kr</b><br><span style="white-space:nowrap">≈ ${l.max === 0 ? "$0" : usd(l.min) + "–" + usd(l.max).slice(1)}</span><br>+ Claude, taxminiy</div></label>`).join("")}</div>
        <div class="caprow"><label><span class="lbl">Yoki limitni yozing, $</span><input class="f" id="usd" type="number" min="0" max="${LV.max_usd}" step="0.01" value="${esc(draft.usd)}" placeholder="masalan 2" aria-describedby="capinfo"></label><div class="capinfo" id="capinfo" role="status"></div></div></div>
      <div class="sec"><h3><span class="n">6</span>Istaklar <em>ixtiyoriy</em></h3>
        <textarea class="f" id="refText" placeholder="Masalan: brend rangi #1E40AF, oxirida logotip chiqsin, spikerning ismi Aziz Karimov">${esc(draft.text)}</textarea>
        <div class="drops"><div class="drop small" data-kind="refdoc" tabindex="0" role="button"><input type="file" multiple accept=".md,.txt" hidden><b>Fayllar</b><span>.md / .txt</span></div>
          <div class="drop small" data-kind="refvideo" tabindex="0" role="button"><input type="file" multiple accept="video/*,.mkv,.mxf,.mts" hidden><b>Yoqqan videolar</b><span>AI namuna sifatida ko'radi</span></div></div>
        <ul class="files" data-list="refdoc"></ul><ul class="files" data-list="refvideo"></ul><div id="refUse"></div></div>
    </form>
    <aside class="card pad summary"><h2 style="margin-bottom:8px">Xulosa</h2><div id="balNote"></div><div id="sum"></div>
      <button type="button" class="btn pri" id="go">Montajni boshlash</button>
      <div class="upload" id="upload" hidden><div class="bar"><i></i></div><div class="utext"></div></div>
      <p class="note msg" id="formMsg" role="status">Tasdiq so'ralmaydi. Tayyor bo'lganda "Videolar"da ko'rinadi.</p></aside></div>`;
  }, after() { ["raw", "material", "refdoc", "refvideo"].forEach(renderFiles); summary(); } },

  "uslub-yarat": { title: "Uslub yaratish", crumb: ["uslublar"], render() {
    return `<div class="wizard"><form class="card" novalidate>
      <div class="sec"><h3><span class="n">1</span>Qaysi kompaniya uchun</h3>
        <select class="f" id="styleCo" aria-label="Kompaniya">${coOptions(draft.sCompany ?? defaultCo())}</select>
        <p class="note" style="margin-top:6px">Uslub baribir hamma kompaniya uchun tanlanadi. Bu faqat qayerdan kelganini belgilaydi.</p></div>
      <div class="sec"><h3><span class="n">2</span>Namuna videolar <em>kamida 2 ta</em></h3>
        <div class="drop" data-kind="stylevideo" tabindex="0" role="button"><input type="file" multiple accept="video/*,.mkv,.mxf,.mts" hidden>${ICON.up}<b>Bir xil uslubdagi videolarni tashlang</b><span>kamida 2 ta · "Before/After" postlarda faqat "After" qismi olinadi</span></div>
        <ul class="files" data-list="stylevideo"></ul></div>
      <div class="sec"><h3><span class="n">3</span>Nomi va izoh <em>ixtiyoriy</em></h3>
        <label style="display:block"><span class="lbl">Uslub nomi</span><input class="f" id="sTitle" maxlength="120" value="${esc(draft.sTitle)}" placeholder="Masalan: Shisha kartalar"></label>
        <label style="display:block;margin-top:12px"><span class="lbl">Nimasi yoqdi</span><textarea class="f" id="sText" placeholder="Masalan: titrlar harflab chiqishi va ikonkalar yoqdi, musiqasi kerak emas">${esc(draft.sText)}</textarea></label></div>
    </form>
    <aside class="card pad summary"><h2 style="margin-bottom:8px">Qanday ishlaydi</h2>
      <ul class="dl"><li><div class="it"><span class="tc">1</span><span>Videolar kadrma-kadr tahlil qilinadi</span></div></li><li><div class="it"><span class="tc">2</span><span>Kamida 2 ta videoda takrorlangan qoidalar olinadi</span></div></li><li><div class="it"><span class="tc">3</span><span>Uslub "Agentlik uslublari"ga qo'shiladi va darhol tanlanadi</span></div></li></ul>
      <div class="row"><span>Higgsfield</span><b>0 kr</b></div><div class="row"><span>Claude</span><b>taxminiy, tokenlar ko'p</b></div>
      <button type="button" class="btn pri" id="styleGo">Uslub yaratish</button>
      <div class="upload" id="styleUpload" hidden><div class="bar"><i></i></div><div class="utext"></div></div>
      <p class="note msg" id="styleMsg" role="status"></p></aside></div>`;
  }, after() { renderFiles("stylevideo"); } },

  video: { title: "", crumb: ["videolar"], render() { return `<div id="vroot"><div class="card pad sub">Yuklanmoqda…</div></div>`; }, after() { renderVideo(true); } },
};

/* ---------- render / routing ---------- */
function parse() {
  const h = decodeURIComponent(location.hash.slice(1));
  if (h.startsWith("video=")) return { name: "video", id: h.slice(6) };
  if (h.startsWith("job=")) return { name: "video", id: h.slice(4) };
  return { name: VIEWS[h] && h !== "video" ? h : "bosh", id: null };
}
const CRUMB = { videolar: ["#videolar", "Videolar"], uslublar: ["#uslublar", "Uslublar"] };
function render() {
  const v = VIEWS[route.name];
  $$("[data-nav]").forEach(a => { const on = a.dataset.nav === route.name || (route.name === "video" && a.dataset.nav === "videolar"); on ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"); });
  $("#crumb").innerHTML = [`<a href="#bosh">${esc(coLabel())}</a>`, ...v.crumb.map(c => `<a href="${CRUMB[c][0]}">${CRUMB[c][1]}</a>`)].join(" / ");
  if (route.name !== "video") { $("#ptitle").textContent = v.title; document.title = v.title + " · Montaj studiyasi"; }
  $("#view").innerHTML = v.render();
  paintAll($("#view"));
  if (v.after) v.after();
}
window.addEventListener("hashchange", () => { const prev = route; route = parse(); if (route.name !== "video" || prev.id !== route.id) vstate = { ver: null, tab: "done", sig: "" }; render(); window.scrollTo(0, 0); });

/* ---------- new video form ---------- */
function allowed(kind, f) { const e = ext(f.name); if (kind === "material") return IMAGE_EXT.includes(e) || VIDEO_EXT.includes(e); return kind === "refdoc" ? DOC_EXT.includes(e) : VIDEO_EXT.includes(e) || (f.type || "").startsWith("video/"); }
function readMeta(f) {    // browser-side input check; the server checks again with ffprobe
  return new Promise(resolve => {
    const v = document.createElement("video"), url = URL.createObjectURL(f);
    const done = r => { URL.revokeObjectURL(url); v.removeAttribute("src"); resolve(r); };
    const t = setTimeout(() => done(null), 8000);
    v.preload = "metadata"; v.muted = true;
    v.onloadedmetadata = () => { clearTimeout(t); done({ w: v.videoWidth, h: v.videoHeight, duration: v.duration }); };
    v.onerror = () => { clearTimeout(t); done(null); };
    v.src = url;
  });
}
async function addFiles(kind, list) {
  const bad = [], low = [];
  for (const f of list) {
    if (!allowed(kind, f)) { bad.push(f.name); continue; }
    if (files[kind].some(x => x.name === f.name && x.size === f.size)) continue;
    if (kind === "raw") {
      const m = await readMeta(f);
      if (m && m.w && Math.min(m.w, m.h) < LV.min_short_side) { low.push(`${f.name} (${m.w}×${m.h})`); continue; }
      if (m) meta.set(f, m);
    }
    files[kind].push(f);
  }
  renderFiles(kind);
  const msgs = [];
  if (bad.length) msgs.push(`Qabul qilinmadi: ${bad.join(", ")}`);
  if (low.length) msgs.push(`Sifati past, kamida 720p kerak: ${low.join(", ")}`);
  const m = $("#formMsg") || $("#styleMsg");
  if (m) { m.textContent = msgs.join(". "); m.className = "note msg" + (msgs.length ? " err" : ""); }
  if (kind === "raw") summary();
}
function renderRefUse() {
  const el = $("#refUse"); if (!el) return;
  if (!files.refvideo.length) { el.innerHTML = ""; return; }
  el.innerHTML = `<label style="display:block;margin-top:12px"><span class="lbl">Bu videolarda nima yoqdi? <em class="sub">ixtiyoriy · o'z so'zingiz bilan</em></span><textarea class="f" id="refLike" rows="3" maxlength="1500" placeholder="Masalan: 1-videodagi so'zlar bittadan sakrab chiqishi, 0:12 dagi tez zoom o'tishi, sariq urg'u rangi. Musiqasi kerak emas.">${esc(draft.refLike)}</textarea></label>
    <p class="note" style="margin:6px 0 0">Qaysi videodan nimani olish va nimani olmaslik kerakligini yozing. AI yozganlaringizga amal qiladi. Namunadagi matn, brend va kadrlar ko'chirilmaydi.</p>`;
}
function renderMaterials() {
  const ul = $('[data-list="material"]'); if (!ul) return;
  ul.innerHTML = files.material.map((f, i) => { const mi = matInfo.get(f) || {}; return `<li class="mat"><span class="nm" title="${esc(f.name)}">${IMAGE_EXT.includes(ext(f.name)) ? "🖼" : "🎞"} ${esc(f.name)}</span><span class="sz">${size(f.size)}</span>
    <input class="f mnote" data-mnote="${i}" maxlength="300" value="${esc(mi.note || "")}" placeholder="Izoh: nima bu / qayerda (ixtiyoriy)">
    <label class="mreq" title="Belgilansa, AI buni albatta ishlatadi"><input type="checkbox" data-mreq="${i}"${mi.required ? " checked" : ""}> majburiy</label>
    <button type="button" data-rm="material:${i}" aria-label="${esc(f.name)} ni olib tashlash">${ICON.x}</button></li>`; }).join("");
}
function renderFiles(kind) {
  if (kind === "material") { renderMaterials(); summary(); return; }
  if (kind === "refvideo") renderRefUse();
  const ul = $(`[data-list="${kind}"]`); if (!ul) return;
  ul.innerHTML = files[kind].map((f, i) => { const m = meta.get(f); return `<li><span class="nm" title="${esc(f.name)}">${esc(f.name)}</span><span class="sz">${m ? `${m.w}×${m.h} · ${Math.round(m.duration)} s · ` : ""}${size(f.size)}</span><button type="button" data-rm="${kind}:${i}" aria-label="${esc(f.name)} ni olib tashlash">${ICON.x}</button></li>`; }).join("");
}
function summary() {
  const custom = draft.usd !== "", l = custom ? null : lvById(draft.level);
  if (!custom && !l) return;
  const mine = custom ? Number(draft.usd) : null;
  const warn = custom && !(Number.isFinite(mine) && mine >= 0 && mine <= LV.max_usd);
  const cap = custom ? (warn ? 0 : Math.floor(mine * LV.rate)) : l.max;
  let txt;
  if (warn) txt = `Limit 0–${LV.max_usd} $ oralig'ida bo'lsin.`;
  else if (custom) txt = `Siz belgilagan limit: <b>${cap} kr</b> (~${usd(cap)}). Daraja tanlanmagan.${cap === 0 ? " Pullik AI generatsiya ishlatilmaydi." : ""}`;
  else if (cap === 0) txt = "Minimal darajada AI generatsiya yo'q: Higgsfield <b>0 kr</b>.";
  else txt = `Agent limiti: <b>${cap} kr</b> (~${usd(cap)}), ${esc(l.title)} darajasining chegarasi.`;
  const ci = $("#capinfo"); if (ci) { ci.innerHTML = txt; ci.className = "capinfo" + (warn ? " warn" : ""); }
  const s = $("#sum"); if (!s) return;
  const fm = fmtById(draft.format);
  const known = files.raw.length && files.raw.every(f => meta.get(f));
  const secs = files.raw.reduce((a, f) => a + ((meta.get(f) || {}).duration || 0), 0);
  const est = known ? estMinutes(secs, draft.level) : null, wait = queueAhead();
  const eta = !files.raw.length ? "video qo'shilgach" : est ? `~${est} daq${wait ? ` + navbat ~${wait} daq` : ""}` : "video yuklangach hisoblanadi";
  const bn = $("#balNote"); if (bn) bn.innerHTML = balanceNote(cap);
  s.innerHTML = `<div class="row"><span>Kompaniya</span><b>${esc(coName(draft.company ?? defaultCo()))}</b></div><div class="row"><span>Video</span><b>${files.raw.length ? files.raw.length + " ta fayl · " + (known ? Math.round(secs) + " s" : size(files.raw.reduce((a, f) => a + f.size, 0))) : "qo'shilmagan"}</b></div>
    <div class="row"><span>Format</span><b>${fm ? esc(fm.title) : "—"}</b></div>
    ${files.material.length ? `<div class="row"><span>Materiallar</span><b>${files.material.length} ta${files.material.filter(f => (matInfo.get(f) || {}).required).length ? ` (${files.material.filter(f => (matInfo.get(f) || {}).required).length} majburiy)` : ""}</b></div>` : ""}<div class="row"><span>Uslub</span><b>${esc(styleTitle(draft.style))}</b></div>${files.refvideo.length ? `<div class="row"><span>Yoqqan videolar</span><b>${files.refvideo.length} ta</b></div>` : ""}<div class="row"><span>${custom ? "Limit tanlovi" : "Daraja"}</span><b>${custom ? "Qo'lda belgilangan" : esc(l.title)}</b></div>
    <div class="row"><span>Higgsfield limiti</span><b class="num">${cap} kr · ${usd(cap)}</b></div><div class="row"><span>Claude</span><b>taxminiy, ish oxirida</b></div>
    <div class="row"><span>Taxminiy vaqt</span><b>${eta}</b></div>`;
}
function say(id, t, cls = "") { const m = $(id); if (m) { m.textContent = t; m.className = "note msg " + cls; } }
async function uploadAll(job, queue, box) {
  const bar = $(".bar i", box), ut = $(".utext", box), total = queue.reduce((a, [, f]) => a + f.size, 0) || 1;
  box.hidden = false; let done = 0;
  for (const [kind, f] of queue) {
    await put(`/api/jobs/${job.id}/upload?kind=${kind}&name=${encodeURIComponent(f.name)}${kind === "mat" ? `&note=${encodeURIComponent((matInfo.get(f) || {}).note || "")}&required=${(matInfo.get(f) || {}).required ? 1 : 0}` : ""}`, f, loaded => {
      bar.style.width = ((done + loaded) / total * 100).toFixed(1) + "%"; ut.textContent = `Yuklanmoqda: ${f.name} · ${size(done + loaded)} / ${size(total)}`;
    });
    done += f.size;
  }
  bar.style.width = "100%"; ut.textContent = "Yuklandi.";
}
async function submitVideo() {
  if (!files.raw.length) return say("#formMsg", "Video qo'shing.", "err");
  const usdCap = draft.usd === "" ? null : Number(draft.usd);
  if (usdCap !== null && !(usdCap >= 0 && usdCap <= LV.max_usd)) return say("#formMsg", `Limit 0–${LV.max_usd} $ oralig'ida bo'lsin.`, "err");
  const go = $("#go"); go.disabled = true; say("#formMsg", "");
  let job;
  try {
    job = await api("/api/jobs", { method: "POST", json: { style: draft.style, title: draft.title, ref_text: draft.text, ref_like: files.refvideo.length ? draft.refLike.trim() : "", level: draft.level, usd_cap: usdCap, company: (draft.company ?? defaultCo()) || null, format: draft.format } });
    await uploadAll(job, [...files.refdoc.map(f => ["ref", f]), ...files.refvideo.map(f => ["ref", f]), ...files.material.map(f => ["mat", f]), ...files.raw.map(f => ["raw", f])], $("#upload"));
    await api(`/api/jobs/${job.id}/submit`, { method: "POST" });
    ["raw", "material", "refdoc", "refvideo"].forEach(k => { files[k] = []; });
    Object.assign(draft, { style: "auto", usd: "", title: "", text: "", refLike: "", level: LV.default, company: null, format: LV.default_format });
    await loadJobs();
    location.hash = "video=" + encodeURIComponent(job.id);
  } catch (err) {
    say("#formMsg", "Xato: " + err.message, "err"); go.disabled = false;
    if (job) api(`/api/jobs/${job.id}/cancel`, { method: "POST" }).catch(() => {});
  }
}
async function submitStyle() {
  if (files.stylevideo.length < 2) return say("#styleMsg", "Kamida 2 ta video qo'shing.", "err");
  const go = $("#styleGo"); go.disabled = true; say("#styleMsg", "");
  let job;
  try {
    job = await api("/api/style-jobs", { method: "POST", json: { title: draft.sTitle, ref_text: draft.sText, company: (draft.sCompany ?? defaultCo()) || null } });
    await uploadAll(job, files.stylevideo.map(f => ["ref", f]), $("#styleUpload"));
    await api(`/api/jobs/${job.id}/submit`, { method: "POST" });
    files.stylevideo = []; draft.sTitle = ""; draft.sText = ""; draft.sCompany = null;
    await loadJobs();
    location.hash = "video=" + encodeURIComponent(job.id);
  } catch (err) {
    say("#styleMsg", "Xato: " + err.message, "err"); go.disabled = false;
    if (job) api(`/api/jobs/${job.id}/cancel`, { method: "POST" }).catch(() => {});
  }
}

/* ---------- video page ---------- */
function allVersions(j) {
  const v = (j.versions || []).filter(x => x.video).map(x => ({ ...x, current: false }));
  if (j.video) v.push({ n: v.length + 1, video: j.video, current: true, summary: j.summary, credits_spent: j.credits_spent, finished: j.finished, timeline: j.timeline, overall: j.overall });
  return v;
}
function doneList(ver) {
  if (!ver || !((ver.timeline || []).length || ver.overall)) return `<p class="sub" style="margin:0">Agent bu versiya uchun ro'yxat yozmagan.</p>`;
  return `<ul class="dl">${(ver.timeline || []).map(it => `<li><button type="button" data-seek="${Number(it.t)}"><span class="tc">${esc(tc(Number(it.t)).replace(/\.\d$/, ""))}</span><span>${esc(it.text)}${it.quote ? `<small>"${esc(it.quote)}"</small>` : ""}</span></button></li>`).join("")}</ul>
    ${ver.overall ? `<div class="whole">${esc(ver.overall)}</div>` : ""}`;
}
function fbForm(j) {
  const l = lvById(j.level), cap = (l || j.usd_cap != null) ? (j.level_cap ?? j.credit_cap) : 20, hasVideo = allVersions(j).length > 0;
  return `<div class="card pad" id="fbBox"><h2 style="margin-bottom:6px">O'zgartirish so'rash</h2>
    <p class="sub" style="margin:0 0 10px">Nimani o'zgartirish kerakligini yozing. AI faqat shu joylarni tuzatadi.${hasVideo ? " Videoni kerakli joyda to'xtatib, vaqtni qo'shing." : ""}</p>
    <textarea class="f" id="fbText" rows="4" placeholder="Masalan:&#10;[0:04.5] titr juda kichik&#10;[0:12.0] logoni olib tashlang">${esc(fb.text)}</textarea>
    <div class="drop small" id="fbDrop" tabindex="0" role="button" style="margin-top:10px"><input type="file" multiple hidden><b>Fayl qo'shish</b><span>rasm, video, hujjat yoki musiqa · ixtiyoriy</span></div>
    <ul class="files" id="fbFiles">${fb.files.map((f, i) => `<li><span class="nm">${esc(f.name)}</span><span class="sz">${size(f.size)}</span><button type="button" data-fbrm="${i}" aria-label="${esc(f.name)} ni olib tashlash">${ICON.x}</button></li>`).join("")}</ul>
    <div class="fbtools">${hasVideo ? `<button type="button" class="btn" id="fbTime">${ICON.clock}Vaqtni qo'shish</button>` : "<span></span>"}
      <span class="sub">Limit: ${l ? `${esc(l.title)}, ${cap} kr (~${usd(cap)})` : `${cap} kr`}</span><button type="button" class="btn pri" id="fbSend">Yuborish</button></div>
    <div class="upload" id="fbUp" hidden><div class="bar"><i></i></div><div class="utext"></div></div><p class="note msg" id="fbMsg" role="status"></p></div>`;
}
async function renderVideo(force) {
  if (route.name !== "video") return;
  let j;
  try { j = await api(`/api/jobs/${encodeURIComponent(route.id)}`); }
  catch (e) { $("#vroot").innerHTML = `<div class="box err">${esc(e.message)}</div>`; return; }
  if (fb.job !== j.id) { fb.job = j.id; fb.text = ""; fb.files = []; }
  const sig = [j.id, j.state, j.revision || 0, (j.versions || []).length, (j.progress || []).length, (j.activity || []).length, j.finished, vstate.ver, vstate.tab,
    j.state === "running" ? Math.floor(Date.now() / 30000) : ""].join("|");
  if (!force && sig === vstate.sig) return;
  const playing = $("#player");
  if (!force && playing && !playing.paused) return;
  const focusFb = document.activeElement && document.activeElement.id === "fbText";
  if (!force && focusFb) return;
  vstate.sig = sig;

  $("#ptitle").textContent = jobName(j); document.title = jobName(j) + " · Montaj studiyasi";
  const styleJob = j.kind === "style", vers = allVersions(j);
  if (vstate.ver != null && !vers.some(v => v.n === vstate.ver)) vstate.ver = null;
  const cur = vers.find(v => v.n === vstate.ver) || vers[vers.length - 1];
  const lv = lvById(j.level);

  const left = [];
  const ml = minLeft(j), qa = j.qa;
  const head = `<div class="chead"><div class="meta">${chip(j.state)}${j.revision ? `<span class="chip">Tuzatish ${j.revision}</span>` : ""}<span>${esc(jobStyle(j))}</span>${lv ? `<span>·</span><span>${esc(lv.title)}</span>` : ""}${j.format ? `<span>·</span><span>${esc(j.format)}</span>` : ""}${ml ? `<span>·</span><span>${j.state === "queued" ? `navbatda, ~${queueAhead(j.id)} daq kutadi, keyin ~${ml} daq` : `taxminan ${ml} daq qoldi`}</span>` : ""}${qa && qa.total ? `<span class="chip ${qa.fails.length ? "bad" : qa.warns.length ? "warn" : "ok"}">QA ${qa.passed}/${qa.total}</span>` : ""}${j.dry_run ? `<span class="chip warn">DRY RUN</span>` : ""}</div>
    ${vers.length > 1 ? `<div class="vtabs" role="tablist">${vers.map(v => `<button type="button" class="btn" role="tab" data-ver="${v.n}" aria-selected="${v.n === cur.n}">v${v.n}</button>`).join("")}</div>` : ""}</div>`;
  if (styleJob) {
    left.push(`<div class="card pad">${head}${j.state === "done" && j.new_style
      ? `<div class="newstyle"><span class="sub">Uslub yaratildi</span><b>${esc(j.new_style_title || j.new_style)}</b><p>${esc(j.new_style_def || "")}</p><p style="margin-top:10px">${styles.some(s => s.name === j.new_style) ? `<a class="btn pri" href="#yangi" data-pick="${esc(j.new_style)}">Shu uslubda video</a>` : `<span class="sub">Bu uslub katalogdan o'chirilgan.</span>`}</p></div>`
      : `<div class="ph-big">${j.state === "queued" ? "Navbatda turibdi…" : j.state === "running" ? "Videolar tahlil qilinmoqda…" : "Uslub yaratilmadi"}</div>`}</div>`);
  } else {
    const others = cur && cur.current ? (j.files || []).filter(f => f.path !== j.video && f.path.startsWith("out/")) : [];
    left.push(`<div class="card pad">${head}${cur ? `<video id="player" class="player" controls preload="metadata" src="${fileUrl(j.id, cur.video)}"></video>
      <div class="filters" style="margin-top:12px"><a class="btn pri" href="${fileUrl(j.id, cur.video, true)}">v${cur.n} ni yuklab olish</a>${others.map(f => `<a class="btn" href="${fileUrl(j.id, f.path)}" target="_blank" rel="noopener">${esc(f.path.replace("out/", ""))}</a>`).join("")}</div>
      ${!cur.current && cur.summary ? `<div class="box info" style="margin-top:10px">${esc(cur.summary)}</div>` : ""}`
      : `<div class="ph-big">${j.expired ? `Saqlash muddati tugagan (${when(j.expired)}): videolar serverdan o'chirilgan, yozuv saqlangan.` : j.state === "queued" ? "Navbatda turibdi…" : j.state === "running" ? "Video tayyorlanmoqda…" : "Video chiqmadi"}</div>`}</div>`);
    if (FB_STATES.includes(j.state) && !j.expired) left.push(fbForm(j));
    if (j.state === "done" && !j.expired && j.video && ["reference", "plugin+reference", "web", "own"].includes(j.style_source)) left.push(saveStyleCard(j));
    else if (j.revision) { const f = (j.feedback || []).find(x => x.n === j.revision) || {}; left.push(`<div class="box info"><b>Tuzatish ${j.revision} bajarilmoqda.</b>${f.text ? `<div style="white-space:pre-wrap;margin-top:6px">${esc(f.text)}</div>` : ""}</div>`); }
  }
  if (j.state === "failed" && !j.expired) left.push(!j.revision && j.retried_as
    ? `<div class="box info">Bu ish qayta yurgizilgan: <a href="#video=${encodeURIComponent(j.retried_as)}">yangi ishni ochish →</a></div>`
    : `<div class="card pad"><h2 style="margin-bottom:6px">Qayta yurgizish</h2><p class="sub" style="margin:0 0 10px">${j.revision
      ? `Tuzatish ${j.revision} xato bilan tugadi. O'sha izoh va fayllar qayta yuboriladi; oldingi versiyalar saqlanadi.`
      : "Xuddi shu videolar, referenslar va sozlamalar bilan yangi ish navbatga qo'yiladi. Bu ish yozuv sifatida qoladi."}</p><button type="button" class="btn pri" data-retry="${esc(j.id)}">Qayta yurgizish</button><p class="note msg" id="rtMsg" role="status"></p></div>`);
  if ((j.state === "queued" || j.state === "running") && j.auto_retries) left.push(`<div class="box info"><b>Avtomatik qayta urinish.</b> ${esc(j.auto_retry_reason || "")}${j.state === "queued" && j.not_before && j.not_before > new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 19) ? ` · ${esc(j.not_before.slice(11, 16))} dan keyin boshlanadi` : ""}</div>`);
  if (j.retry_of) left.push(`<div class="box info">Bu ish xato bilan tugagan ishning qayta yurgizilishi: <a href="#video=${encodeURIComponent(j.retry_of)}">asl ishni ochish</a></div>`);
  if (j.state === "queued" || j.state === "running") left.push(`<div><button type="button" class="btn danger" data-cancel="${esc(j.id)}">Ishni to'xtatish</button></div>`);
  else left.push(`<div class="filters"><span class="sub">${j.expired ? "Videolar o'chirilgan, faqat yozuv qolgan." : daysLeft(j) !== null ? `Videolar ${daysLeft(j)} kundan keyin serverdan avtomatik o'chadi.` : ""}</span><button type="button" class="btn danger" data-del="${esc(j.id)}" style="margin-left:auto">Butunlay o'chirish</button></div>`);

  const tabs = styleJob ? [["info", "Ma'lumot"], ["prog", "Jarayon"]] : [["done", "Nima qilindi"], ["qa", "Tekshiruv"], ["info", "Ma'lumot"], ["prog", "Jarayon"], ["hist", "Tuzatishlar"]];
  if (!tabs.some(t => t[0] === vstate.tab)) vstate.tab = tabs[0][0];
  const kr = jobCredits(j);
  const pane = {
    done: () => doneList(cur),
    qa: () => {
      const q = cur && cur.current ? j.qa : cur && cur.qa;
      if (!q) return `<p class="sub" style="margin:0">${j.state === "done" ? "Bu versiya uchun tekshiruv yo'q." : "Tekshiruv video tayyor bo'lgach avtomatik o'tkaziladi."}</p>`;
      if (q.error) return `<div class="box err">${esc(q.error)}</div>`;
      const ic = { ok: ["ok", "OK"], warn: ["warn", "Diqqat"], fail: ["bad", "Xato"] };
      const cmp = cur && cur.current && j.ref_compare ? `<h3 style="font-size:14px;margin:16px 0 6px">Referens bilan solishtirish</h3><p class="sub" style="margin:0 0 8px">Chapda referens, o'ngda natija, filmning bir xil joylarida. Ko'rinish (titr, rang, kompozitsiya) solishtiriladi, mazmun emas.</p><a href="${fileUrl(j.id, j.ref_compare)}" target="_blank" rel="noopener"><img src="${fileUrl(j.id, j.ref_compare)}" alt="Referens va natija kadrlari yonma-yon" style="width:100%;border-radius:10px;border:1px solid var(--line)"></a>` : "";
      return `<p class="sub" style="margin:0 0 10px">Server tayyor videoni o'zi tekshiradi: ${q.passed}/${q.total} o'tdi${q.fails.length ? `, ${q.fails.length} ta xato` : ""}${q.warns.length ? `, ${q.warns.length} ta diqqat` : ""}.</p>
        <ul class="dl">${q.checks.map(c => `<li><div class="it" style="grid-template-columns:70px minmax(0,1fr)"><span><span class="chip ${ic[c.status][0]}">${ic[c.status][1]}</span></span><span><b>${esc(c.name)}</b><small>${esc(c.detail)}</small></span></div></li>`).join("")}</ul>` + cmp;
    },
    info: () => `<div class="stack">${j.error && j.state !== "done" ? `<div class="box err">${esc(j.error)}</div>` : ""}${j.summary && j.summary !== j.error ? `<div class="box info">${esc(j.summary)}</div>` : ""}${j.style_card ? `<div class="box info"><b>Uslub manbasi:</b> ${esc(SOURCE_UZ[j.style_source] || j.style_source || "—")}${j.ref_use && (j.refs || []).some(r => VIDEO_EXT.includes(ext(r))) ? ` · referensdan: ${esc((REF_USE.find(r => r[0] === j.ref_use) || REF_USE[0])[1])}${j.ref_like ? ` · <span title="${esc(j.ref_like)}">yoqqanlari: ${esc(j.ref_like.length > 80 ? j.ref_like.slice(0, 80) + "…" : j.ref_like)}</span>` : ""}` : ""} · <a href="${fileUrl(j.id, j.style_card)}" target="_blank" rel="noopener">uslub kartasi</a></div>` : ""}${(j.materials || []).length ? `<div class="box info"><b>Materiallar</b><ul style="margin:6px 0 0;padding-left:18px">${j.materials.map(m => { const r = (j.materials_report || []).find(x => x.file === m.name); return `<li>${m.required ? "★ " : ""}${esc(m.name)}${m.note ? ` <span class="sub">(${esc(m.note)})</span>` : ""} — ${r ? (r.used ? `ishlatildi${r.t.length ? ` (${r.t[0]}${r.t[1] != null ? "–" + r.t[1] : ""} s)` : ""}${r.how ? ": " + esc(r.how) : ""}` : `ishlatilmadi: ${esc(r.reason || "sabab yozilmagan")}`) : (j.state === "done" ? "hisobotda yo'q" : "kutilmoqda")}</li>`; }).join("")}</ul></div>` : ""}
      <label style="display:block"><span class="lbl">Kompaniya</span><select class="f" id="jobCo" data-job="${esc(j.id)}">${coOptions(j.company || "")}</select></label>
      <div class="kv">${lv ? `<div><span>Daraja</span><b>${esc(lv.title)}</b></div>` : ""}
        ${styleJob ? `<div><span>Namuna videolar</span><b>${(j.refs || []).filter(r => VIDEO_EXT.includes(ext(r))).length}</b></div>` : `<div><span>${j.revision ? "Bu tuzatish: Higgsfield" : "Higgsfield (sarf / limit)"}</span><b>${j.credits_spent != null ? j.credits_spent : "—"} / ${j.credit_cap} kr</b></div>
        ${(j.versions || []).length ? `<div><span>Jami Higgsfield</span><b>${kr.toFixed(1)} kr · ${usd(kr)}</b></div>` : ""}`}
        <div><span>Claude</span><b>—</b></div><div><span>Boshlandi</span><b>${when(j.started)}</b></div><div><span>Davomiyligi</span><b>${j.started ? dur(j.started, j.finished) : "—"}</b></div></div>
      ${(j.open_issues || []).length ? `<div><h2 style="font-size:14px;margin-bottom:8px">Ochiq masalalar</h2><ul class="loglist">${j.open_issues.map(x => `<li>${esc(x)}</li>`).join("")}</ul></div>` : ""}
      <details><summary>Berilgan fayllar (${(j.raw || []).length + (j.refs || []).length})</summary><ul class="loglist">${[...(j.raw || []).map(n => ["raw", n]), ...(j.refs || []).map(n => ["refs", n])].map(([k, n]) => `<li><a href="${fileUrl(j.id, `input/${k}/${n}`)}" target="_blank" rel="noopener">${k === "raw" ? "Video" : "Referens"}: ${esc(n)}</a></li>`).join("")}</ul></details>
      ${(j.files || []).filter(f => f.path.endsWith(".md")).map(f => `<a class="btn" href="${fileUrl(j.id, f.path)}" target="_blank" rel="noopener">${esc(f.path)}</a>`).join(" ")}</div>`,
    prog: () => `<div class="stack">${(j.progress || []).length ? `<ul class="loglist prog">${j.progress.slice().reverse().map(x => `<li>${esc(x)}</li>`).join("")}</ul>` : `<p class="sub" style="margin:0">${j.state === "queued" ? "Navbatda turibdi." : "Agent hali bosqich yozmadi."}</p>`}
      ${(j.activity || []).length ? `<details ${j.state === "running" ? "open" : ""}><summary>Agent faoliyati (oxirgi ${j.activity.length} qadam)</summary><ul class="loglist act" id="act">${j.activity.map(a => `<li class="k-${a.k}">${esc(a.v)}</li>`).join("")}</ul></details>` : ""}
      ${j.session_id && j.state !== "queued" && !j.dry_run ? `<details><summary>Terminalda davom ettirish</summary><div class="cmd"><code>${esc(`cd "D:\\projects\\higgsfield test01"; claude --resume ${j.session_id}`)}</code><button type="button" class="btn" data-copy="${esc(`cd "D:\\projects\\higgsfield test01"; claude --resume ${j.session_id}`)}">Nusxa</button></div></details>` : ""}</div>`,
    hist: () => { const items = (j.feedback || []).slice().reverse(); if (!items.length) return `<p class="sub" style="margin:0">Hali tuzatish so'ralmagan.</p>`;
      return `<ol class="hist">${items.map(f => { const live = j.revision === f.n && j.state !== "done";
        return `<li><div class="h"><b>Tuzatish ${f.n}</b>${f.based_on ? `<span class="sub">v${f.based_on} asosida</span>` : ""}<span class="sub">${when(f.created)}</span>${live ? chip(j.state) : `<span class="chip ok">Bajarildi</span>`}</div>
          ${f.text ? `<div class="txt">${esc(f.text)}</div>` : ""}${(f.files || []).length ? `<div class="att">${f.files.map(n => `<a href="${fileUrl(j.id, `feedback/r${f.n}/${n}`)}" target="_blank" rel="noopener">${esc(n)}</a>`).join("")}</div>` : ""}</li>`; }).join("")}</ol>`; },
  };
  const right = `<div class="card pad"><div class="tabs" role="tablist">${tabs.map(([k, t]) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${vstate.tab === k}">${t}</button>`).join("")}</div>${pane[vstate.tab]()}</div>`;

  const act = $("#act"), keepBottom = act ? act.scrollTop + act.clientHeight >= act.scrollHeight - 8 : true;
  $("#vroot").innerHTML = `<div class="grid2"><div class="col">${left.join("")}</div><div class="col">${right}</div></div>`;
  const a2 = $("#act"); if (a2 && keepBottom) a2.scrollTop = a2.scrollHeight;
  bindFb(j);
}
function renderFbFiles() {
  const ul = $("#fbFiles"); if (!ul) return;
  ul.innerHTML = fb.files.map((f, i) => `<li><span class="nm">${esc(f.name)}</span><span class="sz">${size(f.size)}</span><button type="button" data-fbrm="${i}" aria-label="${esc(f.name)} ni olib tashlash">${ICON.x}</button></li>`).join("");
}
function bindFb(j) {
  const t = $("#fbText"); if (!t) return;
  t.addEventListener("input", () => { fb.text = t.value; });
  t.addEventListener("keydown", e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); sendFb(j); } });
  bindDrop($("#fbDrop"), list => { const bad = []; for (const f of list) { if (!FB_EXT.includes(ext(f.name))) { bad.push(f.name); continue; } if (!fb.files.some(x => x.name === f.name && x.size === f.size)) fb.files.push(f); } renderFbFiles(); say("#fbMsg", bad.length ? `Qabul qilinmadi: ${bad.join(", ")}` : "", bad.length ? "err" : ""); });
  const tb = $("#fbTime");
  if (tb) tb.addEventListener("click", () => {
    const v = $("#player"); if (!v) return; v.pause();
    const verBtn = $(".vtabs [aria-selected=\"true\"]"), vers = $$(".vtabs button");
    const ver = verBtn && vers.length && verBtn !== vers[vers.length - 1] ? " " + verBtn.textContent.trim() : "";
    const stamp = `[${tc(v.currentTime)}${ver}] `, s = t.selectionStart ?? t.value.length, before = t.value.slice(0, s), lead = before && !before.endsWith("\n") ? "\n" : "";
    t.value = before + lead + stamp + t.value.slice(s); fb.text = t.value;
    const pos = (before + lead + stamp).length; t.focus(); t.setSelectionRange(pos, pos);
  });
  $("#fbSend").addEventListener("click", () => sendFb(j));
}
async function sendFb(j) {
  const text = $("#fbText").value.trim(), btn = $("#fbSend");
  if (!text && !fb.files.length) return say("#fbMsg", "Izoh yozing yoki fayl qo'shing.", "err");
  btn.disabled = true; say("#fbMsg", "");
  try {
    if (fb.files.length) await uploadAll({ id: j.id }, fb.files.map(f => ["fb", f]), $("#fbUp"));
    await api(`/api/jobs/${j.id}/feedback`, { method: "POST", json: { text } });
    fb.text = ""; fb.files = []; vstate.ver = null; vstate.tab = "prog";
    loadJobs(); await renderVideo(true);
  } catch (err) { say("#fbMsg", "Xato: " + err.message, "err"); btn.disabled = false; }
}

/* ---------- events ---------- */
function bindDrop(d, onFiles) {
  if (!d) return;
  const input = $("input", d);
  d.addEventListener("click", e => { if (e.target !== input) input.click(); });
  d.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } });
  input.addEventListener("change", () => { onFiles(input.files); input.value = ""; });
  d.addEventListener("dragover", e => { e.preventDefault(); d.classList.add("over"); });
  d.addEventListener("dragleave", () => d.classList.remove("over"));
  d.addEventListener("drop", e => { e.preventDefault(); d.classList.remove("over"); onFiles(e.dataTransfer.files); });
}
new MutationObserver(() => { $$(".drop[data-kind]:not([data-bound])", $("#view")).forEach(d => { d.dataset.bound = "1"; bindDrop(d, list => addFiles(d.dataset.kind, list)); }); })
  .observe($("#view"), { childList: true, subtree: true });

document.addEventListener("click", async e => {
  const t = e.target, x = s => t.closest(s);
  let el;
  if (x("#cobtn")) { renderSwitcher($("#comenu").hidden); if (!$("#comenu").hidden) $("#coName").focus(); return; }
  if ((el = x("[data-arch]")) || (el = x("[data-unarch]"))) {
    const id = el.dataset.arch || el.dataset.unarch, archive = !!el.dataset.arch;
    if (archive && !confirm(`"${coName(id)}" kompaniyasini arxivlaymi? Videolari saqlanadi, keyin qaytarish mumkin.`)) return;
    try { await api(`/api/companies/${encodeURIComponent(id)}`, { method: "POST", json: { archived: archive } }); } catch (err) { alert(err.message); return; }
    await loadCompanies(); if (archive && curCo === id) setCo(""); else renderSwitcher(!archive);
    return;
  }
  if ((el = x(".coitem"))) { setCo(el.dataset.co); return; }
  if ($("#comenu") && !$("#comenu").hidden && !x("#cosw")) renderSwitcher(false);
  if ((el = x("[data-delete-style]"))) {
    const name = el.dataset.deleteStyle, title = styleTitle(name);
    if (!confirm(`“${title}” uslubini katalogdan o'chirasizmi?\nAvvalgi videolar, ishlayotgan montajlar va ularga tuzatish kiritish imkoniyati saqlanadi.`)) return;
    el.disabled = true; el.textContent = "O'chirilmoqda…"; el.setAttribute("aria-busy", "true");
    try {
      await api(`/api/styles/${encodeURIComponent(name)}/delete`, { method: "POST" });
      styles = styles.filter(s => s.name !== name); $("#cntS").textContent = styles.length;
      if (draft.style === name) draft.style = "auto";
      styleMessage = `“${title}” uslubi katalogdan o'chirildi.`;
      if (route.name === "uslublar") {
        render();
        const next = $("[data-delete-style]") || $("a[href='#uslub-yarat']", $("#view"));
        if (next) next.focus();
      }
    } catch (err) {
      el.disabled = false; el.textContent = "O'chirish"; el.removeAttribute("aria-busy");
      styleMessage = err.message;
      if ($("#styleMessage")) $("#styleMessage").textContent = styleMessage;
    }
    return;
  }
  if ((el = x("[data-pick]"))) {
    if (!styles.some(s => s.name === el.dataset.pick)) { e.preventDefault(); alert("Bu uslub katalogdan o'chirilgan. Boshqa uslub tanlang."); return; }
    draft.style = el.dataset.pick; return;
  }
  if ((el = x("tr[data-go]"))) { location.hash = el.dataset.go.slice(1); return; }
  if ((el = x("[data-fs]"))) { vFilter.s = el.dataset.fs; render(); return; }
  if ((el = x("[data-fm]"))) { vFilter.mode = el.dataset.fm; render(); return; }
  if ((el = x("[data-sf]"))) { sFilter = el.dataset.sf; render(); return; }
  if ((el = x("[data-rm]"))) { const [k, i] = el.dataset.rm.split(":"); files[k].splice(+i, 1); renderFiles(k); if (k === "raw") summary(); return; }
  if ((el = x("[data-fbrm]"))) { fb.files.splice(+el.dataset.fbrm, 1); renderFbFiles(); return; }
  if ((el = x("[data-ver]"))) { vstate.ver = +el.dataset.ver; renderVideo(true); return; }
  if ((el = x("[data-tab]"))) { vstate.tab = el.dataset.tab; renderVideo(true); return; }
  if ((el = x("[data-seek]"))) { const v = $("#player"); if (v) { v.currentTime = +el.dataset.seek; v.play().catch(() => {}); } return; }
  if ((el = x("[data-copy]"))) { navigator.clipboard.writeText(el.dataset.copy).then(() => { el.textContent = "Nusxa olindi"; }).catch(() => {}); return; }
  if ((el = x("[data-savestyle]"))) {
    const name = ($("#ssName").value || "").trim(), m = $("#ssMsg");
    if (!confirm(`"${name || "Nomsiz"}" uslubini yaratish ishini boshlaymi?\n\nAgent namunalarni kadrma-kadr tahlil qilib, yangi uslub va uning renderer'ini yozadi. Bu 1–2 soat oladi; Higgsfield krediti sarflanmaydi.`)) return;
    el.disabled = true;
    try { const sj = await api(`/api/jobs/${el.dataset.savestyle}/save-style`, { method: "POST", json: { title: name } }); await loadJobs(); location.hash = "#video=" + encodeURIComponent(sj.id); }
    catch (err) { m.textContent = err.message; m.className = "note msg err"; el.disabled = false; }
    return;
  }
  if ((el = x("[data-retry]"))) {
    if (!confirm("Ishni qayta yurgizaymi?\n\nXuddi shu fayllar va sozlamalar bilan yangi ish navbatga qo'yiladi. Claude va Higgsfield limiti qaytadan sarflanishi mumkin.")) return;
    el.disabled = true;
    try { const nj = await api(`/api/jobs/${el.dataset.retry}/retry`, { method: "POST" }); await loadJobs(); if (nj.id === el.dataset.retry) renderVideo(true); else location.hash = "#video=" + encodeURIComponent(nj.id); }
    catch (err) { const m = $("#rtMsg"); if (m) { m.textContent = err.message; m.className = "note msg err"; } el.disabled = false; }
    return;
  }
  if ((el = x("[data-del]"))) {
    if (!confirm("Bu ishni butunlay o'chiraymi?\n\nRaw video, referenslar, barcha versiyalar va yozuv serverdan o'chadi. Qaytarib bo'lmaydi.")) return;
    try { await api(`/api/jobs/${el.dataset.del}/delete`, { method: "POST" }); } catch (err) { alert(err.message); return; }
    await loadJobs(); location.hash = "#videolar"; return;
  }
  if ((el = x("[data-cancel]"))) {
    if (!confirm("Ishni to'xtataymi? Agent jarayoni to'xtatiladi.")) return;
    try { await api(`/api/jobs/${el.dataset.cancel}/cancel`, { method: "POST" }); } catch (err) { alert(err.message); }
    loadJobs(); renderVideo(true); return;
  }
  if (t.id === "tgl") { const open = $("#slist").hidden; $("#slist").hidden = !open; t.setAttribute("aria-expanded", String(open)); t.textContent = open ? "Yopish" : "Uslubni o'zgartirish"; return; }
  if (t.id === "go") return submitVideo();
  if (t.id === "styleGo") return submitStyle();
  if (t.id === "logout") { try { await api("/api/logout", { method: "POST" }); } catch (_) {} location.href = "/login"; return; }
  if (t.id === "pwOpen") { $("#pwForm").reset(); $("#pwMsg").textContent = ""; $("#pwDlg").showModal(); $("#pwOld").focus(); return; }
  if (t.id === "pwClose") { $("#pwDlg").close(); return; }
  if (x("#theme")) {
    const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    r.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("ms-theme", r.dataset.theme); } catch (_) {}
  }
});
document.addEventListener("keydown", e => {
  if (e.key === "Enter" && e.target.matches("tr[data-go]")) location.hash = e.target.dataset.go.slice(1);
  if (e.key === "Escape" && $("#comenu") && !$("#comenu").hidden) { renderSwitcher(false); $("#cobtn").focus(); }
});
document.addEventListener("submit", async e => {
  if (e.target.id === "pwForm") {
    e.preventDefault();
    const m = $("#pwMsg"), o = $("#pwOld").value, n = $("#pwNew").value, n2 = $("#pwNew2").value;
    if (n !== n2) { m.textContent = "Yangi parollar bir xil emas."; m.className = "note msg err"; return; }
    try {
      await api("/api/password", { method: "POST", json: { old: o, new: n } });
      m.textContent = "Parol o'zgardi. Boshqa qurilmalardagi sessiyalar yopildi."; m.className = "note msg ok";
      setTimeout(() => $("#pwDlg").close(), 1500);
    } catch (err) { m.textContent = err.message; m.className = "note msg err"; }
    return;
  }
  if (e.target.id !== "coadd") return;
  e.preventDefault();
  const name = $("#coName").value.trim(), m = $("#coMsg");
  if (!name) { m.textContent = "Kompaniya nomini yozing."; m.className = "note msg err"; return; }
  try {
    const c = await api("/api/companies", { method: "POST", json: { name } });
    await loadCompanies(); setCo(c.id);
  } catch (err) { m.textContent = err.message; m.className = "note msg err"; }
});
document.addEventListener("change", async e => {
  const t = e.target;
  if (t.name === "style") {
    draft.style = t.value;
    $("#curName").textContent = styleTitle(t.value);
    $("#curDef").textContent = t.value === "auto" ? AUTO_DEF : (styles.find(s => s.name === t.value) || {}).def || "";
    $("#slist").hidden = true; const tg = $("#tgl"); tg.setAttribute("aria-expanded", "false"); tg.textContent = "Uslubni o'zgartirish"; tg.focus();
    summary();
  } else if (t.name === "lvl") { draft.level = t.value; draft.usd = ""; $("#usd").value = ""; summary(); }
  else if (t.dataset && t.dataset.mreq !== undefined) { const f = files.material[+t.dataset.mreq]; if (f) { matInfo.set(f, { ...(matInfo.get(f) || {}), required: t.checked }); summary(); } }
  else if (t.name === "fmt") { draft.format = t.value; summary(); }
  else if (t.id === "newCo") { draft.company = t.value; summary(); }
  else if (t.id === "styleCo") { draft.sCompany = t.value; }
  else if (t.id === "jobCo") {
    try { await api(`/api/jobs/${encodeURIComponent(t.dataset.job)}/company`, { method: "POST", json: { company: t.value || null } }); listSig = ""; await loadJobs(); renderSwitcher(); renderVideo(true); }
    catch (err) { alert(err.message); }
  }
});
document.addEventListener("input", e => {
  const t = e.target;
  if (t.dataset && t.dataset.mnote !== undefined) { const f = files.material[+t.dataset.mnote]; if (f) matInfo.set(f, { ...(matInfo.get(f) || {}), note: t.value }); return; }
  if (t.id === "usd") { draft.usd = t.value.trim(); draft.level = draft.usd === "" ? LV.default : null; $$('input[name="lvl"]').forEach(r => { r.checked = r.value === draft.level; }); summary(); }
  else if (t.id === "title") draft.title = t.value;
  else if (t.id === "refText") draft.text = t.value;
  else if (t.id === "refLike") draft.refLike = t.value;
  else if (t.id === "sTitle") draft.sTitle = t.value;
  else if (t.id === "sText") draft.sText = t.value;
  else if (t.id === "q") { query = t.value.trim(); if (!["videolar", "uslublar"].includes(route.name)) location.hash = "videolar"; else render(); }
});

/* ---------- start ---------- */
(async function start() {
  route = parse();
  await Promise.all([loadStyles().catch(() => {}), loadLevels().catch(() => {}), loadHealth(), loadCompanies(), loadMe()]);
  await loadJobs();
  render();
  setInterval(loadJobs, 4000);
  setInterval(loadHealth, 10000);
  setInterval(() => { if (route.name === "video") renderVideo(false); }, 3000);
})();
