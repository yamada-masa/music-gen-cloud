# music-gen-cloud

[English](#english) | [日本語](#日本語)

---

# English
A minimal, cost-optimized pipeline for generating music using Meta’s MusicGen on **GCP Spot Instances**.

### ✅ Tested Environment
- **Local / Orchestrator**:
  - OS: macOS / Linux / Windows (WSL2)
  - Container Engine: **Podman** (verified) or Docker
  - Python: 3.10+
- **Cloud / GPU**:
  - Google Cloud Platform (GCP)
  - Instance: `g2-standard-4`
  - GPU: **NVIDIA L4** (24GB VRAM)
  - CUDA: 12.1

### ✨ Key Features
- **Spot L4 GPU**: Optimized for NVIDIA L4 (G2 instances), reducing costs by ~70-90%.
- **Podman/Docker Ready**: Fully containerized environment for reproducibility.
- **Smart Naming**: Files are saved as `tag_s{seed}_h{prompt_hash}` for easy tracking.
- **Automated Workflow**: `driver.py` handles VM lifecycle, result download, and cleanup.

### 🚀 Usage
1. **Setup `.env`**: Define `PROJECT`, `IMAGE`, `MODEL_SIZE`.
2. **Build & Push (Podman)**:
   ```bash
   podman build -t musicgen .
   podman tag musicgen $IMAGE
   podman push $IMAGE

```

3. **Execution**:
```bash
python driver.py

```



### 📝 Batch Configuration (`sample.jsonl`)

Add jobs line by line. GCE Metadata has a 512KB limit; for massive batches, split the file.

```json
{"prompt": "Lo-fi hip hop", "duration": 30, "seed": 42, "filename_tag": "relax"}

```

---

# 日本語

GCP スポットインスタンスを利用した、低コストかつ再現性の高い MusicGen 生成パイプラインです。

### ✅ 動作確認済み環境

* **ローカル / オーケストレーター**:
* OS: macOS / Linux / Windows (WSL2)
* コンテナエンジン: **Podman** (確認済み) または Docker
* Python: 3.10以上


* **クラウド / GPU**:
* Google Cloud Platform (GCP)
* インスタンス: `g2-standard-4`
* GPU: **NVIDIA L4** (24GB VRAM)
* CUDA: 12.1



### ✨ 主な特徴

* **Spot L4 GPU**: 最新の NVIDIA L4 GPU を活用し、生成費用を劇的に削減。
* **Podman 対応**: 現場で使いやすい Podman でのビルド・デプロイ手順を完備。
* **再現性の担保**: シード値とプロンプトのハッシュ値をファイル名に自動付与。
* **フルオート**: `driver.py` 一つで VM の作成から生成、結果の回収、VM の削除まで完結。

### 🚀 使い方

1. **環境設定**: `.env` ファイルにプロジェクト設定を記述。
2. **ビルドとプッシュ**:
上記 English セクションのコマンドを参照（Podman 推奨）。
3. **実行**:
`python driver.py` を実行。生成されたファイルは `./downloaded_wav/` に保存されます。

### 📝 設定ファイル (`sample.jsonl`) の書き方

各行に以下の JSON オブジェクトを記述します。

* `prompt`: 生成したい音楽の説明
* `duration`: 生成する長さ（秒）
* `seed`: 再現用のシード値（任意）
* `filename_tag`: ファイル名のプレフィックス（接頭辞）

> **注意**: GCE メタデータの制限（512KB）があるため、膨大なジョブを一度に投げる場合はファイルを分割してください。
