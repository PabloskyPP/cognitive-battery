# Mental Rotation Task (MRT) - Image Structure

## Overview
The Mental Rotation Task uses images from two locations:
1. **Task Images**: Main rotation test images (from `images/Mental Rotation Test 3D/`)
2. **UI Elements**: Navigation and status indicators (from `tasks/images/MRT/`)

## Image Locations and Mapping

### Main Task Images
**Location**: `/images/Mental Rotation Test 3D/`

The task uses 12 trial sets, each consisting of:
- 1 reference image: `MRT_Xa.png` (where X = 1-12)
- 4 option images: `MRT_Xa_1.png`, `MRT_Xa_2.png`, `MRT_Xa_3.png`, `MRT_Xa_4.png`

**Total**: 60 task images (12 trials × 5 images per trial)

#### Trial Images (12 sets)
```
Trial 1:  MRT_1a.png, MRT_1a_1.png, MRT_1a_2.png, MRT_1a_3.png, MRT_1a_4.png
Trial 2:  MRT_2a.png, MRT_2a_1.png, MRT_2a_2.png, MRT_2a_3.png, MRT_2a_4.png
...
Trial 12: MRT_12a.png, MRT_12a_1.png, MRT_12a_2.png, MRT_12a_3.png, MRT_12a_4.png
```

**Note**: The task has 24 trials total (2 sections of 12 each). Trials 13-24 reuse images from trials 1-12 respectively.

#### Instruction Images (6 images)
```
MRT_Instruktion_1.png - Used for first instruction screen (0a)
MRT_Instruktion_2.png - Used for second instruction screen (0b)
MRT_Instruktion_3.png - Available for additional instructions
MRT_Instruktion_4.png - Available for additional instructions
MRT_Instruktion_5.png - Available for additional instructions
MRT_Instruktion_6.png - Available for additional instructions
```

#### Practice Images
The task uses the first 3 trial sets (trials 1-3) as practice questions:
- Practice 1 uses Trial 1 images
- Practice 2 uses Trial 2 images
- Practice 3 uses Trial 3 images

### UI Elements
**Location**: `/tasks/images/MRT/`

These images provide navigation and visual feedback:
- `circleBlue.png` - Indicator for completed questions
- `circleBlank.png` - Indicator for incomplete questions
- `indicator.png` - Arrow showing current question
- `previous.png` - Previous question button
- `next.png` - Next question button
- `finish.png` - Finish section button
- `correct.png` - Checkmark for practice answer feedback

## Image Mapping Logic

The `get_image_path()` method in `mrt.py` handles the mapping:

### For Trials 1-24
```python
# Trial number gets converted to base 1-12
base_trial = ((trial_num - 1) % 12) + 1

# Question image
"MRT_{base_trial}a.png"

# Answer options (a, b, c, d map to 1, 2, 3, 4)
"MRT_{base_trial}a_1.png"  # Option 'a'
"MRT_{base_trial}a_2.png"  # Option 'b'
"MRT_{base_trial}a_3.png"  # Option 'c'
"MRT_{base_trial}a_4.png"  # Option 'd'
```

### For Practice Questions (p1, p2, p3)
Practice questions use the first 3 trial images:
- 'p1' → Trial 1 images
- 'p2' → Trial 2 images
- 'p3' → Trial 3 images

### For Instructions (0a, 0b)
- '0a' → `MRT_Instruktion_1.png`
- '0b' → `MRT_Instruktion_2.png`

## Image Requirements

All images should be:
- PNG format
- Appropriately sized for display (the task will scale to fit)
- Named exactly as specified above

## Notes

- The original MRT task images are copyrighted (Peters et al., 1995)
- This structure accommodates the standard 12-item MRT format
- UI elements are kept separate to allow easy customization
- Cross-platform compatibility ensured using `os.path.join()`

## References

Peters, M., Laeng, B., Latham, K., Jackson, M., Zaiyouna, R., & Richardson, C. (1995). 
A redrawn Vandenberg and Kuse mental rotations test-different versions and factors 
that affect performance. *Brain and cognition*, 28(1), 39-58.
