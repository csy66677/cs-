"""Gift routes – Steam 自动赠礼 API."""
import threading
import uuid
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.config_loader import get_steam_credentials
from app import gift_engine
router = APIRouter()
_gift_tasks: dict[str, dict] = {}
_task_lock = threading.Lock()
def _new_task(task_id: str):
    with _task_lock:
        _gift_tasks[task_id] = {
            "id": task_id,
            "status": "pending",   
            "progress": [],        
            "result": None,
        }
def _append_progress(task_id: str, step: dict):
    with _task_lock:
        task = _gift_tasks.get(task_id)
        if task:
            task["progress"].append(step)
            if step.get("done"):
                task["status"] = "done" if step.get("ok") else "error"
                task["result"] = step
def _get_task(task_id: str) -> Optional[dict]:
    with _task_lock:
        t = _gift_tasks.get(task_id)
        return dict(t) if t else None
def _get_cookies_raw() -> str:
    """从凭证配置中获取完整 cookies 字符串。"""
    creds = get_steam_credentials()
    return creds.get("cookies", "")
def _get_steam_id() -> str:
    """从凭证配置中获取 steam_id。"""
    creds = get_steam_credentials()
    return creds.get("steam_id", "")
def _check_cookies(cookies_raw: str) -> Optional[dict]:
    """检查 cookies 中是否包含必要的登录字段，不满足时返回错误 dict。"""
    if not cookies_raw:
        return {"ok": False, "error": "Steam 凭证未配置，请先登录 Steam"}
    lower = cookies_raw.lower()
    if "steamloginsecure=" not in lower:
        return {"ok": False, "error": "Steam 凭证未配置，请先登录 Steam"}
    return None
@router.get("/api/gift/friends")
def api_get_friends():
    cookies_raw = _get_cookies_raw()
    err = _check_cookies(cookies_raw)
    if err:
        return err
    steam_id = _get_steam_id()
    if not steam_id:
        return {"ok": False, "error": "Steam steam_id 未配置"}
    try:
        friends = gift_engine.get_friend_list(cookies_raw, steam_id)
        return {"ok": True, "friends": friends, "count": len(friends)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
class EditionsBody(BaseModel):
    store_url: str
@router.post("/api/gift/editions")
def api_get_editions(body: EditionsBody):
    cookies_raw = _get_cookies_raw()
    err = _check_cookies(cookies_raw)
    if err:
        return err
    app_id = gift_engine.extract_appid_from_url(body.store_url)
    if not app_id:
        return {"ok": False, "error": "无法从链接中解析 App ID"}
    try:
        editions, game_title, og_image = gift_engine.get_all_available_editions(app_id, cookies_raw)
        return {"ok": True, "app_id": app_id, "title": game_title, "image": og_image, "editions": editions}
    except Exception as e:
        return {"ok": False, "error": str(e)}
class GiftBody(BaseModel):
    friend_steamid: str
    item_id: str
    item_type: str  
@router.post("/api/gift/send")
def api_gift_send(body: GiftBody):
    cookies_raw = _get_cookies_raw()
    err = _check_cookies(cookies_raw)
    if err:
        return err
    task_id = str(uuid.uuid4())
    _new_task(task_id)
    def _run():
        with _task_lock:
            t = _gift_tasks.get(task_id)
            if t:
                t["status"] = "running"
        gen = gift_engine.run_gift_flow(
            cookies_raw=cookies_raw,
            friend_steamid=body.friend_steamid,
            item_id=body.item_id,
            item_type=body.item_type,
        )
        for step in gen:
            _append_progress(task_id, step)
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return {"ok": True, "task_id": task_id}
@router.get("/api/gift/task/{task_id}")
def api_gift_task(task_id: str):
    task = _get_task(task_id)
    if not task:
        return {"ok": False, "error": "任务不存在"}
    return {"ok": True, "task": task}
@router.get("/api/gift/balance")
def api_gift_balance():
    cookies_raw = _get_cookies_raw()
    err = _check_cookies(cookies_raw)
    if err:
        return err
    try:
        info = gift_engine.get_wallet_balance(cookies_raw)
        return {"ok": True, **info}
    except Exception as e:
        return {"ok": False, "error": str(e)}
@router.get("/api/gift/debug-config")
def api_gift_debug_config():
    """临时调试：查看 Steam store_user_config 的原始字段"""
    cookies_raw = _get_cookies_raw()
    err = _check_cookies(cookies_raw)
    if err:
        return err
    try:
        _, country_code, config_data = gift_engine.get_base_auth_status(cookies_raw)
        wallet_fields = {k: v for k, v in config_data.items() if "wallet" in k.lower() or "balance" in k.lower() or "currency" in k.lower()}
        return {"ok": True, "country_code": country_code, "wallet_fields": wallet_fields, "all_keys": list(config_data.keys())}
    except Exception as e:
        return {"ok": False, "error": str(e)}
