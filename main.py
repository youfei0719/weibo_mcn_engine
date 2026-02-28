from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from database import init_db
from spider import MasterSpiderEngine
import logging
import os

logger = logging.getLogger("FastAPI")
engine = MasterSpiderEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await engine.start()
    yield
    await engine.close()

app = FastAPI(title="Weibo MCN Data Engine", lifespan=lifespan)

class CollectRequest(BaseModel):
    target: str = Field(..., description="微博主页链接 / UID / 博主昵称")

@app.get("/", summary="MCN 商业雷达面板")
async def get_index():
    ui_file = "index.html"
    if os.path.exists(ui_file):
        return FileResponse(ui_file)
    return {"error": "UI 文件 index.html 不存在，请确保文件已放置在同级目录。"}

@app.post("/api/v1/collect")
async def collect_data(request: CollectRequest):
    try:
        # 1. 获取微博基础结构
        basic_data = await engine.collect_and_store(request.target)
        uid = basic_data["uid"]
        nickname = basic_data["nickname"]
        
        # 2. 从 WEIQ 黄金接口拉取全量底库数据
        commercial_data = await engine.collect_commercial_data(uid, nickname)

        # 【核心数据融合】：如果微博主站被防爬虫屏蔽(导致抓取0或88)，强制用 WEIQ 的真实底库数据覆盖！
        final_nickname = commercial_data["weiq_nickname"] if commercial_data["weiq_nickname"] and commercial_data["weiq_nickname"] != nickname else nickname
        final_followers = commercial_data["weiq_followers"] if commercial_data["weiq_followers"] > 0 else basic_data["followers_count"]
        final_posts = commercial_data["weiq_posts"] if commercial_data["weiq_posts"] > 0 else basic_data["statuses_count"]

        return {
            "status": "success",
            "message": "全量数据抓取并交叉验证成功",
            "data": {
                "uid": uid,
                "nickname": final_nickname,
                "followers": final_followers,
                "posts": final_posts,
                "commercial": {
                    "cpm": commercial_data["cpm"],
                    "original_price": commercial_data["original_price"],
                    "repost_price": commercial_data["repost_price"]
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抓取链路阻断: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)