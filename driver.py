import os
import subprocess
import time
import shutil
import platform
import json  # JSONL 読み込み用

# Track overall start time
overall_start = time.time()

def load_env_file(path=".env"):
    """Load .env file / .env 読み込み"""
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
    """Log with time"""
    elapsed = time.time() - overall_start
    print(f"[{elapsed:6.1f}s] {message}")

def get_env_or_error(key: str) -> str:
    """Env get / 環境変数取得"""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Error: '{key}' is not set.")
    return value

# Config
PROJECT = get_env_or_error("PROJECT")
IMAGE = get_env_or_error("IMAGE")
ZONE = os.getenv("ZONE", "us-east1-c")
JSONL_LOCAL = os.getenv("JSONL_LOCAL", "sample.jsonl")
OUTDIR = os.getenv("OUTDIR", "./downloaded_wav")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "musicgen-l4-spot")
DELETE_VM = os.getenv("DELETE_VM", "True").lower() == "true"
MODEL_SIZE = os.getenv("MODEL_SIZE", "medium")

def cmd(name: str) -> str:
    """Check OS command / OS別コマンド名確認"""
    system = platform.system().lower()
    if system.startswith("win"):
        cand = f"{name}.cmd"
        if shutil.which(cand):
            return cand
    return name

def wait_for_completion(max_wait_seconds: int):
    """Monitor VM progress via journalctl / startup-script の終了をログで検知"""
    log_progress(f"Monitoring VM: {INSTANCE_NAME} (Max wait: {max_wait_seconds}s)...")
    start_wait = time.time()

    while True:
        # Check VM status
        res = subprocess.run(
            [
                cmd("gcloud"),
                "compute",
                "instances",
                "describe",
                INSTANCE_NAME,
                f"--zone={ZONE}",
                f"--project={PROJECT}",
                "--format=value(status)",
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            log_progress("Instance disappeared or check failed.")
            return False

        # Monitor via journalctl
        check = subprocess.run(
            [
                cmd("gcloud"),
                "compute",
                "ssh",
                INSTANCE_NAME,
                f"--zone={ZONE}",
                f"--project={PROJECT}",
                "--command",
                "sudo journalctl -u google-startup-scripts.service --no-pager",
            ],
            capture_output=True,
            text=True,
        )

        if "Finished running startup scripts" in check.stdout:
            print("")
            log_progress("VM task finished successfully.")
            return True

        # Dynamic timeout based on JSONL duration
        elapsed = time.time() - start_wait
        if elapsed > max_wait_seconds:
            log_progress(f"Timeout reaching {max_wait_seconds} seconds.")
            return False

        print(
            f"  >>> Waiting for completion... ({elapsed:.0f}s elapsed)      ",
            end="\r",
        )
        time.sleep(20)

def calc_dynamic_timeout(jsonl_path: str) -> int:
    """JSONL の duration 合計からタイムアウト秒数を計算"""
    total_duration = 0
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    total_duration += int(data.get("duration", 0))
                except Exception:
                    continue

    # medium × L4 前提のざっくり係数:
    # 生成時間 ≒ duration * 2.0〜2.5 + 起動オーバーヘッド
    base_overhead = 600  # 起動・pull 等で 10 分ぶん
    gen_factor = 2.0     # 1秒あたり2倍の余裕（かなり安全寄り）
    estimated = base_overhead + int(total_duration * gen_factor)

    # さらに 20% バッファ
    return int(estimated * 1.3)

if __name__ == "__main__":
    success = False
    try:
        log_progress("Starting Pipeline")

        # Calculate dynamic timeout from JSONL
        max_wait = calc_dynamic_timeout(JSONL_LOCAL)
        log_progress(f"Calculated dynamic timeout: {max_wait} seconds.")

        # Line ending fix
        for f_path in [JSONL_LOCAL, "run_musicgen.sh"]:
            if os.path.exists(f_path):
                with open(f_path, "rb") as f:
                    data = f.read()
                with open(f_path, "wb") as f:
                    f.write(data.replace(b"\r\n", b"\n"))

        # Create VM (Keep metadata-from-file as per original design)
        create_args = [
            cmd("gcloud"),
            "compute",
            "instances",
            "create",
            INSTANCE_NAME,
            f"--project={PROJECT}",
            f"--zone={ZONE}",
            "--machine-type=g2-standard-4",
            "--accelerator=count=1,type=nvidia-l4",
            "--provisioning-model=SPOT",
            "--instance-termination-action=DELETE",
            "--image-family=common-cu124-debian-11",
            "--image-project=ml-images",
            f"--metadata=install-nvidia-driver=True,image={IMAGE},model_size={MODEL_SIZE},progress=starting",
            f"--metadata-from-file=startup-script=run_musicgen.sh,jsonl_payload={JSONL_LOCAL}",
            "--scopes=https://www.googleapis.com/auth/cloud-platform",
        ]
        subprocess.run(create_args, check=True)

        # Start monitoring with dynamic timeout
        success = wait_for_completion(max_wait)

        if success:
            log_progress("Downloading results...")
            os.makedirs(OUTDIR, exist_ok=True)
            subprocess.run(
                [
                    cmd("gcloud"),
                    "compute",
                    "scp",
                    "--recurse",
                    f"{INSTANCE_NAME}:/opt/musicgen/out",
                    f"{OUTDIR}/",
                    f"--zone={ZONE}",
                    f"--project={PROJECT}",
                ],
                check=True,
            )

    except Exception as e:
        log_progress(f"Error: {e}")
    finally:
        if DELETE_VM:
            log_progress(f"Cleaning up {INSTANCE_NAME}...")
            subprocess.run(
                [
                    cmd("gcloud"),
                    "compute",
                    "instances",
                    "delete",
                    INSTANCE_NAME,
                    f"--zone={ZONE}",
                    "--project",
                    PROJECT,
                    "--quiet",
                ]
            )
