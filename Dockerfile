# Use official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the working directory
COPY . /app/

# # Expose the port FastAPI will run on
# EXPOSE 8000

# # Run FastAPI with Uvicorn (the ASGI server)
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
