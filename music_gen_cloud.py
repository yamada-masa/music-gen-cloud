python -c "import sys; content = sys.stdin.read(); open('music_gen_cloud.py', 'w', encoding='utf-8').write(content)" << 'EOF'
import argparse
import sys
import json
import os
import torch
import hashlib
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

# ----------------------------------------
# Defaults for batch jobs (can be overridden per job)
# バッチジョブ用のデフォルト値（ジョブごとに上書き可能）
# ----------------------------------------
DEFAULTS = {
    "prompt": "ambient",
    "duration": 10,
    "seed": None,
    "filename_tag": "music",
    "batch_size": 1,
    "num_tracks": 1
}

def get_prompt_hash(prompt: str, length=8):
    """Generate a short hash from the prompt. / プロンプトから短縮ハッシュを生成。"""
    return hashlib.md5(prompt.encode()).hexdigest()[:length]

def merge_with_defaults(job: dict) -> dict:
    """Merge a single job dict with DEFAULTS. / ジョブにデフォルト値をマージ。"""
    merged = DEFAULTS.copy()
    for k, v in job.items():
        if v is not None:
            merged[k] = v
    return merged

def generate_single_track(model: MusicGen, prompt: str, duration: int, seed):
    """Generate a single track from a prompt. / 1トラック生成。"""
    if seed is not None:
        torch.manual_seed(seed)
    model.set_generation_params(duration=duration)
    wav = model.generate([prompt])[0]
    return wav

def save_waveform(path: str, wav, sample_rate: int):
    """Save waveform as audio file. / 音声ファイルとして保存。"""
    audio_write(path, wav, sample_rate=sample_rate, strategy="loudness", loudness_compressor=True)

def run_single_prompt_mode(model: MusicGen, output_dir: str, prompt: str):
    """Single prompt mode. / 単発モード。"""
    p_hash = get_prompt_hash(prompt)
    seed = torch.seed()
    print(f"[MusicGen] Single prompt: {prompt} (Seed: {seed})")
    wav = generate_single_track(model, prompt, 10, seed)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"single_s{seed}_h{p_hash}")
    save_waveform(out_path, wav, model.sample_rate)

def run_batch_mode(model: MusicGen, output_dir: str, stdin_data: str):
    """Batch mode: read JSONL from stdin. / バッチモード：標準入力からJSONLを読み込み。"""
    os.makedirs(output_dir, exist_ok=True)
    lines = [line.strip() for line in stdin_data.splitlines() if line.strip()]
    for job_idx, line in enumerate(lines):
        try:
            job = merge_with_defaults(json.loads(line))
        except:
            continue
        prompt = job["prompt"]
        p_hash = get_prompt_hash(prompt)
        for b in range(int(job["batch_size"])):
            for t in range(int(job["num_tracks"])):
                actual_seed = job["seed"] if job["seed"] is not None else torch.seed()
                wav = generate_single_track(model, prompt, int(job["duration"]), actual_seed)
                # 新しい命名規則: tag_s(シード)_h(ハッシュ)_j(ジョブ)_b_t
                filename = f"{job['filename_tag']}_s{actual_seed}_h{p_hash}_j{job_idx}_b{b}_t{t}"
                save_waveform(os.path.join(output_dir, filename), wav, model.sample_rate)

def main():
    parser = argparse.ArgumentParser(description="MusicGen Cloud Runner: single-prompt and batch JSONL mode.\nMusicGen Cloud Runner：単発プロンプト／JSONLバッチ両対応。")
    parser.add_argument("--model", type=str, default="medium", help="Model size: small | medium | large")
    parser.add_argument("--output", type=str, required=True, help="Output directory path (e.g., /out)")
    parser.add_argument("--prompt", type=str, help="Single prompt mode. If omitted, JSONL batch is read from stdin.\n単発モード用プロンプト。省略時は stdin から JSONL バッチを読み込み。")
    args = parser.parse_args()
    model = MusicGen.get_pretrained(args.model)
    if args.prompt:
        run_single_prompt_mode(model, args.output, args.prompt)
    else:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            parser.error("No prompt provided.\nプロンプトが指定されていません。")
        run_batch_mode(model, args.output, stdin_data)

if __name__ == "__main__":
    main()
EOF