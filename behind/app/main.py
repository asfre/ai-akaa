from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, chat, stats

app = FastAPI(
    title="AI Knowledge Assistant API",
    description="AI知识助理后端API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计"])

@app.get("/")
async def root():
    return {"message": "AI Knowledge Assistant API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "AI Knowledge Assistant"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)