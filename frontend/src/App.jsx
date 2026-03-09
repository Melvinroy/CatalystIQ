import { useEffect, useMemo, useState } from "react";
import { fetchPremarketScanner } from "./api";

const refreshOptions = [
  { label: "15s", value: 15 },
  { label: "30s", value: 30 },
  { label: "60s", value: 60 },
  { label: "Manual", value: 0 },
];

const navItems = ["Scanner", "Catalysts", "Watchlist", "Calendar", "Alerts"];

function formatPercent(value) {
  return `${Number(value).toFixed(2)}%`;
}

function formatSignedPercent(value) {
  const numeric = Number(value);
  const prefix = numeric > 0 ? "+" : "";
  return `${prefix}${numeric.toFixed(2)}%`;
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

  const topMover = rows[0];
  const avgMove =
    rows.length > 0
      ? rows.reduce((sum, row) => sum + Number(row.premarket_change_pct), 0) / rows.length
      : 0;
  const totalVolume = rows.reduce((sum, row) => sum + Number(row.volume), 0);
  const advancers = rows.filter((row) => Number(row.premarket_change_pct) > 0).length;
  const decliners = rows.filter((row) => Number(row.premarket_change_pct) < 0).length;

  const watchlist = rows.slice(0, 5);

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
      <div className="layout-shell">
        <aside className="sidebar">
          <div className="brand">CatalystIQ</div>
          <p className="brand-sub">Stock Intelligence</p>
          <nav className="nav-list">
            {navItems.map((item, index) => (
              <button key={item} className={`nav-item ${index === 0 ? "active" : ""}`}>
                {item}
              </button>
            ))}
          </nav>
          <div className="watch-card">
            <h3>Watchlist</h3>
            {watchlist.length === 0 && <p>No symbols yet</p>}
            {watchlist.map((row) => (
              <div key={`watch-${row.ticker}`} className="watch-row">
                <span>{row.ticker}</span>
                <strong className={Number(row.premarket_change_pct) >= 0 ? "up" : "down"}>
                  {formatSignedPercent(row.premarket_change_pct)}
                </strong>
              </div>
            ))}
          </div>
        </aside>

        <main className="main-pane">
          <header className="topbar">
            <div>
              <h1>Pre-market Scanner</h1>
              <p>Live movers filtered by percent change and volume.</p>
            </div>
            <div className="topbar-meta">
              <span className={`status-dot ${error ? "offline" : "online"}`} />
              <div>
                <small>Last sync</small>
                <strong>{lastFetchAt || "--:--:--"}</strong>
              </div>
              <button className="refresh-btn" onClick={loadRows}>
                Refresh
              </button>
            </div>
          </header>

          <section className="kpi-grid">
            <article className="kpi-card">
              <span>Top mover</span>
              <strong>{topMover ? topMover.ticker : "--"}</strong>
              <p>{topMover ? formatSignedPercent(topMover.premarket_change_pct) : "No data yet"}</p>
            </article>
            <article className="kpi-card">
              <span>Average move</span>
              <strong>{formatSignedPercent(avgMove)}</strong>
              <p>Across {rows.length} symbols</p>
            </article>
            <article className="kpi-card">
              <span>Total volume</span>
              <strong>{formatVolume(totalVolume)}</strong>
              <p>Filtered traded volume</p>
            </article>
            <article className="kpi-card">
              <span>Breadth</span>
              <strong>
                {advancers} / {decliners}
              </strong>
              <p>Advancers vs decliners</p>
            </article>
          </section>

          <section className="filters-card">
            <div className="filters-head">
              <h2>Scanner Filters</h2>
              <small>All fields update the query instantly</small>
            </div>
            <div className="controls-row">
              <label>
                Scan Type
                <select value={scanType} onChange={(e) => setScanType(e.target.value)}>
                  <option value="premarket">Pre-market</option>
                  <option value="bullish">Bullish</option>
                  <option value="bearish">Bearish</option>
                </select>
              </label>
              <label>
                Minimum %
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={minChangePct}
                  onChange={(e) => setMinChangePct(Number(e.target.value))}
                />
              </label>
              <label>
                Minimum Volume
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={minVolume}
                  onChange={(e) => setMinVolume(Number(e.target.value))}
                />
              </label>
              <label>
                Refresh Interval
                <select value={refreshSeconds} onChange={(e) => setRefreshSeconds(Number(e.target.value))}>
                  {refreshOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </section>

          <section className="table-card">
            <div className="table-head">
              <h2>Live Results</h2>
            </div>
            {loading && <div className="state">Loading scanner...</div>}
            {error && !loading && <div className="state error">{error}</div>}
            {!loading && !error && rows.length === 0 && <div className="state">No rows for current filters.</div>}
            {!loading && !error && rows.length > 0 && (
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Ticker</th>
                    <th>Pre-Mkt %</th>
                    <th>Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, index) => (
                    <tr key={`${row.ticker}-${row.last_updated_at}`}>
                      <td>{index + 1}</td>
                      <td>
                        <span className="ticker-pill">{row.ticker}</span>
                      </td>
                      <td className={Number(row.premarket_change_pct) >= 0 ? "up" : "down"}>
                        {formatPercent(row.premarket_change_pct)}
                      </td>
                      <td>{formatVolume(row.volume)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}
