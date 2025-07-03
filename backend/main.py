from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI(
    title="Issues & Insights Tracker API",
    description="API for managing issues and insights.",
    version="0.1.0"
)

# Define a root endpoint to test the API
@app.get("/")
async def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Issues & Insights Tracker API!"}