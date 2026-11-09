import {CAPABILITIES, explicitChoice, parseCommand, recordChoice} from "./parser.js";
import {DemoWorkspace, FileListWorkspace, HandleWorkspace, LIMITS, decodeText, joinPath, normalizePath, parentPath, sha256Bytes, walkWorkspace} from "./workspace.js";

const state = {
  rules: [],
  manifest: null,
  workspace: null,
  currentPath: ".",
  currentIntent: null,
  history: [],
  choices: new Map(),
};

const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
const capabilityLabel = (name) => name.replaceAll("_", " ");

async function initialize() {
  try {
    const [catalog, manifest] = await Promise.all([
      fetch("./data/command_aliases.json").then(checkJson),
      fetch("./data/manifest.json").then(checkJson),
    ]);
    state.rules = catalog.rules;
    state.manifest = manifest;
    const activeRules = state.rules.filter((rule) => CAPABILITIES[rule.capability]).length;
    $("schema-chip").textContent = `${manifest.intent_schema} · ${activeRules} file rules`;
    $("catalog-status").textContent = `${manifest.alias_catalog_version} · ${activeRules} active file rules · ${manifest.rules_sha256.slice(0, 12)}…`;
    await useWorkspace(new DemoWorkspace());
  } catch (error) {
    showResultError(`The interface data could not be loaded. ${error.message}`);
    $("parse-button").disabled = true;
  }
}

async function checkJson(response) {
  if (!response.ok) throw new Error(`Could not load ${response.url}`);
  return response.json();
}

async function useWorkspace(workspace) {
  state.workspace = workspace;
  state.currentPath = ".";
  $("root-name").textContent = workspace.rootName;
  $("workspace-label").textContent = workspace.mode === "demo" ? "Demo workspace · browser memory" : `${workspace.rootName} · local browser access`;
  $("workspace-state").classList.add("connected");
  await renderDirectory(".");
  resetResult();
}

async function renderDirectory(rawPath) {
  const path = normalizePath(rawPath);
  const entries = await state.workspace.list(path);
  if (entries.length > LIMITS.listEntries) throw new Error(`Directory exceeds the ${LIMITS.listEntries}-entry listing bound`);
  state.currentPath = path;
  $("current-path").textContent = path;
  const parent = path === "." ? "" : `<button class="file-row parent-row" type="button" data-path="${escapeHtml(parentPath(path))}" data-kind="directory"><span aria-hidden="true">↰</span><span class="file-name">Parent directory</span><span class="file-kind">up</span></button>`;
  $("file-list").innerHTML = parent + (entries.length ? entries.map((entry) => {
    const fullPath = joinPath(path, entry.name);
    return `<button class="file-row" type="button" data-path="${escapeHtml(fullPath)}" data-kind="${escapeHtml(entry.kind)}"><span class="file-icon ${escapeHtml(entry.kind)}" aria-hidden="true"></span><span class="file-name">${escapeHtml(entry.name)}</span><span class="file-kind">${escapeHtml(entry.kind)}</span></button>`;
  }).join("") : '<p class="muted-copy">This directory is empty.</p>');
}

async function parseCurrent() {
  const source = $("command-input").value;
  $("parse-button").disabled = true;
  $("parse-button").textContent = "Parsing…";
  try {
    state.currentIntent = await parseCommand(
      source,
      state.rules,
      state.manifest,
      async (path) => state.workspace ? state.workspace.kindAt(path) : null,
      state.choices,
    );
    addHistory(source, state.currentIntent.status);
    renderIntent(state.currentIntent);
    resetResult();
  } catch (error) {
    showResultError(error.message);
  } finally {
    $("parse-button").disabled = false;
    $("parse-button").textContent = "Parse command";
  }
}

