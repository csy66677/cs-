from bs4 import BeautifulSoup
from .models import IflowRow
def _text(td) -> str:
    if td is None:
        return ""
    return (td.get_text() or "").strip()
def _href(td) -> str:
    if td is None:
        return ""
    a = td.find("a", href=True)
    return a["href"] if a else ""
def _safe_td(row, i: int):
    try:
        cells = row.find_all("td")
        return cells[i] if i < len(cells) else None
    except (IndexError, AttributeError):
        return None
def parse_table(html: str) -> list[IflowRow]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr", class_="ant-table-row")
    result = []
    for tr in rows:
        try:
            result.append(
                IflowRow(
                    index=_text(_safe_td(tr, 0)),
                    name=_text(_safe_td(tr, 1)),
                    volume=_text(_safe_td(tr, 2)),
                    min_price=_text(_safe_td(tr, 3)),
                    sell_ratio=_text(_safe_td(tr, 4)),
                    buy_ratio=_text(_safe_td(tr, 5)),
                    safe_buy_ratio=_text(_safe_td(tr, 6)),
                    recent_ratio=_text(_safe_td(tr, 7)),
                    platform=_href(_safe_td(tr, 8)),
                    steam_link=_href(_safe_td(tr, 9)),
                    update_time=_text(_safe_td(tr, 10)),
                )
            )
        except Exception:
            continue
    return result
