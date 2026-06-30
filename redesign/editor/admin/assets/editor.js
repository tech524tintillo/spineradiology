/* ============================================================
   editor.js — SpineRadiology hidden /admin editor SPA
   - Auth gate (demo OTP locally; Cloudflare Access in prod)
   - Loads doc list + file contents from the API
   - Markdown editor with live preview (window.mdRender)
   - Save → confirm modal → commit endpoint (branch + PR)
   The same code runs in DEMO (local server) and LIVE
   (Cloudflare Pages Functions); it discovers which from
   GET /admin/api/whoami.
   ============================================================ */
(function () {
  "use strict";

  // ---- API base: works whether served at /admin or root ----
  var API = (function () {
    var p = location.pathname.replace(/\/+$/, "");
    // if we're under /admin, api is /admin/api; else /api
    return (/\/admin$/.test(p) || /\/admin\//.test(location.pathname)) ? "/admin/api" : "./api";
  })();

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var state = {
    mode: "demo",
    user: null,
    files: [],            // [{path, category, slug, title}]
    current: null,        // path
    original: "",         // pristine content of current
    drafts: {},           // path -> edited content (unsaved)
    collapsed: {},        // category -> bool
  };

  // ---------- boot ----------
  whoami();

  function whoami() {
    fetch(API + "/whoami", { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        state.mode = d.mode || "demo";
        paintModeBadge();
        if (d.authenticated) { state.user = d.user; showApp(); }
        else { showGate(d); }
      })
      .catch(function () {
        // No API at all → still show the gate in pure-static demo
        state.mode = "demo";
        paintModeBadge();
        showGate({ mode: "demo" });
      });
  }

  function paintModeBadge() {
    var b = $("#modeBadge");
    if (state.mode === "live") { b.textContent = "LIVE"; b.className = "badge badge--live"; }
    else { b.textContent = "DEMO"; b.className = "badge badge--demo"; }
  }

  // ---------- auth gate ----------
  function showGate(info) {
    $("#app").hidden = true;
    $("#gate").hidden = false;
    if (info && info.mode === "live") {
      $("#gateSub").innerHTML = "This area is protected by <strong>Cloudflare Access</strong>. " +
        "You should have been redirected to email sign-in.";
      $("#demoForm").hidden = true;
    }
    $("#demoForm").addEventListener("submit", function (e) {
      e.preventDefault();
      var email = $("#demoEmail").value.trim();
      var otp = $("#demoOtp").value.trim();
      if (!/^\d{6}$/.test(otp)) { toast("Enter any 6-digit code (demo).", "err"); return; }
      fetch(API + "/login", {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, otp: otp })
      }).then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.ok) { state.user = d.user; showApp(); }
          else { toast(d.error || "Sign-in failed.", "err"); }
        }).catch(function () { toast("Sign-in failed (server offline?).", "err"); });
    });
  }

  // ---------- app ----------
  function showApp() {
    $("#gate").hidden = true;
    $("#app").hidden = false;
    if (state.user) {
      var c = $("#userChip"); c.hidden = false; c.textContent = state.user;
      $("#logoutBtn").hidden = false;
    }
    wireChrome();
    loadFiles();
  }

  function wireChrome() {
    $("#logoutBtn").addEventListener("click", function () {
      fetch(API + "/logout", { method: "POST", credentials: "same-origin" })
        .finally(function () { location.reload(); });
    });
    $("#refreshBtn").addEventListener("click", loadFiles);
    $("#filter").addEventListener("input", function () { renderTree(this.value.trim().toLowerCase()); });
    $("#previewToggle").addEventListener("click", togglePreview);
    $("#saveBtn").addEventListener("click", openSaveModal);
    $("#revertBtn").addEventListener("click", revert);
    $("#md").addEventListener("input", onEdit);

    // modal
    $$("[data-close]").forEach(function (el) { el.addEventListener("click", closeModal); });
    $("#confirmSave").addEventListener("click", doSave);

    // shortcuts
    document.addEventListener("keydown", function (e) {
      var meta = e.metaKey || e.ctrlKey;
      if (meta && e.key.toLowerCase() === "k") { e.preventDefault(); $("#filter").focus(); $("#filter").select(); }
      else if (meta && e.key.toLowerCase() === "s") { e.preventDefault(); if (!$("#saveBtn").disabled) openSaveModal(); }
      else if (meta && e.key.toLowerCase() === "p") { e.preventDefault(); togglePreview(); }
      else if (e.key === "Escape") { closeModal(); }
    });
  }

  // ---------- files ----------
  function loadFiles() {
    fetch(API + "/files", { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        state.files = d.files || [];
        $("#fileCount").textContent = state.files.length + " articles";
        // Collapse every category by default; the user expands on click.
        Object.keys(byCategory()).forEach(function (cat) {
          if (state.collapsed[cat] === undefined) state.collapsed[cat] = true;
        });
        renderTree("");
      })
      .catch(function () { $("#tree").innerHTML = '<div class="tree__empty">Could not load files.</div>'; });
  }

  function byCategory() {
    var map = {};
    state.files.forEach(function (f) { (map[f.category] = map[f.category] || []).push(f); });
    return map;
  }

  function renderTree(q) {
    var tree = $("#tree");
    var map = byCategory();
    var cats = Object.keys(map).sort();
    var html = "";
    var anyMatch = false;

    cats.forEach(function (cat) {
      var items = map[cat].filter(function (f) {
        if (!q) return true;
        return (f.title + " " + f.slug + " " + f.category).toLowerCase().indexOf(q) !== -1;
      });
      if (!items.length) return;
      anyMatch = true;
      var collapsed = q ? false : !!state.collapsed[cat];
      html += '<div class="tree__cat' + (collapsed ? " is-collapsed" : "") + '" data-cat="' + cat + '">';
      html += '<button class="tree__cathead" data-toggle="' + cat + '">' +
        '<span class="tree__chev">▾</span><span>' + prettyCat(cat) + '</span>' +
        '<span class="tree__count">' + items.length + '</span></button>';
      html += '<div class="tree__items">';
      items.forEach(function (f) {
        var active = f.path === state.current;
        var dirty = state.drafts[f.path] != null && state.drafts[f.path] !== undefined;
        html += '<button class="tree__item' + (active ? " is-active" : "") + (dirty ? " is-dirty" : "") +
          '" data-path="' + f.path + '" title="' + f.path + '">' +
          '<span class="dot"></span><span>' + hl(f.title, q) + '</span></button>';
      });
      html += "</div></div>";
    });

    tree.innerHTML = anyMatch ? html :
      '<div class="tree__empty">No articles match “' + escHtml(q) + '”.</div>';

    $$(".tree__cathead", tree).forEach(function (b) {
      b.addEventListener("click", function () {
        var c = b.getAttribute("data-toggle");
        state.collapsed[c] = !state.collapsed[c];
        renderTree($("#filter").value.trim().toLowerCase());
      });
    });
    $$(".tree__item", tree).forEach(function (b) {
      b.addEventListener("click", function () { openDoc(b.getAttribute("data-path")); });
    });
  }

  function prettyCat(c) {
    return c.replace(/-/g, " ").replace(/\b\w/g, function (m) { return m.toUpperCase(); });
  }
  function hl(text, q) {
    var t = escHtml(text);
    if (!q) return t;
    var idx = text.toLowerCase().indexOf(q);
    if (idx === -1) return t;
    var e = escHtml(text.slice(0, idx)) + '<mark class="hl">' +
      escHtml(text.slice(idx, idx + q.length)) + "</mark>" + escHtml(text.slice(idx + q.length));
    return e;
  }
  function escHtml(s) { return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  // ---------- doc open / edit ----------
  function openDoc(path) {
    fetch(API + "/file?path=" + encodeURIComponent(path), { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.error) { toast(d.error, "err"); return; }
        state.current = path;
        state.original = d.content;
        var f = state.files.filter(function (x) { return x.path === path; })[0] || {};
        $("#crumbCat").textContent = prettyCat(f.category || "");
        $("#crumbSlug").textContent = f.title || f.slug || path;
        $("#docPath").textContent = path;
        var content = state.drafts[path] != null ? state.drafts[path] : d.content;
        $("#md").value = content;
        $("#emptyState").hidden = true;
        $("#docView").hidden = false;
        updateDirty();
        renderPreview();
        renderTree($("#filter").value.trim().toLowerCase());
      })
      .catch(function () { toast("Could not open file.", "err"); });
  }

  function onEdit() {
    if (!state.current) return;
    var v = $("#md").value;
    if (v === state.original) delete state.drafts[state.current];
    else state.drafts[state.current] = v;
    updateDirty();
    renderPreview();
    // update dirty dot in tree without full re-render churn
    var item = $('.tree__item[data-path="' + cssEsc(state.current) + '"]');
    if (item) item.classList.toggle("is-dirty", state.drafts[state.current] != null);
  }
  function cssEsc(s) { return s.replace(/(["\\])/g, "\\$1"); }

  function updateDirty() {
    var dirty = state.drafts[state.current] != null;
    $("#dirtyDot").hidden = !dirty;
    $("#saveBtn").disabled = !dirty;
    $("#revertBtn").disabled = !dirty;
  }

  function revert() {
    if (!state.current) return;
    delete state.drafts[state.current];
    $("#md").value = state.original;
    updateDirty();
    renderPreview();
    renderTree($("#filter").value.trim().toLowerCase());
    toast("Reverted to the saved version.", "ok");
  }

  var previewOn = true;
  function togglePreview() {
    previewOn = !previewOn;
    $("#panes").classList.toggle("no-preview", !previewOn);
    $("#previewToggle").setAttribute("aria-pressed", String(previewOn));
    $("#previewToggle").textContent = previewOn ? "Preview" : "Editor only";
  }
  function renderPreview() {
    if (!previewOn) return;
    var src = $("#md").value;
    $("#preview").innerHTML = window.mdRender ? window.mdRender(src) : escHtml(src);
  }

  // ---------- save / PR ----------
  function openSaveModal() {
    if (!state.current || state.drafts[state.current] == null) return;
    var f = state.files.filter(function (x) { return x.path === state.current; })[0] || {};
    var branch = "edit/" + (f.slug || "article") + "-" + stamp();
    $("#planPath").textContent = state.current;
    $("#planBranch").textContent = branch;
    $("#planBase").textContent = "main";
    $("#commitMsg").value = "Edit " + (f.slug || state.current) + ": ";
    $("#modal").hidden = false;
    setTimeout(function () { $("#commitMsg").focus(); var el = $("#commitMsg"); el.selectionStart = el.selectionEnd = el.value.length; }, 30);
    $("#modal").setAttribute("data-branch", branch);
  }
  function closeModal() { $("#modal").hidden = true; }

  function doSave() {
    var path = state.current;
    var content = state.drafts[path];
    if (content == null) { closeModal(); return; }
    var branch = $("#modal").getAttribute("data-branch");
    var msg = $("#commitMsg").value.trim() || ("Edit " + path);
    var btn = $("#confirmSave");
    btn.disabled = true; btn.textContent = "Committing…";

    fetch(API + "/commit", {
      method: "POST", credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: path, content: content, message: msg, branch: branch })
    }).then(function (r) { return r.json(); })
      .then(function (d) {
        btn.disabled = false; btn.textContent = "Save & publish";
        if (d.ok) {
          // committed → it's now the saved version
          state.original = content;
          delete state.drafts[path];
          updateDirty();
          renderTree($("#filter").value.trim().toLowerCase());
          closeModal();
          var link = d.prUrl
            ? ' <a href="' + d.prUrl + '" target="_blank" rel="noopener">View PR →</a>'
            : (d.note ? ' <span class="muted">' + escHtml(d.note) + "</span>" : "");
          if (d.merged) {
            toast("Published ✓ — your change goes live in about a minute." + link, "ok", 9000);
          } else {
            toast("Saved — couldn't auto-publish, so it's a pull request awaiting a manual merge." + link, "ok", 12000);
          }
        } else {
          toast(d.error || "Commit failed.", "err", 7000);
        }
      })
      .catch(function () {
        btn.disabled = false; btn.textContent = "Save & publish";
        toast("Save failed (server offline?).", "err");
      });
  }

  function stamp() {
    var d = new Date();
    function p(n) { return String(n).padStart(2, "0"); }
    return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + "-" + p(d.getHours()) + p(d.getMinutes());
  }

  // ---------- toast ----------
  var toastTimer;
  function toast(html, kind, ms) {
    var t = $("#toast");
    t.className = "toast " + (kind === "err" ? "toast--err" : "toast--ok");
    t.innerHTML = '<span class="toast__icon">' + (kind === "err" ? "✕" : "✓") + "</span><span>" + html + "</span>";
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.hidden = true; }, ms || 4200);
  }
})();
