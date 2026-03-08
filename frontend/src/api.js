const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function fetchPremarketScanner({ minChangePct, minVolume, limit = 50 }) {
  const params = new URLSearchParams({
    min_change_pct: String(minChangePct),
    min_volume: String(minVolume),
    limit: String(limit),
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/scanner/premarket?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Scanner request failed: ${response.status}`);
  }

  return response.json();
}
