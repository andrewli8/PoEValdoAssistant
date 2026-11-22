"""App.open_live_searches: imported Better Trading searches open as live
tabs in the sniper Chrome, spaced out, and never before the profile exists."""

import base64
import json

from conftest import make_config

from sniper import __main__ as main_mod
from sniper.__main__ import App
from sniper.bus import Bus, Notice


def export(*slugs: str) -> str:
    trs = [{"tit": f"t{s}", "loc": f"1:search:{s}"} for s in slugs]
    body = {"icn": None, "tit": "Valdo", "ver": "1", "trs": trs}
    return "3:" + base64.b64encode(json.dumps(body).encode()).decode()


def setup(monkeypatch, tmp_path, first_run=False):
    app = App(make_config(), Bus())
    app.book._league = "Covens"
    opened, sleeps = [], []
    monkeypatch.setattr(main_mod.browser, "open_url", lambda *u: opened.extend(u) or "chrome")
    monkeypatch.setattr(main_mod.browser, "is_first_run", lambda: first_run)

    async def fake_sleep(s):
        sleeps.append(s)

    monkeypatch.setattr(main_mod.asyncio, "sleep", fake_sleep)
    path = tmp_path / "searches.txt"
    return app, path, opened, sleeps


async def test_opens_each_search_live_with_spacing(monkeypatch, tmp_path):
    app, path, opened, sleeps = setup(monkeypatch, tmp_path)
    path.write_text(export("Aa1", "Bb2", "Cc3"))
    await app.open_live_searches(path)
    assert opened == [
        f"https://www.pathofexile.com/trade/search/Covens/{s}/live" for s in ("Aa1", "Bb2", "Cc3")
    ]
    assert sleeps == [main_mod.SEARCH_SPACING_S] * 2


async def test_first_run_opens_setup_page_instead(monkeypatch, tmp_path):
    app, path, opened, _ = setup(monkeypatch, tmp_path, first_run=True)
    path.write_text(export("Aa1"))
    await app.open_live_searches(path)
    assert len(opened) == 1 and opened[0].endswith(":8765/")
    assert not any("/trade/search/" in u for u in opened)


async def test_nothing_imported_says_so(monkeypatch, tmp_path):
    app, path, opened, _ = setup(monkeypatch, tmp_path)
    await app.open_live_searches(path)
    assert opened == []
    notes = [e for e in app.bus.drain() if isinstance(e, Notice)]
    assert notes and not notes[-1].ok
