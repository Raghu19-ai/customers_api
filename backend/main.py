from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from routers.customer_router import router as customer_router, addr_router
from routers.auth_routes import router as auth_router

from utils.exceptions import CustomException
from utils.logger import logger
from utils.rate_limiter import limiter
from utils.context import correlation_id_var

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import uuid


# App Initialization
app = FastAPI(
    title="Customer API",
    description="""
    Advanced Customer Management System with:
    * **Correlation ID Tracking** (via `X-Correlation-ID` header)
    * **JWT Authentication** & Role-Based Access
    * **Rate Limiting** & Structured Logging
    """,
    version="1.1.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    openapi_tags=[
        {"name": "Auth", "description": "Authentication and User Management"},
        {"name": "Customers", "description": "Customer Profile Operations"},
        {"name": "Addresses", "description": "Geographic Data Management"},
    ]
)



# Middleware (ORDER MATTERS)

#  1. Correlation ID Middleware (FIRST)
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)

    response = await call_next(request)

    # attach to response header
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# 2. Logging Middleware (SECOND)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


#  3. Rate Limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


#  4. CORS Middleware (OUTERMOST)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)



# Startup Event
@app.on_event("startup")
def on_startup():
    logger.info("Application started successfully with MongoDB")



# Exception Handlers

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests"}
    )


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logger.error(f"{exc.message} | Status Code: {exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()} | Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )



# Routers
app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(addr_router)



# Root API
@app.get("/")
def home():
    return {"message": "API is running"}