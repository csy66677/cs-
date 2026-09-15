import asyncio
from typing import Any, Dict, List, Optional
from app.services.retry import with_retry
iflow_fetch_timeout = 120
iflow_retry_attempts = 2
class IflowClient:
    def __init__(self, timeout_sec: int = iflow_fetch_timeout) -> None:
        self._timeout = timeout_sec
    def fetch(self, params: Optional[Dict[str, Any]] = None, headless: bool = True) -> List[Any]:
        from iflow.models import IflowQueryParams
        from iflow.fetcher import fetch_iflow_data
        p = params or {}
        query = IflowQueryParams(
            page_num=int(p.get("page_num", 1)),
            platforms=p.get("platforms", "buff-c5"),
            games=p.get("games", "csgo-dota2"),
            sort_by=p.get("sort_by", "sell"),
            min_price=float(p.get("min_price", 2)),
            max_price=float(p.get("max_price", 5000)),
            min_volume=int(p.get("min_volume", 200)),
            max_latency=int(p.get("max_latency", 0)),
            price_mode=p.get("price_mode", "buy"),
        )
        async def _do_fetch():
            return await asyncio.wait_for(
                fetch_iflow_data(query, headless=headless),
                timeout=float(self._timeout),
            )
        return asyncio.run(_do_fetch())
def fetch_iflow_rows(config: dict) -> List[Any]:
    iflow_cfg = config.get("iflow", {})
    client = IflowClient(timeout_sec=int(iflow_cfg.get("fetch_timeout", iflow_fetch_timeout)))
    params = {
        "page_num": iflow_cfg.get("page_num", 1),
        "platforms": iflow_cfg.get("platforms", "buff-c5"),
        "games": iflow_cfg.get("games", "csgo-dota2"),
        "sort_by": iflow_cfg.get("sort_by", "sell"),
        "min_price": iflow_cfg.get("min_price", 2),
        "max_price": iflow_cfg.get("max_price", 5000),
        "min_volume": iflow_cfg.get("min_volume", 200),
        "max_latency": iflow_cfg.get("max_latency", 0),
        "price_mode": iflow_cfg.get("price_mode", "buy"),
    }
    return client.fetch(params, headless=True)
