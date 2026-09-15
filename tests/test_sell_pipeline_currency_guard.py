"""货币守卫回归测试 – 工厂重置后非CNY账号安全性"""
# 覆盖三个关键场景：
# 1. 汇率缺失（重置后 exchange_rate.json 已删除）→ _build_listing_plan 必须返回 []
# 2. 汇率正常 → 价格正确换算后上架
# 3. 无账号（重置后账号列表为空）→ _run_sell_phase_impl 提前返回不调用 _build_listing_plan

from unittest.mock import MagicMock, patch
import pytest


# ------------------------------------------------------------------ helpers --

def _make_sellable():
    return [{
        "name": "AK-47 | Redline",
        "market_hash_name": "AK-47 | Redline",
        "assetid": "12345678",
        "can_sell": True,
        "appid": 730,
        "contextid": "2",
    }]


def _build_ctx(logged_errors):
    """返回一个会把 log 调用追加到 logged_errors 列表的 MagicMock ctx。"""
    ctx = MagicMock()
    ctx.is_stop_requested.return_value = False
    ctx.debug.return_value = None

    def _log(msg, level="info", **kw):
        logged_errors.append((level, msg))

    ctx.log.side_effect = _log
    return ctx


# ------------------------------------------------------------------ test 1 ---

def test_missing_rate_aborts_listing_plan():
    """账号币种=INR，rate_map 为空（汇率文件被工厂重置删除）→ 返回 [] 且记录 error"""
    from app.sell_pipeline import _build_listing_plan

    logged = []
    ctx = _build_ctx(logged)

    orders = {"sell_orders": [{"price": 30000, "quantity": 3}]}

    with patch("app.sell_pipeline.get_sell_orders_cny", return_value=orders), \
         patch("app.sell_pipeline.compute_smart_list_price", return_value=(300.0, "wall")):

        result = _build_listing_plan(
            ctx=ctx,
            cfg={"pipeline": {}},
            session=MagicMock(),
            sellable=_make_sellable(),
            sell_strategy=1,
            pipeline_cfg={},
            purchases_snapshot=[],
            ok_listings=False,
            active_listing_ids=set(),
            listing_assetid_to_name={},
            assetid_to_name_map={},
            account_currency="INR",
            rate_map={},        # 关键：汇率文件已删除
        )

    assert result == [], "汇率缺失时必须终止整批上架，返回空列表"
    errors = [msg for lvl, msg in logged if lvl == "error"]
    assert errors, f"应当记录 error 级别日志，实际 logged={logged}"
    assert any("INR" in e for e in errors), f"error 日志应提及币种 INR，实际: {errors}"


# ------------------------------------------------------------------ test 2 ---

def test_valid_rate_converts_price():
    """rate_map 含 INR 时，price_cents 应按汇率换算而非直接用 CNY 分值"""
    from app.sell_pipeline import _build_listing_plan
    from utils.money import list_price_display_to_cents

    inr_rate = 11.5          # 1 CNY ≈ 11.5 INR
    cny_price = 300.0
    expected_inr = round(cny_price / inr_rate, 2)

    logged = []
    ctx = _build_ctx(logged)

    orders = {"sell_orders": [{"price": 30000, "quantity": 3}]}

    with patch("app.sell_pipeline.get_sell_orders_cny", return_value=orders), \
         patch("app.sell_pipeline.compute_smart_list_price", return_value=(cny_price, "wall")):

        result = _build_listing_plan(
            ctx=ctx,
            cfg={"pipeline": {}},
            session=MagicMock(),
            sellable=_make_sellable(),
            sell_strategy=1,
            pipeline_cfg={},
            purchases_snapshot=[],
            ok_listings=False,
            active_listing_ids=set(),
            listing_assetid_to_name={},
            assetid_to_name_map={},
            account_currency="INR",
            rate_map={"INR": inr_rate},
        )

    assert len(result) == 1, "汇率正常时应生成 1 条上架计划"
    expected_cents = list_price_display_to_cents(expected_inr)
    actual_cents = result[0]["price_cents"]
    assert actual_cents == expected_cents, (
        f"价格换算错误: 期望 {expected_cents} 分 (≈₹{expected_inr}), 实际 {actual_cents} 分"
    )


# ------------------------------------------------------------------ test 3 ---

def test_no_account_skips_sell_phase():
    """工厂重置后 get_current_account 返回 None → _run_sell_phase_impl 提前返回"""
    from app.sell_pipeline import _run_sell_phase_impl

    state = MagicMock()
    state.get_purchases.return_value = []

    with patch("app.sell_pipeline.get_steam_credentials",
               return_value={"steam_id": "x", "session_id": "y", "cookies": "z=v"}), \
         patch("app.sell_pipeline._resolve_steam_session",
               return_value=(MagicMock(), "sid")), \
         patch("app.sell_pipeline._get_inventory",
               return_value=[{"can_sell": True, "assetid": "1",
                              "name": "Knife", "appid": 730}]), \
         patch("app.sell_pipeline.fetch_my_listings",
               return_value=(True, set(), "", {})), \
         patch("app.sell_pipeline.get_current_account", return_value=None), \
         patch("app.sell_pipeline._build_listing_plan") as mock_plan:

        _run_sell_phase_impl({"pipeline": {}}, state, "test-flow")

    mock_plan.assert_not_called()
