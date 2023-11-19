import time
from fastapi import FastAPI, Request
from datetime import datetime
import asyncio
from services import message_queue_services,rate_limiter
from slowapi import _rate_limit_exceeded_handler
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from datetime import datetime
from routes import auth,ingestor

# Configure logging
from logger.logging import get_logger
logger = get_logger(__name__)


    
app = FastAPI()
# Add the rate limit handler and middleware to the app
app.state.limiter = rate_limiter.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# Directory for static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def start_consumer():
    logger.info("Initiating consumer ...")
    asyncio.create_task(message_queue_services.aio_pika_consumer())
    logger.info("Consumer started")

async def api_timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Logging the API call and its execution time
    logger.info(f"API call: {request.url.path} completed in {process_time} seconds")

    return response
    
app.middleware("http")(api_timing_middleware)    

app.include_router(auth.router)
app.include_router(ingestor.router)
