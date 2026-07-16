// The zone gauge is the core visual of the whole app: a horizontal bar
// split into the four ACWR risk bands, with a marker showing exactly
// where today's ratio falls. Scale is fixed 0 -> 2.0 since that comfortably
// covers the whole range you'd realistically see.

// pre-defined sports science bands mapping each ratio range to its CSS theme color variable.
const ZONES = [
  { key: "undertrained", label: "Undertrained", from: 0, to: 0.8, color: "var(--zone-under)" },
  { key: "sweet spot", label: "Sweet Spot", from: 0.8, to: 1.3, color: "var(--zone-sweet)" },
  { key: "moderate risk", label: "Moderate Risk", from: 1.3, to: 1.5, color: "var(--zone-moderate)" },
  { key: "high risk", label: "High Risk", from: 1.5, to: 2.0, color: "var(--zone-high)" },
];

// Setting the right edge of our track. Anything over 2.0 is extremely high risk and gets pegged to the end.
const SCALE_MAX = 2.0;

export default function RiskGauge({ acwr, riskLevel }) {
  // CRITICAL BOUNDARY HANDLING: Clamp  values between 0 and 2.0.
  // This keeps the marker line neatly within the visible track bounds even if
  // a user has a massive load spike (like an ACWR of 3.5) that would otherwise push the needle off the screen.
  const clamped = acwr == null ? null : Math.min(Math.max(acwr, 0), SCALE_MAX);
  
  // Calculate the horizontal offset percentage for our floating needle.
  const markerPct = clamped == null ? null : (clamped / SCALE_MAX) * 100;

  return (
    <div className="gauge">
      <div className="gauge-track">
        {ZONES.map((z) => (
          <div
            key={z.key}
            // Add an active class to highlight/brighten the specific zone the runner is currently in
            className={`gauge-zone ${riskLevel === z.key ? "gauge-zone--active" : ""}`}
            style={{
              // dynamically allocate width relative to our 2.0 scale limit
              width: `${((z.to - z.from) / SCALE_MAX) * 100}%`,
              background: z.color,
            }}
          />
        ))}
        
        {/* Render the physical needle and value bubble overr the bar if we have a valid ACWR score */}
        {markerPct !== null && (
          <div className="gauge-marker" style={{ left: `${markerPct}%` }}>
            <div className="gauge-marker-line" />
            <div className="gauge-marker-value">{clamped.toFixed(2)}</div>
          </div>
        )}
      </div>
      
      {/* footer labels matching each of our zones */}
      <div className="gauge-labels">
        {ZONES.map((z) => (
          <span key={z.key} className="gauge-label">
            {z.label}
          </span>
        ))}
      </div>
    </div>
  );
}