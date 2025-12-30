# music-gen-cloud

[English](#english) | [日本語](#日本語)

---

# English

A minimal, reproducible, and cost-optimized cloud pipeline for generating music using Meta’s MusicGen models on **Google Cloud Platform (GCP)**.

This project allows you to leverage high-performance GPUs for music generation with just a single command, while keeping costs extremely low using Spot Instances.

### ✨ Key Features
- **Cost Optimized**: Uses **GCP Spot Instances** to reduce GPU costs by ~60-90%.
- **High Performance**: Pre-configured for **NVIDIA L4 GPUs** (G2 standard instances).
- **Smart Naming**: Generated files are automatically named with `tag_seed_hash` (e.g., `focus_s42_h8a2b3c4...`) to track exact prompt/seed combinations.
- **Robust Environment**: Docker-based execution ensures the same results locally and in the cloud.
- **Automated Workflow**: `driver.py` handles VM creation, setup, generation, file download, and cleanup.

## 🎵 Usage

### 1. Prerequisites
- A GCP Project with Billing enabled.
- `gcloud` CLI and Python 3.x installed locally.
- A Docker image pushed to Google Artifact Registry.

### 2. Local Setup
Create a `.env` file in the root directory:
```bash
PROJECT=your-project-id
IMAGE=us-east1-docker.pkg.dev/your-project/repo/musicgen:latest
ZONE=us-east1-c
INSTANCE_NAME=musicgen-l4-spot
MODEL_SIZE=medium
DELETE_VM=True

```

### 3. Execution

Simply run the driver script:

```bash
python driver.py

```

This will:

1. Create a Spot L4 VM.
2. Run `music_gen_cloud.py` inside Docker via the startup script.
3. Download all generated `.wav` files to `./downloaded_wav/`.
4. Delete the VM automatically to save costs.

---

# 日本語

Meta の MusicGen モデルを **Google Cloud Platform (GCP)** 上で実行するための、コスト最適化済みミュージック生成パイプラインです。

コマンド一つで最新の GPU 環境を立ち上げ、生成完了後に自動で片付けを行うため、手軽かつ安価に大量の音楽生成が可能です。

### ✨ 主な特徴

* **低コスト**: **GCP スポットインスタンス** を採用し、GPU 費用を通常の 1/3 以下に抑えます。
* **最新 GPU 対応**: 推論効率に優れた **NVIDIA L4 GPU** (G2 インスタンス) に最適化。
* **進化した命名規則**: ファイル名に `タグ_シード値_プロンプトハッシュ` を自動付与。どのプロンプトから生成されたか一目で分かります。
* **ポータビリティ**: Docker 環境により、ローカルでのテストとクラウド実行で全く同じ結果が得られます。
* **フルオート**: `driver.py` が VM の作成から、生成結果の回収、VM の削除までを一括管理します。

## 🚀 使い方

### 1. 事前準備

* GCP プロジェクトと課金設定。
* ローカル環境への `gcloud` CLI と Python 3.x のインストール。
* Artifact Registry への Docker イメージのプッシュ。

### 2. 環境設定

ルートディレクトリに `.env` ファイルを作成します：

```bash
PROJECT=your-project-id
IMAGE=us-east1-docker.pkg.dev/your-project/repo/musicgen:latest
MODEL_SIZE=medium   # small, medium, large から選択

```

### 3. 実行

以下のコマンドを実行するだけです：

```bash
python driver.py

```

実行後、自動的に `./downloaded_wav/` フォルダへ生成された音声ファイルがダウンロードされます。

## 🛠️ File Structure

* `music_gen_cloud.py`: 推論メインスクリプト（コンテナ内実行用）。
* `driver.py`: ローカル側のオーケストレーター。
* `run_musicgen.sh`: VM 起動時に実行されるセットアップスクリプト。
* `sample.jsonl`: 生成プロンプトのバッチリスト。
