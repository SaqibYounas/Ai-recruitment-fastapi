from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
from routes.auth import auth
app = FastAPI()
router = APIRouter()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_limiter = Limiter(Rate(2, Duration.SECOND * 5))


app.include_router(auth)

@app.get(
    "/",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)
async def index():
    return {"msg": "Hello World"}