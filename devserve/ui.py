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


def render_page(title: str, version: str, theme: str, current_path: str) -> str:
    t = THEMES.get(theme, THEMES["dark"])
    title_js = json.dumps(title)
    version_js = json.dumps(version)
    theme_js = json.dumps(theme)
    themes_js = json.dumps(THEMES)
    path_js = json.dumps(current_path or "")

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
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, .85fr);
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      min-height: 0;
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

    .preview-box {{
      min-height: 300px;
      flex: 1;
      overflow: auto;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: var(--panel);
      padding: 14px;
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
      overflow: auto;
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
      min-height: 300px;
      flex: 1;
      overflow: auto;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: var(--panel2);
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
          <button id="upBtn">Up</button>
          <button id="refreshBtn">Refresh</button>
          <button id="newFolderBtn">New folder</button>
          <button id="renameBtn">Rename</button>
          <button id="deleteBtn" class="danger">Delete</button>
          <button id="downloadBtn">Download</button>
          <button id="zipBtn">Zip</button>
          <button id="themeBtn">Theme</button>
        </div>
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

  <script>
    const APP = {{
      title: {title_js},
      version: {version_js},
      theme: {theme_js},
      currentPath: {path_js}
    }};

    const THEMES = {themes_js};

    const state = {{
      items: [],
      selected: null,
      filtered: []
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

        if (data.kind === "text") {{
          previewBoxEl.innerHTML = "<pre>" + esc(data.content || "") + "</pre>";
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

      listEl.innerHTML = items.map(item => {{
        const icon = item.type === "dir" ? "📁" : (item.kind === "image" ? "🖼️" : "📄");
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
      const res = await fetch(apiUrl("/api/list", {{ path: p }}));
      const data = await res.json();

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
      const res = await fetch(url, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(body)
      }});
      return await res.json();
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
      const res = await fetch(apiUrl("/api/upload", {{ path: currentPath() }}), {{
        method: "POST",
        body: form
      }});
      const data = await res.json();
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

    document.getElementById("upBtn").onclick = () => openPath(parentPath(currentPath()));
    document.getElementById("refreshBtn").onclick = () => loadList();
    document.getElementById("newFolderBtn").onclick = () => newFolder();
    document.getElementById("renameBtn").onclick = () => renameSelected();
    document.getElementById("deleteBtn").onclick = () => deleteSelected();
    document.getElementById("downloadBtn").onclick = () => downloadSelected();
    document.getElementById("zipBtn").onclick = () => zipSelected();
    document.getElementById("themeBtn").onclick = () => toggleTheme();
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
    loadList();
  </script>
</body>
</html>
"""