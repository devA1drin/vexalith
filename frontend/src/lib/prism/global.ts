import { Prism } from "prism-react-renderer";

// prismjs language components register themselves on a global `Prism`.
// Point it at prism-react-renderer's instance before they load.
(globalThis as unknown as { Prism: typeof Prism }).Prism = Prism;

export { Prism };
