from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter.depends import RateLimiter
from app.routes.auth import routes
from app.models.auth import create_db_and_tables
app = FastAPI()
router = APIRouter()
origins = ["*"]


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(routes)

@app.get(
    "/"
)
async def index():
    return {"msg": "Hello World"}