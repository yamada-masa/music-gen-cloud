# music-gen-cloud

[English](#english) | [日本語](#日本語)

---

# English

A minimal, reproducible, cloud‑ready pipeline for generating music using Meta’s MusicGen models.

This project provides:

- Local testing with the **small** model  
- Cloud (GCP) generation with the **medium** model  
- A unified script (`music_gen_cloud.py`) that works identically on local machines, Docker, and GCP  
- Prompt input via **standard input** for maximum flexibility  
- Full control over generation parameters (duration, temperature, top‑k, etc.)

This repository is designed for automation, reproducibility, and fast GPU‑accelerated generation.

---

## 🎵 Usage: `music_gen_cloud.py`

### Pass prompt via standard input (recommended)

```bash
echo "bright UK rock with energetic drums" | python music_gen_cloud.py
```

### Pass prompt from a file

```bash
python music_gen_cloud.py < prompt.txt
```

---

## 🎛 Parameters

| Parameter       | Description                          | Default |
|-----------------|--------------------------------------|---------|
| `--model`       | small / medium / large               | medium  |
| `--duration`    | Duration in seconds                  | 30      |
| `--top-k`       | Top‑k sampling                       | 250     |
| `--top-p`       | Top‑p sampling                       | 0.95    |
| `--temperature` | Sampling temperature                 | 1.0     |
| `--cfg-scale`   | Prompt adherence strength            | 3.0     |
| `--output`      | Output WAV file path                 | /output/music.wav |

---

## 🎧 Example

```bash
echo "UK rock with bright guitars and strong drums" \
  | python music_gen_cloud.py \
      --model medium \
      --duration 300 \
      --output /output/uk_rock.wav
```

---

## 🐳 Docker (to be added)

A Dockerfile will be added to support:

- CUDA‑enabled PyTorch  
- ffmpeg  
- audiocraft  
- Automatic model download  
- CPU fallback  
- Minimal image size  

---

## ☁️ Google Cloud Platform (to be added)

Upcoming sections:

- Artifact Registry setup  
- GCS bucket for output  
- VM startup script  
- Fully automated generation pipeline  
- One‑command execution from local machine  

---

## 📄 License

MIT (planned)

---

# 日本語

Meta の MusicGen モデルを使って音楽を生成するための、  
**最小・再現性重視・クラウド対応のパイプライン**です。

このプロジェクトは以下を提供します：

- ローカルでは **small** モデルで軽量テスト  
- GCP では **medium** モデルで高速生成  
- ローカル / Docker / GCP で共通して動作する `music_gen_cloud.py`  
- プロンプトは **標準入力** で渡す UNIX 的な柔軟設計  
- duration / temperature / top‑k などのパラメータを完全制御  

自動化・再現性・高速 GPU 生成を目的に設計されています。

---

## 🎵 `music_gen_cloud.py` の使い方

### 標準入力でプロンプトを渡す（推奨）

```bash
echo "bright uk rock with energetic drums" | python music_gen_cloud.py
```

### ファイルからプロンプトを渡す

```bash
python music_gen_cloud.py < prompt.txt
```

---

## 🎛 パラメーター一覧

| パラメーター | 説明 | デフォルト |
|--------------|------|------------|
| `--model` | small / medium / large | medium |
| `--duration` | 生成秒数 | 30 |
| `--top-k` | 多様性（整数） | 250 |
| `--top-p` | 多様性（確率） | 0.95 |
| `--temperature` | 創造性 | 1.0 |
| `--cfg-scale` | プロンプトの強さ | 3.0 |
| `--output` | 出力 WAV ファイルパス | /output/music.wav |

---

## 🎧 生成例

```bash
echo "UK rock with bright guitars and strong drums" \
  | python music_gen_cloud.py \
      --model medium \
      --duration 300 \
      --output /output/uk_rock.wav
```

---

## 🐳 Docker（後で追加予定）

Dockerfile では以下をサポート予定：

- CUDA 対応 PyTorch  
- ffmpeg  
- audiocraft  
- モデルの自動ダウンロード  
- CPU fallback  
- 最小サイズのコンテナ  

---

## ☁️ GCP（後で追加予定）

- Artifact Registry  
- GCS バケット  
- VM startup-script  
- 自動生成パイプライン  
- ローカルからワンコマンド実行  

---

## 📄 ライセンス

MIT（予定）
