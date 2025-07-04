# backend/Dockerfile

# Use a lightweight Python base image
FROM python:3.11-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app

# Create and set the working directory
WORKDIR $APP_HOME

# Copy the requirements file and install dependencies
# Use a separate step for copying requirements and installing them
# to leverage Docker's build cache. If only requirements change,
# this step will be rebuilt, but not the base image or earlier steps.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application using Uvicorn
# We use 0.0.0.0 to make it accessible from outside the container
# --host 0.0.0.0 is crucial for Docker
# --reload is removed for production-like environments (handled by docker-compose for dev)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
