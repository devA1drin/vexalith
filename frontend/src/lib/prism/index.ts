// Order matters: the global must exist before the grammars are evaluated.
import "./global";
import "prismjs/components/prism-markup-templating";
import "prismjs/components/prism-php";
import "prismjs/components/prism-java";

export { Prism } from "./global";
