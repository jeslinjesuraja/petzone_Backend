from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from db.session import Base, engine
from routers.users import router as userrouter
from routers.pets import router as petrouter
from routers.message import router as messagerouter
from routers.payments import router as paymentsrouter

app = FastAPI()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

print("Server is starting up...")

Base.metadata.create_all(bind=engine)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:8000",
    "file://"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for now to be safe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def greet():
    return {"message": "Hello World"}

# Include Routers
app.include_router(userrouter)
app.include_router(petrouter)
app.include_router(messagerouter)
app.include_router(paymentsrouter)
