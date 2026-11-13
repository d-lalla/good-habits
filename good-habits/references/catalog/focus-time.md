---
key: focus-time
category: productivity
goal_type: quantity       # quantity | time | count | check
period: day               # day | week
unit: minutes
default_target: 25        # one block; example value, user-adjustable
target_min: 15
target_max: 240
quick_log: [25, 50]
progression_step: 15
default_days: [mon, tue, wed, thu, fri]  # workdays; example
default_time: null
---
# Focus time

Work on one important task without interruptions for a block of time.

## Why it helps
Deep work needs uninterrupted time, and interruptions are the default in most days. A protected block,
even a short one, is often where the most important task actually moves.

## Start small
- One block of 25 minutes with notifications off and one task chosen in advance.
- Put it in the calendar at the same time each workday.

## How to log
- Value: minutes of focused work. Quick amounts: 25, 50. Several blocks per day add up.
- Interrupted blocks count for the minutes that were focused; no need to be strict.

## Messages
Fill the numbers from `today`.
- start: "{target} minutes of focus time is today's example."
- midway: "{value} of {target} focused minutes so far today."
- almost there: "{remaining} minutes to go for today's {target}."
