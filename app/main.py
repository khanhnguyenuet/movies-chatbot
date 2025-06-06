from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import keyword_router, suggestion_router, web_search_router, verify_router, pipeline

app = FastAPI(
    title="Movie recommendations",
    description="API for extracting and analyzing documents",
    version="1.0.0",
)

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(keyword_router.router)
api_router.include_router(suggestion_router.router)
api_router.include_router(web_search_router.router)
api_router.include_router(verify_router.router)
api_router.include_router(pipeline.router)

# Include the main router
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "INT6024 - Movie recommendations API"}