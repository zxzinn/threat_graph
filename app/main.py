import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import uvicorn
from app.routes.view import router as view_router
from app.routes.auth import router as auth_router
from app.routes.wazuh import router as wazuh_router
from app.routes.manage import router as manage_router
from app.routes.agent_detail import router as agent_detail_router
from app.routes.modbus_events import router as modbus_events_router
from app.routes.dashboard import router as dashboard_router
from app.routes.rds import router as rds_router
from app.models.user_db import Base, engine
from app.ext.error_handler import add_error_handlers
from fastapi.middleware.cors import CORSMiddleware  


# Load environment variables
load_dotenv()

# Set up centralized application logger
def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    os.makedirs('./logs', exist_ok=True)
        
    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Create centralized logger
app_logger = setup_logger('app_logger', './logs/app.log', level=logging.DEBUG)
logging.getLogger('app_logger').addHandler(logging.StreamHandler())

app = FastAPI(
    title="AIXSOAR ATH API",
    description="API description",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    app_logger.info("Initializing database...")
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database initialized successfully")
    except Exception as e:
        app_logger.error(f"Failed to initialize database: {str(e)}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(view_router, prefix="/api/view")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(wazuh_router, prefix="/api/wazuh") 
app.include_router(manage_router, prefix="/api/manage")
app.include_router(agent_detail_router, prefix="/api/agent_detail")
app.include_router(modbus_events_router, prefix="/api/modbus_events")
app.include_router(dashboard_router, prefix="/api/dashboard")
app.include_router(rds_router, prefix="/api/rds")

# Include error handlers
add_error_handlers(app)

# Serve the HTML file at the root URL
@app.get("/", response_class=HTMLResponse)
async def get_html():
    with open(Path("static/index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)