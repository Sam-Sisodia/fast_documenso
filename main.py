from fastapi import FastAPI
from apps.users.view import router as user_router

app = FastAPI()

# Register the router
app.include_router(user_router, prefix="/users", tags=["Users"])