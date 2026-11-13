---
key: evening-routine
category: sleep
goal_type: check          # quantity | time | count | check
period: day               # day | week
unit: null
default_target: null
target_min: null
target_max: null
quick_log: null
progression_step: null
default_days: null        # every day
default_time: "21:30"     # example value, user-adjustable
---
# Evening routine

A short, repeatable sequence that closes the day.

## Why it helps
Doing the same few things each evening signals that the day is ending, which many people find makes
winding down easier. The content matters less than the repetition.

## Start small
- Agree on two or three steps the user already half does, e.g. tidy one surface, prepare tomorrow's bag,
  wash, dim the lights. Write them in the habit `title` only if the user wants.
- Ten minutes is enough. Same order every evening.
- Start it at the same time, e.g. after dinner or 30 minutes before bed.

## How to log
- One log when the routine is done. No value.
- Doing part of it is fine to log if the user considers it done; don't ask for details.

## Messages
Fill the numbers from `today`. Leave out the numbers while `week.scheduled` is 0.
- before: "Evening routine at {time}, if it suits tonight."
- after: "Evening routine done. This week {week.done} of {week.scheduled} evenings."
