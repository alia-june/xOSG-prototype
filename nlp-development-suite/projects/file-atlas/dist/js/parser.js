export const CAPABILITIES = {
  help: {description: "Show registered commands", arguments: [], example: "help"},
  workspace: {description: "Show the selected workspace", arguments: [], example: "where am I"},
  list_files: {description: "List one directory", arguments: ["path"], example: "list files in notes"},
  read_file: {description: "Read a bounded UTF-8 file", arguments: ["path"], example: "show file README.md"},
  find_files: {description: "Find file names containing text", arguments: ["path", "name"], example: "find files named parser in src"},
  search_text: {description: "Find literal text within files", arguments: ["path", "term"], example: "search for candidate in notes"},
};

const MAX_COMMAND_CHARS = 1024;

function operand(raw) {
  const value = raw.trim();
  if (!value || /[\0\n\r]/.test(value)) return null;
  if (value[0] === "'" || value[0] === '"') {
    if (value.length < 2 || value.at(-1) !== value[0] || value.slice(1, -1).includes(value[0])) return null;
    return value.slice(1, -1) || null;
  }
  if (value.includes('"')) return null;
  return value;
}

function splitUnquotedIn(raw) {
  let quote = null;
  for (let index = 0; index < raw.length; index += 1) {
    const character = raw[index];
    if (character === "'" || character === '"') quote = quote === null ? character : quote === character ? null : quote;
    else if (quote === null && raw.slice(index, index + 4).toLocaleLowerCase() === " in ") return [raw.slice(0, index), raw.slice(index + 4)];
  }
  return null;
}

async function matchRule(rule, command, pathKind) {
  if (!CAPABILITIES[rule.capability]) return null;
  const folded = command.toLocaleLowerCase();
  const prefix = rule.phrase.toLocaleLowerCase();
  if (rule.mode === "exact") {
    if (folded !== prefix) return null;
    return {capability: rule.capability, arguments: {...rule.arguments}, score: rule.score, rule_id: rule.id, evidence: ["exact_alias", `phrase:${rule.phrase}`]};
  }
  if (!folded.startsWith(`${prefix} `)) return null;
  const raw = command.slice(rule.phrase.length + 1);
  const rawFolded = raw.toLocaleLowerCase();
  if (rule.mode === "generic_path" && (
    ["file", "files", "current directory", "relations for"].includes(rawFolded) ||
    ["file ", "files ", "current directory ", "relations for "].some((item) => rawFolded.startsWith(item)))) return null;
  if (rule.id === "read_plain" && (rawFolded === "file" || rawFolded.startsWith("file "))) return null;
  if (rule.id.startsWith("generic_find_") && (
    ["files named", "text"].includes(rawFolded) || ["files named ", "text "].some((item) => rawFolded.startsWith(item)))) return null;
  if (rule.mode === "path" || rule.mode === "generic_path") {
    const path = operand(raw);
    if (path === null) return null;
    const evidence = ["path_operand", `phrase:${rule.phrase}`];
    let score = rule.score;
    if (rule.mode === "generic_path") {
      if ((path.endsWith("/") || path.endsWith("\\")) && rule.capability === "list_files") {
        score += 15;
        evidence.push("directory_separator");
      } else if (/\.[^/\\.]+$/.test(path) && rule.capability === "read_file") {
        score += 15;
        evidence.push("file_extension");
      }
      const kind = await pathKind(path);
      if (kind === "file" || kind === "directory") {
        const expected = rule.capability === "read_file" ? "file" : "directory";
        score += kind === expected ? 25 : -20;
        evidence.push(kind === expected ? `path_is_${kind}` : `path_is_${kind}_conflict`);
      }
    }
    return {capability: rule.capability, arguments: {path}, score, rule_id: rule.id, evidence};
  }
  if (rule.mode === "term") {
    if (rawFolded.endsWith(" in")) return null;
    const split = splitUnquotedIn(raw);
    const [termRaw, pathRaw] = split || [raw, "."];
    const term = operand(termRaw), path = operand(pathRaw);
    if (term === null || path === null) return null;
    const key = rule.capability === "find_files" ? "name" : "term";
    return {
      capability: rule.capability,
      arguments: {[key]: term, path},
      score: rule.score,
      rule_id: rule.id,
      evidence: ["term_operand", split ? "explicit_path" : "default_path", `phrase:${rule.phrase}`],
    };
  }
  return null;
}

