FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install audiocraft

# Create app directory
WORKDIR /app

# Copy script
COPY music_gen_cloud.py /app/music_gen_cloud.py

# Default command (can be overridden)
ENTRYPOINT ["python", "/app/music_gen_cloud.py"]



