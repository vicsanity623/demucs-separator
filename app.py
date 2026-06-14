#!/usr/bin/env python3
"""
Demucs Ultimate Separator - Pinokio Native Script
Runs Demucs htdemucs and outputs separated stems.
Called by Pinokio's template system - no Flask needed.
"""

import sys
import os
import json
import subprocess
import shutil
import uuid
from pathlib import Path

def main():
    """Main entry point when Pinokio calls this script"""

    # Read input from Pinokio (passed as JSON via stdin or args)
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read())

    audio_path = input_data.get('audio')
    mode = input_data.get('mode', '4stem')
    model = input_data.get('model', 'htdemucs')
    segment = input_data.get('segment', 10)
    overlap = input_data.get('overlap', 0.25)

    # Create output directory
    session_id = str(uuid.uuid4())[:8]
    output_dir = Path(f"/tmp/demucs_output_{session_id}")
    output_dir.mkdir(exist_ok=True)

    # Copy audio to temp location
    shutil.copy2(audio_path, output_dir / "input.wav")

    # Build Demucs command
    cmd = [
        "python3", "-m", "demucs",
        "-o", str(output_dir / "separated"),
        "-n", model,
        "--segment", str(segment),
        "--overlap", str(overlap),
        str(output_dir / "input.wav")
    ]

    # Add mode-specific flags
    if mode == "vocals":
        cmd += ["--two-stems", "vocals"]
    elif mode == "2stem":
        cmd += ["--two-stems", "vocals"]

    # Run Demucs
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(json.dumps({"error": f"Demucs failed: {result.stderr}"}))
        sys.exit(1)

    # Find output files
    output_stems_dir = output_dir / "separated" / model
    if not output_stems_dir.exists():
        output_stems_dir = output_dir / "separated"

    stems = {}
    for wav_file in output_stems_dir.rglob("*.wav"):
        stem_name = wav_file.stem
        dest = output_dir / f"{stem_name}.wav"
        shutil.copy2(wav_file, dest)
        stems[stem_name] = str(dest)

    # Output results as JSON for Pinokio
    print(json.dumps({
        "stems": stems,
        "output_dir": str(output_dir),
        "session_id": session_id
    }))

if __name__ == "__main__":
    main()