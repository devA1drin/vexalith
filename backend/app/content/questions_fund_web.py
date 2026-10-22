"""Fundamentals: HTML, CSS and general programming concepts for complete beginners."""

from app.content.qdef import Q

F = "fundamentals"
H, C, G = "html", "css", "general"

QUESTIONS_FUND_HTML = [
    # ── Level 1 · beginner ─────────────────────────────────────────────────
    Q(F, "beginner", H, "Skeleton of a page",
      """<!DOCTYPE html>
<html lang="en">
  <head>
    <title>My page</title>
  </head>
  <body>
    <h1>Hello</h1>
  </body>
</html>""",
      "Which text appears in the browser tab, and which on the page itself? What are the doctype and head for?",
      [("the title shows in the browser tab; the body content shows on the page", ["tab"], 2),
       ("the doctype tells the browser this is modern HTML (standards mode)", ["doctype", "standards", "html5"], 1),
       ("the head holds information about the page (metadata) that is not shown in the page", ["metadata", "not shown", "not visible", "information about"], 1)],
      [],
      "\"My page\" appears in the browser tab because it is the <title>; \"Hello\" appears on the page because "
      "everything visible goes in <body>. The <!DOCTYPE html> line tells the browser to use modern HTML (standards "
      "mode). <head> holds information about the page (metadata) that is not shown in the page itself."),
    Q(F, "beginner", H, "Skipping a heading level",
      """<h1>Recipes</h1>
<h3>Pancakes</h3>
<p>Mix and fry.</p>""",
      "What is wrong with the headings? Why does it matter if h3 just looks smaller?",
      [("it skips h2: headings should go down one level at a time", ["skip", "h2"], 2),
       ("headings describe the structure (screen readers navigate by them), not the size; use CSS for size",
        ["screen reader", "structure", "outline", "css"], 1)],
      [],
      "It skips from h1 to h3; Pancakes should be an h2. Headings describe the structure of the page (screen "
      "readers and search engines use them like a table of contents), not how big the text is. Use CSS to change "
      "the size."),
    Q(F, "beginner", H, "Link without https",
      """<a href="about.html">About us</a>
<a href="www.example.com">Example</a>""",
      "The second link goes to the wrong place. Why, and what is the fix?",
      [("without https:// the browser treats it as a relative path on your own site", ["relative", "https://", "http://", "protocol", "scheme"], 2),
       ("fix: href=\"https://www.example.com\"", ["https://www.example.com"], 1)],
      [],
      "Without https:// the browser treats www.example.com as a relative path, like a file on your own site, so it "
      "opens yoursite/www.example.com. External links need the full address: href=\"https://www.example.com\"."),
    Q(F, "beginner", H, "Image without alt",
      """<img src="cat.jpg">""",
      "Which important attribute is missing, and who needs it?",
      [("the alt attribute (text alternative)", ["alt"], 2),
       ("screen reader users hear it, and it shows if the image fails to load", ["screen reader", "fails", "doesn't load", "not load", "accessib", "blind"], 1)],
      [],
      "It is missing the alt attribute, e.g. alt=\"A ginger cat asleep on a sofa\". Screen reader users hear the alt "
      "text, and it also shows if the image fails to load. Decorative images get an empty alt=\"\"."),
    Q(F, "beginner", H, "Bullets or numbers",
      """<ul>
  <li>Milk</li>
  <li>Eggs</li>
</ul>
<ol>
  <li>Preheat</li>
  <li>Bake</li>
</ol>""",
      "What is the difference between ul and ol, and when do you use each?",
      [("ul is an unordered (bulleted) list, ol is an ordered (numbered) list", ["unordered", "bullet"], 2),
       ("use ol when the order matters, like steps", ["order matters", "steps", "sequence"], 1)],
      [],
      "<ul> is an unordered list, shown with bullets; <ol> is an ordered list, shown with numbers. Use <ol> when "
      "the order matters, like recipe steps, and <ul> for a shopping list. Each item goes in an <li>."),
    Q(F, "beginner", H, "Tags closed out of order",
      """<p>This is <strong>very <em>important</strong> text</em>.</p>""",
      "Spot the mistake and write the corrected line.",
      [("the tags overlap: em was opened inside strong but closed after it", ["overlap", "wrong order", "nest", "order"], 2),
       ("close the inner tag first: <em>important</em></strong>", ["</em></strong>"], 1)],
      [],
      "The tags overlap: <em> was opened inside <strong> but closed after it. Tags must nest like boxes, so close "
      "the inner one first: <p>This is <strong>very <em>important</em></strong> text.</p>"),

    # ── Level 2 · intermediate ─────────────────────────────────────────────
    Q(F, "intermediate", H, "Email and password inputs",
      """<form action="/signup" method="post">
  <label for="mail">Email</label>
  <input id="mail" name="email" type="email">
  <label for="pw">Password</label>
  <input id="pw" name="password" type="password">
  <button>Sign up</button>
</form>""",
      "Why use type=\"email\" and type=\"password\" instead of text? What is the name attribute for?",
      [("email checks the format (and shows an email keyboard); password hides the characters",
        ["validat", "hides", "hidden", "masked", "dots", "checks the format"], 2),
       ("name is the key the value is sent to the server under", ["sent", "server", "key"], 1)],
      [],
      "type=\"email\" makes the browser check the format before submitting (and shows an @ keyboard on phones); "
      "type=\"password\" hides the characters as dots. name is the key the value is sent to the server under, e.g. "
      "email=...&password=..."),
    Q(F, "intermediate", H, "A short table row",
      """<table>
  <tr><th>Name</th><th>Score</th></tr>
  <tr><td>Ana</td><td>9</td></tr>
  <tr><td>Ben</td></tr>
</table>""",
      "What does Ben's row look like? What is the difference between th and td?",
      [("Ben's row has only one cell, so the Score cell is missing/empty", ["one cell", "missing", "empty", "only one", "blank"], 2),
       ("th is a header cell (bold, describes the column); td is a normal data cell", ["header"], 1)],
      [],
      "Ben's row has only one cell, so the Score column is empty (missing) for Ben. <th> is a header cell that "
      "describes a column (bold by default, and announced by screen readers); <td> is a normal data cell."),
    Q(F, "intermediate", H, "checked equals false",
      """<input type="checkbox" checked="false">""",
      "Is the checkbox checked when the page loads? Why?",
      [("yes, it is checked", ["is checked", "still checked", "checked anyway", "it's checked", "yes"], 2),
       ("for boolean attributes, being present means true; the value is ignored, so remove the attribute",
        ["present", "presence", "remove", "boolean", "ignored"], 1)],
      [("thinks it is unchecked", ["not checked", "unchecked"], "Boolean attributes are on whenever they are present, whatever value you write.")],
      "Yes, it is checked. checked is a boolean attribute: if it is present at all it means true, and its value "
      "(\"false\") is ignored. To leave it unchecked, remove the attribute."),
    Q(F, "intermediate", H, "Divs everywhere",
      """<div class="header">...</div>
<div class="nav">...</div>
<div class="main">...</div>
<div class="footer">...</div>""",
      "Rewrite this with semantic elements and explain the benefit.",
      [("use <header>, <nav>, <main> and <footer>", ["<header", "<nav", "<main", "<footer", "header, nav, main"], 2),
       ("they give meaning: screen readers can jump between landmarks and search engines understand the page",
        ["screen reader", "landmark", "search engine", "accessib", "meaning"], 1)],
      [],
      "Use <header>, <nav>, <main> and <footer>. They look the same as divs but carry meaning: screen readers list "
      "them as landmarks so users can jump straight to the navigation or main content, and search engines "
      "understand the page better."),
    Q(F, "intermediate", H, "Radio group by name",
      """<input type="radio" name="size" value="s"> S
<input type="radio" name="size" value="m"> M
<input type="radio" name="Size" value="l"> L""",
      "S and L can both be selected at once. Why?",
      [("L's name is Size, a different name (case-sensitive), so it is a separate group",
        ["different name", "case", "separate group", "capital"], 2),
       ("radios with the same name form one group where only one can be chosen", ["same name", "group", "only one"], 1)],
      [],
      "The third radio has name=\"Size\" with a capital S, which is a different name because names are "
      "case-sensitive, so it forms a separate group. Radios with the same name form one group where only one can be "
      "chosen. Use name=\"size\" on all three."),
    Q(F, "intermediate", H, "Paragraph inside a span",
      """<a href="/shop"><div>Shop now</div></a>
<span><p>Note</p></span>""",
      "One of these lines breaks the nesting rules. Which one, and why?",
      [("<p> inside <span> is invalid: a span may only contain inline (phrasing) content", ["inline", "phrasing"], 2),
       ("<a> wrapping a <div> is allowed in HTML5", ["allowed", "valid", "transparent"], 1)],
      [],
      "The second line: <span> is an inline element and may only contain inline (phrasing) content, but <p> is a "
      "block. The first line is allowed in HTML5: a link may wrap block content like a div."),

    # ── Level 3 · advanced ─────────────────────────────────────────────────
    Q(F, "advanced", H, "Placeholder instead of label",
      """<input type="text" name="name" placeholder="Your name">""",
      "This field has no label, only a placeholder. Why is that a problem?",
      [("the placeholder is not a label: it disappears when you type and isn't reliably announced",
        ["disappear", "not a label", "screen reader", "accessib", "vanish", "goes away"], 2),
       ("add a <label for> (or aria-label)", ["<label", "label for", "aria-label"], 1)],
      [],
      "A placeholder is not a label: it disappears as soon as you type, so you forget what the field was, it is "
      "often low-contrast, and screen readers don't reliably announce it. Add <label for=\"name\">Your name</label> "
      "with a matching id."),
    Q(F, "advanced", H, "Where a search form goes",
      """<form action="/search">
  <input name="q">
  <input name="page" type="hidden" value="1">
  <button>Search</button>
</form>""",
      "You type cats and press Search. Which URL is requested, and why?",
      [("/search?q=cats&page=1", ["?q=cats&page=1", "q=cats&page=1"], 2),
       ("the default method is GET, so fields are added to the URL query string by name", ["get", "query string"], 1)],
      [],
      "The browser requests /search?q=cats&page=1. A form without method uses GET, which adds each field to the "
      "URL query string as name=value, joined with &. The hidden field is sent too."),
    Q(F, "advanced", H, "Tiny on phones",
      """<head>
  <meta charset="utf-8">
  <title>Shop</title>
</head>""",
      "On phones the page looks tiny and zoomed out. What is missing from head?",
      [("the viewport meta tag", ["viewport"], 2),
       ("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">", ["width=device-width", "device-width"], 1)],
      [],
      "The viewport meta tag is missing. Without it, phones pretend the screen is about 980px wide and shrink the "
      "page. Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">."),
    Q(F, "advanced", H, "Nested list in the wrong place",
      """<ul>
  <li>Fruit</li>
  <ul>
    <li>Apple</li>
  </ul>
</ul>""",
      "What breaks the nesting rules here? Write the fix.",
      [("a <ul> may only contain <li> children; the inner list must go inside an <li>",
        ["inside an <li>", "inside the <li>", "inside <li>", "inside the li", "inside an li", "only contain"], 2),
       ("fix: <li>Fruit<ul><li>Apple</li></ul></li>", ["<li>fruit<ul>", "<li>fruit <ul>"], 1)],
      [],
      "A <ul> may only contain <li> children, so the inner list must go inside the Fruit item: "
      "<li>Fruit<ul><li>Apple</li></ul></li>."),
    Q(F, "advanced", H, "Relative or root path",
      """<!-- this page lives at https://site.com/blog/post.html -->
<img src="images/a.png">
<img src="/images/a.png">""",
      "Which full URL does each image load from?",
      [("the first loads /blog/images/a.png", ["/blog/images/a.png"], 2),
       ("a leading / starts from the site root: /images/a.png", ["root"], 1)],
      [],
      "The first is relative to the page's folder, so it loads https://site.com/blog/images/a.png. The second "
      "starts with /, which means the site root: https://site.com/images/a.png."),
    Q(F, "advanced", H, "Link or button",
      """<a href="#" onclick="deleteItem()">Delete</a>
<button onclick="location.href='/about'">About</button>""",
      "What is semantically wrong with these two elements?",
      [("they are swapped: links navigate, buttons perform actions", ["swap", "navigat", "action"], 2),
       ("this breaks expectations for keyboard and screen reader users and things like opening in a new tab",
        ["keyboard", "screen reader", "new tab", "middle"], 1)],
      [],
      "They are swapped. Links (<a href>) navigate to another page; buttons perform actions like deleting. Using "
      "the wrong one confuses screen reader and keyboard users, href=\"#\" jumps to the top, and the About button "
      "can't be opened in a new tab. Use <button> for Delete and <a href=\"/about\"> for About."),
]

QUESTIONS_FUND_CSS = [
    # ── Level 1 · beginner ─────────────────────────────────────────────────
    Q(F, "beginner", C, "Missing semicolon",
      """p {
  color: blue
  font-size: 18px;
}""",
      "The text is neither blue nor 18px. Why?",
      [("the missing semicolon after blue merges both lines into one invalid declaration", ["semicolon"], 2),
       ("the browser drops (ignores) invalid declarations, so both are lost", ["ignore", "drop", "invalid", "both"], 1)],
      [],
      "There is no semicolon after blue, so the browser reads color: blue font-size: 18px as one declaration. That "
      "value is invalid, so the browser ignores it and both styles are lost. Add the semicolon."),
    Q(F, "beginner", C, "Element, class and id selectors",
      """/* HTML: <h2 class="note">  <p class="note">  <h2 id="top"> */
h2 { }        /* A */
.note { }     /* B */
#top { }      /* C */
h2.note { }   /* D */""",
      "Which elements does each selector A–D match?",
      [("D matches only the h2 that also has class note", ["only the h2", "h2 with class", "h2 that has", "h2 that also", "first h2", "both h2 and"], 2),
       ("A both h2s, B both .note elements, C the element with id top", ["both h2", "both .note", "id top", "#top"], 1)],
      [],
      "A (h2) matches both h2 elements. B (.note) matches the h2 and the p with class note. C (#top) matches the "
      "element with id top. D (h2.note, no space) matches only the h2 that also has class note — the first h2."),
    Q(F, "beginner", C, "em versus rem",
      """html { font-size: 16px; }
.box { font-size: 20px; }
.box p { font-size: 1.5em; padding: 1rem; }""",
      "What are the paragraph's font-size and padding in pixels?",
      [("font-size is 30px (1.5 × the parent's 20px)", ["30px", "30 px"], 2),
       ("padding is 16px because rem uses the root (html) font size", ["16px", "16 px", "root"], 1)],
      [],
      "font-size is 30px: em is relative to the parent's font size, 1.5 × 20px. padding is 16px: rem is relative "
      "to the root (html) font size, 1 × 16px."),
    Q(F, "beginner", C, "Padding or margin",
      """.card {
  background: yellow;
  padding: 20px;
  border: 1px solid black;
  margin: 20px;
}""",
      "Which 20px space is yellow and which is transparent? List the layers from inside out.",
      [("padding is inside the border and gets the yellow background; margin is outside and transparent",
        ["margin is transparent", "margin stays transparent", "margin is not yellow", "margin isn't yellow", "outside the border"], 2),
       ("content → padding → border → margin", ["content, padding, border, margin", "content → padding → border → margin", "content padding border margin", "content -> padding -> border -> margin"], 1)],
      [],
      "The padding is yellow, because it is inside the border and the background fills it. The margin is outside "
      "the border, so the margin is transparent. From inside out: content, padding, border, margin."),
    Q(F, "beginner", C, "Width on a span",
      """<span class="tag">New</span>

.tag { width: 100px; height: 40px; background: orange; }""",
      "The width and height do nothing. Why, and what is the fix?",
      [("a span is inline, and inline elements ignore width and height", ["inline"], 2),
       ("use display: inline-block (or block)", ["inline-block", "display: block"], 1)],
      [],
      "A span is an inline element, and inline elements ignore width and height: they are only as big as their "
      "text. Add display: inline-block (keeps it in the line) or display: block."),
    Q(F, "beginner", C, "Stylesheet not loading",
      """<head>
  <link href="styles.css">
</head>""",
      "The styles never apply. What is missing?",
      [("rel=\"stylesheet\" is missing", ["rel=\"stylesheet\"", "rel=stylesheet", "rel", "stylesheet"], 2),
       ("correct form: <link rel=\"stylesheet\" href=\"styles.css\"> in the head, and check the path",
        ["path", "<link rel"], 1)],
      [],
      "The rel=\"stylesheet\" attribute is missing, so the browser doesn't know the file is CSS. Write "
      "<link rel=\"stylesheet\" href=\"styles.css\"> in the head, and check the path is right relative to the page."),

    # ── Level 2 · intermediate ─────────────────────────────────────────────
    Q(F, "intermediate", C, "Three ways to hide",
      """.a { display: none; }
.b { visibility: hidden; }
.c { opacity: 0; }""",
      "Which of these still take up space? Which can still be clicked?",
      [("b and c still take up space; a is removed from the layout", ["takes no space", "no space", "removed from", "doesn't take", "does not take"], 2),
       ("opacity: 0 is invisible but still clickable", ["clickable", "click"], 1)],
      [],
      "display: none removes .a from the layout, so it takes no space. visibility: hidden keeps the space but hides "
      ".b. opacity: 0 keeps the space and is invisible, but .c can still be clicked."),
    Q(F, "intermediate", C, "Space between",
      """.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
/* .row has three children */""",
      "Where do the three children end up?",
      [("side by side in a row: first at the left edge, last at the right, equal space between",
        ["space between", "equal space", "edges", "ends", "left"], 2),
       ("align-items: center centres them vertically (the cross axis)", ["vertical", "cross axis", "cross-axis"], 1)],
      [],
      "They sit side by side in a row: the first at the left edge, the last at the right edge, with equal space "
      "between them. align-items: center centres them vertically, on the cross axis."),
    Q(F, "intermediate", C, "Column direction",
      """.col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 300px;
}""",
      "Does justify-content centre the children horizontally or vertically here? Why?",
      [("vertically: justify-content works on the main axis, which is now vertical", ["vertical"], 2),
       ("in a column the main axis runs top to bottom; use align-items for horizontal", ["main axis", "align-items"], 1)],
      [],
      "Vertically. justify-content always works along the main axis, and flex-direction: column makes the main "
      "axis run top to bottom. To centre horizontally in a column, use align-items: center."),
    Q(F, "intermediate", C, "Percent padding",
      """.parent { width: 400px; padding: 20px; }
.child  { width: 50%; padding: 10%; }""",
      "What is the child's width and its padding on each side?",
      [("width is 200px (50% of the parent's 400px content width)", ["200px", "200 px"], 2),
       ("padding is 40px: percentage padding is based on the parent's width", ["40px", "40 px"], 1)],
      [],
      "The child's width is 200px, 50% of the parent's 400px content width. Its padding is 40px on each side "
      "because percentage padding is always based on the parent's width (10% of 400px)."),
    Q(F, "intermediate", C, "Class beats element",
      """<button class="primary">Buy</button>

.primary { background: green; }
button   { background: gray; }""",
      "Which colour is the button, even though the button rule comes later?",
      [("green", ["green"], 2),
       ("a class selector is more specific than an element selector; order only decides ties", ["specific"], 1)],
      [("thinks the later rule wins", ["gray", "grey"], "Order only matters when specificity is equal.")],
      "It is green. A class selector is more specific than an element selector, so .primary wins even though the "
      "button rule comes later. Source order only decides between rules of equal specificity."),
    Q(F, "intermediate", C, "What gets inherited",
      """body {
  color: navy;
  font-family: Georgia, serif;
  border: 1px solid black;
}""",
      "Which of these do paragraphs inside body inherit?",
      [("color and font-family are inherited; border is not", ["border is not", "border isn't", "not the border", "except the border", "border does not", "border doesn't", "not border"], 2),
       ("text properties inherit by default; box properties like border don't", ["text", "inherit"], 1)],
      [],
      "Paragraphs inherit color and font-family, but the border is not inherited. Text-related properties inherit "
      "by default; box properties like border, margin and padding do not, or every child would get its own border."),

    # ── Level 3 · advanced ─────────────────────────────────────────────────
    Q(F, "advanced", C, "em compounds",
      """html { font-size: 16px; }
li { font-size: 1.2em; }
/* <ul><li>One <ul><li>Two <ul><li>Three</li></ul></li></ul></li></ul> */""",
      "How big is the text of item Three, and why?",
      [("about 27.6px (16 × 1.2 × 1.2 × 1.2)", ["27.6", "27.65"], 2),
       ("em is relative to the parent, so nested items compound; use rem to avoid it", ["compound", "rem", "multipl"], 1)],
      [],
      "About 27.6px (27.648px). em is relative to the parent's font size, so each nested li multiplies by 1.2 "
      "again: 16 × 1.2 × 1.2 × 1.2. This compounding is why rem (relative to the root) is often safer."),
    Q(F, "advanced", C, "Centred but not vertically",
      """.wrap {
  display: flex;
  justify-content: center;
  align-items: center;
}""",
      "The child is centred horizontally but not vertically on the screen. Why?",
      [("the container is only as tall as its content, so there is no extra height to centre in",
        ["as tall as", "no extra", "no height", "height"], 2),
       ("give .wrap a height, e.g. min-height: 100vh", ["min-height", "100vh", "height:"], 1)],
      [],
      "The child is centred vertically inside .wrap, but .wrap is only as tall as its content, so there is no "
      "extra height to centre in. Give the container a height, e.g. min-height: 100vh."),
    Q(F, "advanced", C, "Two halves do not fit",
      """<div class="row"><span class="cell">A</span>
<span class="cell">B</span></div>

.cell { display: inline-block; width: 50%; }""",
      "B wraps onto a new line. Why?",
      [("the whitespace between inline-block elements renders as a space, so 50% + space + 50% is more than 100%",
        ["whitespace", "white space", "space between", "newline", "line break"], 2),
       ("use flexbox (or remove the whitespace)", ["flex"], 1)],
      [],
      "The line break between the two spans is whitespace, and between inline-block elements it renders as a "
      "space character. 50% + a space + 50% is more than 100%, so B wraps. Use display: flex on .row instead."),
    Q(F, "advanced", C, "Sibling selectors",
      """<ul class="menu">
  <li>Home</li>
  <li class="active">Shop</li>
  <li>Blog</li>
</ul>

.menu li { color: gray; }
.active + li { color: red; }
.active ~ li { font-weight: bold; }""",
      "How does the Blog item look? And Home?",
      [("Blog is red and bold", ["red and bold", "bold and red", "red, bold", "red & bold"], 2),
       ("+ selects the next sibling, ~ every later sibling; Home is only gray", ["next sibling", "adjacent", "sibling"], 1)],
      [],
      "Blog is red and bold: + selects the next sibling right after .active, and ~ selects every later sibling. "
      ".active + li is also more specific than .menu li, so red wins. Home comes before .active, so it is just gray."),
    Q(F, "advanced", C, "Sharing space with flex",
      """.row { display: flex; width: 400px; }
.item { flex: 1; }
.item.big { flex: 2; }
/* three items; the middle one is .big; no padding */""",
      "How wide is each item?",
      [("100px, 200px, 100px", ["200px", "200 px"], 2),
       ("flex-grow shares the space in the ratio 1:2:1", ["ratio", "1:2:1", "grow", "share", "proportion"], 1)],
      [],
      "100px, 200px and 100px. flex: 1 and flex: 2 share the 400px in the ratio 1:2:1, so one share is "
      "400 ÷ 4 = 100px and the big item gets two shares."),
    Q(F, "advanced", C, "Three ways to write red",
      """.a { color: #f00; }
.b { color: rgb(255 0 0 / 50%); }
.c { color: hsl(0 100% 50%); }""",
      "Which are the same colour, and what is different about .b?",
      [("all three are red, but .b is 50% transparent", ["transparent", "opacity", "alpha", "see-through"], 2),
       ("#f00 is short for #ff0000; hsl hue 0 is red", ["#ff0000", "short", "hue"], 1)],
      [],
      "All three are pure red. #f00 is short for #ff0000, and hsl(0 100% 50%) is hue 0 (red) at full saturation. "
      ".b has an alpha of 50%, so it is half transparent."),
]

QUESTIONS_FUND_GENERAL = [
    # ── Level 1 · beginner ─────────────────────────────────────────────────
    Q(F, "beginner", G, "Making tea",
      """Algorithm: make a cup of tea
1. Pour the water into the cup
2. Boil the water
3. Add a tea bag
4. Drink""",
      "What is wrong with this algorithm? What makes a good algorithm?",
      [("the steps are in the wrong order: boil the water before pouring it", ["order", "before"], 2),
       ("an algorithm is a precise, ordered, finite list of steps", ["precise", "ordered", "finite", "unambiguous", "clear"], 1)],
      [],
      "The steps are in the wrong order: you must boil the water before pouring it. An algorithm is a precise, "
      "ordered, finite list of steps; each step must be clear and the order matters (it also forgets to wait "
      "before drinking!)."),
    Q(F, "beginner", G, "Adding up in pseudocode",
      """SET total TO 0
FOR n FROM 1 TO 4
    SET total TO total + n
END FOR
PRINT total""",
      "What is printed? Trace the value of total.",
      [("prints 10", ["10"], 2),
       ("total goes 1, 3, 6, 10 (1 + 2 + 3 + 4)", ["1 + 2 + 3 + 4", "1+2+3+4", "1, 3, 6"], 1)],
      [],
      "It prints 10. total starts at 0 and each step adds n: 1, 3, 6, 10. That is 1 + 2 + 3 + 4."),
    Q(F, "beginner", G, "Binary 1011",
      """1011 (binary)""",
      "What is this number in decimal? Show the place values.",
      [("11", ["11"], 2),
       ("place values are powers of 2: 8 + 0 + 2 + 1", ["8 + 0 + 2 + 1", "8+0+2+1", "8 + 2 + 1", "8+2+1", "power", "place value"], 1)],
      [],
      "It is 11. Binary place values are powers of 2: 8, 4, 2, 1. 1011 means 8 + 0 + 2 + 1 = 11."),
    Q(F, "beginner", G, "Umbrella rule",
      """raining  = TRUE
umbrella = FALSE
go_out   = (NOT raining) OR umbrella""",
      "Is go_out TRUE or FALSE? Work it out step by step.",
      [("FALSE: you don't go out", ["false", "stay", "don't go", "do not go"], 2),
       ("NOT raining is FALSE, and FALSE OR FALSE is FALSE", ["not raining is false", "false or false"], 1)],
      [],
      "go_out is FALSE. NOT raining is NOT TRUE, which is FALSE. umbrella is FALSE. FALSE OR FALSE is FALSE, so you "
      "stay in."),
    Q(F, "beginner", G, "Reading a flowchart",
      """[Start] → (Read age) → <age >= 18 ?>
                 yes → (Print "adult") → [End]
                 no  → (Print "minor") → [End]""",
      "What does the diamond < > shape mean, and what is printed for age 18?",
      [("prints adult, because 18 >= 18 is true", ["adult"], 2),
       ("a diamond is a decision: a yes/no question that splits the path", ["decision", "question", "condition"], 1)],
      [("thinks 18 is a minor", ["minor"], ">= means 'greater than or equal to', so 18 passes the test.")],
      "For age 18 it prints adult, because >= means greater than or equal, and 18 >= 18 is true. A diamond in a "
      "flowchart is a decision: a yes/no question that splits the path."),

    # ── Level 2 · intermediate ─────────────────────────────────────────────
    Q(F, "intermediate", G, "Decimal 13 to binary",
      """13 (decimal)""",
      "Write 13 in binary and show how you got it.",
      [("1101", ["1101"], 2),
       ("13 = 8 + 4 + 1 (or divide by 2 and read the remainders)", ["8 + 4 + 1", "8+4+1", "divid", "remainder"], 1)],
      [],
      "13 is 1101 in binary. 13 = 8 + 4 + 1, so the 8, 4 and 1 places are 1 and the 2 place is 0. (Or divide by 2 "
      "repeatedly and read the remainders bottom-up.)"),
    Q(F, "intermediate", G, "Halving until one",
      """SET n TO 20
SET steps TO 0
WHILE n > 1
    SET n TO n / 2   (whole-number division)
    SET steps TO steps + 1
END WHILE
PRINT steps""",
      "What is printed? Show the values of n.",
      [("prints 4", ["prints 4", "4 steps", "is 4", "= 4", "four"], 2),
       ("n goes 20, 10, 5, 2, 1", ["10, 5, 2, 1", "10 5 2 1"], 1)],
      [],
      "It prints 4. n goes 20, 10, 5, 2, 1 (5 / 2 is 2 with whole-number division). The loop stops when n is 1, "
      "after 4 steps."),
    Q(F, "intermediate", G, "When OR is false",
      """A | B | A OR B | A AND B
--+---+--------+--------
T | T |   ?    |   ?
T | F |   ?    |   ?
F | T |   ?    |   ?
F | F |   ?    |   ?""",
      "Fill in the table. In which single row is OR false? AND true?",
      [("OR is false only when both A and B are false", ["both false", "both are false", "both a and b are false", "f, f", "f f"], 2),
       ("AND is true only when both are true", ["both true", "both are true", "t, t", "t t"], 1)],
      [],
      "OR is true in the first three rows and false only when both are false (F, F). AND is true only when both "
      "are true (T, T) and false in the other three rows."),
    Q(F, "intermediate", G, "FF in hexadecimal",
      """color: #FF8800""",
      "What is FF in decimal, and why do colours use two hex digits per channel?",
      [("FF is 255", ["255"], 2),
       ("F is 15, so FF = 15 × 16 + 15; two hex digits are one byte (0–255) per red, green or blue channel",
        ["byte", "15 × 16", "15*16", "channel", "red, green"], 1)],
      [],
      "FF is 255: F is 15, so FF = 15 × 16 + 15 = 255. Two hex digits cover exactly one byte (0–255), so a colour "
      "uses one pair for each channel: red FF, green 88, blue 00."),
    Q(F, "intermediate", G, "Finding the largest",
      """SET largest TO 0
FOR EACH x IN list
    IF x > largest THEN SET largest TO x
END FOR
PRINT largest""",
      "This works for [3, 9, 2] but is wrong for some lists. Which ones, and what should largest start as?",
      [("start with the first element, not 0; otherwise an all-negative list gives 0",
        ["first element", "first item", "first number", "first value", "negative"], 2),
       ("compare each item and update when it is bigger; an empty list needs special handling", ["empty", "compare", "each"], 1)],
      [],
      "It fails when every number is negative: for [-5, -2] it prints 0, which isn't in the list. Start largest "
      "at the first element, then compare each item and update when it is bigger. An empty list needs special "
      "handling."),

    # ── Level 3 · advanced ─────────────────────────────────────────────────
    Q(F, "advanced", G, "How many values in a byte",
      """1 byte = 8 bits""",
      "How many different values can 8 bits hold? What range is that for whole numbers starting at 0?",
      [("256 values (2 to the power 8)", ["256"], 2),
       ("0 to 255", ["255"], 1)],
      [],
      "8 bits can hold 2^8 = 256 different values, because each bit doubles the possibilities. Starting at 0, the "
      "range is 0 to 255."),
    Q(F, "advanced", G, "Triangle of loops",
      """SET count TO 0
FOR i FROM 1 TO 3
    FOR j FROM 1 TO i
        SET count TO count + 1
    END FOR
END FOR
PRINT count""",
      "What is printed? Explain how many times the inner loop runs.",
      [("prints 6", ["prints 6", "is 6", "= 6", "six", "count 6"], 2),
       ("the inner loop runs 1, then 2, then 3 times: 1 + 2 + 3", ["1 + 2 + 3", "1+2+3", "1, 2, 3"], 1)],
      [],
      "It prints 6. The inner loop runs i times: once when i is 1, twice when i is 2, three times when i is 3. "
      "1 + 2 + 3 = 6."),
    Q(F, "advanced", G, "A redundant condition",
      """IF age >= 13 AND age >= 18 THEN
    PRINT "can sign up"
END IF""",
      "Simplify the condition. Why is that allowed?",
      [("it simplifies to age >= 18", ["age >= 18", "age>=18"], 2),
       ("anyone 18 or over is also 13 or over, so the first check is redundant", ["redundant", "already", "also"], 1)],
      [],
      "It simplifies to age >= 18. Anyone 18 or over is also 13 or over, so the first check is redundant: it "
      "never changes the result."),
    Q(F, "advanced", G, "A loop that never ends",
      """SET i TO 1
WHILE i ≠ 10
    SET i TO i + 2
END WHILE
PRINT "done\"""",
      "Does this ever print done? Why or why not?",
      [("no — it is an infinite loop", ["infinite", "never ends", "never stops", "never finish", "forever", "never print"], 2),
       ("i is always odd (1, 3, 5, 7, 9, 11…) so it skips 10; use i < 10", ["odd", "skips 10", "< 10"], 1)],
      [],
      "No, it is an infinite loop. i starts at 1 and goes up by 2, so it is always odd: 1, 3, 5, 7, 9, 11… It "
      "jumps over 10 and never stops. Use WHILE i < 10 instead of ≠."),
    Q(F, "advanced", G, "Adding in binary",
      """  0110
+ 0011
------""",
      "What is the sum in binary? Check it in decimal.",
      [("1001", ["1001"], 2),
       ("6 + 3 = 9, with carries in binary", ["carry", "6 + 3", "6+3", "9"], 1)],
      [],
      "The sum is 1001. In decimal 0110 is 6 and 0011 is 3, and 6 + 3 = 9, which is 1001 in binary. Adding column "
      "by column from the right needs a carry wherever 1 + 1 = 10."),
]
