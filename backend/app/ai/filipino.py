"""Filipino / Tagalog / Taglish support for the offline grader.

Learners may explain their reasoning in English, Filipino (Tagalog) or Taglish
(a mix of both). The rubric keywords are English, so before matching we build an
English *gloss* of the answer:

1. Known multi-word phrases are replaced first ("walang katapusan" -> "infinite").
2. Every other word is looked up in a curated glossary of programming and
   reasoning terms. Tagalog verbs carry affixes (um-, mag-, nag-, i-, -in, -an,
   infixes and reduplication: "inuulit", "bumabalik", "ibinalik"), so we also try
   the root left after removing them ("inuulit" -> "ulit" -> "repeat").
3. Grammar words with no English counterpart ("ang", "ng", "mga") are dropped.
4. Anything else (English words in Taglish, numbers, code such as `i < 5`,
   `acc.append(x)`) is kept exactly as written. Taglish verb forms built on an
   English word ("nagpi-print", "i-assign", "nagre-return") keep the English word.

The grader then matches the rubric against the original answer *and* the gloss,
so an answer in Filipino with the same ideas scores like the English one. No AI
service and no network are involved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── Glossary ────────────────────────────────────────────────────────────────
# root -> "primary | alternatives". The first entry is the main translation
# (kept in word order, so multi-word rubric phrases still line up); the rest
# are synonyms that single-word rubric keywords can match.
GLOSSARY: dict[str, str] = {
    # reasoning connectives
    "dahil": "because", "kasi": "because", "sapagkat": "because", "palibhasa": "because",
    "kaya": "so|therefore", "samakatuwid": "therefore|thus", "kung": "if|when", "kapag": "when|if",
    "pag": "when|if", "tuwing": "every time|each time|whenever", "habang": "while", "hanggang": "until",
    "pero": "but|however", "ngunit": "but|however", "subalit": "but|however", "kahit": "even|even if",
    "para": "to|for|so that", "upang": "so that|to", "o": "or", "at": "and", "saka": "and then|then",
    "tapos": "then|after", "pagkatapos": "after", "bago": "before|new", "una": "first", "muna": "first",
    "huli": "last|late", "hulihan": "last|end", "susunod": "next|following", "sunod": "next|follow|order",
    "dati": "before|previous", "ngayon": "now", "agad": "immediately", "kaagad": "immediately",
    "noong": "when", "nung": "when", "may": "has|there is", "alam": "know", "basta": "just",
    "gana": "works|work", "bigay": "gives|give", "yari": "happens|happen", "deklara": "declared|define", "epekto": "effect", "pareho lang": "same",
    # logic
    "totoo": "true", "tama": "correct|right|true", "mali": "false|wrong|incorrect|error",
    "hindi": "not|no", "di": "not", "wala": "nothing|none|no|null|zero", "meron": "has|there is",
    "mayroon": "has|there is", "lagi": "always", "palagi": "always", "kailanman": "ever",
    "lahat": "all|every|each", "bawat": "each|every", "kada": "each|per|every", "iba": "different|other",
    "pareho": "same|equal|both", "kapareho": "same|equal", "magkapareho": "same|equal", "parehas": "same|both",
    "pantay": "equal", "katumbas": "equal|equivalent", "kaysa": "than", "mas": "more", "pinaka": "most",
    "lamang": "only", "lang": "only|just", "tangi": "only", "eksakto": "exactly", "tiyak": "definitely|sure",
    "siguro": "maybe", "dapat": "should|must", "kailangan": "need|must|should|required",
    "pwede": "can|may", "puwede": "can|may", "maaari": "can|may|possible", "ibig sabihin": "means|this means",
    # loops / control flow
    "ulit": "again|repeat|loop", "ikot": "loop|iteration|pass", "pasada": "pass|iteration",
    "tigil": "stop|stops", "hinto": "stop|stops", "tuloy": "continue|keeps going", "patuloy": "continue|keeps going",
    "laktaw": "skip|skips|skipped", "lukso": "jump|skip", "talon": "jump|skip", "takbo": "run|runs|execute",
    "patakbo": "run|execute", "labas": "outside|out", "loob": "inside|in", "dulo": "end", "katapusan": "end",
    "wakas": "end", "simula": "start|beginning", "umpisa": "start|beginning", "hakbang": "step",
    "kondisyon": "condition", "lampas": "past|beyond|exceed", "lagpas": "past|beyond|exceed",
    "sobra": "extra|too many|one extra", "kulang": "short|missing|lacking", "hangganan": "bound|limit|boundary",
    "hintay": "wait|await", "sabay": "same time|parallel|concurrent",
    # numbers & arithmetic
    "isa": "one|1|single", "dalawa": "two|2", "tatlo": "three|3", "apat": "four|4", "lima": "five|5",
    "anim": "six|6", "pito": "seven|7", "walo": "eight|8", "siyam": "nine|9", "sampu": "ten|10",
    "sero": "zero|0", "beses": "times", "minsan": "once|sometimes", "ika": "th",
    "ikalawa": "second", "pangalawa": "second", "ikatlo": "third", "pangatlo": "third", "ikaapat": "fourth",
    "bilang": "number|count", "numero": "number", "bilangin": "count", "kabuuan": "total|sum", "suma": "sum|total",
    "dagdag": "add|adds|plus|increment", "bawas": "subtract|minus|decrement", "hati": "divide|division|shared|split",
    "kalahati": "half", "doble": "double", "buo": "whole|integer", "desimal": "decimal",
    "tira": "remainder|left|remaining", "natira": "remainder|remaining", "negatibo": "negative",
    "positibo": "positive", "laki": "size|big|large", "malaki": "big|large|huge", "napakalaki": "huge",
    "liit": "small", "maliit": "small", "dami": "amount|many|count", "marami": "many", "kaunti": "few",
    "ilan": "how many|some", "bilis": "speed|fast", "mabilis": "fast|faster", "bagal": "slow", "mabagal": "slow",
    "lapad": "width|wide", "taas": "height|top|up", "baba": "bottom|down", "kaliwa": "left", "kanan": "right",
    "gitna": "middle|center", "sentro": "center",
    # data
    "listahan": "list", "talaan": "list|table|record", "hanay": "array|row", "elemento": "element|item",
    "aytem": "item", "susi": "key", "halaga": "value", "laman": "contents|value", "salita": "word|string",
    "titik": "letter|character", "letra": "letter|character", "pangalan": "name", "uri": "type", "tipo": "type",
    "sukat": "size|length", "haba": "length|long", "posisyon": "position|index", "lugar": "place|position",
    "kopya": "copy|copies", "orihinal": "original", "sarili": "own|itself", "bagay": "object|thing",
    "obheto": "object", "katangian": "property|attribute", "klase": "class", "punsyon": "function",
    "baryabol": "variable", "memorya": "memory", "alaala": "memory", "tirahan": "address",
    "turo": "point|points|points to", "linya": "line", "espasyo": "space|whitespace", "puwang": "space|gap",
    "tuldok": "dot|period", "kuwit": "comma", "panipi": "quote", "panaklong": "parenthesis|bracket",
    "pahina": "page", "kulay": "color", "pindutan": "button", "pindot": "press|click", "lalagyan": "container",
    "kahon": "box", "oras": "time", "petsa": "date", "halimbawa": "example", "kaso": "case",
    # actions
    "balik": "return|returns|back", "tawag": "call|called|calls", "gamit": "use|uses|used",
    "palit": "change|replace|swap", "gawa": "created|made|make|do", "likha": "created|create",
    "takda": "set|assigned|defined", "lagay": "put|store|set|assign", "tago": "store|hidden|hide",
    "imbak": "store|stored", "hawak": "holds|hold", "kuha": "get|got|take", "tanggap": "accept|accepted|receive",
    "pasa": "pass|passed", "abot": "reach|reaches", "dating": "reach|arrive", "sara": "closed|close",
    "bukas": "open", "basa": "read|reads", "sulat": "write|writes", "pakita": "show|display|print",
    "kita": "visible|seen|see", "tingin": "check|look", "tingnan": "check|look", "suri": "check|validate|inspect",
    "patunay": "proof|prove", "ayos": "fix|sorted|arrange", "ayusin": "fix|arrange",
    "hanap": "search|find|look up", "pasok": "insert|enter|inside", "singit": "insert", "sama": "include|included|with",
    "kasama": "included|with", "alis": "remove|removed", "tanggal": "remove|removed|delete|drop",
    "tapon": "thrown away|discard|drop", "salo": "shared|share", "bahagi": "part|shared|share",
    "hiwalay": "separate", "tagas": "leak|leaks", "sira": "broken|crash|bug", "bagsak": "crash|fail|fails",
    "ugat": "root", "sanhi": "cause", "dahilan": "reason|cause", "problema": "problem|bug",
    "solusyon": "solution|fix", "pagkakamali": "mistake|error", "sagot": "answer|result",
    "resulta": "result|output", "tanong": "question", "kalkula": "compute|calculate",
    "ulitin": "repeat|again", "ligtas": "safe|secure", "delikado": "dangerous|unsafe", "atake": "attack",
    "sunud": "order|in order", "tumpak": "accurate|precise|exact",
}

# Whole-word forms whose root would be ambiguous or misleading.
FORMS: dict[str, str] = {
    "nagbago": "changed|change", "nagbabago": "changes|change", "magbago": "change", "magbabago": "change|changes",
    "binago": "changed|modified", "binabago": "changes|modifies", "baguhin": "change|modify", "pagbabago": "change",
    "lumabas": "printed|output|prints|shows", "lumalabas": "prints|output|printed|shows", "ilabas": "print|output",
    "ilalabas": "prints|output", "inilabas": "printed|output", "kunin": "get|take", "kinuha": "got|took",
    "isang": "one|a", "unang": "first", "huling": "last", "dalawang": "two|2", "tatlong": "three|3",
    "apat na": "four|4", "nang": "", "walang": "no|without|nothing", "habang": "while",
    "mahaba": "long", "mahabang": "long", "bagong": "new", "parehong": "same|both",
    "pagkakasunod": "order", "pagkakasunud-sunod": "order|in order", "sunod-sunod": "in order|consecutive",
    "paulit-ulit": "repeatedly|repeat|loop|again and again", "tuloy-tuloy": "continuously|forever|keeps going",
    "ulit-ulit": "repeatedly|repeat", "pinakamaliit": "smallest|minimum", "pinakamalaki": "largest|maximum",
    "pinakamasama": "worst", "pinakamabuti": "best", "pinakamahusay": "best",
    "lalabas": "prints|output|printed|shows", "maglalabas": "prints|output", "naglalabas": "prints|outputs",
    "lumalaki": "grows|increases|bigger", "lumaki": "grew|grows|bigger", "tumataas": "increases|grows|goes up",
    "nangyayari": "happens", "nangyari": "happened|happens", "mangyayari": "will happen|happens",
    "ipinapakita": "shows|prints|displays", "nagpapakita": "shows|prints", "ipakita": "show|print|display",
}

# Multi-word phrases, matched before single words.
PHRASES: list[tuple[str, str]] = [
    ("walang katapusan", "infinite|never ends|forever"), ("walang hanggan", "infinite|forever|never ends"),
    ("walang hangganan", "infinite|unbounded|forever"), ("hindi natatapos", "never ends|infinite|forever"),
    ("hindi matatapos", "never ends|infinite|forever"), ("hindi tumitigil", "never stops|infinite|forever"),
    ("hindi titigil", "never stops|infinite|forever"), ("hindi humihinto", "never stops|infinite|forever"),
    ("hindi kailanman", "never"), ("magpakailanman", "forever"),
    ("paulit ulit", "repeatedly|repeat|loop"), ("hindi totoo", "false|not true"),
    ("laging totoo", "always true"), ("palaging totoo", "always true"), ("lagi na lang", "always"),
    ("pa rin", "still"), ("pa din", "still"), ("hindi pa", "not yet"),
    ("isang beses lang", "only once|once"), ("isang beses lamang", "only once|once"), ("isang beses", "once"),
    ("minsan lang", "only once|once"), ("dalawang beses", "twice|two times"), ("ilang beses", "how many times"),
    ("tatlong beses", "three times|3 times"), ("apat na beses", "four times|4 times"),
    ("limang beses", "five times|5 times"), ("bawat ikot", "each iteration|each time|every pass"),
    ("bawat pag ikot", "each iteration|each time"), ("bawat isa", "each|every"),
    ("hindi kasama", "not included|excluded|exclusive"), ("hindi nasasama", "not included|excluded"),
    ("kulang ng isa", "one short|off by one|off-by-one"), ("sobra ng isa", "one extra|off by one|off-by-one"),
    ("lampas ng isa", "one past|off by one"), ("isa ang kulang", "one short|off by one"),
    ("sa labas ng", "outside the|outside"), ("sa loob ng", "inside the|inside|within"),
    ("pagkatapos ng loop", "after the loop"), ("bago ang loop", "before the loop"),
    ("lumabas sa", "exits|exit|leaves"), ("lalabas sa", "exits|exit|leaves"), ("umalis sa", "exits|leaves"),
    ("walang laman", "empty"), ("walang lamang", "empty"), ("bakante", "empty"),
    ("buong numero", "whole number|integer"), ("buong bilang", "whole number|integer"),
    ("bagong linya", "newline|new line|line break"), ("bagong listahan", "new list"),
    ("parehong listahan", "same list"), ("parehong object", "same object"), ("parehong array", "same array"),
    ("parehong variable", "same variable"), ("iisang listahan", "same list"), ("iisang object", "same object"),
    ("iisang", "same|single"), ("mas malaki sa", "greater than|bigger than"), ("mas maliit sa", "less than|smaller than"),
    ("mas mabilis", "faster"), ("mas mabagal", "slower"), ("pinakamasamang kaso", "worst case"),
    ("sa halip", "instead"), ("kung hindi", "otherwise|else"), ("dahil dito", "because of this|as a result"),
    ("bilang resulta", "as a result"), ("bago ang", "before the"), ("bago ma", "before"),
    ("bumabalik sa", "jumps back to the|goes back to the"), ("babalik sa", "jumps back to the|goes back to the"),
    ("bumalik sa", "jumps back to the|goes back to the"), ("lumalaki pa rin", "still grows|keeps growing"),
    ("tumataas pa rin", "still grows|still increases"), ("ibig sabihin", "this means|which means"), ("kaya naman", "therefore|so"),
    ("ugat ng problema", "root cause"), ("tunay na dahilan", "root cause"),
    ("hindi nagbabago", "does not change|unchanged|not change"), ("hindi nagbago", "unchanged|did not change|not change"),
    ("hindi magbabago", "does not change|unchanged|not change"), ("walang epekto", "no effect|unchanged"),
    ("hindi naisara", "not closed|never closed"), ("hindi isinara", "not closed|never closed"),
    ("hindi nasasara", "not closed|never closed"), ("hindi masasara", "not closed|never closed"),
    ("hindi sinasara", "not closed|never closed"), ("hindi maisasara", "not closed|never closed"),
    ("hindi nadadagdag", "never adds|not added"), ("hindi naidadagdag", "never adds|not added"),
    ("hindi naidagdag", "never adds|not added"), ("hindi umaabot", "never reaches|does not reach"),
    ("hindi naaabot", "never reaches|not reached"), ("hindi makikita", "not visible|hidden"),
    ("hindi nakikita", "not visible|hidden"), ("hindi umiiral", "does not exist"), ("hindi nag eexist", "does not exist"),
    ("wala nang", "no more"), ("isa isa", "one by one|one at a time"), ("isa-isa", "one by one|one at a time"),
    ("kaliwa pakanan", "left to right"), ("mula kaliwa pakanan", "left to right"),
    ("itaas pababa", "top to bottom"), ("mula itaas pababa", "top to bottom"),
]

# Grammar words without an English counterpart: dropped from the gloss.
PARTICLES = frozenset(
    "ang ng nang mga sa si ni kay ay na yung iyong ung yun yon iyon po ho naman ba nga daw raw eh e "
    "nito niya siya ito iyan yan ko mo natin namin nila sila kami tayo ako ikaw ka dito doon diyan "
    "ganito ganyan ganoon parang tulad mismo talaga pala sana itong siyang niyang nitong iyang yang".split()
)

# Words that mark text as Tagalog (for detection only).
TL_MARKERS = frozenset(
    "ang ng nang mga sa si ni ay na yung ung kasi dahil kung kapag pag hindi siya ito nito niya lang din rin "
    "po naman para tapos kaya mo ko natin ba wala walang meron mayroon yan iyan dito ganito pero ngunit bawat "
    "hanggang habang lahat isang ulit ibig sabihin upang kaysa mas pa kahit tuwing ano bakit paano kaya "
    "lalabas lumabas magiging ginagawa ginawa dapat kailangan".split()
)
# Everyday English words (not technical terms) for spotting the English half of Taglish.
EN_MARKERS = frozenset(
    "the is are was were a an of to and it its because that this these those will would be been being "
    "then when so with which what why how there their they you we he she not does do did but after before "
    "each every until while from by into on in at as or only still same also just than more less".split()
)

# English verbs often wrapped in Tagalog affixes in Taglish ("nagpi-print", "i-assign").
EN_VERBS = frozenset(
    "print prints return returns assign append add call run compile crash close open declare skip break "
    "continue index iterate increment decrement check copy change update stop use loop push pop insert "
    "remove delete sort search compare convert cast read write store save load save throw raise catch "
    "handle fix debug test log output input render display show hide click submit validate escape "
    "sanitize bind reference point allocate free leak overflow round truncate divide multiply subtract "
    "concatenate concat join split trim parse format override inherit extend implement import export "
    "define initialize init reset clear count sum exit enter wait await resolve reject map filter reduce "
    "access mutate modify execute evaluate shadow hoist share".split()
)

EN_TECH = frozenset(
    "value values variable function call calls list array string number numbers loop condition index element "
    "key object class method file line output input result total error bug code program first second last "
    "next part decimal remainder double integer division memory pointer address default copy reference case "
    "type types true false null empty shared same infinite missing included excluded fix change still "
    "always never only once twice times since though even".split()
)

_VOWELS = set("aeiou")
_PREFIXES = (
    "pinakama", "ini", "ni", "pinaka", "ipinapa", "ipinag", "ipina", "nakapag", "makapag", "nakaka", "pinag", "ipag",
    "ipa", "naka", "maka", "napa", "mapa", "nag", "mag", "pag", "ika", "ma", "na", "pa", "ka", "i",
)
_SUFFIXES = ("han", "hin", "nan", "nin", "an", "in")
_EDGE_PUNCT = ",;:!?\"'“”‘’"


def _tokens(text: str) -> list[str]:
    """Whitespace tokens without sentence punctuation; code such as acc.append(x) stays whole."""
    out = []
    for chunk in text.split():
        core = chunk.strip(_EDGE_PUNCT)
        if core.endswith(".") and not core.endswith(".."):
            core = core[:-1]
        if core.startswith("(") and core.count("(") > core.count(")"):
            core = core[1:]
        if core.endswith(")") and core.count(")") > core.count("("):
            core = core[:-1]
        if core:
            out.append(core)
    return out
_ALPHA = re.compile(r"^[a-zñ]+(?:-[a-zñ]+)*$", re.I)


def _strip_redup(s: str) -> str | None:
    """'uulit' -> 'ulit', 'babalik' -> 'balik', 'pipi' style first-syllable copies."""
    if len(s) >= 4 and s[0] in _VOWELS and s[0] == s[1]:
        return s[1:]
    if len(s) >= 5 and s[0] not in _VOWELS and s[1] in _VOWELS and s[:2] == s[2:4]:
        return s[2:]
    return None


def _candidates(word: str) -> list[str]:
    """Possible roots of a Tagalog word, most specific first."""
    seen: list[str] = []
    frontier = [word]
    for _ in range(4):
        nxt: list[str] = []
        for s in frontier:
            if s in seen or len(s) < 2:
                continue
            seen.append(s)
            if s.endswith("ng") and len(s) > 4:
                nxt.append(s[:-2])
            for p in _PREFIXES:
                if s.startswith(p) and len(s) - len(p) >= 3:
                    nxt.append(s[len(p):])
            if len(s) >= 5 and s[0] not in _VOWELS and s[1:3] in ("um", "in"):
                nxt.append(s[0] + s[3:])
            if len(s) >= 5 and s[:2] in ("um", "in") and s[2] in _VOWELS:
                nxt.append(s[2:])
            if s.endswith("u") and len(s) >= 4:
                nxt.append(s[:-1] + "o")  # takbuhin -> takbu -> takbo
            r = _strip_redup(s)
            if r:
                nxt.append(r)
            for suf in _SUFFIXES:
                if s.endswith(suf) and len(s) - len(suf) >= 3:
                    nxt.append(s[: -len(suf)])
        frontier = nxt
    return [c for c in seen if len(c) >= 2]


def lemma(word: str) -> tuple[str, str] | None:
    """(kind, translation) for one word: kind is 'tl' (glossary) or 'en' (English verb inside Tagalog affixes)."""
    w = word.lower()
    if w in FORMS:
        return ("tl", FORMS[w])
    if w in GLOSSARY:
        return ("tl", GLOSSARY[w])
    if "-" in w:
        parts = w.split("-")
        if w.replace("-", " ") in GLOSSARY:
            return ("tl", GLOSSARY[w.replace("-", " ")])
        last = parts[-1]
        # Taglish: "nagpi-print", "i-assign", "mag-loop" -> keep the English verb.
        if last in EN_VERBS or (last.endswith("s") and last[:-1] in EN_VERBS):
            return ("en", last)
        for p in parts[::-1]:
            got = lemma(p)
            if got:
                return got
        return None
    cands = _candidates(w)
    best: tuple[str, str] | None = None
    for c in cands[1:]:
        if c in GLOSSARY and (best is None or len(c) > len(best[0])):
            best = (c, GLOSSARY[c])
    if best:
        return ("tl", best[1])
    for c in cands[1:]:
        if c in EN_VERBS:
            return ("en", c)
    return None


@dataclass
class Gloss:
    language: str  # "en" | "fil" | "taglish"
    primary: str = ""  # English rendering, word order kept (main translations only)
    full: str = ""  # same, with every synonym (for single-word keywords)
    tl_words: int = 0
    words: int = 0
    unknown: list[str] = field(default_factory=list)


def _phrase_pattern() -> re.Pattern[str]:
    alts = sorted((p for p, _ in PHRASES), key=len, reverse=True)
    return re.compile(r"(?<![\w-])(" + "|".join(re.escape(a).replace(r"\ ", r"[\s-]+") for a in alts) + r")(?![\w-])", re.I)


_PHRASE_RE = _phrase_pattern()
_PHRASE_MAP = {p: e for p, e in PHRASES}


def detect_language(text: str) -> str:
    return gloss(text).language


def gloss(text: str) -> Gloss:
    """Detect English / Filipino / Taglish and build the English gloss."""
    low = text.lower()
    tokens = _tokens(low)
    alpha = [t for t in tokens if _ALPHA.match(t)]
    tl = sum(1 for t in alpha if t in TL_MARKERS or (t not in EN_MARKERS and t not in EN_VERBS and lemma(t) and lemma(t)[0] == "tl"))
    # English share: everyday words plus programming vocabulary ("value", "call", "loop").
    en = sum(
        1 for t in alpha
        if t in EN_MARKERS or t in EN_VERBS or t in EN_TECH or ("-" in t and t.split("-")[-1] in EN_VERBS)
    )
    n = max(1, len(alpha))
    if tl < 2 or tl / n < 0.15:
        return Gloss(language="en", words=len(tokens))
    language = "taglish" if en / n >= 0.2 else "fil"

    primary: list[str] = []
    full: list[str] = []
    unknown: list[str] = []

    def emit(translation: str) -> None:
        opts = [o.strip() for o in translation.split("|") if o.strip()]
        if opts:
            primary.append(opts[0])
            full.extend(opts)

    pos = 0
    for m in _PHRASE_RE.finditer(low):
        _emit_words(low[pos:m.start()], emit, primary, full, unknown)
        key = re.sub(r"[\s-]+", " ", m.group(1))
        emit(_PHRASE_MAP.get(key) or _PHRASE_MAP.get(m.group(1), ""))
        pos = m.end()
    _emit_words(low[pos:], emit, primary, full, unknown)
    return Gloss(
        language=language, primary=" ".join(primary), full=" ".join(full),
        tl_words=tl, words=len(tokens), unknown=unknown,
    )


def _emit_words(chunk: str, emit, primary: list[str], full: list[str], unknown: list[str]) -> None:
    for tok in _tokens(chunk):
        if not _ALPHA.match(tok):
            # numbers, code, punctuation-attached tokens: keep as written
            primary.append(tok)
            full.append(tok)
            continue
        if tok in PARTICLES:
            continue
        if tok in EN_MARKERS or tok in EN_VERBS:
            primary.append(tok)
            full.append(tok)
            continue
        got = lemma(tok)
        if got is None:
            primary.append(tok)  # English or an identifier: keep as is
            full.append(tok)
            unknown.append(tok)
        elif got[0] == "en":
            primary.append(got[1])
            full.extend([got[1], got[1] + "s"])
        elif got[1]:
            emit(got[1])


FILIPINO_NOTE = "Tinanggap ang sagot mo sa Filipino. Ang mga ideya ang minamarkahan, hindi ang wika."
TAGLISH_NOTE = "Tinanggap ang sagot mo sa Taglish. Ang mga ideya ang minamarkahan, hindi ang wika."
