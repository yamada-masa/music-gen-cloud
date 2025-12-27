import argparse
import sys
import json
import os
import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

# ----------------------------------------
# Defaults for batch jobs (can be overridden per job)
# バッチジョブ用のデフォルト値（ジョブごとに上書き可能）
# ----------------------------------------
DEFAULTS = {
    "prompt": "ambient",               # Default prompt / デフォルトのプロンプト
    "duration": 10,                     # Default duration in seconds / デフォルトの長さ（秒）
    "seed": None,                       # Default: random seed / デフォルト：ランダムシード
    "filename_tag": "music",            # Base filename tag / ファイル名の共通プレフィックス
    "batch_size": 1,                    # How many times to repeat this job / このジョブを何セット繰り返すか
    "num_tracks": 1                     # Tracks per batch (multi-track) / 1セットあたり何トラック生成するか
} 


def merge_with_defaults(job: dict) -> dict:
    """
    Merge a single job dict with DEFAULTS.
    DEFAULTS are used when a key is missing or None in the job.

    1つのジョブ dict に DEFAULTS をマージする。
    ジョブ側で指定が無い（または None）の項目は DEFAULTS の値で補完する。
    """
    merged = DEFAULTS.copy()
    for k, v in job.items():
        if v is not None:
            merged[k] = v
    return merged


def generate_single_track(model: MusicGen, prompt: str, duration: int, seed):
    """
    Generate a single track from a prompt.

    1トラック分の音源をプロンプトから生成する。
    """
    if seed is not None:
        # Fix random seed for reproducibility.
        # 再現性のためにランダムシードを固定する。
        torch.manual_seed(seed)

    # Set generation parameters (duration only here; others can be added if needed).
    # 生成パラメータを設定（ここでは duration のみ。必要に応じて拡張可能）。
    model.set_generation_params(duration=duration)

    # Generate returns [B, C, T], we take the first in the batch.
    # generate() の戻り値は [バッチ, チャンネル, サンプル] → 先頭の 1 つを使用。
    wav = model.generate([prompt])[0]
    return wav


def ensure_dir(path: str):
    """
    Ensure directory exists.

    ディレクトリが存在しなければ作成する。
    """
    os.makedirs(path, exist_ok=True)


def save_waveform(path: str, wav, sample_rate: int):
    """
    Save waveform as audio file using audiocraft's audio_write.

    audiocraft の audio_write を使って音声ファイルとして保存する。
    """
    # strategy="loudness" is what MusicGen uses internally.
    # strategy="loudness" は MusicGen の実装で使われている推奨設定。
    audio_write(
        path,
        wav,
        sample_rate=sample_rate,
        strategy="loudness",
        loudness_compressor=True
    )


def run_single_prompt_mode(model: MusicGen, output_dir: str, prompt: str):
    """
    Single prompt mode: use --prompt and generate one file.

    単発モード：--prompt で受け取ったプロンプトから 1 ファイル生成する。
    """
    job = merge_with_defaults({"prompt": prompt})

    print(f"[MusicGen] Single prompt mode")
    print(f"[MusicGen] Prompt: {job['prompt']}")
    print(f"[MusicGen] Duration: {job['duration']} sec")

    wav = generate_single_track(
        model=model,
        prompt=job["prompt"],
        duration=job["duration"],
        seed=job["seed"],
    )

    ensure_dir(output_dir)
    out_path = os.path.join(output_dir, f"{job['filename_tag']}.wav")
    print(f"[MusicGen] Saving: {out_path}")
    save_waveform(out_path, wav, model.sample_rate)
    print("[MusicGen] Done (single prompt).")


def run_batch_mode(model: MusicGen, output_dir: str, stdin_data: str):
    """
    Batch mode: read JSONL from stdin, each line is one job.

    バッチモード：標準入力から JSONL を読み込み、1行1ジョブとして処理する。
    """
    ensure_dir(output_dir)

    lines = [line.strip() for line in stdin_data.splitlines() if line.strip()]
    print(f"[MusicGen] Batch mode: {len(lines)} job(s)")

    for job_idx, line in enumerate(lines):
        # Parse JSON per line.
        # 各行を JSON としてパースする。
        try:
            job_raw = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"[MusicGen] Skipping invalid JSON line {job_idx}: {e}")
            continue

        job = merge_with_defaults(job_raw)

        prompt = job["prompt"]
        duration = int(job["duration"])
        seed = job["seed"]
        filename_tag = str(job["filename_tag"])
        batch_size = int(job["batch_size"])
        num_tracks = int(job["num_tracks"])

        print(
            f"[MusicGen] Job {job_idx}: "
            f"prompt='{prompt}', duration={duration}, "
            f"batch_size={batch_size}, num_tracks={num_tracks}, seed={seed}"
        )

        for b in range(batch_size):
            for t in range(num_tracks):
                wav = generate_single_track(
                    model=model,
                    prompt=prompt,
                    duration=duration,
                    seed=seed,
                )
                filename = f"{filename_tag}_job{job_idx}_b{b}_t{t}.wav"
                out_path = os.path.join(output_dir, filename)
                print(f"[MusicGen] Saving: {out_path}")
                save_waveform(out_path, wav, model.sample_rate)

    print("[MusicGen] All batch jobs completed.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "MusicGen Cloud Runner: single-prompt and batch JSONL mode.\n"
            "MusicGen Cloud Runner：単発プロンプト／JSONLバッチ両対応。"
        )
    )

    # Model size option
    # モデルサイズ指定
    parser.add_argument(
        "--model",
        type=str,
        default="medium",
        help="Model size: small | medium | large"
    )

    # Output directory (not a single file)
    # 出力先ディレクトリ（単一ファイルではなくディレクトリ）
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output directory path (e.g., /out)"
    )

    # Single prompt mode
    # 単発モード用プロンプト
    parser.add_argument(
        "--prompt",
        type=str,
        help="Single prompt mode. If omitted, JSONL batch is read from stdin.\n"
             "単発モード用プロンプト。省略時は stdin から JSONL バッチを読み込み。"
    )

    args = parser.parse_args()

    print(f"[MusicGen] Loading model: {args.model}")
    model = MusicGen.get_pretrained(args.model)

    # Single prompt mode: --prompt is given
    # 単発モード：--prompt が指定されている場合
    if args.prompt:
        run_single_prompt_mode(model=model, output_dir=args.output, prompt=args.prompt)
        return

    # Batch mode: read stdin as JSONL
    # バッチモード：標準入力から JSONL を読む
    stdin_data = sys.stdin.read()
    if not stdin_data.strip():
        parser.error(
            "No prompt provided. Use --prompt for single mode or pipe JSONL into stdin.\n"
            "プロンプトが指定されていません。単発モードでは --prompt を、"
            "バッチモードでは JSONL を stdin にパイプしてください。"
        )

    run_batch_mode(model=model, output_dir=args.output, stdin_data=stdin_data)


if __name__ == "__main__":
    main()

