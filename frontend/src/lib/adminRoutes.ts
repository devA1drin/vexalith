/** Admin routes the same-origin proxy forwards. The backend still checks admin rights on every call. */
export type ProxyRule = { method: "GET" | "POST" | "PUT"; pattern: RegExp; public?: boolean };

export const ADMIN_RULES: ProxyRule[] = [
  { method: "GET", pattern: /^admin\/(me|overview|learners|questions|exercises|feedback|audit)$/ },
  { method: "GET", pattern: /^admin\/questions\/\d{1,10}$/ },
  { method: "POST", pattern: /^admin\/learners\/\d{1,10}\/(board|reset-xp|delete)$/ },
  { method: "POST", pattern: /^admin\/questions(\/\d{1,10}(\/visibility)?)?$/ },
  { method: "POST", pattern: /^admin\/style-check$/ },
  { method: "POST", pattern: /^admin\/feedback\/\d{1,10}\/(review|visibility|delete)$/ },
];
