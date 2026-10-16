from fastapi import FastAPI

from routers.explain import router as explain_router

app = FastAPI(
    title="Explain This Error API",
    description="AI-powered error explanations for VS Code",
    version="1.0.0",
)

@app.get("/")
def home():
    return {"message": "Explain This Error API is running!"}

app.include_router(explain_router)
