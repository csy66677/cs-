import math
from typing import List, Optional, Tuple
USD_TO_CNY_DEFAULT = 7.2
CURRENCY_CNY = "CNY"
CURRENCY_USD = "USD"
g_rgWalletInfo = {
    "rwgrsn": -2,
    "success": True,
    "wallet_balance": "14669",
    "wallet_country": "CN",
    "wallet_currency": 23,
    "wallet_currency_increment": "1",
    "wallet_delayed_balance": "356",
    "wallet_fee": "1",
    "wallet_fee_base": "0",
    "wallet_fee_minimum": "7",
    "wallet_fee_percent": "0.05",
    "wallet_market_minimum": "7",
    "wallet_max_balance": "1400000",
    "wallet_publisher_fee_percent_default": "0.10",
    "wallet_state": "",
    "wallet_trade_max_balance": "1260000"
}


def calculate_fee(base_amt: int, pct: float, rg_wallet: dict) -> int:
    if pct > 0:
        return max(int(rg_wallet['wallet_fee_minimum']), math.floor(base_amt * pct))
    return 0


def get_total_with_fees(base_amt: int, ppct: float, spct: float, rg_wallet: dict) -> int:
    n_base = base_amt
    n_pub_fee = calculate_fee(base_amt, ppct, rg_wallet)
    n_steam_fee = calculate_fee(base_amt, spct, rg_wallet)
    return n_base + n_pub_fee + n_steam_fee


def to_valid_market_price(n_price: int, rg_wallet: dict) -> int:
    n_floor = int(rg_wallet['wallet_market_minimum'])
    n_increment = int(rg_wallet['wallet_currency_increment'])
    if n_price <= n_floor:
        return n_floor
    if n_increment > 1:
        d_amount = n_price / n_increment
        d_sign = -1 if d_amount < 0 else 1
        d_amount = (d_sign * math.floor(abs(d_amount) + 0.5)) * n_increment
        return int(d_amount)
    return n_price


def get_item_price_from_total(n_total: int, rg_wallet: dict) -> int:
    ppct = float(rg_wallet['wallet_publisher_fee_percent_default'])
    spct = float(rg_wallet['wallet_fee_percent'])
    n_increment = int(rg_wallet['wallet_currency_increment'])
    n_floor = int(rg_wallet['wallet_market_minimum'])
    n_fee_min = int(rg_wallet['wallet_fee_minimum'])
    
    n_initial_guess = math.floor(n_total / (1.0 + ppct + spct))
    n_max_base = n_total - (2 * n_fee_min)
    n_base = to_valid_market_price(min(n_initial_guess, n_max_base), rg_wallet)
    
    for _ in range(3):
        n_calculated = get_total_with_fees(n_base, ppct, spct, rg_wallet)
        if n_calculated == n_total:
            return n_base
        if n_calculated < n_total:
            n_base += n_increment
        else:
            n_base -= n_increment
            break
    return max(n_floor, n_base)


def usd_to_cny(amount: float, rate: float = USD_TO_CNY_DEFAULT) -> float:
    return amount * rate
def apply_currency(
    prices: List[float],
    currency: Optional[str],
    usd_to_cny_rate: float = USD_TO_CNY_DEFAULT,
) -> Tuple[List[float], str]:
    if currency == CURRENCY_USD:
        return [p * usd_to_cny_rate for p in prices], CURRENCY_CNY
    return prices, (currency or CURRENCY_CNY)
def yuan_to_cents(yuan: float) -> int:
    return max(1, int(round(yuan * 100)))


def list_price_display_to_cents(display_amount: float, account_currency: str = "CNY") -> int:
    display_amount = round(display_amount, 2)
    total_cents = max(1, int(round(display_amount * 100)))
    
    wallet_info = dict(g_rgWalletInfo)
    if account_currency.upper() != "CNY":
        wallet_info["wallet_fee_minimum"] = "1"
        wallet_info["wallet_market_minimum"] = "1"
        
    return get_item_price_from_total(total_cents, wallet_info)
def cents_to_yuan(cents: int) -> float:
    return cents / 100.0
