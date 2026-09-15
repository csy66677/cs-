from typing import Optional
from .client import get_page_content
from .models import IflowQueryParams, IflowRow, build_iflow_url
from .parser import parse_table
async def fetch_iflow_data(
    params: Optional[IflowQueryParams] = None,
    **client_kw,
) -> list[IflowRow]:
    url = build_iflow_url(params)
    html = await get_page_content(url, **client_kw)
    return parse_table(html)
