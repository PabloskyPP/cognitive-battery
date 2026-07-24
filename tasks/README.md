# Tasks

## Attention Network Test (ANT)

- 1 practice block with 24 trials (~2 minutes)
- 96 trials per block in the main task (~7 minutes)
- Number of blocks adjustable in Settings
- Fixation duration: 400-1600ms
- Cue duration: 100ms
- Flanker/stimulus duration: 1700ms
- Maximum inter-trial interval: 3500ms
- Congruency levels: neutral, congruent, incongruent
- Cue types: no cue, center, spatial, double

## Backwards Digit Span
- Digit set: 1-9 (inclusive)
- 1 practice trial
- Shortest sequence length: 3 digits
- Longest sequence length: 9 digits
- Each sequence length is repeated twice
- Sequences get progressively longer
- 14 total trials (~5 minutes)
- Digit duration: 1000ms
- Time between digits: 100ms

## Digits Memorization
- 3 sections: forward, backward, ascending
- Each section ends after 2 failed trials
- Sequence length increases every 2 trials
- Presentation duration: one second per digit
- Response timeout warning: 10-second countdown after 2 × sequence length seconds
- Exports one row with `forward_span`, `backward_span`, and `ascending_span`, each storing the length of the last correctly completed sequence in that section

## Eriksen Flanker Task
- A single set contains each trial type combination (left/congruent, left/incongruent, right/congruent, right/incongruent)
- 3 practice sets by default, adjustable in settings
- 25 sets in the main blocks, adjustable in settings (~10 minutes)
- Contains options for adding compatible (respond in direction of arrow) and incompatible (respond in opposite direction of arrow) blocks
- 1 compatible block by default
- Flanker stimululs duration: 200ms
- Maximum response time (before timeout): 1500ms
- Inter-trial interval: 1500ms

## Mental Rotation Task (MRT)
- 3 practice questions
- 2 main blocks (with a break inbetween)
- 12 questions per block (4 answer options each)
- Each block has a maximum time limit of 3 minutes

## Raven's Progressive Matrices
- Advanced Set #2
- 1 practice question
- 12 main questions (adjustable in Settings)
- 8 answer options per question
- Each question has a maximum time limit of 1 minute
- **Note:** The Raven's image set contains 36 questions. By default, the battery use 12 images starting from image #13 (middle 3rd of the set)

## Sternberg Task
- 1 practice block with 24 trials
- 48 trials per block in the main task
- Number of blocks adjustable in Settings
- Digit set: 0-9 (inclusive)
- Short sequence length: 2 digits
- Long sequence length: 6 digits
- Digit duration: 1200ms
- Time between digits: 250ms
- Probe duration: 2250ms

## Raven's Progressive Matrices Task (Standard Scale)
- **New implementation using standard scale images**
- 60 trials across 5 sets (A, B, C, D, E)
- 12 trials per set
- Sets A and B: 6 answer options per trial (3×2 grid)
- Sets C, D, and E: 8 answer options per trial (4×2 grid)
- Mouse click selection with visual feedback (blue border)
- Spacebar to advance to next trial
- Automatic data saving after each trial
- **File:** `tasks/raven_task.py`
- **Class:** `RavenTask`
- **Note:** Requires manual configuration of ANSWER_KEY in the source code (lines 68-128)

## Sustained Attention to Response Task (SART)
- Digit set: 1-9 (inclusive)
- Mask follows presentation of each digit
- 1 practice set with 10 digits
- 225 main trials, 25 repeats of each digit (~5 minutes)
- Digit duration: 250ms
- Mask duration: 900ms

## FourFigures
- 4 parts with part-specific instructions
- Practice + experimental block per part
- Response options: Cuadrado / Círculo / Triángulo / Cruz
- Part 4 includes red rule-switch stimuli
- Exports contour/content response accuracy per trial

## Ikigai
- 1 introduction screen followed by 2 selection screens
- Page 1 asks for 4 jobs considered most important for the world
- Page 2 asks for 4 personal skills or behavioral tendencies
- Options are loaded dynamically from the `enunciados/IKIGAI_WorldNeed` and `enunciados/IKIGAI_PaidFor` files
- Each page requires exactly 4 selections before enabling the advance/finish button
