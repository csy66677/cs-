import sys
import threading
from collections import Counter
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _构造代理管理器(entries: list):
    """用假数据直接构造 ProxyManager，跳过读配置文件"""
    from utils.proxy_manager import ProxyManager
    with patch.object(ProxyManager, "_reload", return_value=None):
        mgr = ProxyManager.__new__(ProxyManager)
        mgr._lock = threading.Lock()
        mgr._warming_up = False
        mgr._proxies = entries
        mgr._cached_strategy = 2  # 完全走代理
        mgr._cached_enabled = True
        mgr._proxy_configs = [p["config"] for p in entries]
        mgr._proxy_weights = [max(0, p["score"]) for p in entries]
    return mgr


def test_代理_score为0的永远不被选():
    entries = [
        {"config": {"host": "好的", "port": 80},  "score": 1000},
        {"config": {"host": "坏的",  "port": 80},  "score": 0},
    ]
    mgr = _构造代理管理器(entries)
    结果 = [mgr.get_next_proxy_dict() for _ in range(200)]
    hosts = [d["http"].split("//")[1].split(":")[0] for d in 结果 if d]
    assert "坏的" not in hosts, f"score=0的代理不应被选中: {Counter(hosts)}"
    assert "好的" in hosts


def test_代理_空池返回None():
    mgr = _构造代理管理器([])
    assert mgr.get_next_proxy_dict() is None


def test_代理_全挂了返回None():
    # 所有代理score都是0
    entries = [
        {"config": {"host": "死的1", "port": 80}, "score": 0},
        {"config": {"host": "死的2", "port": 80}, "score": 0},
    ]
    mgr = _构造代理管理器(entries)
    assert mgr.get_next_proxy_dict() is None


def test_代理_高分代理被选得明显更多():
    # score=9000 vs score=100，跑500次看分布
    entries = [
        {"config": {"host": "快代理", "port": 80}, "score": 9000},
        {"config": {"host": "慢代理", "port": 80}, "score": 100},
    ]
    mgr = _构造代理管理器(entries)
    结果 = [mgr.get_next_proxy_dict() for _ in range(500)]
    hosts = [d["http"].split("//")[1].split(":")[0] for d in 结果 if d]
    counts = Counter(hosts)
    # 快代理至少应该比慢代理多5倍
    assert counts["快代理"] > counts["慢代理"] * 5, f"高分代理没被优先选: {counts}"
