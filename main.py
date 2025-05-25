import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger
import time
from contextlib import asynccontextmanager
import os

from app.api.routes import router
from app.models.database import create_tables
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logging.info("🚀 LP管理系统启动")
    try:
        # 测试数据库连接
        from app.models.database import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logging.info("✅ 数据库连接成功")
    except Exception as e:
        logging.warning(f"⚠️  数据库连接失败: {e}")
    
    yield
    
    # 关闭时
    logging.info("🛑 LP管理系统关闭")

# 创建FastAPI应用
app = FastAPI(
    title="🥞 PancakeSwap V3 LP管理系统",
    description="""
    **高性能LP流动性头寸管理系统**
    
    ## 🌟 主要功能
    - 🔗 **OKX钱包API集成** - 支持多链钱包管理
    - 🥞 **PancakeSwap V3 LP管理** - 创建、监控LP头寸
    - 💰 **多链支持** - BSC、Ethereum、Polygon
    - 📊 **实时监控** - 区块链数据实时读取
    - ⚡ **批量操作** - 高效批量创建和管理
    - 🔄 **自动重平衡** - 智能重平衡策略
    - 🖥️ **现代化Web界面** - 响应式设计
    
    ## 🛠️ 技术栈
    - **后端**: FastAPI + SQLAlchemy + MySQL
    - **区块链**: Web3.py + PancakeSwap V3 合约
    - **前端**: HTML5 + CSS3 + JavaScript
    - **API集成**: OKX Wallet API
    
    ## 📚 API文档
    - **Swagger UI**: [/docs](/docs)
    - **ReDoc**: [/redoc](/redoc)
    - **Web界面**: [/](/web)
    """,
    version="1.0.0",
    contact={
        "name": "LP管理系统",
        "url": "https://github.com/your-repo",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    logger.info(f"请求完成: {request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    
    return response

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常捕获: {request.method} {request.url} - {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "error": str(exc)
        }
    )

# 注册路由
app.include_router(router, prefix="/api/v1", tags=["LP管理"])

# 静态文件服务
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def serve_web_interface():
        """提供Web管理界面"""
        return FileResponse('static/index.html')
    
    @app.get("/web")
    async def web_interface():
        """Web界面入口"""
        return FileResponse('static/index.html')
else:
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "🥞 PancakeSwap V3 LP管理系统",
            "version": "1.0.0",
            "status": "运行中",
            "features": [
                "🔗 OKX钱包API集成",
                "🥞 PancakeSwap V3 LP管理", 
                "💰 多链支持 (BSC, Ethereum, Polygon)",
                "📊 实时头寸监控",
                "⚡ 批量操作",
                "🔄 自动重平衡"
            ],
            "endpoints": {
                "api_docs": "/docs",
                "redoc": "/redoc",
                "health": "/api/v1/health",
                "lp_positions": "/api/v1/lp/positions/{wallet_address}",
                "create_position": "/api/v1/lp/create",
                "auto_rebalance": "/api/v1/lp/auto-rebalance/config"
            },
            "note": "Web界面需要配置静态文件目录"
        }

# 健康检查（直接路由，不需要前缀）
@app.get("/health", tags=["系统"])
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "message": "🥞 LP管理系统运行正常",
        "version": "1.0.0"
    }

# 404错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "页面未找到",
            "message": "请检查URL路径是否正确",
            "available_endpoints": {
                "Web界面": "/",
                "API文档": "/docs", 
                "健康检查": "/health",
                "LP头寸API": "/api/v1/lp/positions/{wallet_address}"
            }
        }
    )

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 OKX钱包LP管理系统启动中...")
    
    try:
        # 检查数据库连接（非阻塞）
        try:
            await create_tables()
            logger.info("✅ 数据库连接成功，表创建完成")
        except Exception as db_error:
            logger.warning(f"⚠️  数据库连接失败，将在无数据库模式下运行: {db_error}")
            logger.info("💡 您可以稍后启动PostgreSQL数据库服务")
        
        # 验证配置
        if settings.okx_api_key == "your_okx_api_key_here":
            logger.warning("⚠️  请配置OKX API密钥")
        
        logger.info("🎉 系统启动完成!")
        logger.info("📍 API文档地址:")
        logger.info("   - Swagger UI: http://localhost:8000/docs")
        logger.info("   - ReDoc: http://localhost:8000/redoc")
        logger.info("   - 健康检查: http://localhost:8000/api/v1/health")
        
    except Exception as e:
        logger.error(f"❌ 系统启动失败: {e}")
        # 不再抛出异常，允许系统在降级模式下运行
        logger.info("🔄 系统将在降级模式下运行")

# 关闭事件  
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("👋 OKX钱包LP管理系统正在关闭...")

if __name__ == "__main__":
    # 配置日志
    logger.add(
        settings.log_file_path,
        rotation="1 day",
        retention="30 days",
        level=settings.log_level
    )
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    ) 