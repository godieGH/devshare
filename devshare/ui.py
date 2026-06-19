from __future__ import annotations

import json


THEMES = {
    "dark": {
        "bg": "#0b1020",
        "panel": "#111827",
        "panel_2": "#0f172a",
        "panel_alt": "#111827",
        "text": "#e5e7eb",
        "muted": "#94a3b8",
        "border": "#243044",
        "accent": "#7c3aed",
        "accent_2": "#22c55e",
        "danger": "#ef4444",
        "shadow": "0 14px 35px rgba(0,0,0,.35)",
    },
    "light": {
        "bg": "#f8fafc",
        "panel": "#ffffff",
        "panel_2": "#eef2ff",
        "panel_alt": "#f1f5f9",
        "text": "#0f172a",
        "muted": "#475569",
        "border": "#cbd5e1",
        "accent": "#4f46e5",
        "accent_2": "#16a34a",
        "danger": "#dc2626",
        "shadow": "0 14px 35px rgba(15,23,42,.06)",
    },
}


def _theme_vars(theme: str) -> dict:
    return THEMES.get(theme, THEMES["dark"])


def _base_css(t: dict) -> str:
    return f"""
    :root {{
      --bg: {t["bg"]};
      --panel: {t["panel"]};
      --panel2: {t["panel_2"]};
      --panel-alt: {t["panel_alt"]};
      --text: {t["text"]};
      --muted: {t["muted"]};
      --border: {t["border"]};
      --accent: {t["accent"]};
      --accent2: {t["accent_2"]};
      --danger: {t["danger"]};
      --shadow: {t["shadow"]};
      --radius: 18px;
    }}

    * {{ box-sizing: border-box; }}

    html, body {{
      margin: 0;
      padding: 0;
      height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }}

    body {{
      display: flex;
      flex-direction: column;
      height: 100dvh;
      overflow: hidden;
    }}

    button, .btn {{
      border: 1px solid var(--border);
      background: var(--panel);
      color: var(--text);
      padding: 10px 12px;
      border-radius: 12px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 650;
    }}

    button:hover, .btn:hover {{ filter: brightness(1.04); }}

    .primary {{
      background: var(--accent);
      color: white;
      border-color: transparent;
    }}

    .danger {{
      background: var(--danger);
      color: white;
      border-color: transparent;
    }}
    """


def render_login_page(title: str, theme: str) -> str:
    t = _theme_vars(theme)
    title_js = json.dumps(title)
    theme_js = json.dumps(theme)
    themes_js = json.dumps(THEMES)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Login</title>
  <style>
    {_base_css(t)}

    body {{
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
    }}

    .card {{
      width: min(420px, 100%);
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 28px;
    }}

    h1 {{
      margin: 0 0 8px;
      font-size: 22px;
    }}

    p {{
      margin: 0 0 20px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }}

    input {{
      width: 100%;
      border: 1px solid var(--border);
      background: var(--panel2);
      color: var(--text);
      padding: 14px 16px;
      border-radius: 14px;
      font-size: 24px;
      letter-spacing: 0.35em;
      text-align: center;
      outline: none;
    }}

    input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 20%, transparent);
    }}

    .actions {{
      margin-top: 16px;
      display: grid;
      gap: 10px;
    }}

    .error {{
      margin-top: 12px;
      color: var(--danger);
      font-size: 13px;
      min-height: 18px;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{title}</h1>
    <p>Enter the host PIN shown in the terminal to manage shared files on this device.</p>
    <input id="pinInput" type="password" inputmode="numeric" maxlength="12" autocomplete="one-time-code" placeholder="••••••">
    <div class="actions">
      <button id="loginBtn" class="primary">Unlock host access</button>
    </div>
    <div id="error" class="error"></div>
  </div>
  <script>
    const THEMES = {themes_js};
    const themeName = {theme_js};
    const theme = THEMES[themeName] || THEMES.dark;
    for (const [k, v] of Object.entries(theme)) {{
      document.documentElement.style.setProperty("--" + k.replaceAll("_", "-"), v);
    }}

    const pinInput = document.getElementById("pinInput");
    const errorEl = document.getElementById("error");

    async function login() {{
      errorEl.textContent = "";
      const res = await fetch("/api/login", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ pin: pinInput.value.trim() }})
      }});
      const data = await res.json();
      if (!res.ok) {{
        errorEl.textContent = data.error || "Login failed";
        return;
      }}
      window.location.href = "/";
    }}

    document.getElementById("loginBtn").onclick = login;
    pinInput.addEventListener("keydown", (e) => {{
      if (e.key === "Enter") login();
    }});
    pinInput.focus();
  </script>
