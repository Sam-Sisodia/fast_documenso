from fastapi import FastAPI
from apps.users.view import router as user_router

app = FastAPI()

# Register the router
app.include_router(user_router, prefix="/users", tags=["Users"])


from fastapi.middleware.cors import CORSMiddleware



origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000"
    "http://localhost:3001",
    "http://172.19.0.1:3001",
    "http://127.0.0.1:3001"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
