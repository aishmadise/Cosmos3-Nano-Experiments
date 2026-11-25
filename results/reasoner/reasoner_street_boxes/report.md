# Box every car and person in a still frame

- Case: `street_boxes`
- Model: `nvidia/cosmos3-nano-reasoner`
- Selected profile: `b8a63a79898682e96de125b05b52d5f9f80593145285c8a95477af3499bcfc1b`
- Asset: `reasoner/assets/street_frame.png`
- Format validation: `passed`
- Annotated spatial output: `annotated.png`

## Prompt

~~~~text
Locate the accurate bounding box of every car and every person in the image. Return a json.
~~~~

## Final answer

~~~~text
```json
[
    {"bbox_2d": [0, 556, 147, 613], "label": "car"},
    {"bbox_2d": [25, 555, 176, 605], "label": "car"},
    {"bbox_2d": [112, 547, 303, 601], "label": "car"},
    {"bbox_2d": [291, 552, 347, 578], "label": "car"},
    {"bbox_2d": [536, 515, 779, 610], "label": "car"},
    {"bbox_2d": [762, 539, 797, 555], "label": "car"},
    {"bbox_2d": [779, 535, 845, 553], "label": "car"},
    {"bbox_2d": [814, 530, 883, 548], "label": "car"},
    {"bbox_2d": [818, 530, 998, 629], "label": "car"},
    {"bbox_2d": [869, 529, 948, 545], "label": "car"},
    {"bbox_2d": [380, 540, 407, 577], "label": "person"}
]
```
~~~~

## Qualitative review

These task-level criteria require human or application-specific review; passing
format validation does not establish them.

- [ ] Every visible car and person has one box, and no box covers empty road.
