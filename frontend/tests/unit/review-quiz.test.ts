/**
 * Unit tests for the small helpers behind Review mistakes and Timed quiz.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { mmss, until, ago } from "../../src/lib/when";
import { filtersQuery, readFilters } from "../../src/lib/reviewFilters";

test("mmss rounds up and never goes negative", () => {
  assert.equal(mmss(600), "10:00");
  assert.equal(mmss(59.2), "1:00");
  assert.equal(mmss(0.4), "0:01");
  assert.equal(mmss(-3), "0:00");
});

test("relative days read plainly", () => {
  const now = new Date(2026, 9, 26, 12).getTime();
  assert.equal(ago(new Date(2026, 9, 26, 8).toISOString(), now), "today");
  assert.equal(ago(new Date(2026, 9, 25, 23).toISOString(), now), "yesterday");
  assert.equal(ago(new Date(2026, 9, 23, 9).toISOString(), now), "3 days ago");
  assert.equal(until(new Date(2026, 9, 27, 1).toISOString(), now), "tomorrow");
  assert.equal(until(new Date(2026, 9, 29, 1).toISOString(), now), "in 3 days");
});

test("review filters survive the URL round trip", () => {
  const q = filtersQuery({ language: "python", difficulty: "beginner" }, { start: "q:12" });
  assert.equal(q, "?language=python&difficulty=beginner&start=q%3A12");
  assert.deepEqual(readFilters(q), { language: "python", difficulty: "beginner" });
  assert.equal(filtersQuery({}), "");
});
