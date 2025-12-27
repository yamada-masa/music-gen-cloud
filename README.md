# music-gen-cloud

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
