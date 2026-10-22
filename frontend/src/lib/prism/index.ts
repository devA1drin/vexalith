// Order matters: the global must exist before the grammars are evaluated.
import "./global";
import "prismjs/components/prism-markup-templating";
import "prismjs/components/prism-php";

export { Prism } from "./global";
