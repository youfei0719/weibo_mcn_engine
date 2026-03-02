import sys, traceback

try:
    import os, multiprocessing, subprocess
    from contextlib import asynccontextmanager
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from pydantic import BaseModel, Field
    
    from database import init_db
    from spider import MasterSpiderEngine

    def release_port(port):
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if f":{port}" in line and 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass

    engine = MasterSpiderEngine()

    def get_resource_path(relative_path):
        return os.path.join(sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath("."), relative_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await init_db()
        await engine.start()
        yield
        await engine.close()

    app = FastAPI(title="Weibo MCN Batch Engine", lifespan=lifespan)

    class CollectRequest(BaseModel):
        target: str = Field(...)

    @app.get("/")
    async def get_index():
        return FileResponse(get_resource_path("index.html"))

    @app.post("/api/v1/login")
    async def trigger_auth():
        await engine.trigger_manual_login()
        return {"status": "success"}

    @app.post("/api/v1/collect")
    async def collect_data(request: CollectRequest):
        try:
            data = await engine.collect_all(request.target)
            return {"status": "success", "data": data}
            
        except Exception as e:
            err_msg = str(e)
            print(f"\n⚠️ [追踪] 目标 '{request.target}' 异常: {err_msg}")
            
            if "AUTH_EXPIRED" in err_msg:
                raise HTTPException(status_code=401, detail="WEIQ授权已失效，需重新扫码登录")
            elif "WEIQ_VERIFY_BLOCKED" in err_msg:
                raise HTTPException(status_code=403, detail="WEIQ触发防爬滑块验证码，需人工滑动")
            elif "NETWORK_ERROR" in err_msg:
                raise HTTPException(status_code=429, detail="服务器网络动荡或请求被重置")
            elif "WEIQ_NO_DATA" in err_msg:
                return {"status": "failed", "detail": "WEIQ未收录该账号报价"}
            elif "ID_NOT_FOUND" in err_msg:
                return {"status": "failed", "detail": "解析不到UID或查无此人"}
            else:
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"底层代码崩溃: {type(e).__name__}")

    if __name__ == "__main__":
        multiprocessing.freeze_support()
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
        release_port(8000)
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000, workers=1)

except Exception as e:
    print("\n" + "!" * 60)
    print("🚨 致命报错拦截成功：")
    traceback.print_exc()
    print("!" * 60 + "\n")
    input("请截图发给我，按回车键退出...")
    sys.exit(1)