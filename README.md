# music-gen-cloud

[English](#english) | [日本語](#日本語)

---

# English
A minimal, cost-optimized pipeline for generating music using Meta’s MusicGen on **GCP Spot Instances**.

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

Add jobs line by line:

```json
{"prompt": "Lo-fi hip hop", "duration": 30, "seed": 42, "filename_tag": "relax"}

```

---

# 日本語

GCP スポットインスタンスを利用した、低コストかつ再現性の高い MusicGen 生成パイプラインです。

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

* `prompt`: 生成したい音楽の説明
* `duration`: 生成する長さ（秒）
* `seed`: 再現用のシード値（任意）
* `filename_tag`: ファイル名のプレフィックス
