"""Event link enrichment.

Fetches an event page, pulls structured hints (OpenGraph / JSON-LD /
title), then asks DeepSeek to normalize them into canonical fields plus a
`match_key` so the *same real-world event* listed on different platforms
collapses to one matchable event.
"""

import ipaddress
import json
import os
import re
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _is_safe_url(url: str) -> bool:
    """Block non-http(s) and private/loopback targets (basic SSRF guard)."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False
        infos = socket.getaddrinfo(parsed.hostname, None)
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
            ):
                return False
        return True
    except Exception:
        return False


def _slug(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def _fallback_match_key(d: dict) -> str:
    parts = [
        _slug(d.get("performer") or d.get("title", "")),
        _slug(d.get("city", "")),
        (d.get("date") or "")[:10],
    ]
    return "|".join(p for p in parts if p)


def scrape(url: str) -> dict:
    """Best-effort metadata from OpenGraph / JSON-LD / <title>."""
    out: dict = {"source_url": url}
    try:
        resp = httpx.get(
            url, headers={"User-Agent": _UA}, follow_redirects=True, timeout=12
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        def og(prop):
            tag = soup.find("meta", property=prop)
            return tag["content"].strip() if tag and tag.get("content") else ""

        out["title"] = og("og:title") or (
            soup.title.string.strip() if soup.title and soup.title.string else ""
        )
        out["description"] = og("og:description")
        out["image_url"] = og("og:image")

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
            except Exception:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and "Event" in str(
                    item.get("@type", "")
                ):
                    out["title"] = item.get("name") or out["title"]
                    out["date"] = item.get("startDate", "")
                    loc = item.get("location", {})
                    if isinstance(loc, dict):
                        out["venue"] = loc.get("name", "")
                        addr = loc.get("address", {})
                        if isinstance(addr, dict):
                            out["city"] = addr.get("addressLocality", "")
                    perf = item.get("performer")
                    if isinstance(perf, list) and perf:
                        perf = perf[0]
                    if isinstance(perf, dict):
                        out["performer"] = perf.get("name", "")
    except Exception:
        pass
    return out


async def _ai_normalize(scraped: dict) -> dict | None:
    if not GEMINI_API_KEY:
        return None
    prompt = (
        "You normalize event listings so the same real-world event from "
        "different ticketing sites can be matched. Given the scraped data, "
        "return STRICT JSON with keys: title, performer, category "
        "(one of: concert, nightlife, festival, hike, meetup, sports, "
        "conference, other), venue, city, date (ISO 8601 or empty), "
        "description (<=200 chars), and match_key. match_key MUST be a "
        "lowercase canonical id of the form "
        "'<performer-or-title-slug>|<city-slug>|<YYYY-MM-DD>' that is "
        "identical for the same event regardless of platform. "
        "Return ONLY valid JSON, no markdown.\n\n"
        f"Scraped data:\n{json.dumps(scraped, ensure_ascii=False)[:4000]}"
    )
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [
                        {
                            "parts": [{"text": prompt}],
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                    },
                },
            )
        resp.raise_for_status()
        content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(content)
    except Exception:
        return None


async def enrich(url: str) -> dict:
    """Return normalized event fields + match_key for a pasted link."""
    if not _is_safe_url(url):
        return {
            "external_url": url,
            "title": "",
            "category": "other",
            "ai_enriched": False,
            "error": "URL could not be fetched safely.",
        }

    scraped = scrape(url)
    ai = await _ai_normalize(scraped)

    if ai:
        result = {
            "title": ai.get("title") or scraped.get("title", ""),
            "performer": ai.get("performer", ""),
            "category": ai.get("category", "other"),
            "venue": ai.get("venue", ""),
            "city": ai.get("city", ""),
            "starts_at": ai.get("date") or None,
            "description": ai.get("description", ""),
            "image_url": scraped.get("image_url", ""),
            "match_key": ai.get("match_key") or _fallback_match_key(ai),
            "ai_enriched": True,
        }
    else:
        result = {
            "title": scraped.get("title", ""),
            "performer": scraped.get("performer", ""),
            "category": "other",
            "venue": scraped.get("venue", ""),
            "city": scraped.get("city", ""),
            "starts_at": scraped.get("date") or None,
            "description": scraped.get("description", ""),
            "image_url": scraped.get("image_url", ""),
            "match_key": _fallback_match_key(scraped),
            "ai_enriched": False,
        }

    result["external_url"] = url
    location = ", ".join(p for p in [result["venue"], result["city"]] if p)
    result["location"] = location
    if not result["match_key"]:
        result["match_key"] = _slug(result["title"]) or _slug(url)
    return result
