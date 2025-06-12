FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY app/ .

# Create uploads directory
RUN mkdir -p uploads

# Expose Streamlit port
EXPOSE 8501

# Set environment variables
ENV ENVIRONMENT=container
ENV USE_S3=false

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]