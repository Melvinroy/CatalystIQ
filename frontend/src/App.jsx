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
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export default function App() {
  const [scanType, setScanType] = useState("premarket");
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
    <div className="app-page">
      <div className="site-strip">
        <div className="strip-inner">
          <span>Scanner</span>
          <span>Breakouts</span>
          <span>Momentum</span>
        </div>
      </div>
      <div className="masthead">CATALYSTIQ</div>
      <main className="main-pane">
        <div className="content-wrap">
          <header className="top-header">
            <div>
              <h2>Scanner</h2>
            </div>
            <div className="header-actions">
              <span className={`status-dot ${error ? "offline" : "online"}`} title={error ? "Offline" : "Live"} />
              <button className="refresh-btn icon-only" onClick={loadRows} title="Refresh">
                ↻
              </button>
            </div>
          </header>

          <section className="controls-row">
            <label>
              Scan
              <select value={scanType} onChange={(e) => setScanType(e.target.value)}>
                <option value="premarket">Pre-market</option>
                <option value="bullish">Bullish</option>
                <option value="bearish">Bearish</option>
              </select>
            </label>
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
              Min Vol
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
            <div className="last-update">{lastFetchAt || "-"}</div>
          </section>

          <section className="table-card">
            {loading && <div className="state">Loading scanner...</div>}
            {error && !loading && <div className="state error">{error}</div>}
            {!loading && !error && rows.length === 0 && (
              <div className="state">No rows for current filters.</div>
            )}
            {!loading && !error && rows.length > 0 && (
              <table>
                <thead>
                  <tr>
                    <th>Ticker</th>
                    <th>Pre-Mkt %</th>
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
        </div>
      </main>
    </div>
  );
}
