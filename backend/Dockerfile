# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000
RUN DJANGO_SECRET_KEY=placeholder-build-key \
    OPENAI_API_KEY=placeholder \
    AZURE_CONNECTION_STRING=placeholder \
    AZURE_CONTAINER_NAME=placeholder \
    python manage.py collectstatic --noinput

CMD ["gunicorn", "user_service.wsgi:application", "--bind", "0.0.0.0:8000"]