function renderIntent(intent) {
  const status = intent.status;
  const trace = `<details class="trace"><summary>Layer trace and provenance</summary><ol>${intent.layer_trace.map((item) => `<li><strong>${escapeHtml(item.layer)}</strong> · ${escapeHtml(item.status)}</li>`).join("")}<li><strong>rules</strong> · ${escapeHtml(intent.alias_rules_sha256.slice(0, 16))}…</li><li><strong>source</strong> · ${escapeHtml(intent.source_sha256.slice(0, 16))}…</li></ol></details>`;
  const header = `<div class="intent-head"><span class="status-label ${escapeHtml(status)}">${escapeHtml(status)}</span><span class="intent-source">${escapeHtml(intent.schema_version)}</span></div>`;
  if (status === "parsed") {
    const details = CAPABILITIES[intent.capability];
    $("intent-card").innerHTML = `${header}<div class="intent-summary"><strong>${escapeHtml(capabilityLabel(intent.capability))}</strong><p class="intent-note">${escapeHtml(details.description)}</p><div class="argument-list">${Object.entries(intent.arguments).map(([key, value]) => `<span class="argument">${escapeHtml(key)} = ${escapeHtml(value)}</span>`).join("") || '<span class="argument">no arguments</span>'}</div><div class="run-row"><span>Parsed grammar only · registered read-only adapter</span><button class="primary-button" id="run-intent" type="button">Run read-only operation</button></div></div>${trace}`;
    $("run-intent").addEventListener("click", executeCurrentIntent);
    return;
  }
  if (status === "collision") {
    $("intent-card").innerHTML = `${header}<p class="intent-note">${escapeHtml(intent.reason)} Every meaning stays visible. Choosing one rewrites the input as an explicit command and does not run it.</p><div class="candidate-list">${intent.candidates.map((candidate, index) => renderCandidate(candidate, index)).join("")}</div>${trace}`;
    $("intent-card").querySelectorAll("[data-choice]").forEach((button) => button.addEventListener("click", async () => {
      const candidate = intent.candidates[Number(button.dataset.choice)];
      const command = explicitChoice(candidate);
      if (!command) return;
      recordChoice(state.choices, intent.source_text, candidate);
      $("command-input").value = command;
      updateCount();
      await parseCurrent();
    }));
    return;
  }
  $("intent-card").innerHTML = `${header}<div class="error-card"><strong>No file command was selected.</strong><br>${escapeHtml(intent.reason)}</div>${trace}`;
}

function renderCandidate(candidate, index) {
  const details = CAPABILITIES[candidate.capability];
  const command = explicitChoice(candidate);
  return `<article class="candidate-card"><div class="candidate-top"><strong>${escapeHtml(capabilityLabel(candidate.capability))}</strong><span class="candidate-score">rank ${candidate.score}</span></div><p>${escapeHtml(details.description)}</p><div class="argument-list">${Object.entries(candidate.arguments).map(([key, value]) => `<span class="argument">${escapeHtml(key)} = ${escapeHtml(value)}</span>`).join("")}</div><div class="evidence-list">${candidate.evidence.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div>${command ? `<button class="choice-button" data-choice="${index}" type="button">Use: ${escapeHtml(command)}</button>` : ""}</article>`;
}

async function executeCurrentIntent() {
  const intent = state.currentIntent;
  if (!intent || intent.status !== "parsed") return;
  setResultStatus("Reading…", "");
  $("result-body").innerHTML = '<div class="empty-result"><span class="loader">•••</span><strong>Applying the bounded adapter</strong></div>';
  try {
    let result;
    switch (intent.capability) {
      case "help": result = {type: "help", capabilities: CAPABILITIES}; break;
      case "workspace": result = {type: "workspace", root: state.workspace.rootName, mode: state.workspace.mode}; break;
      case "list_files": result = await executeList(intent.arguments.path); break;
      case "read_file": result = await executeRead(intent.arguments.path); break;
      case "find_files": result = await executeFind(intent.arguments.path, intent.arguments.name); break;
      case "search_text": result = await executeSearch(intent.arguments.path, intent.arguments.term); break;
      default: throw new Error("Capability is not registered in this browser front end");
    }
    renderResult(result);
    setResultStatus("Completed", "completed");
  } catch (error) {
    showResultError(error.message);
  }
}

async function executeList(path) {
  const normalized = normalizePath(path);
  const entries = await state.workspace.list(normalized);
  if (entries.length > LIMITS.listEntries) throw new Error(`Directory exceeds the ${LIMITS.listEntries}-entry listing bound`);
  return {type: "list", path: normalized, entries, count: entries.length};
}

