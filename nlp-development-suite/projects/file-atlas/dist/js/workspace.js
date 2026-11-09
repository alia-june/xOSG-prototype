export const LIMITS = {
  listEntries: 500,
  readBytes: 128 * 1024,
  searchFiles: 1000,
  searchDirectories: 200,
  searchBytes: 8 * 1024 * 1024,
  searchResults: 50,
};

const SKIP_DIRECTORIES = new Set([".git", ".venv", ".wn_data", "__pycache__"]);

export function normalizePath(raw) {
  const value = String(raw ?? "").trim().replaceAll("\\", "/");
  if (!value || value === ".") return ".";
  if (value.startsWith("/") || /^[A-Za-z]:/.test(value) || value.includes("\0")) throw new Error("Path must stay inside the selected workspace");
  const parts = value.split("/").filter((part) => part && part !== ".");
  if (!parts.length) return ".";
  if (parts.some((part) => part === ".." || part.includes(":"))) throw new Error("Parent traversal and absolute paths are not allowed");
  return parts.join("/");
}

export function joinPath(parent, child) { return parent === "." ? child : `${parent}/${child}`; }
export function parentPath(path) {
  const normalized = normalizePath(path);
  if (normalized === "." || !normalized.includes("/")) return ".";
  return normalized.slice(0, normalized.lastIndexOf("/"));
}

function sortEntries(entries) { return entries.sort((a, b) => a.name.localeCompare(b.name, undefined, {sensitivity: "base"}) || a.name.localeCompare(b.name)); }

export class DemoWorkspace {
  constructor() {
    this.rootName = "Demo workspace";
    this.mode = "demo";
    this.files = new Map([
      ["README.md", new TextEncoder().encode("# Demo workspace\n\nThis read-only workspace demonstrates deterministic file commands.\n\nTry searching for candidate or listing the notes directory.\n")],
      ["notes/design.md", new TextEncoder().encode("# File interface design\n\nParsing creates a candidate intent before any read adapter runs.\nCollisions remain visible and require an explicit phrase.\n")],
      ["notes/candidates.txt", new TextEncoder().encode("candidate: list_files\ncandidate: read_file\nstatus: proposal only\n")],
      ["src/parser.js", new TextEncoder().encode("export function parseCommand(source) {\n  // Deterministic alias parsing lives here.\n  return { source, status: 'candidate' };\n}\n")],
      ["src/catalog.json", new TextEncoder().encode('{"schema":"demo","capabilities":["list_files","read_file","find_files","search_text"]}\n')],
      ["data/sample.bin", new Uint8Array([0, 1, 2, 3, 255, 17])],
    ]);
    this.directories = new Set(["."]);
    for (const path of this.files.keys()) {
      const parts = path.split("/");
      for (let index = 1; index < parts.length; index += 1) this.directories.add(parts.slice(0, index).join("/"));
    }
  }
  async kindAt(rawPath) {
    const path = normalizePath(rawPath);
    if (this.files.has(path)) return "file";
    if (this.directories.has(path)) return "directory";
    return null;
  }
  async list(rawPath, enforceLimit = true) {
    const path = normalizePath(rawPath);
    if (!this.directories.has(path)) throw new Error("List target is not a directory");
    const prefix = path === "." ? "" : `${path}/`;
    const found = new Map();
    for (const directory of this.directories) {
      if (directory === "." || !directory.startsWith(prefix)) continue;
      const remainder = directory.slice(prefix.length);
      if (remainder && !remainder.includes("/")) found.set(remainder, "directory");
    }
    for (const file of this.files.keys()) {
      if (!file.startsWith(prefix)) continue;
      const remainder = file.slice(prefix.length);
      if (remainder && !remainder.includes("/")) found.set(remainder, "file");
    }
    const entries = sortEntries([...found].map(([name, kind]) => ({name, kind})));
    if (enforceLimit && entries.length > LIMITS.listEntries) throw new Error(`Directory exceeds the ${LIMITS.listEntries}-entry listing bound`);
    return entries;
  }
  async readBytes(rawPath) {
    const path = normalizePath(rawPath);
    if (!this.files.has(path)) throw new Error("Read target is not a regular file");
    return this.files.get(path);
  }
  async fileSize(rawPath) {
    const path = normalizePath(rawPath);
    if (!this.files.has(path)) throw new Error("Read target is not a regular file");
    return this.files.get(path).length;
  }
}

