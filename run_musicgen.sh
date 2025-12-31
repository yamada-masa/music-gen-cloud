#!/bin/bash
# run_musicgen.sh

# --- Configuration / 設定 ---
IMAGE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/image)
MODEL_SIZE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/model_size || echo "medium")
JSONL_DATA=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/jsonl_payload)

WORKDIR="/opt/musicgen"
OUTDIR="${WORKDIR}/out"
INPUT="${WORKDIR}/input.jsonl"
mkdir -p "${OUTDIR}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

# Update progress function / 進捗更新関数
update_progress() {
    log "Status: $1"
    curl -s -X POST \
        -H "Metadata-Flavor: Google" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data-urlencode "progress=$1" \
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/"
}

# 1. Wait for GPU Readiness / GPUの準備完了を待機
log "Checking GPU status..."
until nvidia-smi; do
    log "GPU not ready. Waiting 10s..."
    sleep 10
done

update_progress "Preparing"

# 2. Setup environment / 環境構築
log "Restoring JSONL and pulling image..."
printf "%s\n" "$JSONL_DATA" > "${INPUT}"
gcloud auth configure-docker us-east1-docker.pkg.dev -q
docker pull "${IMAGE}"

update_progress "Generating"
log "EXECUTION_STARTED"

# 3. Execution / 実行
docker run --gpus all -i --rm -v "${OUTDIR}:/out" "${IMAGE}" --model "${MODEL_SIZE}" --output /out < "${INPUT}"

# 4. Completion / 完了報告
update_progress "Finalizing"
log "EXECUTION_FINISHED"
log "All processes completed."

# driver.py が journalctl で検知するための終了シグナル
echo "Finished running startup scripts"
