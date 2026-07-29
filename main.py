from fastapi import FastAPI

from src.routes.StudentRoutes import router as student_router
from src.routes.RecruiterRoutes import router as recruiter_router

app = FastAPI()

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