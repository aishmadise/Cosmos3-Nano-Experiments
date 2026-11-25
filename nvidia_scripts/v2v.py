# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: OpenMDW-1.1

"""Generate a video conditioned on an existing cookbook video."""

import argparse
import os
from pathlib import Path

import requests
from common import decode_video, media_to_data_url, require_generator_profile

NIM_URL = os.environ.get("NIM_URL", "http://localhost:8000").rstrip("/")
COSMOS3_ROOT = Path(__file__).resolve().parents[2]
VIDEO = (
    COSMOS3_ROOT
    / "generator"
    / "audiovisual"
    / "assets"
    / "videos"
    / "car_driving_plain.mp4"
)
OUTPUT = Path(__file__).parent / "outputs" / "v2v.mp4"

# --- Portfolio additions: continue my fixed-camera street clip ---
STREET_VIDEO = COSMOS3_ROOT / "reasoner" / "assets" / "street_first7s_24fps.mp4"
FIXED_CAMERA = (
    " The camera is fixed on a tripod and does not move. The viewpoint, framing,"
    " and background stay exactly the same."
)
STREET_PROMPTS = {
    "street_continue": "Cars and pedestrians keep moving naturally through the street.",
    "street_pedestrian": (
        "A pedestrian suddenly steps off the curb into the street in front of an"
        " approaching car, and the car brakes hard to avoid them."
    ),
    "street_cyclist": "A cyclist rides quickly through the street, weaving between the moving cars.",
    # Rain test C: ask a continuation to start rain, instead of restyling with Transfer.
    "street_rain_start": (
        "Heavy rain begins to fall over the street. Rain streaks fall through the air,"
        " drops splash in puddles, and the road turns wet and reflective, while cars"
        " and pedestrians keep moving."
    ),
}
CASES = ("nvidia_sample",) + tuple(STREET_PROMPTS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, default="nvidia_sample")
    case = parser.parse_args().case
    require_generator_profile(
        NIM_URL,
        allowed_variants=("nano", "super"),
    )

    request = {
        "model_mode": "video2video",
        "prompt": (
            "A red sports car drives through a dramatic landscape with realistic "
            "motion, stable geometry, and cinematic lighting."
        ),
        "input_reference": media_to_data_url(VIDEO),
        "condition_frame_indexes_vision": [0, 1],
        "condition_video_keep": "first",
        "resolution": "720",
        "num_frames": 93,
        "fps": 24.0,
        "num_inference_steps": 35,
        "guidance_scale": 6.0,
        "flow_shift": 10.0,
        "seed": 0,
    }
    output = OUTPUT
    if case != "nvidia_sample":
        request["prompt"] = STREET_PROMPTS[case] + FIXED_CAMERA
        request["input_reference"] = media_to_data_url(STREET_VIDEO)
        request["condition_video_keep"] = "last"  # continue from the end of my clip
        request["resolution"] = "720_9_16"  # my phone video is vertical
        output = OUTPUT.with_name(f"{case}.mp4")

    response = requests.post(f"{NIM_URL}/v1/infer", json=request, timeout=1800)
    response.raise_for_status()

    output.parent.mkdir(exist_ok=True)
    output.write_bytes(decode_video(response.json()["b64_video"]))
    print(f"Saved video to {output}")


if __name__ == "__main__":
    main()
