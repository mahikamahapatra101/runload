export default function SessionsTable({ sessions }) {
  // **We copy the array with `[...sessions]` first because `.reverse()` 
  // mutates arrays in place. Copying prevents us from accidentally reversing the 
  // master list in the parent state. We then grab the top 8 most recent runs to display.
  const recent = [...sessions].reverse().slice(0, 8);

  // Gracefully render a simple text placeholder if the user has a brand new profile
  if (recent.length === 0) {
    return <p className="hint">No runs logged yet.</p>;
  }

  return (
    <table className="sessions-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Distance</th>
          <th>Duration</th>
          <th>RPE</th>
          <th>Load</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
        {recent.map((s) => (
          <tr key={s.id}>
            <td>{s.date}</td>
            {/* fallback to an em-dash if distance wasn't provided (e.g. treadmill run with no track data) */}
            <td>{s.distance_mi != null ? `${s.distance_mi} mi` : "—"}</td>
            <td>{s.duration_min} min</td>
            <td>{s.rpe}</td>
            {/* Format load as an integer since decimal precision isn't necessaryy for training load totals */}
            <td>{s.load.toFixed(0)}</td>
            {/* Clamped via CSS class 'notes-cell' to prevent text overflows from stretching the layout */}
            <td className="notes-cell">{s.notes || "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}