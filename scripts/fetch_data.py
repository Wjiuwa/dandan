#!/usr/bin/env python3
"""
Fetches real, free, publicly available data relevant to the Dangote
Petroleum Refinery IPO and writes it to data/data.json.

Data sources (no API key required):
  - FX:    https://open.er-api.com/v6/latest/USD   (USD/NGN rate)
  - News:  Google News RSS search feeds, one per "warning sign" category

This script only reads publicly published data. It does NOT predict prices,
invent targets, or infer anything not present in the source data.
"""

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "data.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (dangote-refinery-monitor/1.0)"}

# One query per structural signal category the user wants tracked.
NEWS_QUERIES = {
    "utilization": "Dangote refinery capacity utilization OR crude allocation",
    "freight_margins": "Dangote refinery crack spread OR crude import OR freight",
    "block_trades": "Dangote refinery shares NGX OR block trade OR institutional sale",
    "fx_liquidity": "naira dollar liquidity OR CBN forex OR FPI outflow Nigeria",
}

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-NG&gl=NG&ceid=NG:en"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_fx_usd_ngn() -> float | None:
    try:
        data = fetch_json("https://open.er-api.com/v6/latest/USD")
        return data.get("rates", {}).get("NGN")
    except Exception as e:
        print(f"FX fetch failed: {e}")
        return None


def strip_html(text: str) -> str:
    return re.sub("<[^<]+?>", "", text or "").strip()


def fetch_news(query: str, limit: int = 5) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(query=urllib.parse.quote(query))
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            xml_bytes = resp.read()
        root = ET.fromstring(xml_bytes)
        items = []
        for item in root.findall(".//item")[:limit]:
            title = strip_html(item.findtext("title", default=""))
            link = item.findtext("link", default="")
            pub_date = item.findtext("pubDate", default="")
            source_el = item.find("source")
            source = source_el.text if source_el is not None else ""
            items.append(
                {"title": title, "link": link, "published": pub_date, "source": source}
            )
        return items
    except Exception as e:
        print(f"News fetch failed for '{query}': {e}")
        return []


def main():
    data = json.loads(DATA_PATH.read_text()) if DATA_PATH.exists() else {}
    data.setdefault("fx", {}).setdefault("history", [])
    data.setdefault("news", {})

    now_iso = datetime.now(timezone.utc).isoformat()

    # --- FX ---
    rate = fetch_fx_usd_ngn()
    if rate is not None:
        data["fx"]["usd_ngn"] = rate
        data["fx"]["source"] = "open.er-api.com"
        data["fx"]["history"].append({"t": now_iso, "rate": rate})
        data["fx"]["history"] = data["fx"]["history"][-120:]  # cap history length

    # --- News, one feed per warning-sign category ---
    for category, query in NEWS_QUERIES.items():
        data["news"][category] = fetch_news(query)

    data["last_updated"] = now_iso

    DATA_PATH.write_text(json.dumps(data, indent=2))
    print(f"Updated {DATA_PATH} at {now_iso}")


if __name__ == "__main__":
    main()
