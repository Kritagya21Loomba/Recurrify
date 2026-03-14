from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from recurrify.api.routes_parse import router as parse_router
from recurrify.api.routes_solve import router as solve_router
from recurrify.api.routes_guided import router as guided_router

app = FastAPI(
    title="Recurrify",
    description="A recurrence-relation solver, explainer, and verifier for algorithm students.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse_router)
app.include_router(solve_router)
app.include_router(guided_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
