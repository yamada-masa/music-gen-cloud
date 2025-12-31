import os
import subprocess
import time
import json
import shutil
import platform

# Track the overall start time / 全体の開始時間を記録
overall_start = time.time()

def load_env_file(path=".env"):
    """Load .env file / .env ファイルを読み込む"""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

load_env_file()

def log_progress(message):
    """Print message with elapsed time / 経過時間と共にメッセージを表示"""
    elapsed = time.time() - overall_start
    print(f"[{elapsed:6.1f}s] {message}")

def get_env_or_error(key: str) -> str:
    """Get env var / 環境変数を取得"""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Error: Environment variable '{key}' is not set.")
    return value

# Config from .env
PROJECT = get_env_or_error("PROJECT")
IMAGE = get_env_or_error("IMAGE")
ZONE = os.getenv("ZONE", "us-east1-c")
JSONL_LOCAL = os.getenv("JSONL_LOCAL", "sample.jsonl")
OUTDIR = os.getenv("OUTDIR", "./downloaded_wav")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "musicgen-l4")
DELETE_VM = os.getenv("DELETE_VM", "True").lower() == "true"
MODEL_SIZE = os.getenv("MODEL_SIZE", "medium")

def cmd(name: str) -> str:
    """Return command name / OS に応じて実行ファイル名を返す"""
    system = platform.system().lower()
    if system.startswith("win"):
        cand = f"{name}.cmd"
        if shutil.which(cand):
            return cand
    return name

def wait_for_completion():
    """Monitor VM progress via metadata / メタデータを監視して進捗を表示"""
    log_progress(f"Monitoring VM: {INSTANCE_NAME}...")
    start_wait = time.time()

    while True:
        # Get progress status from metadata / メタデータから進捗を取得
        res = subprocess.run([cmd("gcloud"), "compute", "instances", "describe", INSTANCE_NAME, f"--zone={ZONE}", f"--project={PROJECT}", "--format=value(metadata.items.progress)"], capture_output=True, text=True)
        status = res.stdout.strip() or "Initializing"

        # Check if startup script finished via SSH / SSH経由で起動スクリプトの終了判定
        # Note: Needs gcloud auth and project access
        check = subprocess.run([cmd("gcloud"), "compute", "ssh", INSTANCE_NAME, f"--zone={ZONE}", "--project", PROJECT, "--command", "sudo journalctl -u google-startup-scripts.service --no-pager"], capture_output=True, text=True)

        if "Finished running startup scripts" in check.stdout:
            print("") # New line
            log_progress("VM task finished successfully.")
            break

        waiting_for = time.time() - start_wait
        print(f"  >>> Current Status: [{status}] ({waiting_for:.0f}s elapsed)      ", end="\r")
        time.sleep(10)

if __name__ == "__main__":
    try:
        log_progress("Starting MusicGen Cloud Pipeline")

        # Create Spot L4 Instance / Spot L4 インスタンスを作成
        log_progress(f"Creating Spot L4 Instance (Model: {MODEL_SIZE})...")
        
        # NOTE: --metadata-from-file is used for 'jsonl_payload' to prevent gcloud comma-parsing errors on Windows.
        # 注: Windowsでのカンマ区切り解析エラーを防ぐため、jsonl_payload はファイルから読み込ませます。
        
        create_args = [
            cmd("gcloud"), "compute", "instances", "create", INSTANCE_NAME,
            f"--project={PROJECT}", f"--zone={ZONE}",
            "--machine-type=g2-standard-4",
            "--accelerator=count=1,type=nvidia-l4",
            "--provisioning-model=SPOT",
            "--instance-termination-action=STOP",
            "--image-family=common-cu124-debian-11",
            "--image-project=ml-images",
            f"--metadata=image={IMAGE},model_size={MODEL_SIZE},progress=starting",
            f"--metadata-from-file=startup-script=run_musicgen.sh,jsonl_payload={JSONL_LOCAL}",
            "--scopes=https://www.googleapis.com/auth/cloud-platform"
        ]


        subprocess.run(create_args, check=True)
        
        # Monitor the process / 進捗を監視
        wait_for_completion()

        # Download result wav files / 結果のwavファイルをダウンロード
        log_progress(f"Downloading results to {OUTDIR}...")
        os.makedirs(OUTDIR, exist_ok=True)
        # scp result files / ファイルをローカルへ転送
        subprocess.run([cmd("gcloud"), "compute", "scp", "--recurse", f"{INSTANCE_NAME}:/opt/musicgen/out/*.wav", OUTDIR, f"--zone={ZONE}", f"--project={PROJECT}"], check=True)

    except Exception as e:
        log_progress(f"An error occurred: {e}")

    finally:
        # Final cleanup / 最終クリーンアップ（インスタンス削除）
        if DELETE_VM:
            log_progress(f"Deleting instance {INSTANCE_NAME}...")
            subprocess.run([cmd("gcloud"), "compute", "instances", "delete", INSTANCE_NAME, f"--zone={ZONE}", "--project", PROJECT, "--quiet"])