async function executeRead(path) {
  const normalized = normalizePath(path);
  const size = await state.workspace.fileSize(normalized);
  if (size > LIMITS.readBytes) throw new Error(`File exceeds the ${LIMITS.readBytes}-byte read bound`);
  const bytes = await state.workspace.readBytes(normalized);
  const text = decodeText(bytes);
  return {type: "read", path: normalized, bytes: bytes.length, sha256: await sha256Bytes(bytes), text};
}

async function executeFind(path, name) {
  const normalized = normalizePath(path);
  const needle = name.toLocaleLowerCase();
  const matches = [];
  const stats = await walkWorkspace(state.workspace, normalized, async (filePath) => {
    if (filePath.split("/").at(-1).toLocaleLowerCase().includes(needle)) matches.push(filePath);
    return matches.length < LIMITS.searchResults;
  });
  return {type: "find", path: normalized, name, matches, stats};
}

async function executeSearch(path, term) {
  const normalized = normalizePath(path);
  const needle = term.toLocaleLowerCase();
  const matches = [];
  let bytesExamined = 0, skippedBinary = 0, skippedLarge = 0;
  const stats = await walkWorkspace(state.workspace, normalized, async (filePath) => {
    const size = await state.workspace.fileSize(filePath);
    if (size > LIMITS.readBytes) { skippedLarge += 1; return true; }
    if (bytesExamined + size > LIMITS.searchBytes) return false;
    const bytes = await state.workspace.readBytes(filePath);
    bytesExamined += bytes.length;
    let text;
    try { text = decodeText(bytes); }
    catch { skippedBinary += 1; return true; }
    for (const [index, line] of text.split(/\r?\n/).entries()) {
      if (line.toLocaleLowerCase().includes(needle)) matches.push({path: filePath, line: index + 1, text: line.slice(0, 300)});
      if (matches.length >= LIMITS.searchResults) return false;
    }
    return true;
  });
  return {type: "search", path: normalized, term, matches, stats, bytesExamined, skippedBinary, skippedLarge};
}

function renderResult(result) {
  if (result.type === "workspace") {
    $("result-body").innerHTML = `<div class="result-meta"><span>workspace</span><span>${escapeHtml(result.mode)}</span></div><div class="intent-summary"><strong>${escapeHtml(result.root)}</strong><p class="intent-note">Browser-selected root. Commands cannot navigate above it.</p></div>`;
  } else if (result.type === "help") {
    $("result-body").innerHTML = `<div class="result-list">${Object.entries(result.capabilities).map(([name, item]) => `<div class="result-row"><div><strong>${escapeHtml(capabilityLabel(name))}</strong><p class="intent-note">${escapeHtml(item.description)} · ${escapeHtml(item.example)}</p></div><span>read only</span></div>`).join("")}</div>`;
  } else if (result.type === "list") {
    $("result-body").innerHTML = `<div class="result-meta"><span>${escapeHtml(result.path)}</span><span>${result.count} entries</span></div><div class="result-list">${result.entries.map((entry) => `<div class="result-row"><strong>${escapeHtml(entry.name)}</strong><span>${escapeHtml(entry.kind)}</span></div>`).join("") || '<p class="muted-copy">Directory is empty.</p>'}</div>`;
  } else if (result.type === "read") {
    $("result-body").innerHTML = `<div class="result-meta"><span>${escapeHtml(result.path)}</span><span>${result.bytes.toLocaleString()} bytes</span><span>sha256 ${escapeHtml(result.sha256.slice(0, 14))}…</span></div><pre class="file-preview">${escapeHtml(result.text)}</pre>`;
  } else if (result.type === "find") {
    $("result-body").innerHTML = `${scanMeta(result, `${result.matches.length} names`)}<div class="result-list">${result.matches.map((path) => `<div class="result-row"><strong>${escapeHtml(path)}</strong><span>file</span></div>`).join("") || '<p class="muted-copy">No matching file names.</p>'}</div>${boundedNote(result.stats)}`;
  } else if (result.type === "search") {
    $("result-body").innerHTML = `${scanMeta(result, `${result.matches.length} lines`)}<div class="result-list">${result.matches.map((match) => `<div class="result-row match-row"><strong>${escapeHtml(match.path)}</strong><span>line ${match.line}</span><code>${escapeHtml(match.text)}</code></div>`).join("") || '<p class="muted-copy">No matching text.</p>'}</div>${boundedNote(result.stats)}${result.skippedBinary || result.skippedLarge ? `<p class="bounded-note">Skipped ${result.skippedBinary} binary/non-UTF-8 and ${result.skippedLarge} oversized files.</p>` : ""}`;
  }
}

