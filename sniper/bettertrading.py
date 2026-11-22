"""Import Better Trading bookmark exports as live-search URLs.

Format, from Better Trading's own source (exile-center/better-trading,
app/services/bookmarks/export.ts): one export string per folder.

- v3: "3:" + base64(utf-8 JSON) {icn, tit, ver, trs: [{tit, loc: "ver:type:slug"}]}
- v2: "2:" + base64(utf-8 JSON) with loc "type:slug" (PoE 1)
- v1: bare base64 (latin-1) with loc "type:slug"

Exports carry no league: a saved search is league-independent, so the URL
is built for the current league. Only PoE 1 "search" bookmarks become live
searches (exchange bookmarks have no live mode; PoE 2 is not supported).

These strings come from outside the program and end up in a URL handed to
Chrome on its command line, so every slug is checked against the trade
site's id alphabet before use.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

SEARCHES_NAME = "searches.txt"  # beside config.yaml: one export string per line
TRADE_BASE = "https://www.pathofexile.com/trade/search"
_SLUG_RE = re.compile(r"^[A-Za-z0-9]{1,32}$")


@dataclass(frozen=True)
class SavedSearch:
    folder: str
    title: str
    slug: str


@dataclass(frozen=True)
class ImportResult:
    searches: tuple[SavedSearch, ...]
    skipped: tuple[str, ...]  # human-readable reasons, one per skipped item


def _decode(export: str) -> dict:
    export = export.strip()
    if export[:2] in ("2:", "3:"):
        raw = base64.b64decode(export[2:], validate=True).decode("utf-8")
    else:
        raw = base64.b64decode(export, validate=True).decode("latin-1")
    payload = json.loads(raw)
    if not isinstance(payload, dict) or not isinstance(payload.get("trs"), list):
        raise ValueError("not a Better Trading folder export")
    return payload


def parse_exports(text: str) -> ImportResult:
    """Every export string in `text` (one per line; blank lines ignored)."""
    searches: list[SavedSearch] = []
    skipped: list[str] = []
    seen: set[str] = set()
    for n, line in enumerate((ln.strip() for ln in text.splitlines()), start=1):
        if not line:
            continue
        version3 = line.startswith("3:")
        try:
            payload = _decode(line)
        except (binascii.Error, UnicodeDecodeError, ValueError) as e:
            skipped.append(f"line {n}: not a Better Trading export ({e.__class__.__name__})")
            continue
        folder = str(payload.get("tit") or "untitled")
        if version3 and str(payload.get("ver", "1")) != "1":
            skipped.append(f"{folder}: PoE 2 folder, not supported")
            continue
        for trade in payload["trs"]:
            if not isinstance(trade, dict):
                continue
            title = str(trade.get("tit") or "untitled")
            parts = str(trade.get("loc", "")).split(":")
            if version3:
                parts = parts[1:]  # drop the per-trade site version
            if len(parts) != 2:
                skipped.append(f"{title}: unreadable location")
                continue
            kind, slug = parts
            if kind != "search":
                skipped.append(f"{title}: {kind} bookmark has no live search")
                continue
            if not _SLUG_RE.match(slug):
                skipped.append(f"{title}: invalid search id")
                continue
            if slug not in seen:
                seen.add(slug)
                searches.append(SavedSearch(folder=folder, title=title, slug=slug))
    return ImportResult(tuple(searches), tuple(skipped))


def live_url(search: SavedSearch, league: str) -> str:
    return f"{TRADE_BASE}/{quote(league, safe='')}/{search.slug}/live"


def load(path: Path) -> ImportResult:
    try:
        return parse_exports(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ImportResult((), ())


def save(path: Path, text: str) -> ImportResult:
    """Validate first; only a paste with at least one usable search replaces
    the saved file, so a bad paste can never wipe working searches."""
    result = parse_exports(text)
    if result.searches:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result