function candidateKey(candidate) {
  return `${candidate.capability}|${Object.entries(candidate.arguments).sort(([a], [b]) => a.localeCompare(b)).map(([key, value]) => `${key}=${value}`).join("|")}`;
}

function historyKey(source) { return source.toLocaleLowerCase().trim().replace(/\s+/g, " "); }

async function sha256Text(value) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function parseCommand(source, rules, manifest, pathKind, choices = new Map()) {
  const command = source.trim();
  const base = {
    schema_version: "omni-intent/0.4-browser",
    source_text: source,
    source_sha256: await sha256Text(source),
    alias_catalog_version: manifest.alias_catalog_version,
    alias_rules_sha256: manifest.rules_sha256,
    capability: null,
    arguments: {},
    candidates: [],
    side_effect_class: null,
  };
  if (!command || command.length > MAX_COMMAND_CHARS || /[\n\r]/.test(command)) {
    return {...base, status: "unparsed", reason: "Command is empty, multiline, or over the length bound.", layer_trace: [{layer: "aliases", status: "unparsed"}]};
  }

  const best = new Map();
  for (const rule of rules) {
    const candidate = await matchRule(rule, command, pathKind);
    if (!candidate) continue;
    const key = candidateKey(candidate);
    const prior = best.get(key);
    if (!prior || candidate.score > prior.score || (candidate.score === prior.score && candidate.rule_id > prior.rule_id)) best.set(key, candidate);
  }
  let candidates = [...best.values()].sort((a, b) => b.score - a.score || a.capability.localeCompare(b.capability) || a.rule_id.localeCompare(b.rule_id));
  if (candidates.length === 1) {
    const winner = candidates[0];
    return {...base, status: "parsed", capability: winner.capability, arguments: winner.arguments, reason: null, candidates, side_effect_class: "read_only", layer_trace: [{layer: "aliases", status: "parsed"}]};
  }
  if (candidates.length > 1) {
    const previous = choices.get(historyKey(source));
    if (previous) {
      candidates = candidates.map((candidate) => candidateKey(candidate) === previous
        ? {...candidate, score: candidate.score + 20, evidence: [...candidate.evidence, "session_history_choice"]}
        : candidate).sort((a, b) => b.score - a.score || a.capability.localeCompare(b.capability));
    }
    return {
      ...base,
      status: "collision",
      reason: "Multiple distinct meanings matched; choose an explicit phrase.",
      candidates,
      layer_trace: [{layer: "aliases", status: "collision"}, {layer: "history", status: previous ? "ranked" : "no_choice"}],
    };
  }

  const previous = choices.get(historyKey(source));
  const trace = [
    {layer: "aliases", status: "unparsed"},
    {layer: "wordnet", status: "not_bundled"},
    {layer: "history", status: previous ? "suggestion_recorded" : "no_choice"},
    {layer: "web", status: "not_configured"},
    {layer: "llm", status: "disabled"},
  ];
  return {...base, status: "unparsed", reason: "No registered file alias matched the complete input.", candidates: [], layer_trace: trace};
}

function quoted(value) {
  if (!value.includes('"')) return `"${value}"`;
  if (!value.includes("'")) return `'${value}'`;
  return null;
}

export function explicitChoice(candidate) {
  const args = candidate.arguments;
  if (candidate.capability === "help") return "help";
  if (candidate.capability === "workspace") return "where am I";
  const path = quoted(args.path || ".");
  if (!path) return null;
  if (candidate.capability === "read_file") return `read file ${path}`;
  if (candidate.capability === "list_files") return `list files in ${path}`;
  if (candidate.capability === "find_files") {
    const name = quoted(args.name);
    return name ? `find files named ${name} in ${path}` : null;
  }
  if (candidate.capability === "search_text") {
    const term = quoted(args.term);
    return term ? `search for ${term} in ${path}` : null;
  }
  return null;
}

export function recordChoice(choices, original, candidate) {
  if (choices.size >= 100 && !choices.has(historyKey(original))) choices.delete(choices.keys().next().value);
  choices.set(historyKey(original), candidateKey(candidate));
}
