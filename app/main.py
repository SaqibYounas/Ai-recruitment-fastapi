from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

app = FastAPI()

origins = [
"http://localhost:8080",
]

app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

@app.get(
"/",
dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5))))],
)
async def index():
    return {"msg": "Hello World"}
