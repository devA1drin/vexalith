import { ImageResponse } from "next/og";

export const alt = "Vexalith — Build Logic. Break Limits.";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  const grid = "rgba(242,241,236,0.06)";
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between",
          padding: 72, background: "#0c0d0c", color: "#f2f1ec",
          backgroundImage: `linear-gradient(${grid} 1px, transparent 1px), linear-gradient(90deg, ${grid} 1px, transparent 1px)`,
          backgroundSize: "60px 60px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <svg width="72" height="72" viewBox="0 0 64 64">
            <rect width="64" height="64" fill="#0c0d0c" stroke="#323331" />
            <path d="M12 13v6l20 29" fill="none" stroke="#c8f031" strokeWidth="5" />
            <path d="M52 13v6L32 48" fill="none" stroke="#c8f031" strokeWidth="5" />
            <rect x="8" y="7" width="8" height="8" fill="#0c0d0c" stroke="#c8f031" strokeWidth="3" />
            <rect x="48" y="7" width="8" height="8" fill="#0c0d0c" stroke="#c8f031" strokeWidth="3" />
            <rect x="28" y="44" width="8" height="8" fill="#c8f031" />
          </svg>
          <div style={{ fontSize: 44, fontWeight: 700 }}>Vexalith</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 118, fontWeight: 800, letterSpacing: -4, lineHeight: 0.95 }}>Build Logic.</div>
          <div style={{ display: "flex", alignItems: "center", fontSize: 118, fontWeight: 800, letterSpacing: -4, lineHeight: 0.95, color: "#c8f031" }}>
            Break Limits.
            <div style={{ width: 4, height: 110, background: "#ff5b2e", marginLeft: 24 }} />
          </div>
        </div>
        <div style={{ display: "flex", fontSize: 26, color: "#a5a49d" }}>Reasoning drills for programmers · Python · JavaScript</div>
      </div>
    ),
    size,
  );
}
