"""Seed questions: CSS (specificity, cascade, box model, flexbox/grid, layout bugs, responsive edge cases)."""

from app.content.qdef import Q

C = "css"

QUESTIONS_CSS = [
    # ── Beginner ────────────────────────────────────────────────────────────
    Q("code_tracing", "beginner", C, "Id beats class",
      """/* <h1 id="title" class="title">Hi</h1> */
#title { color: blue; }
.title { color: red; }
h1     { color: green; }""",
      "What color is the heading? Explain how the browser decides.",
      [("blue", ["blue"], 2), ("the id selector is more specific", ["specific", "id"], 1)],
      [("last rule wins", ["green because", "last rule"], "Source order only breaks ties between equal specificity; an id outranks classes and types.")],
      "Blue. All three rules match, so specificity decides: the id selector #title (1,0,0) beats .title (0,1,0) "
      "and h1 (0,0,1). Source order only matters when specificity ties."),
    Q("code_tracing", "beginner", C, "Box model width",
      """.box {
  width: 200px;
  padding: 20px;
  border: 5px solid;
  margin: 10px;
}""",
      "How wide is the .box border box, and how much horizontal space does it occupy?",
      [("250px border box", ["250"], 2), ("default box-sizing is content-box", ["content-box", "content box"], 1),
       ("margin adds outside: 270px of space", ["270", "margin"], 1)],
      [("thinks width includes padding", ["200px wide", "200 total"], "With the default content-box, width sets only the content; padding and border are added.")],
      "The border box is 250px: 200 content + 2×20 padding + 2×5 border, because the default box-sizing is "
      "content-box. Margin is outside the box, so it occupies 270px horizontally."),
    Q("debugging", "beginner", C, "margin: auto on a span",
      """/* <span class="card">Hello</span> */
.card { margin: 0 auto; }""",
      "The card is not centered. Why, and how do you fix it?",
      [("a span is inline", ["inline"], 2), ("needs display:block and a width (or a flex parent)", ["display: block", "display:block", "width", "flex"], 1)],
      [],
      "A span is an inline element, and auto horizontal margins only center block-level boxes with a width. "
      "Use display: block plus a width (or max-width), or center it from a flex parent."),
    Q("debugging", "beginner", C, "Accidental descendant selector",
      """/* <li class="nav-item">Home</li> */
.nav-item:hover { color: red; }
.nav item { font-weight: bold; }""",
      "Why is the item never bold?",
      [("the space makes a descendant selector", ["descendant", "space"], 2),
       ("it selects <item> elements inside .nav", ["item element", "<item>", "element named item", "tag"], 1),
       ("fix: .nav-item", [".nav-item"], 1)],
      [],
      "“.nav item” has a space, so it is a descendant selector: an <item> element (a tag) inside an element with "
      "class nav. Nothing matches. Use .nav-item."),
    Q("edge_cases_testing", "beginner", C, "Long unbroken text",
      """.card { width: 200px; border: 1px solid; }""",
      "What edge-case content breaks this card, and how do you make it robust?",
      [("a long unbroken string overflows", ["overflow"], 2),
       ("fix with overflow-wrap / word-break", ["overflow-wrap", "word-break", "break-word", "anywhere"], 1),
       ("test with a long URL or word without spaces", ["url", "no spaces", "without spaces"], 1)],
      [],
      "A long URL or word without spaces cannot wrap and will overflow the 200px card. Add overflow-wrap: anywhere "
      "(or word-break) and test with long URLs, emails and other strings without spaces."),
    Q("code_review_design", "beginner", C, "!important everywhere",
      """.btn        { color: white !important; background: #333 !important; }
.btn-danger { background: red; }""",
      "`<button class=\"btn btn-danger\">` stays grey. Review the approach.",
      [("!important blocks normal overrides", ["override", "cannot", "can't"], 2),
       ("remove it and rely on the cascade / specificity", ["remove", "cascade", "specificity"], 1),
       ("it escalates into a maintenance war", ["maintain", "escalat", "war"], 1)],
      [],
      "!important on .btn means .btn-danger cannot override the background without another !important — an "
      "escalating specificity war that is hard to maintain. Remove it and use modifier classes with the cascade."),

    # ── Intermediate ────────────────────────────────────────────────────────
    Q("code_tracing", "intermediate", C, "Margin collapse",
      """/* <div class="a"></div><div class="b"></div> */
.a { height: 10px; margin-bottom: 30px; }
.b { height: 10px; margin-top: 20px; }""",
      "How big is the vertical gap between the two boxes? Why?",
      [("30px", ["30"], 2), ("adjacent vertical margins collapse to the larger", ["collapse"], 1)],
      [("adds the margins", ["50"], "Adjacent vertical margins of block siblings collapse; the gap is the larger one, not the sum.")],
      "30px. Adjacent vertical margins between block siblings collapse into one margin equal to the larger of the "
      "two, so 30px, not 50px."),
    Q("code_tracing", "intermediate", C, "Flex distribution",
      """/* three empty children: .a .b .c */
.row { display: flex; width: 300px; }
.a   { flex: 1; }
.b   { flex: 2; }
.c   { flex: none; width: 60px; }""",
      "What are the widths of .a, .b and .c?",
      [("a = 80px, b = 160px, c = 60px", ["80", "160"], 2),
       ("flex: 1 means basis 0, so free space splits by ratio", ["ratio", "basis", "free space", "remaining"], 1)],
      [],
      ".c keeps 60px (flex: none). The remaining 240px is free space; flex: 1 / flex: 2 have flex-basis 0, so it "
      "splits by the 1:2 ratio: .a = 80px, .b = 160px."),
    Q("code_tracing", "intermediate", C, "Grid auto-placement with span",
      """/* items 1, 2 (class="wide"), 3, 4 */
.grid { display: grid; grid-template-columns: repeat(3, 100px); }
.wide { grid-column: span 2; }""",
      "Where does each item land?",
      [("item 2 spans columns 2–3 of row 1", ["columns 2", "column 2"], 2),
       ("items 3 and 4 go to row 2", ["row 2", "second row"], 1),
       ("auto-placement fills cells in source order", ["auto-placement", "auto placement", "source order", "in order"], 1)],
      [],
      "Auto-placement fills cells in source order: row 1 has item 1 in column 1 and item 2 spanning columns 2–3. "
      "Row 2 has item 3 in column 1 and item 4 in column 2; the last cell stays empty."),
    Q("debugging", "intermediate", C, "z-index ignored",
      """.header { position: relative; z-index: 10; }
.modal  { z-index: 999; }   /* still appears under the header */""",
      "Why does the modal render under the header?",
      [("z-index has no effect on position: static", ["static", "position"], 2),
       ("give it position fixed/absolute/relative", ["fixed", "absolute", "relative"], 1),
       ("watch for stacking contexts from ancestors", ["stacking context"], 1)],
      [],
      "The modal is position: static, and z-index is ignored on static non-flex/grid items. Give it position: "
      "fixed (or absolute/relative). Also check that it isn't trapped inside an ancestor's stacking context."),
    Q("debugging", "intermediate", C, "height: 100% does nothing",
      """/* <div class="layout"><aside class="sidebar">…</aside></div> */
.sidebar { height: 100%; background: #222; }""",
      "The sidebar is only as tall as its content. Explain and fix.",
      [("the parent has no definite height (auto)", ["parent", "definite", "auto"], 2),
       ("fix: give the parent a height, use 100vh/min-height, or flex/grid stretch", ["100vh", "dvh", "flex", "grid", "min-height"], 1)],
      [],
      "A percentage height resolves against the parent's height; .layout has auto height (not definite), so 100% "
      "behaves like auto. Give the parent a height (e.g. min-height: 100vh) or make it a flex/grid container so "
      "the sidebar stretches."),
    Q("edge_cases_testing", "intermediate", C, "Breakpoint overlap",
      """@media (max-width: 768px) { .menu        { display: none; } }
@media (min-width: 768px) { .menu-toggle { display: none; } }""",
      "Which viewport width breaks navigation, and how do you fix the boundaries?",
      [("at exactly 768px both queries match", ["768", "both"], 2),
       ("then neither menu nor toggle is visible", ["neither", "no navigation", "nothing", "both hidden"], 1),
       ("fix the boundaries (769px, 767.98px or range syntax)", ["769", "767.98", "range"], 1)],
      [],
      "At exactly 768px both media queries match (max-width and min-width are inclusive), so the menu and the "
      "toggle are both hidden and there is no navigation. Use non-overlapping bounds such as max-width: 767.98px, "
      "min-width: 769px, or range syntax (width < 768px)."),
    Q("code_review_design", "intermediate", C, "Animating layout properties",
      """.panel      { transition: height .3s, left .3s; position: absolute; }
.panel.open { height: 400px; left: 0; }""",
      "Review this animation for performance and accessibility.",
      [("animating height/left triggers layout (reflow) every frame", ["layout", "reflow"], 2),
       ("prefer transform / opacity", ["transform"], 1),
       ("respect prefers-reduced-motion", ["reduced-motion", "reduced motion", "reduce motion"], 1)],
      [],
      "height and left trigger layout (reflow) on every frame, which can cause jank. Animate transform (translate/"
      "scale) and opacity, which the compositor can handle, and disable or shorten it under "
      "prefers-reduced-motion."),

    # ── Advanced ────────────────────────────────────────────────────────────
    Q("code_tracing", "advanced", C, "Specificity tally",
      """/* <nav><ul id="nav"><li class="active">
       <a class="link current">Docs</a></li></ul></nav> */
ul#nav li.active a        { color: red; }
#nav .active a:hover      { color: blue; }
nav ul li a.link.current  { color: green; }""",
      "What color is the link normally, and on hover? Show the specificity of each rule.",
      [("red normally", ["red"], 2), ("blue on hover", ["blue"], 1),
       ("specificity: (1,1,3) vs (1,2,1) vs (0,2,4); the id outweighs classes", ["1,1,3", "(1,1,3)", "1-1-3", "id"], 1)],
      [],
      "Rule 1 is (1,1,3), rule 2 is (1,2,1) and applies only on hover, rule 3 is (0,2,4). Normally red wins because "
      "the id outranks any number of classes. On hover blue wins: (1,2,1) beats (1,1,3)."),
    Q("code_tracing", "advanced", C, "Cascade layers",
      """/* <button id="save" class="btn">Save</button> */
@layer base, components;
@layer components { .btn  { color: blue; } }
@layer base       { #save { color: red; } }
.btn { color: green; }""",
      "What color is the button? Explain the cascade layers involved.",
      [("green", ["green"], 2),
       ("unlayered styles beat all layered styles", ["unlayered", "not in a layer", "outside"], 1),
       ("between layers, layer order beats specificity", ["layer order", "regardless of specificity", "order"], 1)],
      [],
      "Green. Unlayered styles beat all layered normal styles, regardless of specificity. Among the layers, "
      "components (declared later) would beat base even though #save is more specific — layer order is checked "
      "before specificity."),
    Q("debugging", "advanced", C, "Flex item refuses to shrink",
      """.row  { display: flex; }
.main { flex: 1; }
.main pre { overflow-x: auto; }   /* long code line still widens the page */""",
      "Why does the long <pre> push .main wider than the row, and what is the one-line fix?",
      [("flex items default to min-width: auto (content size)", ["min-width"], 2),
       ("fix: min-width: 0 on .main", ["min-width: 0", "min-width:0", "overflow: hidden"], 1)],
      [],
      "Flex items have min-width: auto, so .main can't shrink below its content's min-content width (the long pre "
      "line). Set min-width: 0 on .main (or overflow: hidden) so the pre's own overflow-x scrolling takes over."),
    Q("debugging", "advanced", C, "Sticky that never sticks",
      """.page    { overflow: hidden; }
.toolbar { position: sticky; }   /* inside .page */""",
      "Find both reasons the toolbar never sticks.",
      [("no top (inset) value", ["top"], 2),
       ("an ancestor with overflow hidden becomes the scroll container", ["overflow"], 1),
       ("fix: add top and use overflow: clip or remove it", ["clip", "remove"], 1)],
      [],
      "Sticky needs an inset like top: 0 — without it, it never sticks. Also, .page has overflow: hidden, which "
      "makes it the sticky element's scroll container even though it doesn't scroll. Add top: 0 and remove the "
      "overflow (or use overflow: clip)."),
    Q("edge_cases_testing", "advanced", C, "Viewport-only font size",
      """h1 { font-size: 5vw; }""",
      "What breaks at the extremes, and what is a robust replacement?",
      [("extreme sizes on small and large screens", ["2560", "128", "huge", "tiny", "small screen", "large screen"], 2),
       ("vw-only text ignores user zoom / text resizing", ["zoom", "resize", "accessib"], 1),
       ("use clamp() with rem", ["clamp"], 1)],
      [],
      "At 320px it is 16px, at 2560px it is a huge 128px, and because it depends only on the viewport, browser "
      "zoom/text resize barely changes it (an accessibility failure). Use clamp(1.75rem, 1rem + 3vw, 3.5rem)."),
    Q("code_review_design", "advanced", C, "Deep selector coupling",
      """.sidebar > div:nth-child(3) ul li a span.label { color: #c00; }""",
      "Review this selector for maintainability and performance of change.",
      [("tightly coupled to DOM structure; breaks when markup changes", ["coupl", "markup change", "structure", "fragile", "brittle"], 2),
       ("high specificity makes overrides hard", ["specificity", "override"], 1),
       ("use a single semantic class (e.g. BEM-style)", ["class", "bem"], 1)],
      [],
      "It is brittle: coupled to exact DOM structure (any extra div or reorder breaks it) and its high specificity "
      "makes overrides hard. Put a single semantic class on the element (e.g. .nav-label, BEM-style) and style that."),
]
