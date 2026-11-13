---
key: active-breaks
category: activity
goal_type: count          # quantity | time | count | check
period: day               # day | week
unit: breaks
default_target: 3         # example value, user-adjustable
target_min: 1
target_max: 10
quick_log: null
progression_step: 1
default_days: [mon, tue, wed, thu, fri]  # workdays; example
default_time: null
---
# Active breaks

Stand up and move for a few minutes during long stretches of sitting.

## Why it helps
Long sitting without a break is common at desks. Standing up, walking to get water or stretching for two
or three minutes breaks it up, and many people find it clears the head too.

## Start small
- Start with two or three breaks on workdays, tied to moments that exist (after a meeting, after lunch).
- Two minutes counts: stand, walk, look out of a window.

## How to log
- One log per break. No value.
- The user can log several at once at the end of the day ("I took 3 breaks"): three logs.

## Messages
Fill the numbers from `today`.
- start: "{target} short breaks is today's example."
- midway: "{value} of {target} breaks so far today."
- almost there: "{remaining} more break for today's {target}."
