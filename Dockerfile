# --- Stage 1: Builder (dependency installation) ---
# --- ステージ1: ビルダー（依存関係のインストール） ---
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel AS builder

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install minimal build tools and rsync
# 最小限のビルドツールと rsync をインストール
RUN apt-get update && apt-get install -y --no-install-recommends git curl rsync && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
# uv をインストール（高速な Python パッケージインストーラー）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies from requirements file
# requirements ファイルから依存関係をインストール
COPY requirements-musicgen.txt .
RUN uv pip install --system -r requirements-musicgen.txt

# Install audiocraft separately WITHOUT dependencies to avoid PyAV (av) build errors
# 依存関係の問題や PyAV のビルドエラーを避けるため、本体のみを個別にインストール
RUN uv pip install --system --no-deps audiocraft==1.3.0 

# Remove PyAV import from audiocraft without importing it (avoids ModuleNotFoundError)
# Pythonを起動せずにパスを特定し、直接 sed で PyAV 依存を削除
RUN TARGET_FILE=$(find /opt/conda/lib -name "audio.py" | grep "audiocraft/data/audio.py") && sed -i '/import av/d' "$TARGET_FILE" 

# Create SAFE exclude list and slim down conda directory
# ヒアドキュメントを避け、Cloud Build 互換の printf に変更
RUN printf "lib/libmkl_*\ninclude/\nshare/doc/\nshare/man/\nshare/info/\n" > exclude.txt && \
    mkdir -p /opt/conda_slim && \
    rsync -aW --inplace --no-compress --exclude-from=exclude.txt /opt/conda/ /opt/conda_slim/

# Separate Python environment and Shared Libraries to prevent layer bloat/hangs
# レイヤーの巨大化とハングを防ぐため、Python環境と共有ライブラリを物理的に分離
RUN mkdir -p /opt/stage_lib /opt/stage_python && \
    mv /opt/conda_slim/lib/python3.10 /opt/stage_python/ && \
    mv /opt/conda_slim/lib /opt/stage_lib/

# --- Stage 2: Runtime (lightweight execution environment) ---
# --- ステージ2: ランタイム（軽量な実行環境） ---
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 1. Copy binaries first (Small layer) / まずバイナリをコピー（小レイヤー）
COPY --from=builder /opt/conda_slim/bin /opt/conda/bin

# 2. Copy shared libraries (Shared Lib layer - No Python files)
# 共有ライブラリをコピー（Python関連を含まないため、転送が安定）
COPY --from=builder /opt/stage_lib/lib /opt/conda/lib

# 3. Copy Python environment (Python layer - Including site-packages)
# Python環境一式をコピー（site-packages を含む独立したレイヤー）
COPY --from=builder /opt/stage_python/python3.10 /opt/conda/lib/python3.10

# Install ffmpeg (required for audio output)
# ffmpeg をインストール（音声出力に必須）
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy main execution script
# メインスクリプトをコピー
COPY music_gen_cloud.py .

# Ensure copied binaries are available in PATH
# コピーしたバイナリが PATH で利用できるように設定
ENV PATH="/opt/conda/bin:${PATH}"

ENTRYPOINT ["python", "music_gen_cloud.py"]