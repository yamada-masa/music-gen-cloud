#!/bin/bash
# Startup script for musicgen generation / MusicGen 生成用のスタートアップスクリプト
set -euo pipefail

# Update progress metadata / 進捗メタデータを更新する関数
update_progress() {
    curl -X PUT -H "Metadata-Flavor: Google" -d "$1" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/progress"
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

update_progress "Setting up environment"
log "Starting startup script..."

# Fetch metadata / メタデータ取得
IMAGE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/image)
JSONL_DATA=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/jsonl_payload)
MODEL_SIZE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/model_size || echo "medium")

WORKDIR="/opt/musicgen"
OUTDIR="${WORKDIR}/out"
INPUT="${WORKDIR}/input.jsonl"
mkdir -p "${OUTDIR}"

# Restore JSONL / JSONL復元
printf "%s\n" "$JSONL_DATA" > "${INPUT}"

update_progress "Pulling Docker image"
gcloud auth configure-docker us-east1-docker.pkg.dev -q
docker pull "${IMAGE}"

update_progress "Generating Music (${MODEL_SIZE})"
log "Starting MusicGen Docker with model: ${MODEL_SIZE}"

# Run container / コンテナ実行
docker run -i --rm -v "${OUTDIR}:/out" "${IMAGE}" --model "${MODEL_SIZE}" --output /out < "${INPUT}"

update_progress "Finalizing"
log "All processes completed."