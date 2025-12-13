"""
FastAPI application for the E-commerce Product Scraper API.

This API provides endpoints to access scraped product data with AI enrichments.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.api.routes import products


# Create FastAPI application
app = FastAPI(
    title="E-commerce Product Scraper API",
    description="API for accessing scraped product data with AI-generated enrichments",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "E-commerce Product Scraper API",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
