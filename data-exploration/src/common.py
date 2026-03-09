"""Reusable helpers for CatalystIQ data exploration notebooks."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv

UTC = ZoneInfo("UTC")
ET = ZoneInfo("America/New_York")


@dataclass
class ExplorationConfig:
    provider_order: list[str]
    symbols_source: str
    lookback_trading_days: int
    outputs_raw_dir: Path
    outputs_processed_dir: Path
    report_path: Path


def load_config(config_path: str = "../config/exploration.yaml") -> ExplorationConfig:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    return ExplorationConfig(
        provider_order=cfg["provider_order"],
        symbols_source=cfg["symbols_source"],
        lookback_trading_days=int(cfg["lookback_trading_days"]),
        outputs_raw_dir=Path("../") / cfg["outputs"]["raw_dir"],
        outputs_processed_dir=Path("../") / cfg["outputs"]["processed_dir"],
        report_path=Path("../") / cfg["outputs"]["report_path"],
    )


def load_env(env_path: str = "../.env") -> None:
    load_dotenv(dotenv_path=env_path, override=False)


def get_api_keys() -> dict[str, str | None]:
    return {
        "polygon": os.getenv("POLYGON_API_KEY"),
        "finnhub": os.getenv("FINNHUB_API_KEY"),
        "polygon_base": os.getenv("POLYGON_BASE_URL", "https://api.polygon.io"),
        "finnhub_base": os.getenv("FINNHUB_BASE_URL", "https://finnhub.io/api/v1"),
    }


def classify_session(ts_utc: pd.Timestamp) -> str:
    ts_et = ts_utc.tz_convert(ET)
    t = ts_et.time()
    if time(4, 0) <= t < time(9, 30):
        return "premarket"
    if time(9, 30) <= t < time(16, 0):
        return "regular"
    if time(16, 0) <= t < time(20, 0):
        return "afterhours"
    return "offhours"


def new_pull_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now(tz=UTC).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"


def polygon_gainers(api_key: str, base_url: str) -> dict:
    url = f"{base_url.rstrip('/')}/v2/snapshot/locale/us/markets/stocks/gainers"
    resp = requests.get(url, params={"apiKey": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def polygon_snapshot_all(api_key: str, base_url: str) -> dict:
    url = f"{base_url.rstrip('/')}/v2/snapshot/locale/us/markets/stocks/tickers"
    resp = requests.get(url, params={"apiKey": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def polygon_grouped_daily(api_key: str, base_url: str, market_date: str) -> dict:
    url = f"{base_url.rstrip('/')}/v2/aggs/grouped/locale/us/market/stocks/{market_date}"
    resp = requests.get(url, params={"adjusted": "true", "apiKey": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def polygon_intraday_bars(api_key: str, base_url: str, symbol: str, start_date: str, end_date: str) -> dict:
    url = f"{base_url.rstrip('/')}/v2/aggs/ticker/{symbol}/range/1/minute/{start_date}/{end_date}"
    resp = requests.get(url, params={"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def finnhub_quote(api_key: str, base_url: str, symbol: str) -> dict:
    url = f"{base_url.rstrip('/')}/quote"
    resp = requests.get(url, params={"symbol": symbol, "token": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def finnhub_candle(api_key: str, base_url: str, symbol: str, from_unix: int, to_unix: int) -> dict:
    url = f"{base_url.rstrip('/')}/stock/candle"
    resp = requests.get(
        url,
        params={"symbol": symbol, "resolution": "1", "from": from_unix, "to": to_unix, "token": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def normalize_polygon_snapshot(snapshot_payload: dict, source_endpoint: str, pull_id: str) -> pd.DataFrame:
    now = pd.Timestamp.now(tz=UTC)
    rows = []
    for item in snapshot_payload.get("tickers", []):
        symbol = item.get("ticker")
        if not symbol:
            continue
        day = item.get("day") or {}
        prev_day = item.get("prevDay") or {}
        last_price = day.get("c")
        prev_close = prev_day.get("c")
        if last_price is None or prev_close in (None, 0):
            change_pct = None
        else:
            change_pct = ((float(last_price) - float(prev_close)) / float(prev_close)) * 100.0

        row = {
            "provider": "polygon",
            "symbol": symbol,
            "ts_utc": now,
            "session": classify_session(now),
            "last_price": float(last_price) if last_price is not None else None,
            "change_pct": float(change_pct) if change_pct is not None else None,
            "volume": int(day.get("v") or 0),
            "prev_close": float(prev_close) if prev_close is not None else None,
            "source_endpoint": source_endpoint,
            "pull_id": pull_id,
            "provider_payload": json.dumps(item),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def normalize_finnhub_quote(symbol: str, quote: dict, source_endpoint: str, pull_id: str) -> pd.DataFrame:
    ts = pd.to_datetime(quote.get("t"), unit="s", utc=True) if quote.get("t") else pd.Timestamp.now(tz=UTC)
    prev_close = quote.get("pc")
    current = quote.get("c")
    change_pct = None
    if current is not None and prev_close not in (None, 0):
        change_pct = ((float(current) - float(prev_close)) / float(prev_close)) * 100.0

    row = {
        "provider": "finnhub",
        "symbol": symbol,
        "ts_utc": ts,
        "session": classify_session(ts),
        "last_price": float(current) if current is not None else None,
        "change_pct": float(change_pct) if change_pct is not None else None,
        "volume": 0,
        "prev_close": float(prev_close) if prev_close is not None else None,
        "source_endpoint": source_endpoint,
        "pull_id": pull_id,
        "provider_payload": json.dumps(quote),
    }
    return pd.DataFrame([row])


def quality_summary(df: pd.DataFrame) -> dict:
    required = [
        "provider",
        "symbol",
        "ts_utc",
        "session",
        "last_price",
        "change_pct",
        "volume",
        "prev_close",
        "source_endpoint",
        "pull_id",
    ]
    null_rates = {col: float(df[col].isna().mean()) for col in required if col in df.columns}

    dedupe_cols = ["provider", "symbol", "ts_utc", "source_endpoint"]
    duplicated_count = int(df.duplicated(subset=dedupe_cols).sum()) if all(c in df.columns for c in dedupe_cols) else -1

    outlier_count = 0
    if "last_price" in df.columns:
        outlier_count += int((df["last_price"] <= 0).sum())
    if "volume" in df.columns:
        outlier_count += int((df["volume"] < 0).sum())

    return {
        "rows": int(len(df)),
        "null_rates": null_rates,
        "duplicated_count": duplicated_count,
        "outlier_count": outlier_count,
    }


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def save_raw_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(path, index=False)
    except Exception:
        fallback = path.with_suffix(".csv")
        df.to_csv(fallback, index=False)
