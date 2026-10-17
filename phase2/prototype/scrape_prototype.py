"""Minimal Phase 2 prototype: find and download a few policy documents.

Starts from the policy index page, collects links that look like policy
documents (by file extension), downloads a small number of them under a
hard request budget, and prints metadata so the outcome can be judged.

Standard library only, so it runs with any Python 3.10+ (no `uv sync`
needed). It is a proof of concept, not the production scraper.
"""

from __future__ import annotations

import argparse
import http.client
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlsplit

DEFAULT_START_URL = "https://uwa-policy.cits5501.arranstewart.io/policy/"
USER_AGENT = "CITS5501-Group15-prototype/0.1 (student project)"
MIN_DOCS = 3  # the brief asks for 3-5 distinct documents
MAX_REQUESTS = 20  # the brief allows at most 20 requests in total

# Extensions we treat as "policy documents" (office files and PDFs).
DOCUMENT_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".rtf", ".odt",
    ".xls", ".xlsx", ".ppt", ".pptx",
)

# Leading bytes ("magic numbers") for each family of file we expect.
SIGNATURES = {
    "pdf": (b"%PDF-",),
    "zip": (b"PK\x03\x04",),  # .docx/.xlsx/.pptx/.odt are ZIP containers
    "ole2": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),  # legacy .doc/.xls/.ppt
    "rtf": (b"{\\rtf",),
}
EXPECTED_SIGNATURE = {
    ".pdf": "pdf",
    ".docx": "zip", ".xlsx": "zip", ".pptx": "zip", ".odt": "zip",
    ".doc": "ole2", ".xls": "ole2", ".ppt": "ole2",
    ".rtf": "rtf",
}


class _LinkCollector(HTMLParser):
    """Collects the href of every <a> element, in document order."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value.strip())


def extension_of(url: str) -> str:
    """Lower-cased file extension of the URL path ('' if none)."""
    path = urlsplit(url).path.lower()
    last = path.rsplit("/", 1)[-1]
    return "." + last.rsplit(".", 1)[-1] if "." in last else ""


def extract_document_links(html: str, base_url: str) -> list[str]:
    """Absolute, de-duplicated document links on the same host as base_url."""
    collector = _LinkCollector()
    collector.feed(html)
    base_host = urlsplit(base_url).netloc.lower()
    seen: set[str] = set()
    links: list[str] = []
    for href in collector.hrefs:
        url, _fragment = urldefrag(urljoin(base_url, href))
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or parts.netloc.lower() != base_host:
            continue  # other websites, mailto:, tel:, javascript:
        if extension_of(url) not in DOCUMENT_EXTENSIONS:
            continue
        if url not in seen:  # exact match: the site's paths are case-sensitive
            seen.add(url)
            links.append(url)
    return links


def pick_varied(links: list[str], count: int) -> list[str]:
    """Pick up to `count` links, cycling through extensions for variety."""
    by_ext: dict[str, list[str]] = {}
    for url in links:
        by_ext.setdefault(extension_of(url), []).append(url)
    picked: list[str] = []
    while len(picked) < count and any(by_ext.values()):
        for bucket in by_ext.values():
            if bucket and len(picked) < count:
                picked.append(bucket.pop(0))
    return picked


def sniff(data: bytes) -> str:
    """Name of the file family the leading bytes indicate."""
    for family, prefixes in SIGNATURES.items():
        if data.startswith(prefixes):
            return family
    head = data[:512].lstrip().lower()
    if head.startswith((b"<!doctype html", b"<html")) or b"<html" in head:
        return "html"
    return "unknown"


@dataclass
class FetchResult:
    url: str
    status: int | None
    content_type: str
    size: int
    head: bytes
    retry_after: str | None = None
    error: str | None = None
    body: bytes = b""


class _BudgetedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Counts every redirect hop against the fetcher's request budget."""

    def __init__(self, fetcher: Fetcher) -> None:
        self.fetcher = fetcher

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if self.fetcher.used >= self.fetcher.max_requests:
            return None  # urllib then reports the 3xx itself as an HTTPError
        self.fetcher.used += 1
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Fetcher:
    """Plain GET client that refuses to exceed a fixed request budget.

    Every HTTP request counts, including redirect hops and retries.
    """

    def __init__(self, max_requests: int, delay: float, timeout: float) -> None:
        if not 1 <= max_requests <= MAX_REQUESTS:
            raise ValueError(f"max_requests must be between 1 and {MAX_REQUESTS}")
        self.max_requests = max_requests
        self.delay = delay
        self.timeout = timeout
        self.used = 0
        self._opener = urllib.request.build_opener(_BudgetedRedirectHandler(self))

    def get(self, url: str, pause: bool = True) -> FetchResult:
        if self.used >= self.max_requests:
            raise RuntimeError(f"request budget of {self.max_requests} exhausted")
        if pause and self.used and self.delay:
            time.sleep(self.delay)  # space requests out rather than hitting the live site rapidly
        self.used += 1
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with self._opener.open(request, timeout=self.timeout) as resp:
                body = resp.read()
                return FetchResult(url, resp.status, resp.headers.get("Content-Type", ""),
                                   len(body), body[:16], body=body)
        except urllib.error.HTTPError as exc:  # 4xx/5xx still carry metadata
            body = exc.read()
            return FetchResult(url, exc.code, exc.headers.get("Content-Type", ""),
                               len(body), body[:16], exc.headers.get("Retry-After"),
                               body=body)
        except http.client.IncompleteRead as exc:  # connection dropped mid-body
            return FetchResult(url, None, "", len(exc.partial), exc.partial[:16],
                               error=f"incomplete download, {len(exc.partial)} bytes received")
        except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
            return FetchResult(url, None, "", 0, b"", error=str(exc))


