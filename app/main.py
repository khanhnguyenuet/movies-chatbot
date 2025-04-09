from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import keyword_router, suggestion_router, verify_router

import uvicorn

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
api_router.include_router(verify_router.router)

# Include the main router
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "INT6024 - Movie recommendations API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)