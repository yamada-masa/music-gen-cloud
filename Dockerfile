FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY music_gen_cloud.py /app/music_gen_cloud.py
COPY requirements-musicgen.txt /app/requirements-musicgen.txt

# conda の pip を使う（これが重要）
RUN /opt/conda/bin/pip install --no-deps audiocraft==1.3.0

# MusicGen に必要な依存だけ uv で一括インストール
RUN uv pip install --system -r /app/requirements-musicgen.txt

# PyAV を使う行を自動削除（パスを自動検出）
RUN AUDIO_PY=$(find /opt/conda/lib -type f -path "*/site-packages/audiocraft/data/audio.py") && \
    sed -i '/import av/d' "$AUDIO_PY" 

ENTRYPOINT ["python3", "/app/music_gen_cloud.py"]

