# Track each cyclist in the generated clip

- Case: `street_track_cyclist`
- Model: `nvidia/cosmos3-nano-reasoner`
- Selected profile: `b8a63a79898682e96de125b05b52d5f9f80593145285c8a95477af3499bcfc1b`
- Asset: `reasoner/assets/street_cyclist.mp4`
- Format validation: `not_applicable`

## Prompt

~~~~text
Describe each cyclist in this video: where each one starts, where it goes, and where it ends. Answer the question using the following format: <think> Your reasoning. </think> Write your final answer immediately after the </think> tag.
~~~~

## Final answer

~~~~text
<think> The cyclist starts behind the white car, then moves forward to pass in front of the camera, and finally exits the frame. </think>

A cyclist is riding on the road behind the white car, moving forward toward the camera.
~~~~

## Qualitative review

These task-level criteria require human or application-specific review; passing
format validation does not establish them.

- [ ] Correct is two cyclists, light clothing riding away and fading, dark clothing appearing near that spot.
- [ ] One cyclist described means it merged the two.