export class HandleWorkspace {
  constructor(rootHandle) { this.root = rootHandle; this.rootName = rootHandle.name; this.mode = "folder"; }
  async handleAt(rawPath) {
    const path = normalizePath(rawPath);
    if (path === ".") return this.root;
    const parts = path.split("/");
    let current = this.root;
    for (let index = 0; index < parts.length; index += 1) {
      if (current.kind !== "directory") throw new Error("Path crosses a file");
      const name = parts[index], last = index === parts.length - 1;
      if (!last) current = await current.getDirectoryHandle(name);
      else {
        try { current = await current.getDirectoryHandle(name); }
        catch { current = await current.getFileHandle(name); }
      }
    }
    return current;
  }
  async kindAt(path) {
    try { return (await this.handleAt(path)).kind; }
    catch { return null; }
  }
  async list(path, enforceLimit = true) {
    const handle = await this.handleAt(path);
    if (handle.kind !== "directory") throw new Error("List target is not a directory");
    const entries = [];
    for await (const [name, child] of handle.entries()) {
      entries.push({name, kind: child.kind});
      if (enforceLimit && entries.length > LIMITS.listEntries) throw new Error(`Directory exceeds the ${LIMITS.listEntries}-entry listing bound`);
    }
    return sortEntries(entries);
  }
  async readBytes(path) {
    const handle = await this.handleAt(path);
    if (handle.kind !== "file") throw new Error("Read target is not a regular file");
    const file = await handle.getFile();
    return new Uint8Array(await file.arrayBuffer());
  }
  async fileSize(path) {
    const handle = await this.handleAt(path);
    if (handle.kind !== "file") throw new Error("Read target is not a regular file");
    return (await handle.getFile()).size;
  }
}

export class FileListWorkspace {
  constructor(files) {
    const firstPath = files[0]?.webkitRelativePath || files[0]?.name || "Selected files";
    const rootPart = firstPath.includes("/") ? firstPath.split("/")[0] : "Selected files";
    this.rootName = rootPart;
    this.mode = "folder-fallback";
    this.files = new Map();
    this.directories = new Set(["."]);
    for (const file of files) {
      const supplied = file.webkitRelativePath || file.name;
      const path = normalizePath(supplied.startsWith(`${rootPart}/`) ? supplied.slice(rootPart.length + 1) : supplied);
      this.files.set(path, file);
      const parts = path.split("/");
      for (let index = 1; index < parts.length; index += 1) this.directories.add(parts.slice(0, index).join("/"));
    }
  }
  async kindAt(rawPath) {
    const path = normalizePath(rawPath);
    if (this.files.has(path)) return "file";
    if (this.directories.has(path)) return "directory";
    return null;
  }
  async list(rawPath, enforceLimit = true) {
    const path = normalizePath(rawPath);
    if (!this.directories.has(path)) throw new Error("List target is not a directory");
    const prefix = path === "." ? "" : `${path}/`;
    const found = new Map();
    for (const directory of this.directories) {
      if (directory === "." || !directory.startsWith(prefix)) continue;
      const remainder = directory.slice(prefix.length);
      if (remainder && !remainder.includes("/")) found.set(remainder, "directory");
    }
    for (const file of this.files.keys()) {
      if (!file.startsWith(prefix)) continue;
      const remainder = file.slice(prefix.length);
      if (remainder && !remainder.includes("/")) found.set(remainder, "file");
    }
    const entries = sortEntries([...found].map(([name, kind]) => ({name, kind})));
    if (enforceLimit && entries.length > LIMITS.listEntries) throw new Error(`Directory exceeds the ${LIMITS.listEntries}-entry listing bound`);
    return entries;
  }
  async readBytes(rawPath) {
    const path = normalizePath(rawPath);
    const file = this.files.get(path);
    if (!file) throw new Error("Read target is not a regular file");
    return new Uint8Array(await file.arrayBuffer());
  }
  async fileSize(rawPath) {
    const path = normalizePath(rawPath);
    const file = this.files.get(path);
    if (!file) throw new Error("Read target is not a regular file");
    return file.size;
  }
}

export function decodeText(bytes) {
  if (bytes.length > LIMITS.readBytes) throw new Error(`File exceeds the ${LIMITS.readBytes}-byte read bound`);
  if (bytes.includes(0)) throw new Error("File is binary because it contains a NUL byte");
  try { return new TextDecoder("utf-8", {fatal: true}).decode(bytes); }
  catch { throw new Error("File is not valid UTF-8 text"); }
}

export async function sha256Bytes(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function walkWorkspace(workspace, rawPath, onFile) {
  const start = normalizePath(rawPath);
  const kind = await workspace.kindAt(start);
  if (!kind) throw new Error("Search target does not exist in the workspace");
  const stats = {files: 0, directories: 0, skippedDirectories: 0, truncated: false};
  if (kind === "file") {
    stats.files = 1;
    await onFile(start);
    return stats;
  }
  const queue = [start];
  while (queue.length && !stats.truncated) {
    const directory = queue.shift();
    if (stats.directories >= LIMITS.searchDirectories) { stats.truncated = true; break; }
    stats.directories += 1;
    const entries = await workspace.list(directory, false);
    for (const entry of entries) {
      const path = joinPath(directory, entry.name);
      if (entry.kind === "directory") {
        if (SKIP_DIRECTORIES.has(entry.name)) stats.skippedDirectories += 1;
        else queue.push(path);
      } else if (entry.kind === "file") {
        if (stats.files >= LIMITS.searchFiles) { stats.truncated = true; break; }
        stats.files += 1;
        const shouldContinue = await onFile(path);
        if (shouldContinue === false) { stats.truncated = true; break; }
      }
    }
  }
  return stats;
}
