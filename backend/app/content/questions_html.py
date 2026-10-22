"""Seed questions: HTML (semantics, accessibility, forms, DOM structure, rendering)."""

from app.content.qdef import Q

H = "html"

QUESTIONS_HTML = [
    # ── Beginner ────────────────────────────────────────────────────────────
    Q("code_tracing", "beginner", H, "Button default type",
      """<form action="/search">
  <input name="q" value="css">
  <button>Clear</button>
</form>""",
      "What happens when the user clicks “Clear”? Explain why.",
      [("the form is submitted", ["submit"], 2),
       ("a button's default type inside a form is submit", ["default", 'type="button"', "type=button"], 1)],
      [("thinks it clears the field", ["clears the input", "clears the field", "resets the form"],
        "A <button> with no type inside a form is type=\"submit\"; it only resets with type=\"reset\" or script.")],
      "The form is submitted to /search?q=css. A <button> without a type attribute inside a form defaults to "
      "type=\"submit\", so the label “Clear” is misleading. Use type=\"button\" (plus script) or type=\"reset\"."),
    Q("code_tracing", "beginner", H, "Whitespace collapsing",
      """<p>Hello      world
   again</p>""",
      "How does the browser render this paragraph? Explain what happens to the spaces and the line break.",
      [("renders on one line as 'Hello world again'", ["hello world again", "one line", "single line"], 2),
       ("runs of whitespace collapse to one space", ["collapse", "single space", "one space"], 1)],
      [("expects the line break to show", ["two lines", "new line is kept", "line break is kept"],
        "In normal flow, newlines are whitespace and collapse like spaces; use <br>, <pre> or white-space: pre.")],
      "It renders “Hello world again” on one line (wrapping only if needed). In normal white-space handling, "
      "runs of spaces, tabs and newlines collapse into a single space."),
    Q("debugging", "beginner", H, "Link to the wrong place",
      """<!-- page URL: https://site.dev/help/ -->
<a href="www.example.com">Docs</a>""",
      "Clicking “Docs” leads to a 404 on site.dev. What is the bug and how do you fix it?",
      [("href is treated as a relative path", ["relative"], 2),
       ("fix: include the scheme (https://)", ["https://", "http://", "scheme", "protocol"], 1)],
      [],
      "Without a scheme, “www.example.com” is a relative URL, so the browser resolves it to "
      "https://site.dev/help/www.example.com. Fix: href=\"https://www.example.com\" (include the scheme)."),
    Q("debugging", "beginner", H, "Label does not focus the input",
      """<label for="email">Email</label>
<input id="e-mail" type="email">""",
      "Clicking the label does not focus the field and screen readers announce an unlabeled input. Why?",
      [("for and id do not match", ["match", "mismatch", "e-mail", "same value"], 2),
       ("fix by making them equal or wrapping the input", ['for="e-mail"', 'id="email"', "rename", "wrap"], 1)],
      [],
      "The label's for=\"email\" does not match the input's id=\"e-mail\", so they are not associated. "
      "Make them equal (e.g. id=\"email\") or wrap the input inside the <label>."),
    Q("edge_cases_testing", "beginner", H, "Required is not enough",
      """<form>
  <input name="username" required minlength="3">
  <button>Save</button>
</form>""",
      "The user types each of: (empty), \"ab\", \"   \" (three spaces), \"abc\". Which pass browser validation, "
      "and what does that mean for the server?",
      [("three spaces pass validation", ["spaces", "whitespace"], 2),
       ("empty and 'ab' fail", ["empty", "ab"], 1),
       ("server-side validation is still required", ["server", "trim", "pattern"], 1)],
      [],
      "Empty fails (required) and \"ab\" fails minlength. Three spaces pass because required only checks for a "
      "non-empty value and spaces count as characters; \"abc\" passes. The server must still validate (trim, "
      "pattern), since client validation is bypassable."),
    Q("code_review_design", "beginner", H, "Clickable div",
      """<div class="btn" onclick="save()">Save</div>""",
      "Review this control. What is wrong and what would you use instead?",
      [("use a real <button>", ["<button", "button element", "use a button", "use button"], 2),
       ("not keyboard focusable / operable", ["keyboard", "focus", "tab"], 1),
       ("no role for screen readers", ["screen reader", "role", "assistive", "accessib"], 1)],
      [],
      "A div is not focusable, has no button role and does not respond to Enter/Space, so keyboard and screen "
      "reader users cannot use it. Use <button type=\"button\" onclick=\"save()\">Save</button>, which gives focus, "
      "keyboard activation and the correct role for free."),

    # ── Intermediate ────────────────────────────────────────────────────────
    Q("code_tracing", "intermediate", H, "Implicit tbody",
      """<table id="t">
  <tr><td>1</td></tr>
</table>
<script>
  console.log(document.getElementById("t").children[0].tagName);
</script>""",
      "What is logged? Explain how the parser builds this table.",
      [("logs TBODY", ["tbody"], 2),
       ("the parser inserts tbody automatically", ["implicit", "insert", "automatically", "parser"], 1)],
      [("expects TR", ["logs tr", '"tr"'], "The HTML parser wraps rows in an implied <tbody>, so the first child is TBODY.")],
      "It logs \"TBODY\". The HTML parser automatically inserts an implicit <tbody> around table rows, so the "
      "table's first element child is the tbody, not the tr."),
    Q("code_tracing", "intermediate", H, "Div inside a paragraph",
      """<p>Intro <div>Box</div> outro</p>""",
      "What DOM does the browser actually build? Explain why.",
      [("the p is closed before the div", ["closes the p", "closed before", "implicitly closed", "closes p", "auto-close"], 2),
       ("a p cannot contain a div (only phrasing content)", ["cannot contain", "can't contain", "phrasing content", "not allowed"], 1),
       ("the stray </p> creates an empty <p></p>", ["empty p", "empty <p>", "<p></p>"], 1)],
      [],
      "A <p> cannot contain block-level flow content like <div> (only phrasing content), so the parser implicitly "
      "closes the p before the div: <p>Intro </p><div>Box</div> outro<p></p>. “ outro” becomes a text node and "
      "the stray </p> creates an empty <p></p>."),
    Q("debugging", "intermediate", H, "Password in the URL",
      """<form action="/login">
  <input name="user">
  <input name="pass" type="password">
  <button>Log in</button>
</form>""",
      "Security review flags this login form. What is the bug and the fix?",
      [("default method is GET", ["get"], 2),
       ("credentials end up in the URL / history / logs", ["url", "query string", "history", "logs"], 1),
       ("fix: method=\"post\" (over HTTPS)", ["post"], 1)],
      [],
      "With no method attribute the form uses GET, so the password is put in the query string — visible in the "
      "URL, browser history, server logs and Referer headers. Use method=\"post\" over HTTPS."),
    Q("debugging", "intermediate", H, "Disabled field not sent",
      """<form method="post" action="/order">
  <input name="price" value="9.99" disabled>
  <input name="qty" value="2">
  <button>Buy</button>
</form>""",
      "The server only receives qty. Why, and what should you change?",
      [("disabled controls are not submitted", ["not submitted", "not sent", "excluded", "omitted", "isn't sent", "is not sent"], 2),
       ("readonly fields are submitted", ["readonly"], 1),
       ("never trust a client-side price", ["server", "trust"], 1)],
      [],
      "Disabled controls are excluded from form submission, so price is not sent. readonly would be submitted, "
      "but the server should never trust a price from the client anyway — look it up server-side."),
    Q("edge_cases_testing", "intermediate", H, "Number input edge cases",
      """<form>
  <input type="number" name="age" min="0" max="120" step="1">
  <button>Go</button>
</form>""",
      "Which of these values submit: (empty), \"1e2\", \"12.5\", \"-0\", \"121\"? What must the server still handle?",
      [("1e2 is valid (it is 100)", ["1e2", "100"], 2),
       ("empty is allowed because it is not required", ["empty", "required"], 1),
       ("12.5 fails the step", ["step"], 1),
       ("the server must validate the string itself", ["server"], 1)],
      [],
      "Empty submits (not required) and arrives as an empty string; \"1e2\" is valid scientific notation for 100; "
      "\"-0\" is valid; \"12.5\" fails step=1 and \"121\" overflows max. The server receives strings and must "
      "validate type and range itself."),
    Q("code_review_design", "intermediate", H, "Div soup and heading levels",
      """<div class="header"><div class="title">Shop</div></div>
<div class="nav"><a href="/">Home</a> <a href="/cart">Cart</a></div>
<div class="main">
  <h3>Products</h3>
</div>""",
      "Review the semantics. What would you change and why does it matter?",
      [("use semantic landmarks (header, nav, main)", ["<nav", "<main", "<header", "landmark", "semantic"], 2),
       ("heading hierarchy: an h1, no skipped levels", ["h1", "skip", "hierarchy", "heading level"], 1),
       ("screen reader navigation relies on it", ["screen reader", "assistive", "accessib"], 1)],
      [],
      "Replace the divs with semantic landmarks: <header> with an <h1>Shop</h1>, <nav> for the links and <main> "
      "for content, and don't skip from no h1 to h3. Screen reader users navigate by landmarks and heading level."),

    # ── Advanced ────────────────────────────────────────────────────────────
    Q("code_tracing", "advanced", H, "Template contents",
      """<template id="row"><li>Item</li></template>
<ul id="list"></ul>
<script>
  const t = document.getElementById("row");
  console.log(t.children.length, t.content.children.length);
  list.append(t.content.cloneNode(true));
  list.append(t.content.cloneNode(true));
  console.log(list.children.length);
</script>""",
      "What are the two logs? Explain where the template's <li> lives.",
      [("first log is 0 1", ["0 1", "0, 1"], 2),
       ("template contents live in an inert .content fragment", ["content", "fragment", "inert"], 1),
       ("second log is 2 because each clone appends one li", ["2", "clone"], 1)],
      [],
      "Logs “0 1” then “2”. The template's children are parsed into an inert DocumentFragment at t.content, so "
      "t.children is empty. Each cloneNode(true) of the content appends one <li>, giving 2 (the global `list` "
      "comes from the element's id)."),
    Q("code_tracing", "advanced", H, "Controls outside the form",
      """<form id="f" action="/save" method="post">
  <input name="a" value="1">
</form>
<input name="b" value="2" form="f">
<input name="c" value="3">
<button form="f">Save</button>""",
      "Which name/value pairs are sent when Save is clicked? Why?",
      [("sends a and b", ["a=1&b=2", "a and b", "a=1, b=2", "a=1 and b=2"], 2),
       ("the form attribute associates controls outside the form", ["form attribute", 'form="f"', "associat", "owner"], 1),
       ("c is not included", ["c is not", "not c", "without c", "c isn't", "excluded"], 1)],
      [],
      "It sends a=1&b=2. The form attribute (form=\"f\") associates input b and the button with the form even "
      "though they are outside it; c has no form owner, so it is not included."),
    Q("debugging", "advanced", H, "Focusable inside aria-hidden",
      """<div class="dialog-backdrop" aria-hidden="true">
  <button>Close</button>
</div>""",
      "Keyboard users report a “ghost” focus stop. Explain the problem and the fix.",
      [("the button is still focusable via keyboard", ["focus", "tab"], 2),
       ("it is hidden from screen readers, so focus lands on nothing announced", ["screen reader", "announce", "assistive"], 1),
       ("fix: inert / hidden / remove from the tab order", ["inert", "hidden attribute", "display: none", "display:none", "remove"], 1)],
      [],
      "aria-hidden only hides content from assistive technology; the button is still focusable with Tab, so "
      "screen reader users land on something that is not announced. Use the inert attribute (or hidden / "
      "display:none), or remove focusable content from the hidden region."),
    Q("debugging", "advanced", H, "Duplicate ids",
      """<label for="qty">Qty</label><input id="qty" name="qty1">
<label for="qty">Qty</label><input id="qty" name="qty2">
<script>document.getElementById("qty").value = 5;</script>""",
      "Only one field gets 5 and the second label behaves oddly. Explain both symptoms.",
      [("getElementById returns only the first match", ["first"], 2),
       ("ids must be unique", ["unique", "duplicate"], 1),
       ("the second label also points to the first input", ["second label", "label"], 1)],
      [],
      "ids must be unique. getElementById returns the first element with that id, so only the first input gets 5, "
      "and the second label (for=\"qty\") also targets the first input. Give each input a unique id."),
    Q("edge_cases_testing", "advanced", H, "Rendering a URL parameter",
      """<span id="name"></span>
<script>
  const params = new URLSearchParams(location.search);
  document.getElementById("name").innerHTML = params.get("name");
</script>""",
      "List the edge-case inputs you would test and what goes wrong for each.",
      [("HTML/script injection (XSS) via innerHTML", ["xss", "inject", "script injection"], 2),
       ("use textContent instead", ["textcontent", "innertext", "escape"], 1),
       ("a missing parameter renders 'null'", ["null"], 1)],
      [],
      "A value like <img src=x onerror=alert(1)> executes script — XSS through innerHTML. A missing ?name renders "
      "the text “null”. Use textContent (and a default) so input is treated as text, not markup."),
    Q("code_review_design", "advanced", H, "Custom checkbox",
      """<span class="check" onclick="this.classList.toggle('on')"></span> Subscribe""",
      "Review this custom checkbox for accessibility. What is the best fix, and what would a custom version need?",
      [("prefer a native checkbox with a label", ['type="checkbox"', "type=checkbox", "native", "<input"], 2),
       ("state and role are not exposed (role, aria-checked)", ["aria-checked", "role"], 1),
       ("keyboard support (focusable, Space toggles)", ["keyboard", "tabindex", "space"], 1)],
      [],
      "Use a native <input type=\"checkbox\"> inside a <label> and style it. A custom one would need "
      "role=\"checkbox\", aria-checked kept in sync, tabindex=\"0\" and Space key handling — none of which the span has."),
]
