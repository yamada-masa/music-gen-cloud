# --- Stage 1: Builder (dependency installation) ---
# --- ステージ1: ビルダー（依存関係のインストール） ---
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel AS builder

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install minimal build tools / 最小限のビルドツールをインストール
RUN apt-get update && apt-get install -y --no-install-recommends git curl && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer) / uv をインストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies from requirements file / 依存関係をインストール
COPY requirements-musicgen.txt .
RUN uv pip install --system -r requirements-musicgen.txt

# Install audiocraft separately WITHOUT dependencies to avoid PyAV (av) build errors
# 依存関係の問題や PyAV のビルドエラーを避けるため、本体のみを個別にインストール
RUN uv pip install --system --no-deps audiocraft==1.3.0 

# Remove PyAV import from audiocraft without importing it (avoids ModuleNotFoundError)
# Pythonを起動せずにパスを特定し、直接 sed で PyAV 依存を削除
RUN TARGET_FILE=$(find /opt/conda/lib -name "audio.py" | grep "audiocraft/data/audio.py") && sed -i '/import av/d' "$TARGET_FILE" 

# --- Stage 2: Runtime (lightweight execution environment) ---
# --- ステージ2: ランタイム（軽量な実行環境） ---
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Copy Python libs and GPU-related shared libraries (.so)
# Python ライブラリと GPU 関連の共有ライブラリ (.so) をコピー
COPY --from=builder /opt/conda/lib /opt/conda/lib

# Copy binaries (used by xformers, accelerate, etc.)
# バイナリをコピー（xformers や accelerate が内部で使用）
COPY --from=builder /opt/conda/bin /opt/conda/bin

# Install ffmpeg (required for audio output) / ffmpeg をインストール
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy main script / メインスクリプトをコピー
COPY music_gen_cloud.py .

# Ensure copied binaries are available in PATH / バイナリが PATH で利用可能に設定
ENV PATH="/opt/conda/bin:${PATH}"

ENTRYPOINT ["python", "music_gen_cloud.py"]