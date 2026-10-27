/**
 * Unit tests for the admin dashboard helpers and the proxy allow-list.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { actionLabel, actionTone, adminQuery, confirmMatches, niceMax, pct, ratingBand } from "../../src/lib/adminFormat";
import { ADMIN_RULES } from "../../src/lib/adminRoutes";

const allowed = (method: string, path: string) => ADMIN_RULES.some((r) => r.method === method && r.pattern.test(path));

test("the proxy forwards only the admin routes it should", () => {
  for (const p of ["admin/me", "admin/overview", "admin/learners", "admin/questions", "admin/questions/12", "admin/exercises", "admin/feedback", "admin/audit"]) {
    assert.ok(allowed("GET", p), p);
  }
  for (const p of ["admin/learners/3/board", "admin/learners/3/reset-xp", "admin/learners/3/delete", "admin/questions", "admin/questions/7", "admin/questions/7/visibility", "admin/style-check", "admin/feedback/9/review", "admin/feedback/9/visibility", "admin/feedback/9/delete"]) {
    assert.ok(allowed("POST", p), p);
  }
  for (const [m, p] of [["GET", "admin/purge-users"], ["POST", "admin/purge-users"], ["GET", "admin/learners/3/delete"], ["POST", "admin/learners/abc/delete"], ["POST", "admin/learners/3/../../x"], ["GET", "admin"], ["POST", "admin/me"]]) {
    assert.ok(!allowed(m, p), `${m} ${p}`);
  }
  assert.ok(ADMIN_RULES.every((r) => !r.public), "admin routes always need a session");
});

test("typed confirmation ignores @ and case but not other letters", () => {
  assert.ok(confirmMatches("@ana-reyes", "ana-reyes"));
  assert.ok(confirmMatches("ana-reyes", " @Ana-Reyes "));
  assert.ok(!confirmMatches("ana-reyes", "ana-reye"));
  assert.ok(!confirmMatches("", ""));
});

test("chart axis and formatting helpers", () => {
  assert.equal(niceMax([]), 1);
  assert.equal(niceMax([0, 0]), 1);
  assert.equal(niceMax([7]), 10);
  assert.equal(niceMax([12]), 20);
  assert.equal(niceMax([41]), 50);
  assert.equal(niceMax([100]), 100);
  assert.equal(pct(0.456), "46%");
  assert.equal(pct(null), "—");
  assert.equal(ratingBand(820), "hard");
  assert.equal(ratingBand(500), "medium");
  assert.equal(ratingBand(200), "easy");
});

test("query strings drop empty filters and page 1", () => {
  assert.equal(adminQuery({ q: "", page: 1, sort: "xp" }), "?sort=xp");
  assert.equal(adminQuery({ q: "a b", page: 2 }), "?q=a+b&page=2");
  assert.equal(adminQuery({}), "");
});

test("audit actions read as words", () => {
  assert.equal(actionLabel("learner.deleted"), "Deleted learner data");
  assert.equal(actionLabel("something.new"), "something.new");
  assert.equal(actionTone("learner.deleted"), "danger");
  assert.equal(actionTone("learner.xp_reset"), "danger");
  assert.equal(actionTone("question.edited"), "edit");
  assert.equal(actionTone("feedback.reviewed"), "plain");
});