</body>
</html>
"""


def render_share_page(
    title: str,
    theme: str,
    token: str,
    name: str,
    is_file: bool,
    allow_upload: bool,
    requires_password: bool = False,
) -> str:
    t = _theme_vars(theme)
    title_js = json.dumps(title)
    theme_js = json.dumps(theme)
    token_js = json.dumps(token)
    name_js = json.dumps(name)
    themes_js = json.dumps(THEMES)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Shared</title>
  <style>
    {_base_css(t)}

    body {{
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    .topbar {{
      border-bottom: 1px solid var(--border);
      background: var(--panel);
      padding: 16px;
    }}

    .wrap {{
      max-width: 900px;
      width: 100%;
      margin: 0 auto;
      padding: 16px;
      flex: 1;
    }}

    h1 {{
      margin: 0;
      font-size: 20px;
    }}

    .subtle {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 13px;
    }}

    .dropzone {{
      border: 1.5px dashed color-mix(in srgb, var(--accent) 45%, var(--border));
      border-radius: 16px;
      padding: 16px;
      text-align: center;
      color: var(--muted);
      margin: 16px 0;
      cursor: pointer;
    }}

    .list {{
      display: grid;
      gap: 10px;
    }}

    .item {{
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: var(--panel-alt);
      cursor: pointer;
    }}

    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 24px;
    }}

    .status {{
      font-size: 12px;
      color: var(--muted);
      margin-top: 8px;
    }}

    /* Share modal */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,.45);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    }}

    .modal {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      width: min(560px, 95%);
      max-width: 95%;
      box-shadow: var(--shadow);
    }}

    .modal .row {{ display:flex; gap:8px; align-items:center; }}
    .modal .actions {{ display:flex; gap:8px; justify-content:flex-end; margin-top:12px }}
    .modal img.qr {{ max-width: 220px; max-height:220px; display:block; margin:8px auto }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="wrap" style="padding-top:0;padding-bottom:0">
      <h1>Shared: {name}</h1>
      <div class="subtle">Secure guest access — download{" and upload" if allow_upload else ""} only within this share.</div>
    </div>
  </div>
  <div class="wrap">
    {"<div id='dropzone' class='dropzone'>Drop files here to upload into this shared folder</div>" if allow_upload else ""}
    <div id="list" class="list"></div>
    <div id="status" class="status">Loading...</div>
  </div>
  <input id="fileInput" type="file" multiple hidden>

  {"<div id='pwOverlay' style='position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.5);z-index:9999;'><div style=\"background:var(--panel);padding:20px;border-radius:12px;min-width:280px;\"><h3 style=\"margin:0 0 8px\">Enter password</h3><input id=\"sharePw\" type=\"password\" style=\"width:100%;padding:8px;margin-bottom:8px;border-radius:8px;border:1px solid var(--border);\" placeholder=\"Share password\" /><div style=\"display:flex;gap:8px;justify-content:flex-end\"><button id=\"pwCancel\">Cancel</button><button id=\"pwSubmit\" class=\"primary\">Unlock</button></div><div id=\"pwErr\" style=\"color:var(--danger);margin-top:8px\"></div></div></div>" if requires_password else ""}

  <script>
    const SHARE = {{
      token: {token_js},
      name: {name_js},
      isFile: {"true" if is_file else "false"},
      allowUpload: {"true" if allow_upload else "false"}
    }};
    const REQUIRES_PASSWORD = {"true" if requires_password else "false"};
    const THEMES = {themes_js};
    const theme = THEMES[{theme_js}] || THEMES.dark;
    for (const [k, v] of Object.entries(theme)) {{
      document.documentElement.style.setProperty("--" + k.replaceAll("_", "-"), v);
    }}

    const listEl = document.getElementById("list");
    const statusEl = document.getElementById("status");
    const fileInputEl = document.getElementById("fileInput");
    const dropzoneEl = document.getElementById("dropzone");
    let currentPath = "";

    function esc(s) {{
      return String(s)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }}

    function apiUrl(path, params) {{
      const u = new URL(path, window.location.origin);
      if (params) {{
        for (const [k, v] of Object.entries(params)) {{
          if (v !== null && v !== undefined && v !== "") u.searchParams.set(k, v);
        }}
      }}
      return u.toString();
    }}

    function downloadItem(item) {{
      const url = apiUrl("/api/guest/file", {{ path: item.path, download: "1" }});
      window.open(url, "_blank");
    }}

    function renderItems(items) {{
      if (!items.length) {{
        listEl.innerHTML = '<div class="empty">Nothing here yet.</div>';
        return;
      }}
      listEl.innerHTML = items.map(item => {{
        const icon = item.type === "dir" ? "📁" : "📄";
        return (
          '<div class="item" data-path="' + esc(item.path) + '" data-type="' + esc(item.type) + '">' +
            '<div>' + icon + '</div>' +
            '<div><strong>' + esc(item.name) + '</strong><br><span style="color:var(--muted);font-size:12px">' + esc(item.size_h || "") + '</span></div>' +
            '<button type="button">' + (item.type === "dir" ? "Open" : "Download") + '</button>' +
          '</div>'
        );
      }}).join("");

      listEl.querySelectorAll(".item").forEach(el => {{
        const path = el.getAttribute("data-path");
        const type = el.getAttribute("data-type");
        el.querySelector("button").addEventListener("click", (e) => {{
          e.stopPropagation();
          if (type === "dir") {{
            currentPath = path;
            loadList();
          }} else {{
            downloadItem({{ path }});
          }}
        }});
        el.addEventListener("dblclick", () => {{
          if (type === "dir") {{
            currentPath = path;
            loadList();
          }} else {{
            downloadItem({{ path }});
          }}
        }});
      }});
    }}

    async function loadList() {{
      statusEl.textContent = "Loading...";
      const res = await fetch(apiUrl("/api/guest/list", {{ path: currentPath }}));
      const data = await res.json();
      if (!res.ok) {{
        listEl.innerHTML = '<div class="empty">' + esc(data.error || "Failed to load") + '</div>';
        statusEl.textContent = "Error";
        return;
      }}
      renderItems(data.items || []);
      statusEl.textContent = (data.items || []).length + " item(s)";
    }}

    async function uploadFiles(files) {{
      if (!files || !files.length || !SHARE.allowUpload) return;
      const form = new FormData();
      for (const file of files) form.append("files", file, file.name);
      statusEl.textContent = "Uploading...";
      const res = await fetch(apiUrl("/api/guest/upload", {{ path: currentPath }}), {{
        method: "POST",
        body: form
      }});
      const data = await res.json();
      if (!res.ok) {{
        alert(data.error || "Upload failed");
        statusEl.textContent = "Upload failed";
        return;
      }}
      statusEl.textContent = "Upload complete";
      loadList();
    }}

    if (dropzoneEl) {{
      dropzoneEl.addEventListener("click", () => fileInputEl.click());
      dropzoneEl.addEventListener("dragover", (e) => {{ e.preventDefault(); }});
      dropzoneEl.addEventListener("drop", (e) => {{
        e.preventDefault();
        uploadFiles(e.dataTransfer.files);
      }});
      fileInputEl.addEventListener("change", () => uploadFiles(fileInputEl.files));
    }}

    loadList();

    if (REQUIRES_PASSWORD) {{
      const overlay = document.getElementById('pwOverlay');
      const err = document.getElementById('pwErr');
      const input = document.getElementById('sharePw');
      document.getElementById('pwCancel').onclick = () => window.location.href = '/';
      document.getElementById('pwSubmit').onclick = async () => {{
        err.textContent = '';
        const pw = input.value || '';
        const res = await fetch('/api/guest/auth', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ token: SHARE.token, password: pw }})
        }});
        const data = await res.json();
        if (!res.ok) {{ err.textContent = data.error || 'Invalid password'; return; }}
        overlay.style.display = 'none';
        loadList();
      }};
    }}
  </script>
</body>
</html>
"""


