import { useEffect, useMemo, useState } from "react";
import { fetchPremarketScanner } from "./api";

const refreshOptions = [
  { label: "15s", value: 15 },
  { label: "30s", value: 30 },
  { label: "60s", value: 60 },
  { label: "Manual", value: 0 },
];

function formatPercent(value) {
  return `${Number(value).toFixed(2)}%`;
}

function formatVolume(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

export default function App() {
  const [isRailOpen, setIsRailOpen] = useState(true);
  const [minChangePct, setMinChangePct] = useState(4);
  const [minVolume, setMinVolume] = useState(100000);
  const [refreshSeconds, setRefreshSeconds] = useState(30);

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastFetchAt, setLastFetchAt] = useState("");

  const query = useMemo(
    () => ({ minChangePct, minVolume, limit: 50 }),
    [minChangePct, minVolume]
  );

  async function loadRows() {
    setError("");
    setLoading(true);
    try {
      const data = await fetchPremarketScanner(query);
      setRows(data);
      setLastFetchAt(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err.message || "Failed to load scanner data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRows();
  }, [query]);

  useEffect(() => {
    if (refreshSeconds === 0) {
      return undefined;
    }
    const timer = setInterval(loadRows, refreshSeconds * 1000);
    return () => clearInterval(timer);
  }, [refreshSeconds, query]);

  return (
    <div className="app-shell">
      <aside className={`left-rail ${isRailOpen ? "open" : "closed"}`}>
        <button className="rail-toggle" onClick={() => setIsRailOpen((v) => !v)}>
          {isRailOpen ? "<" : ">"}
        </button>
        {isRailOpen && (
          <div className="rail-content">
            <h1>CatalystIQ</h1>
            <p>Pre-market breakout scanner</p>
            <div className="placeholder-card">
              <h3>Component B</h3>
              <p>Coming soon</p>
            </div>
          </div>
        )}
      </aside>

      <main className="main-pane">
        <header className="top-header">
          <div>
            <h2>Pre-market Breakouts</h2>
            <p>Session: 4:00-9:30 ET</p>
          </div>
          <div className="header-actions">
            <button className="refresh-btn" onClick={loadRows}>Refresh</button>
          </div>
        </header>

        <section className="controls-row">
          <label>
            Min %
            <input
              type="number"
              min="0"
              step="0.1"
              value={minChangePct}
              onChange={(e) => setMinChangePct(Number(e.target.value))}
            />
          </label>
          <label>
            Min Volume
            <input
              type="number"
              min="0"
              step="1000"
              value={minVolume}
              onChange={(e) => setMinVolume(Number(e.target.value))}
            />
          </label>
          <label>
            Refresh
            <select value={refreshSeconds} onChange={(e) => setRefreshSeconds(Number(e.target.value))}>
              {refreshOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <div className="last-update">Last update: {lastFetchAt || "-"}</div>
        </section>

        <section className="table-card">
          {loading && <div className="state">Loading scanner...</div>}
          {error && !loading && <div className="state error">{error}</div>}
          {!loading && !error && rows.length === 0 && (
            <div className="state">No pre-market breakouts for current filters.</div>
          )}
          {!loading && !error && rows.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Pre-market %</th>
                  <th>Volume</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={`${row.ticker}-${row.last_updated_at}`}>
                    <td>{row.ticker}</td>
                    <td>{formatPercent(row.premarket_change_pct)}</td>
                    <td>{formatVolume(row.volume)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}
