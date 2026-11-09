import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {parseCommand, recordChoice} from "./dist/js/parser.js";
import {DemoWorkspace, decodeText, normalizePath, walkWorkspace} from "./dist/js/workspace.js";

const catalog = JSON.parse(await readFile(new URL("./dist/data/command_aliases.json", import.meta.url), "utf8"));
const manifest = JSON.parse(await readFile(new URL("./dist/data/manifest.json", import.meta.url), "utf8"));
const workspace = new DemoWorkspace();
const choices = new Map();
const parse = (source) => parseCommand(source, catalog.rules, manifest, (path) => workspace.kindAt(path), choices);

const listed = await parse("list files");
assert.equal(listed.status, "parsed");
assert.equal(listed.capability, "list_files");

const searched = await parse('search for "candidate" in notes');
assert.equal(searched.status, "parsed");
assert.deepEqual(searched.arguments, {term: "candidate", path: "notes"});

const collision = await parse("find notes in .");
assert.equal(collision.status, "collision");
assert.deepEqual(collision.candidates.map((item) => item.capability).sort(), ["find_files", "search_text"]);
recordChoice(choices, collision.source_text, collision.candidates.find((item) => item.capability === "search_text"));
const reranked = await parse("find notes in .");
assert.equal(reranked.status, "collision");
assert.equal(reranked.candidates[0].capability, "search_text");
assert.ok(reranked.candidates[0].evidence.includes("session_history_choice"));

const unsupported = await parse("delete everything");
assert.equal(unsupported.status, "unparsed");
assert.equal(unsupported.layer_trace.at(-1).layer, "llm");

assert.throws(() => normalizePath("../outside"));
assert.equal(decodeText(await workspace.readBytes("README.md")).includes("read-only workspace"), true);
let walked = 0;
const stats = await walkWorkspace(workspace, ".", async () => { walked += 1; return true; });
assert.equal(walked, 6);
assert.equal(stats.truncated, false);

console.log(JSON.stringify({checks: 12, status: "passed", rules: manifest.active_file_rule_count}));
