"""Pipeline start/stop routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.pipeline import start_pipeline
from app.state import request_stop, set_status, log
router = APIRouter()
class ConfigBody(BaseModel):
    config: dict
@router.post("/api/pipeline/start")
def api_pipeline_start(body: ConfigBody):
    start_pipeline(body.config)
    return {"ok": True}
@router.post("/api/pipeline/stop")
def api_pipeline_stop():
    request_stop()
    log("接收到停止运行指令，正在终止任务...", level="warn", category="system")
    set_status("stopped", "正在停止并清理...")
    return {"ok": True}
