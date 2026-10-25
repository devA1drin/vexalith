import type { CodeLanguage } from "./api";

/** One short, friendly sentence that explains a common error. */
export function errorTip(error: string, language: CodeLanguage): string | null {
  const e = error;
  if (/took longer than/.test(e)) return null;
  if (/didn't compile/.test(e)) return "Read the first error: it gives the line number and what the compiler expected there.";
  if (/SyntaxError|ParseError|syntax error/i.test(e)) return "Check that line for a missing bracket, quote, colon or semicolon.";
  if (/IndentationError/.test(e)) return "Python uses indentation for blocks. Line the code inside the function up with 4 spaces.";
  if (/NameError|ReferenceError|Undefined variable|cannot find symbol|undeclared identifier/i.test(e))
    return "A name is misspelled or used before it's created. Check the spelling and that you set it first.";
  if (/IndexError|out of range|ArrayIndexOutOfBounds|Undefined (array key|offset)|outside a vector/i.test(e))
    return "You reached past the end of a list or string. Check where your loop starts and stops.";
  if (/KeyError/.test(e)) return "You read a dictionary key that isn't there yet. Use .get(key, 0) or check with `in` first.";
  if (/TypeError/.test(e))
    return language === "javascript"
      ? "Something has a different type than expected, e.g. calling a method on undefined."
      : "Two values of different types were mixed, e.g. adding text to a number.";
  if (/NullPointerException/.test(e)) return "Something is null. Make sure every variable gets a value before you use it.";
  if (/ZeroDivision|division by zero|DivisionByZero/i.test(e)) return "Something was divided by zero. Check the case with an empty input.";
  if (/couldn't find a function/.test(e)) return null;
  return null;
}

/** A hint for a wrong (but error-free) answer. */
export function wrongTip(got: unknown, expected: unknown, language: CodeLanguage): string | null {
  if (got === null || got === undefined) {
    return language === "python" ? "Your function returned None. Did you forget the return line?" : "Your function returned nothing. Did you forget to return the result?";
  }
  if (typeof got !== typeof expected || Array.isArray(got) !== Array.isArray(expected)) {
    const kind = (v: unknown) => (Array.isArray(v) ? "a list" : v === null ? "nothing" : typeof v === "object" ? "a map/dictionary" : typeof v === "string" ? "text" : typeof v === "boolean" ? "true/false" : "a number");
    return `The answer should be ${kind(expected)}, but you returned ${kind(got)}.`;
  }
  if (Array.isArray(got) && Array.isArray(expected) && got.length !== expected.length) {
    return `Your list has ${got.length} item${got.length === 1 ? "" : "s"}; it should have ${expected.length}.`;
  }
  if (typeof got === "string" && typeof expected === "string" && got.toLowerCase() === expected.toLowerCase()) {
    return "Almost: only upper/lower case is different.";
  }
  return null;
}
