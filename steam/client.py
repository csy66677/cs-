import json
import os
from typing import Optional, Union
from urllib.parse import quote, unquote, urlparse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CURRENCY_CNY = "CNY"
CURRENCY_USD = "USD"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://steamcommunity.com/market/",
}
def _extract_line1(html: str) -> Optional[list]:
    prefix = "var line1="
    i = html.find(prefix)
    if i == -1:
        return None
    start = i + len(prefix)
    if start >= len(html) or html[start] != "[":
        return None
    depth = 0
    for j in range(start, len(html)):
        c = html[j]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return json.loads(html[start : j + 1])
    return None
def detect_currency(html: str) -> Optional[str]:  
    s = html or ""
    if "¥" in s or "CNY" in s or "RMB" in s or "人民币" in s:
        return CURRENCY_CNY
    if "HK$" in s or "HKD" in s:
        return "HKD"
    if "₹" in s or "INR" in s:
        return "INR"
    if "₽" in s or "RUB" in s:
        return "RUB"
    if "€" in s or "EUR" in s:
        return "EUR"
    if "₺" in s or "TRY" in s:
        return "TRY"
    if "R$" in s or "BRL" in s:
        return "BRL"
    if "ARS" in s or "AR$" in s:
        return "ARS"
    if "CLP" in s or "CL$" in s:
        return "CLP"
    if "¥" in s or "JPY" in s:
        return "JPY"
    if "USD" in s or "US$" in s or " USD" in s or '"USD"' in s:
        return CURRENCY_USD
    if "$" in s:  
        return CURRENCY_USD
    return None
def build_listing_url(market_hash_name: str, app_id: int = 730) -> str:
    encoded = quote(market_hash_name, safe="")
    return f"https://steamcommunity.com/market/listings/{app_id}/{encoded}"
def market_hash_name_from_listing_url(url: str) -> Optional[str]:
    if not url or "steamcommunity.com/market/listings/" not in url:
        return None
    parsed = urlparse(url)
    path = (parsed.path or "").rstrip("/")
    if not path:
        return None
    name_encoded = path.split("/")[-1]
    if not name_encoded:
        return None
    return unquote(name_encoded)
def _parse_cookie_str(s: str) -> dict:
    out = {}
    for part in (s or "").split(";"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            out[k.strip()] = v.strip()
    return out
def fetch_history(
    market_hash_name: str,
    app_id: int = 730,
    *,
    headers: Optional[dict] = None,
    timeout: int = 15,
    verify: bool = False,
    proxies: Optional[dict] = None,
    cookies: Optional[Union[dict, str]] = None,
    return_currency: bool = False,
) -> Union[Optional[list], Optional[dict]]:
    encoded = quote(market_hash_name, safe="")
    url = f"https://steamcommunity.com/market/pricehistory/?appid={app_id}&market_hash_name={encoded}"
    h = {**DEFAULT_HEADERS, **(headers or {})}
    if proxies is None:
        px = {}
        if os.environ.get("HTTP_PROXY"):
            px["http"] = os.environ["HTTP_PROXY"]
        if os.environ.get("HTTPS_PROXY"):
            px["https"] = os.environ["HTTPS_PROXY"]
        proxies = px if px else None
    if isinstance(cookies, str):
        cookies = _parse_cookie_str(cookies)
    try:
        resp = requests.get(
            url,
            headers=h,
            verify=verify,
            proxies=proxies,
            cookies=cookies,
            timeout=timeout,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data or not data.get("success") or "prices" not in data:
            return None
        history = data["prices"]
        if return_currency:
            currency_clue = data.get("price_prefix", "") + data.get("price_suffix", "")
            currency = detect_currency(currency_clue)
            if not currency:
                currency = detect_currency(resp.text)
            return {"history": history, "currency": currency}
        return history
    except Exception:
        return None
