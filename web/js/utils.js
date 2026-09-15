
const API = '/api';
const REFRESH_INTERVAL_DEFAULT = 60;
function el(id) {
  return document.getElementById(id);
}
function toast(title, detail = "") {
  const host = el("toast-host");
  if (!host) return;
  const node = document.createElement("div");
  node.className = "toast";
  node.innerHTML = `<div class="t">${escapeHtml(title)}</div>${detail ? `<div class="d">${escapeHtml(detail)}</div>` : ""}`;
  host.appendChild(node);
  const ttl = 3500;
  setTimeout(() => {
    node.classList.add("toast-exit");
  }, ttl - 400);
  setTimeout(() => node.remove(), ttl);
}
function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = String(s ?? "");
  return div.innerHTML;
}
async function fetchJson(url, opts = {}) {
  const res = await fetch(url, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(opts.headers || {}),
    },
  });
  const text = await res.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }
  }
  if (!res.ok) {
    const msg = (data && (data.error || data.message)) || res.statusText || "请求失败";
    throw new Error(msg);
  }
  return data;
}
function buildAccountAvatar(name, avatarUrl, size = 40) {
  const initial = (name || "?").trim().charAt(0).toUpperCase() || "?";
  if (avatarUrl) {
    return `<div class="account-avatar-wrap" style="width:${size}px;height:${size}px">
      <img class="account-avatar" style="width:${size}px;height:${size}px" src="${escapeHtml(avatarUrl)}" alt="" onerror="this.style.display='none';var s=this.nextElementSibling;if(s)s.style.display='flex';" />
      <div class="account-avatar placeholder" style="display:none;width:${size}px;height:${size}px">${escapeHtml(initial)}</div>
    </div>`;
  }
  return `<div class="account-avatar placeholder" style="width:${size}px;height:${size}px">${escapeHtml(initial)}</div>`;
}
function deepMerge(a, b) {
  const out = { ...a };
  for (const k of Object.keys(b)) {
    if (b[k] != null && typeof b[k] === "object" && !Array.isArray(b[k]) && typeof a[k] === "object" && a[k] != null) {
      out[k] = deepMerge(a[k], b[k]);
    } else {
      out[k] = b[k];
    }
  }
  return out;
}
function animateValue(elem, end, duration = 600) {
  if (!elem) return;
  const text = elem.textContent || "0";
  const start = parseFloat(text.replace(/[^0-9.\-]/g, "")) || 0;
  if (Math.abs(start - end) < 0.005) { elem.textContent = end.toFixed(text.includes(".") ? (text.split(".")[1] || "").length || 2 : 0); return; }
  const decimals = text.includes(".") ? Math.max((text.split(".")[1] || "").length, 2) : 0;
  const startTime = performance.now();
  const step = (now) => {
    const t = Math.min((now - startTime) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    elem.textContent = (start + (end - start) * ease).toFixed(decimals);
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}