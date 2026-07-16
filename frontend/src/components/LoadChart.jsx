import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

/**
 * This formats ISO date strings (e.g., "2026-07-15") into a user-friendly "Jul 15" layout.
 * Appending "T00:00:00" forces JavaScript to parse the date in local time rather than UTC,
 * which prevents the chart dates from shifting backward or forward by a day
 */
function formatDate(d) {
  const date = new Date(d + "T00:00:00");
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export default function LoadChart({ data }) {
  // render a helpful message instead of throwing an error or rendering an empty box
  if (!data || data.length === 0) {
    return (
      <div className="chart-empty">
        No training data yet. Upload a CSV or log a run to see your trend.
      </div>
    );
  }

  return (
    // ResponsiveContainer lets the chart dynamically stretch and squeeze to fit different screen widths
    <ResponsiveContainer width="100%" height={280}>
      {/* A ComposedChart is perfect here because it allows us to mix discrete Bars (daily runs)
        with continuous Lines (our rolling 7-day and 28-day averages) on the exact same axis.
      */}
      <ComposedChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        {/* Only keep horizontal gridlines to prevent visual clutter */}
        <CartesianGrid stroke="var(--line)" vertical={false} />
        
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          stroke="var(--muted)"
          fontSize={11}
          fontFamily="var(--mono)"
          tickLine={false}
        />
        
        <YAxis stroke="var(--muted)" fontSize={11} fontFamily="var(--mono)" tickLine={false} />
        
        {/* Custom style the tooltip box to match our minimalist "paper-and-ink" styling */}
        <Tooltip
          labelFormatter={formatDate}
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--line)",
            borderRadius: 4,
            fontFamily: "var(--mono)",
            fontSize: 12,
          }}
        />
        
        {/* Daily workload spikes as subtle vertical grey bars in the background */}
        <Bar dataKey="daily_load" fill="var(--line)" radius={[2, 2, 0, 0]} name="Daily load" />
        
        {/* Acute load (fatigue) represented as a prominent, solid red/orange line.
          Disabled dots/circles to keep the time-series path clean.
        */}
        <Line
          type="monotone"
          dataKey="acute_load"
          stroke="var(--zone-high)"
          strokeWidth={2}
          dot={false}
          name="Acute (7d)"
        />
        
        {/* chronic load (fitness baseline) represented as a dashed black line,
          making it visually distinct from the acute trend even on low-res screens.
        */}
        <Line
          type="monotone"
          dataKey="chronic_load"
          stroke="var(--ink)"
          strokeWidth={2}
          strokeDasharray="4 3" // Daashed line pattern (4px stroke, 3px gap)
          dot={false}
          name="Chronic (28d)"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}