def render_page(title: str, version: str, theme: str, current_path: str, auth_enabled: bool = False) -> str:
    t = THEMES.get(theme, THEMES["dark"])
    title_js = json.dumps(title)
    version_js = json.dumps(version)
    theme_js = json.dumps(theme)
    themes_js = json.dumps(THEMES)
    path_js = json.dumps(current_path or "")
    auth_enabled_js = json.dumps(auth_enabled)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} {version}</title>
  <style>
    :root {{
      --bg: {t["bg"]};
      --panel: {t["panel"]};
      --panel2: {t["panel_2"]};
      --panel-alt: {t["panel_alt"]};
      --text: {t["text"]};
      --muted: {t["muted"]};
      --border: {t["border"]};
      --accent: {t["accent"]};
      --accent2: {t["accent_2"]};
      --danger: {t["danger"]};
      --shadow: {t["shadow"]};
      --radius: 18px;
    }}

    * {{
      box-sizing: border-box;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }}

    body {{
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    .topbar {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: color-mix(in srgb, var(--panel) 92%, transparent);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border);
      box-shadow: 0 4px 24px rgba(15,23,42,.08);
    }}

    .topbar-inner {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 14px 16px;
      display: grid;
      gap: 10px;
    }}

    .brand-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }}

    .logo {{
      width: 38px;
      height: 38px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      box-shadow: var(--shadow);
    }}

    .title-wrap {{
      min-width: 0;
    }}

    .title {{
      font-size: 18px;
      font-weight: 800;
      margin: 0;
      line-height: 1.15;
    }}

    .subtle {{
      margin-top: 4px;
      font-size: 12px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: min(70vw, 900px);
    }}

    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}

    button, .btn {{
      border: 1px solid var(--border);
      background: var(--panel);
      color: var(--text);
      padding: 10px 12px;
      border-radius: 12px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 650;
    }}

    .item .mini button {{
      min-width: 88px;
    }}

    button:hover, .btn:hover {{
      filter: brightness(1.04);
    }}

    .primary {{
      background: var(--accent);
      color: white;
      border-color: transparent;
    }}

    .danger {{
      background: var(--danger);
      color: white;
      border-color: transparent;
    }}

    .search {{
      width: 100%;
      border: 1px solid var(--border);
      background: var(--panel);
      color: var(--text);
      padding: 12px 14px;
      border-radius: 14px;
      font-size: 14px;
      outline: none;
    }}

    .search:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 20%, transparent);
    }}

    main {{
      flex: 1;
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
      padding: 16px;
      display: grid;
      gap: 16px;
      min-height: 0;
      overflow: hidden;
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      min-height: 0;
      overflow: hidden;
    }}

    .panel-inner {{
      padding: 14px;
      height: 100%;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }}

    .dropzone {{
      border: 1.5px dashed color-mix(in srgb, var(--accent) 45%, var(--border));
      border-radius: 16px;
      padding: 16px;
      text-align: center;
      color: var(--muted);
      background: var(--panel);
      transition: .15s ease;
      margin-bottom: 12px;
    }}

    .item {{
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 14px;
      cursor: pointer;
      background: var(--panel_alt);
    }}

    .dropzone.dragover {{
      transform: scale(1.01);
      border-color: var(--accent);
      color: var(--text);
    }}

    .crumbs {{
      font-size: 13px;
      color: var(--muted);
      padding: 2px 0 8px;
      word-break: break-word;
    }}

    .stats {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}

    .list {{
      overflow-y: auto;
      flex: 1;
      min-height: 0;
      display: grid;
      gap: 10px;
      padding-right: 4px;
    }}

    .item {{
      display: grid;
      grid-template-columns: 44px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 14px;
      cursor: pointer;
      background: var(--panel_alt);
    }}

    .item:hover {{
      border-color: color-mix(in srgb, var(--accent) 45%, var(--border));
    }}

    .item.selected {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 14%, transparent);
    }}

    .ico {{
      width: 44px;
      height: 44px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      font-size: 22px;
      background: color-mix(in srgb, var(--accent) 6%, transparent);
      border: 1px solid color-mix(in srgb, var(--accent) 18%, var(--border));
    }}

    .meta {{
      min-width: 0;
    }}

    .name {{
      font-weight: 750;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .info {{
      margin-top: 4px;
      font-size: 12px;
      color: var(--muted);
    }}

    .mini {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .preview-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      padding-bottom: 12px;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }}

    .preview-title {{
      margin: 0;
      font-size: 16px;
      font-weight: 800;
      word-break: break-word;
    }}

    .preview-box {{
      min-height: 0;
      flex: 1;
      overflow: auto;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
      padding: 14px;
    }}

    .preview-box img {{
      max-width: 100%;
      height: auto;
      border-radius: 12px;
      display: block;
    }}

    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.55;
      color: var(--text);
    }}

    .empty {{
      color: var(--muted);
      padding: 24px;
      text-align: center;
    }}

    .status {{
      font-size: 12px;
      color: var(--muted);
    }}

    /* ── Share modal — lives directly in <body>, z-index beats everything ── */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, .55);
      display: none;
      align-items: flex-start;
      justify-content: center;
      z-index: 9999;
      padding: 24px 16px;
      overflow-y: auto;
    }}

    .modal {{
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 22px;
      width: 100%;
      max-width: 480px;
      box-shadow: var(--shadow);
      margin: auto;
    }}

    .modal h3 {{
      margin: 0 0 16px;
      font-size: 17px;
      font-weight: 800;
      color: var(--text);
    }}

    .modal-row {{
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 10px;
    }}

    .modal-label {{
      min-width: 80px;
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
      flex-shrink: 0;
    }}

    .modal-input {{
      flex: 1;
      background: var(--bg);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 12px;
      font-size: 13px;
      outline: none;
      width: 100%;
      min-width: 0;
    }}

    .modal-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 20%, transparent);
    }}

    .modal-target {{
      flex: 1;
      font-size: 13px;
      font-weight: 700;
      color: var(--text);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .modal-actions {{
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      margin-top: 16px;
    }}

    .modal button {{
      background: var(--panel-alt);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 16px;
      font-size: 13px;
      font-weight: 650;
      cursor: pointer;
    }}

    .modal button:hover {{ filter: brightness(1.06); }}

    .modal button.primary {{
      background: var(--accent);
      color: #ffffff;
      border-color: transparent;
    }}

    .modal button.primary:disabled {{ opacity: .55; cursor: not-allowed; }}

    .modal-result {{
      display: none;
      margin-top: 14px;
      border-top: 1px solid var(--border);
      padding-top: 14px;
    }}

    .modal-url {{
      word-break: break-all;
      font-size: 13px;
      color: var(--accent);
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      line-height: 1.5;
    }}

    .modal-qr-wrap {{
      display: none;
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px;
      margin: 12px 0;
      text-align: center;
    }}

    .modal-qr-wrap img {{
      display: block;
      width: 100%;
      max-width: 220px;
      height: auto;
      margin: 0 auto;
    }}

    .modal-qr-wrap p {{
      margin: 8px 0 0;
      font-size: 11px;
      color: var(--muted);
    }}

    .modal-result-actions {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
      margin-top: 10px;
    }}

    /* ── Preview read-more clamp ── */
    .preview-clamp {{
      position: relative;
    }}

    .preview-clamp pre {{
      max-height: 260px;
      overflow: hidden;
      transition: max-height .3s ease;
    }}

    .preview-clamp.expanded pre {{
      max-height: none;
    }}

    .preview-clamp .fade {{
      position: absolute;
      bottom: 28px;
      left: 0;
      right: 0;
      height: 60px;
      background: linear-gradient(to bottom, transparent, var(--bg));
      pointer-events: none;
      transition: opacity .2s;
    }}

    .preview-clamp.expanded .fade {{
      opacity: 0;
    }}

    .read-more-btn {{
      display: block;
      width: 100%;
      margin-top: 6px;
      padding: 7px;
      font-size: 12px;
      font-weight: 700;
      border-radius: 10px;
      background: var(--panel-alt);
      border: 1px solid var(--border);
      color: var(--accent);
      cursor: pointer;
      text-align: center;
    }}

    .read-more-btn:hover {{ filter: brightness(1.06); }}

    .lan-panel {{
      font-size: 13px;
      color: var(--text);
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: var(--bg);
      word-break: break-all;
    }}

    .lan-panel strong {{
      color: var(--accent);
      margin-right: 8px;
    }}

    .sort-bar {{
      display: flex;
      gap: 6px;
      align-items: center;
      margin-bottom: 8px;
      flex-wrap: wrap;
    }}

    .sort-label {{
      font-size: 12px;
      color: var(--muted);
      margin-right: 2px;
    }}

    .sort-btn {{
      padding: 5px 10px;
      font-size: 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--panel-alt);
      color: var(--muted);
      cursor: pointer;
      font-weight: 600;
    }}

    .sort-btn.active {{
      color: var(--accent);
      border-color: var(--accent);
      background: color-mix(in srgb, var(--accent) 8%, var(--panel-alt));
    }}

    .sort-toggle {{
      padding: 5px 10px;
      font-size: 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--panel-alt);
      color: var(--muted);
      cursor: pointer;
      font-weight: 600;
    }}

    .sort-toggle:hover, .sort-btn:hover {{ filter: brightness(1.06); }}

    @media (max-width: 980px) {{
      main {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <div class="brand-row">
        <div class="brand">
          <div class="logo"></div>
          <div class="title-wrap">
            <h1 class="title">{title}</h1>
            <div class="subtle" id="pathText"></div>
          </div>
        </div>
        <div class="toolbar">
          <button id="shareBtn" class="primary">Share</button>
          <button id="upBtn">Up</button>
          <button id="refreshBtn">Refresh</button>
          <button id="newFolderBtn">New folder</button>
          <button id="renameBtn">Rename</button>
          <button id="deleteBtn" class="danger">Delete</button>
          <button id="downloadBtn">Download</button>
          <button id="zipBtn">Zip</button>
          <button id="themeBtn">Theme</button>
          {"<button id='logoutBtn'>Logout</button>" if auth_enabled else ""}
        </div>
      </div>
      <div id="lanPanel" class="lan-panel" hidden>
        <strong>Share on your network:</strong>
        <span id="lanUrls"></span>
      </div>
      <input id="search" class="search" placeholder="Search files and folders...">
      <div class="status" id="status">Ready</div>
    </div>
  </div>

  <main>
    <section class="panel">
      <div class="panel-inner">
        <div id="dropzone" class="dropzone">
          Drag & drop files here or use your phone gallery / file picker
        </div>
        <div class="stats">
          <div id="countText">0 items</div>
          <div id="selectedText">Nothing selected</div>
        </div>
        <div class="sort-bar">
          <span class="sort-label">Sort:</span>
          <button class="sort-btn active" data-sort="name">Name</button>
          <button class="sort-btn" data-sort="mtime">Date</button>
          <button class="sort-btn" data-sort="size">Size</button>
          <button class="sort-toggle" id="sortDirBtn" title="Toggle sort direction">↑</button>
          <button class="sort-toggle" id="groupBtn" title="Group folders first">📁 First</button>
        </div>
        <div id="list" class="list"></div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-inner">
        <div class="preview-head">
          <h2 class="preview-title" id="previewTitle">Preview</h2>
          <div class="mini" id="previewMini"></div>
        </div>
        <div id="previewBox" class="preview-box">
          <div class="empty">Select a file to preview it here.</div>
        </div>
      </div>
    </section>
  </main>

  <input id="fileInput" type="file" multiple hidden>

  <!-- Share modal — direct child of body so backdrop-filter on topbar cannot trap it -->
  <div id="shareBackdrop" class="modal-backdrop">
    <div class="modal" id="shareModal">
      <h3>Create share link</h3>
      <div class="modal-row">
        <span class="modal-label">Sharing</span>
        <span class="modal-target" id="shareTargetName">—</span>
      </div>
      <div class="modal-row">
        <span class="modal-label">Password</span>
        <input id="sharePasswordInput" class="modal-input" type="password" placeholder="Optional — leave blank for open access">
      </div>
      <!-- Create / Cancel actions -->
      <div class="modal-actions" id="shareActions">
        <button id="shareCancel">Cancel</button>
        <button id="shareCreate" class="primary">Create link</button>
      </div>
      <!-- Result shown after creation -->
      <div class="modal-result" id="shareResult">
        <div class="modal-url" id="shareUrl"></div>
        <div class="modal-qr-wrap" id="shareQrWrap">
          <img id="shareQrImg" src="" alt="QR code for share link">
          <p>Scan to open on another device</p>
        </div>
        <div class="modal-result-actions">
          <button id="shareCopyBtn">Copy link</button>
          <button id="shareNativeBtn" style="display:none">Share…</button>
          <button id="shareCloseBtn" class="primary">Done</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    const APP = {{
      title: {title_js},
      version: {version_js},
      theme: {theme_js},
      currentPath: {path_js},
      authEnabled: {auth_enabled_js}
    }};

    const THEMES = {themes_js};

    const state = {{
      items: [],
      selected: null,
      filtered: [],
      sortBy: "name",
      sortAsc: true,
      groupDirs: true,
    }};

    const themeKey = "devshare-theme";

    function applyTheme(themeName) {{
      const theme = THEMES[themeName] || THEMES.dark;
      const root = document.documentElement;
      for (const [k, v] of Object.entries(theme)) {{
        root.style.setProperty("--" + k.replaceAll("_", "-"), v);
      }}
      localStorage.setItem(themeKey, themeName);
    }}

    function getInitialTheme() {{
      return localStorage.getItem(themeKey) || APP.theme || "dark";
    }}

    const INITIAL_THEME = getInitialTheme();
    applyTheme(INITIAL_THEME);

    const listEl = document.getElementById("list");
    const searchEl = document.getElementById("search");
    const statusEl = document.getElementById("status");
    const countEl = document.getElementById("countText");
    const selectedEl = document.getElementById("selectedText");
    const pathTextEl = document.getElementById("pathText");
    const previewTitleEl = document.getElementById("previewTitle");
    const previewBoxEl = document.getElementById("previewBox");
    const previewMiniEl = document.getElementById("previewMini");
    const fileInputEl = document.getElementById("fileInput");
    const dropzoneEl = document.getElementById("dropzone");

    const enc = encodeURIComponent;

    function setStatus(msg) {{
      statusEl.textContent = msg;
    }}

    function esc(s) {{
      return String(s)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }}

    async function fetchJson(url, options) {{
      const res = await fetch(url, options);
      const data = await res.json();
      if (res.status === 401 && APP.authEnabled) {{
        window.location.href = "/login";
        throw new Error("Unauthorized");
      }}
      return {{ res, data }};
    }}

    async function loadInfo() {{
      try {{
        const {{ res, data }} = await fetchJson("/api/info");
        if (!res.ok) return;
        const panel = document.getElementById("lanPanel");
        const urlsEl = document.getElementById("lanUrls");
        if (panel && urlsEl && data.urls && data.urls.length) {{
          urlsEl.textContent = data.urls.join("  ·  ");
          panel.hidden = false;
        }}
      }} catch (err) {{
        // ignore
      }}
    }}

    async function openShareModal() {{
      if (!state.selected) return alert('Select a file or folder to share first');
      const bd = document.getElementById('shareBackdrop');
      document.getElementById('sharePasswordInput').value = '';
      document.getElementById('shareUrl').textContent = '';
      document.getElementById('shareQrImg').src = '';
      document.getElementById('shareQrWrap').style.display = 'none';
      document.getElementById('shareResult').style.display = 'none';
      document.getElementById('shareActions').style.display = 'flex';
      document.getElementById('shareTargetName').textContent = state.selected.name;
      bd.style.display = 'flex';
    }}

    async function createShareFromModal() {{
      if (!state.selected) return alert('Select a file or folder to share');
      const allowUpload = state.selected.type === 'dir';
      const pw = document.getElementById('sharePasswordInput').value || null;
      const createBtn = document.getElementById('shareCreate');
      createBtn.disabled = true;
      try {{
        const {{ res, data }} = await fetchJson('/api/share', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ path: state.selected.path, allow_upload: allowUpload, password: pw, theme: localStorage.getItem(themeKey) || APP.theme || 'dark' }})
        }});
        if (!res.ok) return alert(data.error || 'Share failed');

        document.getElementById('shareUrl').textContent = data.url;

        const qrWrap = document.getElementById('shareQrWrap');
        const qrImg = document.getElementById('shareQrImg');
        if (data.qr) {{
          qrImg.src = data.qr;
          qrWrap.style.display = 'block';
        }} else {{
          qrWrap.style.display = 'none';
        }}

        document.getElementById('shareActions').style.display = 'none';
        document.getElementById('shareResult').style.display = 'block';

        const nativeBtn = document.getElementById('shareNativeBtn');
        if (navigator.share) nativeBtn.style.display = '';

        try {{
          if (navigator.clipboard && navigator.clipboard.writeText) {{
            await navigator.clipboard.writeText(data.url);
          }}
        }} catch (e) {{}}
      }} finally {{
        createBtn.disabled = false;
      }}
    }}

    function closeShareModal() {{
      document.getElementById('shareBackdrop').style.display = 'none';
      document.getElementById('shareActions').style.display = 'flex';
      document.getElementById('shareResult').style.display = 'none';
      document.getElementById('shareQrWrap').style.display = 'none';
      document.getElementById('sharePasswordInput').value = '';
    }}

    async function logout() {{
      await fetch("/api/logout", {{ method: "POST" }});
      window.location.href = "/login";
    }}

    function apiUrl(path, params) {{
      const u = new URL(path, window.location.origin);
      if (params) {{
        for (const [k, v] of Object.entries(params)) {{
          if (v !== null && v !== undefined && v !== "") u.searchParams.set(k, v);
        }}
      }}
      return u.toString();
    }}

    function currentPath() {{
      return new URL(window.location.href).searchParams.get("path") || "";
    }}

    function openPath(path) {{
      const u = new URL(window.location.href);
      if (path) u.searchParams.set("path", path);
      else u.searchParams.delete("path");
      window.location.href = u.toString();
    }}

    function parentPath(path) {{
      if (!path) return "";
      const parts = path.replaceAll("\\\\", "/").split("/").filter(Boolean);
      parts.pop();
      return parts.join("/");
    }}

    function joinPath(base, name) {{
      base = (base || "").replaceAll("\\\\", "/").replace(/\\/+$/, "");
      return base ? base + "/" + name : name;
    }}

    function fmtDate(ts) {{
      return new Date(ts * 1000).toLocaleString();
    }}

    function renderBreadcrumb() {{
      const p = currentPath();
      pathTextEl.textContent = p ? ("Current path: " + p) : "Current path: /";
    }}

    function selectItem(item) {{
      state.selected = item;
      document.querySelectorAll(".item").forEach(el => el.classList.remove("selected"));
      const row = document.querySelector('.item[data-path="' + CSS.escape(item.path) + '"]');
      if (row) row.classList.add("selected");
      selectedEl.textContent = item.name + " (" + item.type + ")";
      previewItem(item);
      renderPreviewActions();
    }}

    function renderPreviewActions() {{
      previewMiniEl.innerHTML = "";
      if (!state.selected) return;

      const item = state.selected;

      const download = document.createElement("button");
      download.textContent = "Open";
      download.onclick = () => {{
        const url = apiUrl("/api/file", {{ path: item.path }});
        window.open(url, "_blank");
      }};

      previewMiniEl.appendChild(download);

      const shareBtn = document.createElement("button");
      shareBtn.textContent = "Share link";
      shareBtn.className = "primary";
      shareBtn.onclick = () => {{
        state.selected = item;
        openShareModal();
      }};
      previewMiniEl.appendChild(shareBtn);

      if (item.type === "dir") {{
        const zip = document.createElement("button");
        zip.textContent = "Zip";
        zip.onclick = () => window.open(apiUrl("/api/zip", {{ path: item.path }}), "_blank");
        previewMiniEl.appendChild(zip);
      }}
    }}

    async function previewItem(item) {{
      previewTitleEl.textContent = item.name;
      setStatus("Loading preview...");
      previewBoxEl.innerHTML = '<div class="empty">Loading...</div>';

      try {{
        const res = await fetch(apiUrl("/api/preview", {{ path: item.path }}));
        const data = await res.json();

        if (!res.ok) {{
          previewBoxEl.innerHTML = '<div class="empty">' + esc(data.error || "Preview failed") + "</div>";
          setStatus("Preview failed");
          return;
        }}

        if (data.kind === "dir") {{
          const list = (data.items || []).map(x => "<li>" + esc(x) + "</li>").join("");
          previewBoxEl.innerHTML =
            "<div class='empty' style='text-align:left'>" +
            "<b>Folder</b><br><br>" +
            "Contains " + esc(String(data.count || 0)) + " item(s)." +
            "<ul>" + list + "</ul>" +
            "</div>";
          setStatus("Folder preview ready");
          return;
        }}

        if (data.kind === "image") {{
          previewBoxEl.innerHTML = "<img src='" + esc(data.url) + "' alt='" + esc(data.name) + "'>";
          setStatus("Image preview ready");
          return;
        }}

        if (data.kind === "audio") {{
          previewBoxEl.innerHTML =
            '<div style="padding:16px 8px">' +
            '<audio controls style="width:100%;border-radius:10px" src="' + esc(data.url) + '"></audio>' +
            '<div class="info" style="margin-top:10px;text-align:center;font-size:13px">' + esc(data.name) + '</div>' +
            '</div>';
          setStatus("Audio ready");
          return;
        }}

        if (data.kind === "text") {{
          const content = data.content || "";
          const lines = content.split("\\n").length;
          const needsClamp = lines > 14 || content.length > 800;
          if (needsClamp) {{
            previewBoxEl.innerHTML =
              '<div class="preview-clamp" id="previewClamp">' +
                '<pre>' + esc(content) + '</pre>' +
                '<div class="fade"></div>' +
                '<button class="read-more-btn" id="readMoreBtn">Read more</button>' +
              '</div>';
            document.getElementById("readMoreBtn").addEventListener("click", () => {{
              const clamp = document.getElementById("previewClamp");
              const btn = document.getElementById("readMoreBtn");
              const expanded = clamp.classList.toggle("expanded");
              btn.textContent = expanded ? "See less" : "Read more";
            }});
          }} else {{
            previewBoxEl.innerHTML = "<pre>" + esc(content) + "</pre>";
          }}
          setStatus("Text preview ready");
          return;
        }}

        previewBoxEl.innerHTML =
          "<div class='empty'>" +
          "<b>Binary file</b><br><br>" +
          esc(data.name || item.name) +
          "<br><br>" +
          "Use Open or Download." +
          "</div>";
        setStatus("Binary file");
      }} catch (err) {{
        previewBoxEl.innerHTML = '<div class="empty">Preview error</div>';
        setStatus("Preview error");
      }}
    }}

    function getSorted(items) {{
      const {{ sortBy, sortAsc, groupDirs }} = state;
      const cmp = (a, b) => {{
        let v = 0;
        if (sortBy === "size") v = a.size - b.size;
        else if (sortBy === "mtime") v = a.mtime - b.mtime;
        else v = a.name.localeCompare(b.name);
        return sortAsc ? v : -v;
      }};
      if (groupDirs) {{
        const dirs = items.filter(x => x.type === "dir").sort(cmp);
        const files = items.filter(x => x.type !== "dir").sort(cmp);
        return [...dirs, ...files];
      }}
      return [...items].sort(cmp);
    }}

    function renderList() {{
      const q = searchEl.value.trim().toLowerCase();
      const items = state.items.filter(item => {{
        if (!q) return true;
        return item.name.toLowerCase().includes(q) || item.type.toLowerCase().includes(q);
      }});
      state.filtered = items;
      countEl.textContent = items.length + " item(s)";
      if (!items.length) {{
        listEl.innerHTML = '<div class="empty">No matching files.</div>';
        return;
      }}

      const sorted = getSorted(items);

      listEl.innerHTML = sorted.map(item => {{
        const icon = item.type === "dir" ? "📁"
          : item.kind === "image" ? "🖼️"
          : item.kind === "audio" ? "🎵"
          : "📄";
        return (
          '<div class="item" data-path="' + esc(item.path) + '" data-kind="' + esc(item.kind) + '">' +
            '<div class="ico">' + icon + '</div>' +
            '<div class="meta">' +
              '<div class="name">' + esc(item.name) + '</div>' +
              '<div class="info">' + esc(item.size_h || "") + ' · ' + esc(item.mtime_h || "") + '</div>' +
            '</div>' +
            '<div class="mini">' +
              '<button data-open="1">Open</button>' +
            '</div>' +
          '</div>'
        );
      }}).join("");

      document.querySelectorAll(".item").forEach(el => {{
        const path = el.getAttribute("data-path");
        const item = state.items.find(x => x.path === path);
        if (!item) return;

        el.addEventListener("click", () => selectItem(item));
        el.querySelector('[data-open="1"]').addEventListener("click", (e) => {{
          e.stopPropagation();
          if (item.type === "dir") openPath(item.path);
          else window.open(apiUrl("/api/file", {{ path: item.path }}), "_blank");
        }});
        el.addEventListener("dblclick", () => {{
          if (item.type === "dir") openPath(item.path);
          else window.open(apiUrl("/api/file", {{ path: item.path }}), "_blank");
        }});
      }});

      setStatus("Loaded " + items.length + " item(s)");
    }}

    async function loadList() {{
      renderBreadcrumb();
      setStatus("Loading folder...");
      const p = currentPath();
      const {{ res, data }} = await fetchJson(apiUrl("/api/list", {{ path: p }}));

      if (!res.ok) {{
        listEl.innerHTML = '<div class="empty">' + esc(data.error || "Failed to load folder") + "</div>";
        setStatus("Load failed");
        return;
      }}

      state.items = data.items || [];
      state.selected = null;
      selectedEl.textContent = "Nothing selected";
      previewTitleEl.textContent = "Preview";
      previewBoxEl.innerHTML = '<div class="empty">Select a file to preview it here.</div>';
      previewMiniEl.innerHTML = "";
      renderList();
    }}

    async function postJson(url, body) {{
      const {{ res, data }} = await fetchJson(url, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(body)
      }});
      return data;
    }}

    async function deleteSelected() {{
      if (!state.selected) return alert("Select a file or folder first");
      if (!confirm("Delete " + state.selected.name + "?")) return;
      const data = await postJson("/api/delete", {{ path: state.selected.path }});
      if (data.ok) loadList(); else alert(data.error || "Delete failed");
    }}

    async function renameSelected() {{
      if (!state.selected) return alert("Select a file or folder first");
      const next = prompt("New name", state.selected.name);
      if (!next) return;
      const data = await postJson("/api/rename", {{ path: state.selected.path, name: next }});
      if (data.ok) loadList(); else alert(data.error || "Rename failed");
    }}

    async function newFolder() {{
      const name = prompt("Folder name");
      if (!name) return;
      const data = await postJson("/api/mkdir", {{ path: currentPath(), name }});
      if (data.ok) loadList(); else alert(data.error || "Create folder failed");
    }}

    async function uploadFiles(files) {{
      if (!files || !files.length) return;
      const form = new FormData();
      for (const file of files) form.append("files", file, file.name);

      setStatus("Uploading...");
      const {{ res, data }} = await fetchJson(apiUrl("/api/upload", {{ path: currentPath() }}), {{
        method: "POST",
        body: form
      }});
      if (!res.ok) {{
        alert(data.error || "Upload failed");
        setStatus("Upload failed");
        return;
      }}
      setStatus("Upload done");
      loadList();
    }}

    async function downloadSelected() {{
      if (!state.selected) return alert("Select a file or folder first");
      if (state.selected.type === "dir") {{
        window.open(apiUrl("/api/zip", {{ path: state.selected.path }}), "_blank");
      }} else {{
        window.open(apiUrl("/api/file", {{ path: state.selected.path, download: "1" }}), "_blank");
      }}
    }}

    async function zipSelected() {{
      if (!state.selected) return alert("Select a folder first");
      if (state.selected.type !== "dir") return alert("Zip works on folders only");
      window.open(apiUrl("/api/zip", {{ path: state.selected.path }}), "_blank");
    }}

    function toggleTheme() {{
      const current = localStorage.getItem(themeKey) || APP.theme || "dark";
      const nextName = current === "dark" ? "light" : "dark";
      applyTheme(nextName);
    }}

    document.getElementById("shareBtn").onclick = () => openShareModal();
    document.getElementById("upBtn").onclick = () => openPath(parentPath(currentPath()));
    document.getElementById("refreshBtn").onclick = () => loadList();
    document.getElementById("newFolderBtn").onclick = () => newFolder();
    document.getElementById("renameBtn").onclick = () => renameSelected();
    document.getElementById("deleteBtn").onclick = () => deleteSelected();
    document.getElementById("downloadBtn").onclick = () => downloadSelected();
    document.getElementById("zipBtn").onclick = () => zipSelected();
    document.getElementById("themeBtn").onclick = () => toggleTheme();
    if (APP.authEnabled) {{
      document.getElementById("logoutBtn").onclick = () => logout();
    }}

    // Modal bindings
    document.getElementById('shareCancel').onclick = () => closeShareModal();
    document.getElementById('shareCloseBtn').onclick = () => closeShareModal();
    document.getElementById('shareCopyBtn').onclick = async () => {{
      const url = document.getElementById('shareUrl').textContent || '';
      try {{ await navigator.clipboard.writeText(url); alert('Link copied!'); }} catch (e) {{ prompt('Copy this link:', url); }}
    }};
    document.getElementById('shareNativeBtn').onclick = async () => {{
      const url = document.getElementById('shareUrl').textContent || '';
      try {{ await navigator.share({{ title: APP.title + ' — shared link', url }}); }} catch (e) {{}}
    }};
    document.getElementById('shareCreate').onclick = () => createShareFromModal();
    document.getElementById('shareBackdrop').addEventListener('click', (e) => {{
      if (e.target.id === 'shareBackdrop') closeShareModal();
    }});

    document.querySelectorAll(".sort-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        document.querySelectorAll(".sort-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.sortBy = btn.dataset.sort;
        renderList();
      }});
    }});

    document.getElementById("sortDirBtn").addEventListener("click", () => {{
      state.sortAsc = !state.sortAsc;
      document.getElementById("sortDirBtn").textContent = state.sortAsc ? "↑" : "↓";
      renderList();
    }});

    document.getElementById("groupBtn").addEventListener("click", () => {{
      state.groupDirs = !state.groupDirs;
      document.getElementById("groupBtn").style.opacity = state.groupDirs ? "1" : "0.45";
      renderList();
    }});

    searchEl.addEventListener("input", renderList);

    fileInputEl.addEventListener("change", () => uploadFiles(fileInputEl.files));
    dropzoneEl.addEventListener("click", () => fileInputEl.click());
    dropzoneEl.addEventListener("dragover", (e) => {{
      e.preventDefault();
      dropzoneEl.classList.add("dragover");
    }});
    dropzoneEl.addEventListener("dragleave", () => dropzoneEl.classList.remove("dragover"));
    dropzoneEl.addEventListener("drop", (e) => {{
      e.preventDefault();
      dropzoneEl.classList.remove("dragover");
      uploadFiles(e.dataTransfer.files);
    }});

    renderBreadcrumb();
    loadInfo();
    loadList();
  </script>
</body>
</html>
"""