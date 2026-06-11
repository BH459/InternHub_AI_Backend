from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.StudentRoutes import router as student_router
from src.routes.RecruiterRoutes import router as recruiter_router

app = FastAPI()

# CORS setup
origins = [
    "https://internhub-backend-fqmw.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Student routes
app.include_router(
    student_router,
    prefix="/student",
    tags=["Student"]
)

# Recruiter routes
app.include_router(
    recruiter_router,
    prefix="/recruiter",
    tags=["Recruiter"]
)

@app.get("/", tags=["Home"])
def home():
    return {
        "message": "FastAPI Server Running"
    }