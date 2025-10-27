import asyncio
import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_408_REQUEST_TIMEOUT

from app.routers import health, verification

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="TTB Label Verification System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nfthomas-ttb-label-app.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add timeout middleware
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=60.0)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=HTTP_408_REQUEST_TIMEOUT, content={"detail": "Request timeout"}
        )


# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(verification.router, prefix="/api", tags=["verification"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # Log unexpected errors
    logging.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