def verdict(result: FetchResult) -> str:
    """Judge one download: OK only if 200 and the bytes match the extension."""
    if result.error:
        return f"FAILED ({result.error})"
    if result.status != 200:
        return f"FAILED (HTTP {result.status})"
    expected = EXPECTED_SIGNATURE.get(extension_of(result.url))
    found = sniff(result.head)
    if expected and found != expected:
        return f"SUSPECT (expected {expected} bytes, got {found})"
    return f"OK ({found} signature)"


def get_with_one_retry(fetcher: Fetcher, url: str, max_wait: float = 15.0) -> FetchResult:
    """GET once; on 429 wait for Retry-After (capped) and try exactly once more.

    Only the numeric (seconds) form of Retry-After is understood; anything
    else, such as an HTTP date, falls back to waiting max_wait.
    """
    result = fetcher.get(url)
    if result.status == 429 and fetcher.used < fetcher.max_requests:
        try:
            wait = float(result.retry_after or fetcher.delay)
        except ValueError:
            wait = max_wait
        wait = max(0.0, min(wait, max_wait))
        print(f"  429 Too Many Requests; waiting {wait:.0f}s and retrying once")
        time.sleep(wait)
        result = fetcher.get(url, pause=False)  # already waited
    return result


def run(start_url: str, max_docs: int, max_requests: int, delay: float,
        timeout: float) -> list[FetchResult]:
    fetcher = Fetcher(max_requests, delay, timeout)
    print(f"Index page: {start_url}")
    index = get_with_one_retry(fetcher, start_url)
    if index.status != 200:
        print(f"Could not load index page: {index.error or f'HTTP {index.status}'}")
        return []
    html = index.body.decode("utf-8", errors="replace")
    links = extract_document_links(html, start_url)
    counts: dict[str, int] = {}
    for url in links:
        counts[extension_of(url)] = counts.get(extension_of(url), 0) + 1
    summary = ", ".join(f"{ext} x{n}" for ext, n in sorted(counts.items()))
    print(f"Found {len(links)} candidate document links ({summary})")
    if len(links) < MIN_DOCS:
        print(f"Warning: fewer than {MIN_DOCS} candidates; the page layout may have changed.")

    results: list[FetchResult] = []
    for n, url in enumerate(pick_varied(links, max_docs), start=1):
        if fetcher.used >= max_requests:
            print("Request budget exhausted; stopping.")
            break
        print(f"\n[{n}] {url}")
        result = get_with_one_retry(fetcher, url)
        results.append(result)
        print(f"  HTTP status   : {result.status}")
        print(f"  Content-Type  : {result.content_type or '-'}")
        print(f"  Size (bytes)  : {result.size}")
        print(f"  Initial bytes : {result.head!r}")
        print(f"  Outcome       : {verdict(result)}")

    ok = sum(verdict(r).startswith("OK") for r in results)
    print(f"\n{ok}/{len(results)} documents downloaded and look valid; "
          f"{fetcher.used}/{max_requests} requests used.")
    return results


def request_budget(text: str) -> int:
    """argparse type for --max-requests: an integer from 1 to MAX_REQUESTS."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid int value: {text!r}") from None
    if not 1 <= value <= MAX_REQUESTS:
        raise argparse.ArgumentTypeError(f"must be between 1 and {MAX_REQUESTS}, got {value}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start-url", default=DEFAULT_START_URL,
                        help="index page to start from (default: the course site)")
    parser.add_argument("--max-docs", type=int, default=5, choices=range(MIN_DOCS, 6),
                        metavar="{3,4,5}",
                        help="number of documents to download, 3-5 (default 5)")
    parser.add_argument("--max-requests", type=request_budget, default=MAX_REQUESTS,
                        metavar="N",
                        help=f"hard cap on HTTP requests, incl. index, 1-{MAX_REQUESTS} "
                             f"(default {MAX_REQUESTS})")
    parser.add_argument("--delay", type=float, default=3.5,
                        help="seconds between requests (default 3.5)")
    parser.add_argument("--timeout", type=float, default=15.0,
                        help="per-request timeout in seconds (default 15)")
    args = parser.parse_args(argv)
    results = run(args.start_url, args.max_docs, args.max_requests, args.delay, args.timeout)
    enough = len(results) >= MIN_DOCS
    return 0 if enough and all(verdict(r).startswith("OK") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
