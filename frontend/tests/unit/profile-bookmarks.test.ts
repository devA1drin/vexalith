/**
 * Unit tests for the helpers behind Profile and Bookmarks.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { gridCells, initials, seedOf } from "../../src/lib/avatar";
import { ANSWER_PLACEHOLDER, changedFields, pickLanguage } from "../../src/lib/prefs";
import { bookmarkHref, bookmarkQuery, readBookmarkFilters } from "../../src/lib/bookmarkFilters";

const ALL = ["python", "javascript", "php", "cpp", "java", "html", "css", "general"];

test("initials take the first and last word", () => {
  assert.equal(initials("Ada Lovelace"), "AL");
  assert.equal(initials("maria niña de la cruz"), "MC");
  assert.equal(initials("Ñora"), "ÑO");
  assert.equal(initials("  "), "?");
  assert.equal(initials(null), "?");
  assert.equal(initials("<script>"), "SC");
});

test("pattern marks are stable and never blank", () => {
  assert.equal(seedOf("Ada"), seedOf("Ada"));
  assert.notEqual(seedOf("Ada"), seedOf("Ben"));
  for (const seed of [0, 1, 0xffffffff, seedOf("x")]) {
    const cells = gridCells(seed);
    assert.equal(cells.length, 25);
    assert.ok(cells.some(Boolean));
    for (let r = 0; r < 5; r++) assert.equal(cells[r * 5], cells[r * 5 + 4]); // mirrored
  }
});

test("practice language: URL, then last used, then profile, then Python", () => {
  assert.equal(pickLanguage("java", "php", ["css"], ALL), "java");
  assert.equal(pickLanguage("cobol", "php", ["css"], ALL), "php");
  assert.equal(pickLanguage(null, null, ["css", "java"], ALL), "css");
  assert.equal(pickLanguage(null, "nope", [], ALL), "python");
});

test("every answer language has both hints", () => {
  for (const v of Object.values(ANSWER_PLACEHOLDER)) assert.ok(v.long && v.short);
});

test("only changed fields are sent", () => {
  const before = { a: "x", list: ["python"], q: null as null | { n: number } };
  assert.deepEqual(changedFields(before, { ...before }), {});
  assert.deepEqual(changedFields(before, { ...before, list: ["python", "java"] }), { list: ["python", "java"] });
  assert.deepEqual(changedFields(before, { ...before, q: { n: 1 } }), { q: { n: 1 } });
});

test("bookmark filters survive the URL and reject junk", () => {
  const q = bookmarkQuery({ kind: "question", language: "python" }, { start: "q:7" });
  assert.equal(q, "?kind=question&language=python&start=q%3A7");
  assert.deepEqual(readBookmarkFilters(q), { kind: "question", language: "python" });
  assert.deepEqual(readBookmarkFilters("?kind=all&topic=<b>&language=java"), { language: "java" });
  assert.equal(bookmarkQuery({}), "");
});

test("saved items open in the right place", () => {
  assert.equal(bookmarkHref({ kind: "question", id: 12, slug: null, language: "java" }), "/practice?question=12&language=java");
  assert.equal(bookmarkHref({ kind: "exercise", id: null, slug: "sum-list", language: "python" }), "/code/sum-list");
});
