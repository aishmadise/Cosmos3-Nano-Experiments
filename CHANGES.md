# Changes to NVIDIA's official examples

Base: [NVIDIA/cosmos-framework](https://github.com/NVIDIA/cosmos-framework) at commit `1f1737931214166d5e7b253def319c562cf7a1eb` (Nov 13, 2026), folder `.agents/skills/cookbooks/cosmos3/nim/examples/`.

Ran on Nov 14 to 15, 2026, plus a retest session on Nov 19: Brev, 1x RTX PRO 6000 Blackwell (96 GB), container `nvcr.io/nim/nvidia/cosmos3:2.1.0`, Cosmos 3 Nano. The NIM picked the precision by itself: FP8 for the Generator, and NVFP4 (4-bit) with speculative decoding for the Reasoner. Reasoner launched with `NIM_VIDEO_PRUNING_RATE=0` to match NVIDIA's validated baseline.

Three files changed: 426 lines added, 6 of NVIDIA's lines changed, only to read the new options and name the output file. Every original case still runs exactly as shipped, `reasoner.py` is unchanged, and NVIDIA's `negative_prompt.json` is untouched. Full diff: `street_edits.patch` (apply from the root of NVIDIA's repo at that commit with `git apply street_edits.patch`; tested on a fresh copy).

## Input

One 22 s vertical phone video of a busy street, fixed camera. Converted with ffmpeg (720 x 1280, no audio) into:

| File | Covers | Used by |
|---|---|---|
| `street_full_4fps.mp4` | 0:00 to 0:22 | Reasoner: caption, timeline |
| `street_first7s_4fps.mp4` | 0:10 to 0:17 | Reasoner: prediction |
| `street_first7s_24fps.mp4` | 0:10 to 0:17 | Generator: v2v continuations |
| `street_last3s_24fps.mp4` | 0:17 to 0:20 | Ground truth; Reasoner controls |
| `street_transfer_30fps.mp4` | 0:10 to 0:15 | Generator: Transfer (needs 121+ frames) |
| `street_frame.png` | still at 0:13 | Reasoner: boxes |
| `street_cyclist_crop.mp4` | top right of the generated cyclist clip, 2x zoom, 24 fps | Reasoner: retest C3 and C4 |
| `street_last3s_crop.mp4` | same 2x zoom of the real 0:17 to 0:20 | Reasoner: retest C4 control |

All media go in `cosmos3/reasoner/assets/`. The copies in this repo are blurred (license plates and the one recognizable person). `street_last3s_crop.mp4` was rebuilt from the blurred `street_last3s_24fps.mp4` with the same crop, so it isn't byte-identical to what the Reasoner saw.

## v2v.py (video-to-video generation)

- Added a `--case` option, following the pattern NVIDIA already uses in `transfer.py`. The default, `nvidia_sample`, is the original request, unchanged.
- Added 4 cases: `street_continue`, `street_pedestrian`, `street_cyclist`, and (retest) `street_rain_start`.
- Each street case changes 4 fields of NVIDIA's request and nothing else:
  - `input_reference`: my clip (`street_first7s_24fps.mp4`) instead of NVIDIA's sample
  - `prompt`: my edge case, plus a "camera is fixed" sentence
  - `condition_video_keep`: `"last"` instead of `"first"`, so the model continues from the end of my clip
  - `resolution`: `"720_9_16"` (720 x 1280) instead of `"720"`, because my phone video is vertical
- `street_rain_start` (retest, rain test C): asks a continuation to start heavy rain, instead of restyling with Transfer. Reason: Transfer gave wet roads but never falling rain. Same seed (0) as the other continuations.
- Output: `outputs/<case>.mp4` for street cases; NVIDIA's sample still writes `outputs/v2v.mp4`.

## transfer.py (restyle a video, keep its layout)

- Added 2 cases: `street_night`, `street_rain`. Each is NVIDIA's own `derived_edge` request (the server computes edges from the input video), with only `input_reference` (my clip), `prompt`, and `resolution` (`"720_9_16"`, vertical) changed.
- Added options that apply to my street cases only (NVIDIA's cases ignore them):
  - `--seed` (NVIDIA's default is 2026). Reason: `street_rain` at seed 2026 was fully generated, then blocked by the output safety filter (`guardrail=siglip`, HTTP 422). Seed 1 passed.
  - `--control-guidance` (NVIDIA default 1.5) and `--first-frames` (`num_first_chunk_conditional_frames`, NVIDIA default 0). Reason: with NVIDIA's defaults, night and rain lost my street's layout; raising `control_guidance` to 3.0 kept it.
  - `--prompt-file`: loads a structured JSON prompt with NVIDIA's own `compact_json_file()` helper, the format NVIDIA's precomputed Transfer examples use (`generator/transfer/assets/*/prompt.json`). `street_rain_prompt.json` is my rain prompt in that format (written by hand, not with NVIDIA's upsampler). Reason: the one-line rain prompt gave wet streets but no falling rain.
  - `--negative-prompt-file` (retest): replaces NVIDIA's `negative_prompt.json` with another JSON file, loaded with the same `compact_json_file()` helper. Reason: every Transfer request sends NVIDIA's negative prompt, which tells the model to avoid flicker, noise, shimmering outlines and moiré patterns. Falling rain (thin streaks that change every frame) looks a lot like those. This option tested whether that was what held rain back (test A: it was).
  - `--tag`: suffix for the output file name, so variants don't overwrite each other.
- Output: `outputs/transfer_<case><tag>.mp4`

### street_negative_prompt.json (retest)

A copy of NVIDIA's `generator/transfer/assets/negative_prompt.json` with one rule applied: remove every sentence or list item that mentions flicker, shimmer, noise or moiré, and change nothing else. 13 edits; 16 keyword mentions before, 0 after; about 6% shorter (14,658 to 13,752 characters as sent). Every other part of NVIDIA's text is kept word for word.

| Field | Removed text | Now |
|---|---|---|
| `subjects[0].state_changes` | Surface textures flicker between different materials randomly. Outlines shimmer and vibrate. | (removed) |
| `subjects[1].state_changes` | Surface textures flicker between different materials randomly. Outlines shimmer and vibrate. | (removed) |
| `subjects[2].state_changes` | Surface textures flicker between different materials randomly. Outlines shimmer and vibrate. | (removed) |
| `subjects[2].description` | flickering edges, inconsistent depth | inconsistent depth |
| `background_setting` | Background elements flicker in and out of existence between frames, particularly at the edges of the field of view. | (removed) |
| `lighting.shadows` | The shadow rendering appears to be temporally unstable — even static objects have shadows that shimmer and crawl frame to frame, breaking the illusion of a stable light source. | (removed) |
| `aesthetics.patterns` | Visible tiling artifacts in textures, moiré patterns, and aliasing on edges. | Visible tiling artifacts in textures and aliasing on edges. |
| `actions[0].description` | Background elements flicker and shift between frames. | (removed) |
| `segments[0].description` | Noise patterns change between frames in ways that draw attention rather than being invisible. | (removed) |
| `temporal_caption` | visible compression artifacts, color banding in the sky, and flickering in the shadows | visible compression artifacts and color banding in the sky |
| `temporal_caption` | with increasing noise, blur, and a general loss | with increasing blur and a general loss |
| `temporal_caption` | macro-blocking and mosquito noise around moving edges | macro-blocking around moving edges |
| `temporal_caption` | Temporal noise patterns are spatially correlated, creating swimming artifacts on flat surfaces. | (removed) |

Not removed, on purpose (one idea per test): "Textures swim and shift across surfaces", "Fog and atmospheric effects pop in and out", and "individual pixels changing color randomly". Test A gave falling rain without touching them; removing them is the next thing to try for rain that lands on surfaces (splashes, ripples).

## reasoner_cases.yaml (Reasoner test cases)

No changes to `reasoner.py`. NVIDIA's 18 cases are unchanged. Added 19 cases, each modeled on one of NVIDIA's:

| My case | Modeled on | Input |
|---|---|---|
| `street_caption` | `video_caption` | full clip, 4 fps |
| `street_timeline` | `event_timeline` | full clip, 4 fps |
| `street_boxes` | `grounding_2d` | one still frame |
| `street_predict` | `robotics_next_action` (format) | 0:10 to 0:17, 4 fps |
| `street_plausibility_real` | `physical_plausibility` | real 0:17 to 0:20 (control) |
| `street_plausibility_continue` / `_pedestrian` / `_cyclist` | `physical_plausibility` | generated continuations |
| `street_plausibility_night` / `_rain` | `physical_plausibility` | final Transfer clips |
| `street_permanence_cyclist` | my targeted object-permanence question, NVIDIA's `<think>` format | generated cyclist clip |
| `street_permanence_real` | same question | real 0:17 to 0:20 (control) |
| `street_count_cyclist` (retest C1) | `<think>` format | generated cyclist clip |
| `street_track_cyclist` (retest C2) | `<think>` format | generated cyclist clip |
| `street_track_real` (retest C2 control) | `<think>` format | real 0:17 to 0:20 |
| `street_permanence_cyclist_zoom` (retest C3) | same as `street_permanence_cyclist` | 2x zoom of the cyclist region |
| `street_plausibility_cyclist_zoom` (retest C4) | same as `street_plausibility_cyclist` (NVIDIA's prompt) | 2x zoom of the cyclist region |
| `street_plausibility_real_zoom` (retest C4 control) | same as C4 | same 2x zoom of real 0:17 to 0:20 |
| `street_plausibility_cyclist_zoom_think` (retest C4, reasoning shown) | C4 plus NVIDIA's `<think>` format | 2x zoom of the cyclist region |

- Video cases set a pixel budget through the `request_extensions` field NVIDIA already supports: `mm_processor_kwargs: {size: {shortest_edge: 1568, longest_edge: 25165824}}`. Reason: in my Nov 7 test, the default budget led to invented details. Measured on Nov 15: 11,735 prompt tokens for the 22 s clip, 7,184 for a generated clip.
- Plausibility prompt: NVIDIA's text, with one line about their sample's "rising wall" removed.
- The two `street_permanence_*` cases were added on Nov 15, after every plausibility case answered "(A) Possible." Their entries were missing from my saved case files, so they were rebuilt for this repo from the exact prompt, which `street_permanence_cyclist_zoom` reuses word for word.
- The retest cases each change one thing from an earlier case (the question asked, or a zoomed input), so any difference in the answer comes from that one change. The last two were added during the session: a control for C4, and C4 with its reasoning shown.
- A planned distant-people retest (Part B, three boxes cases) was dropped before running: checking `annotated.png` showed `street_boxes` had already boxed every visible person and car, and its 910 prompt tokens showed the frame went in at full size.
- This file is the complete catalog. During the retest I ran a smaller copy with only the retest cases, because `reasoner.py` checks every case's file at startup.

## How each final clip was made

Run from `.agents/skills/cookbooks/cosmos3/nim` with `uv run python`:

| Output | Command |
|---|---|
| `v2v.mp4` (NVIDIA sample) | `examples/v2v.py` |
| `street_continue.mp4` | `examples/v2v.py --case street_continue` |
| `street_pedestrian.mp4` | `examples/v2v.py --case street_pedestrian` |
| `street_cyclist.mp4` | `examples/v2v.py --case street_cyclist` |
| `transfer_street_night.mp4` (defaults, layout lost) | `examples/transfer.py --case street_night` |
| `transfer_street_rain.mp4` (seed 1, defaults, layout lost) | `examples/transfer.py --case street_rain --seed 1` |
| `transfer_street_night_cg3.mp4` (final night) | `examples/transfer.py --case street_night --seed 1 --control-guidance 3.0 --tag _cg3` |
| `transfer_street_rain_cg3.mp4` | `examples/transfer.py --case street_rain --seed 1 --control-guidance 3.0 --tag _cg3` |
| `transfer_street_rain_cg3_json.mp4` (final rain, Nov 15) | `examples/transfer.py --case street_rain --seed 1 --control-guidance 3.0 --prompt-file street_rain_prompt.json --tag _cg3_json` |
| `transfer_street_rain_cg3_json_neg.mp4` (retest A) | same as above, plus `--negative-prompt-file street_negative_prompt.json`, `--tag _cg3_json_neg` |
| `transfer_street_rain_cg2_json.mp4` (retest B) | `examples/transfer.py --case street_rain --seed 1 --control-guidance 2.0 --prompt-file street_rain_prompt.json --tag _cg2_json` |
| `street_rain_start.mp4` (retest C) | `examples/v2v.py --case street_rain_start` |

For the Reasoner, the final night and rain clips were copied into `reasoner/assets/` as `transfer_street_night.mp4` and `transfer_street_rain.mp4`.

Reasoner: `examples/reasoner.py --case <case>` for each case above (NVIDIA's sanity check: `--case video`).

## Tips for rerunning

1. **Install `git-lfs` before cloning.** NVIDIA's sample videos are Git LFS files; without it, `git clone` gives small placeholder files. The main README covers this.
2. **Copy every clip into `reasoner/assets/` before running any Reasoner case, or delete the cases you can't run.** `reasoner.py` checks all cases' files at startup, so one missing file stops every case. The README's steps make every clip except the two 2x zoom crops (`street_cyclist_crop.mp4`, `street_last3s_crop.mp4`); without them, delete the four `*_zoom` cases from `reasoner_cases.yaml`.
3. **Make 4 fps copies of your clips for the Reasoner.** Every video case is sampled at the catalog-wide `video_fps` (4.0).
4. **Use `--case` on `v2v.py` to try your own clip.** It follows the same pattern as NVIDIA's `transfer.py`.
5. **If a run returns `422 Unprocessable Entity` after generating, check the server log.** A `[NIM_POLICY] decision=blocked` line means the output safety filter caught it; a different seed passed for me.
6. **For a busy scene, raise `control_guidance`.** 3.0 kept my street's layout in Transfer; the default 1.5 favors the prompt over the outlines.
7. **For weather like rain, look at the Transfer negative prompt.** NVIDIA's examples send `negative_prompt.json` (about 14,700 characters) with every request, and its anti-flicker lines work against falling rain. The edited copy above gave falling rain.
8. **`shortest_edge` and `longest_edge` are pixel counts.** In NVIDIA's Qwen3-VL processor code they're passed as `min_pixels` and `max_pixels` (`cosmos_framework/model/generator/reasoner/qwen3_vl/video_processing_qwen3_vl.py`, lines 197 to 198), so `longest_edge: 25165824` means "at most about 25 million pixels." The names come from Hugging Face's Qwen processors. Check: my 720 x 1280 still frame used 910 prompt tokens with the default image settings, which is full size (one token per 32 x 32 pixels).
