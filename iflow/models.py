from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode, urlunparse
@dataclass(frozen=True)
class IflowQueryParams:
    page_num: int = 1
    platforms: str = "buff-c5"
    games: str = "csgo-dota2"
    sort_by: str = "sell"
    min_price: float = 2
    max_price: float = 5000
    min_volume: int = 200
    max_latency: int = 0
    price_mode: str = "buy"
    def to_query(self) -> dict:
        return {
            "page_num": self.page_num,
            "platforms": self.platforms,
            "games": self.games,
            "sort_by": self.sort_by,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "min_volume": self.min_volume,
            "max_latency": self.max_latency,
            "price_mode": self.price_mode,
        }
def build_iflow_url(params: Optional[IflowQueryParams] = None) -> str:
    p = params or IflowQueryParams()
    query = urlencode(p.to_query())
    return urlunparse(("https", "www.iflow.work", "/", "", query, ""))
@dataclass
class IflowRow:
    index: str
    name: str
    volume: str
    min_price: str
    sell_ratio: str
    buy_ratio: str
    safe_buy_ratio: str
    recent_ratio: str
    platform: str
    steam_link: str
    update_time: str
