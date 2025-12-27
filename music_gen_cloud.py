#!/usr/bin/env python3
import argparse
import sys
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write


def read_prompt_from_stdin():
    """Read prompt text from stdin."""
    prompt = sys.stdin.read().strip()
    if not prompt:
        print("Error: No prompt provided. Please pipe or redirect a prompt into stdin.", file=sys.stderr)
        sys.exit(1)
    return prompt


def load_model(model_name):
    """Load MusicGen model."""
    valid = ["small", "medium", "large"]
    if model_name not in valid:
        print(f"Error: Invalid model '{model_name}'. Choose from {valid}.", file=sys.stderr)
        sys.exit(1)
    return MusicGen.get_pretrained(model_name)


def main():
    parser = argparse.ArgumentParser(description="MusicGen Cloud Runner")
    parser.add_argument("--model", type=str, default="medium",
                        help="Model size: small | medium | large")
    parser.add_argument("--duration", type=int, default=30,
                        help="Duration in seconds")
    parser.add_argument("--top-k", type=int, default=250,
                        help="Top-k sampling")
    parser.add_argument("--top-p", type=float, default=0.95,
                        help="Top-p sampling")
    parser.add_argument("--temperature", type=float, default=1.0,
                        help="Sampling temperature")
    parser.add_argument("--cfg-scale", type=float, default=3.0,
                        help="Classifier-free guidance scale")
    parser.add_argument("--output", type=str, default="/output/music.wav",
                        help="Output WAV file path")

    args = parser.parse_args()

    # Read prompt
    prompt = read_prompt_from_stdin()

    # Load model
    print(f"Loading model: {args.model}")
    model = load_model(args.model)

    # Apply parameters
    model.set_generation_params(
        duration=args.duration,
        top_k=args.top_k,
        top_p=args.top_p,
        temperature=args.temperature,
        cfg_coef=args.cfg_scale,
    )

    # Generate
    print("Generating music...")
    wav = model.generate([prompt])

    # Save
    print(f"Saving to: {args.output}")
    audio_write(
        args.output.replace(".wav", ""),
        wav[0].cpu(),
        model.sample_rate,
        strategy="loudness",
    )

    print("Done.")


if __name__ == "__main__":
    main()