function scanMeta(result, resultCount) {
  return `<div class="result-meta"><span>${escapeHtml(result.path)}</span><span>${escapeHtml(resultCount)}</span><span>${result.stats.files} files examined</span><span>${result.stats.directories} directories</span>${result.bytesExamined !== undefined ? `<span>${result.bytesExamined.toLocaleString()} bytes</span>` : ""}</div>`;
}
function boundedNote(stats) { return stats.truncated ? '<p class="bounded-note">The result is explicitly truncated at a configured traversal or result bound.</p>' : ""; }

function resetResult() {
  setResultStatus("Not run", "");
  $("result-body").innerHTML = '<div class="empty-result"><span>02</span><strong>Waiting for a parsed command</strong><p>Only a single registered read-only meaning can reach this panel.</p></div>';
}
function showResultError(message) {
  setResultStatus("Rejected", "rejected");
  $("result-body").innerHTML = `<div class="error-card"><strong>The read-only operation was rejected.</strong><br>${escapeHtml(message)}</div>`;
}
function setResultStatus(text, className) { $("result-status").textContent = text; $("result-status").className = `result-status ${className}`.trim(); }

function addHistory(source, status) {
  if (!source.trim()) return;
  state.history.unshift({source, status});
  state.history = state.history.slice(0, 10);
  renderHistory();
}
function renderHistory() {
  $("history-list").innerHTML = state.history.length ? state.history.map((item, index) => `<button class="history-item" type="button" data-history="${index}" title="${escapeHtml(item.status)}">${escapeHtml(item.source)}</button>`).join("") : '<p class="muted-copy">Commands stay in this browser session.</p>';
}
function updateCount() { $("command-count").textContent = `${$("command-input").value.length} / 1024`; }

$("command-form").addEventListener("submit", async (event) => { event.preventDefault(); await parseCurrent(); });
$("command-input").addEventListener("input", updateCount);
$("file-list").addEventListener("click", async (event) => {
  const row = event.target.closest("[data-path]");
  if (!row) return;
  if (row.dataset.kind === "directory") {
    try { await renderDirectory(row.dataset.path); }
    catch (error) { showResultError(error.message); }
  } else {
    $("command-input").value = `read file "${row.dataset.path.replaceAll('"', "")}"`;
    updateCount();
    await parseCurrent();
  }
});
$("history-list").addEventListener("click", (event) => {
  const item = event.target.closest("[data-history]");
  if (!item) return;
  $("command-input").value = state.history[Number(item.dataset.history)].source;
  updateCount();
  $("command-input").focus();
});
$("clear-history").addEventListener("click", () => { state.history = []; state.choices.clear(); renderHistory(); });
document.querySelectorAll("[data-command]").forEach((button) => button.addEventListener("click", () => { $("command-input").value = button.dataset.command; updateCount(); $("command-input").focus(); }));
$("demo-button").addEventListener("click", async () => { await useWorkspace(new DemoWorkspace()); });
$("folder-button").addEventListener("click", async () => {
  if ("showDirectoryPicker" in window) {
    try { await useWorkspace(new HandleWorkspace(await window.showDirectoryPicker({mode: "read"}))); }
    catch (error) { if (error.name !== "AbortError") showResultError(`Folder access was not opened. ${error.message}`); }
  } else $("folder-input").click();
});
$("folder-input").addEventListener("change", async (event) => {
  const files = [...event.target.files];
  if (files.length) await useWorkspace(new FileListWorkspace(files));
  event.target.value = "";
});
$("about-button").addEventListener("click", () => $("about-dialog").showModal());
$("about-close").addEventListener("click", () => $("about-dialog").close());

initialize();
