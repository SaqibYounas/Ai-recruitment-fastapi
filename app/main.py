from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter.depends import RateLimiter
from app.routes.auth import routes
from app.models.auth import create_db
app = FastAPI()
router = APIRouter()
origins = ["*"]


@app.on_event("startup")
def on_startup():
     create_db()

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