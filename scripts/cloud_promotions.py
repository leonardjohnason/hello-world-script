#!/usr/bin/env python3
"""Fetch current cloud service promotion/free-tier pages.

The script checks mainstream cloud provider offer pages and extracts a concise
summary plus relevant promotion links. It uses only Python's standard library.

Usage:
  python3 scripts/cloud_promotions.py
  python3 scripts/cloud_promotions.py --json
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen

KEYWORDS = (
    "free", "credit", "trial", "offer", "promo", "promotion", "discount",
    "startup", "always free", "free tier", "new customers", "grant",
)

PROVIDERS = [
    {
        "provider": "AWS",
        "url": "https://aws.amazon.com/free/",
        "fallback": "AWS Free Tier and trial offers for new and existing AWS customers.",
    },
    {
        "provider": "Microsoft Azure",
        "url": "https://azure.microsoft.com/en-us/pricing/offers/",
        "fallback": "Azure free account, credits, and pricing offers.",
    },
    {
        "provider": "Google Cloud",
        "url": "https://cloud.google.com/free",
        "fallback": "Google Cloud free program, credits, and Always Free products.",
    },
    {
        "provider": "Oracle Cloud",
        "url": "https://www.oracle.com/cloud/free/",
        "fallback": "Oracle Cloud Free Tier, trials, and Always Free services.",
    },
    {
        "provider": "IBM Cloud",
        "url": "https://www.ibm.com/cloud/free",
        "fallback": "IBM Cloud free tier and trial offerings.",
    },
    {
        "provider": "DigitalOcean",
        "url": "https://www.digitalocean.com/pricing/free-trial",
        "fallback": "DigitalOcean free trial credits and cloud platform offers.",
    },
    {
        "provider": "Cloudflare",
        "url": "https://www.cloudflare.com/plans/",
        "fallback": "Cloudflare free and paid plans for internet application services.",
    },
]


@dataclass
class Promotion:
    provider: str
    url: str
    status: str
    title: str
    summary: str
    relevant_links: list[dict[str, str]]
    fetched_at_unix: int


class SimpleHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.meta_description = ""
        self.links: list[tuple[str, str]] = []
        self._in_title = False
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        if tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "meta":
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            if name in {"description", "og:description", "twitter:description"} and not self.meta_description:
                self.meta_description = clean(attrs_dict.get("content", ""))
        elif tag.lower() == "a" and attrs_dict.get("href"):
            self._current_href = attrs_dict["href"]
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        elif tag.lower() == "a" and self._current_href:
            text = clean(" ".join(self._current_text))
            if text:
                self.links.append((self._current_href, text))
            self._current_href = None
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._current_href is not None:
            self._current_text.append(data)


def clean(value: str) -> str:
    value = html.unescape(value or "")
    return re.sub(r"\s+", " ", value).strip()


def fetch(url: str, timeout: int = 20) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; OpenClaw cloud-promotions/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def relevant_links(base_url: str, links: Iterable[tuple[str, str]], limit: int = 5) -> list[dict[str, str]]:
    seen = set()
    picked: list[dict[str, str]] = []
    for href, text in links:
        haystack = f"{href} {text}".lower()
        if not any(k in haystack for k in KEYWORDS):
            continue
        abs_url = urljoin(base_url, href)
        key = (abs_url, text.lower())
        if key in seen:
            continue
        seen.add(key)
        picked.append({"text": text[:120], "url": abs_url})
        if len(picked) >= limit:
            break
    return picked


def get_promotion(provider: dict[str, str]) -> Promotion:
    now = int(time.time())
    try:
        body = fetch(provider["url"])
        parser = SimpleHTMLExtractor()
        parser.feed(body)
        title = clean(" ".join(parser.title_parts)) or provider["provider"]
        summary = parser.meta_description or provider["fallback"]
        links = relevant_links(provider["url"], parser.links)
        return Promotion(provider["provider"], provider["url"], "ok", title, summary, links, now)
    except Exception as exc:  # Keep going even if one provider blocks scraping.
        return Promotion(
            provider["provider"],
            provider["url"],
            f"error: {exc.__class__.__name__}",
            provider["provider"],
            provider["fallback"],
            [],
            now,
        )


def render_text(promotions: list[Promotion]) -> str:
    lines = ["Latest cloud service promotions / free-tier pages", ""]
    for idx, item in enumerate(promotions, 1):
        lines.append(f"{idx}. {item.provider}: {item.title}")
        lines.append(f"   Summary: {item.summary}")
        lines.append(f"   Page: {item.url}")
        if item.relevant_links:
            lines.append("   Relevant links:")
            for link in item.relevant_links[:3]:
                lines.append(f"   - {link['text']}: {link['url']}")
        if item.status != "ok":
            lines.append(f"   Note: live fetch had {item.status}; fallback summary shown.")
        lines.append("")
    return "\n".join(lines).strip()


def main() -> int:
    argp = argparse.ArgumentParser(description="Fetch latest cloud service promotions/free-tier pages.")
    argp.add_argument("--json", action="store_true", help="Output JSON instead of text")
    args = argp.parse_args()

    promotions = [get_promotion(p) for p in PROVIDERS]
    if args.json:
        print(json.dumps([asdict(p) for p in promotions], ensure_ascii=False, indent=2))
    else:
        print(render_text(promotions))

    ok_count = sum(1 for p in promotions if p.status == "ok")
    return 0 if ok_count >= 3 else 2


if __name__ == "__main__":
    sys.exit(main())
