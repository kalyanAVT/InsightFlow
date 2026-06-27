import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.routes import router

# Load environment variables
load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(
        title="InsightFlow",
        description="Autonomous Research & Competitive Intelligence Agent",
        version="0.1.0-step1"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router, prefix="/api/v1")
    
    @app.on_event("startup")
    async def startup():
        print("InsightFlow Step 1 starting up...")
        print(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'groq')}")
        print(f"Qdrant URL: {os.getenv('QDRANT_URL', 'not set')}")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)