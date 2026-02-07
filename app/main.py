import logging

from fastapi import FastAPI

from app.routes.calls import router as calls_router
from app.routes.webhooks import router as webhooks_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Outbound Call Agent",
    description="KI-gestuetzter Outbound Call Agent mit Twilio und Claude",
    version="1.0.0",
)

app.include_router(calls_router)
app.include_router(webhooks_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
