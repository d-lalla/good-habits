---
key: daily-steps
category: activity
goal_type: quantity       # quantity | time | count | check
period: day               # day | week
unit: steps
default_target: 6000      # example value, user-adjustable
target_min: 1000
target_max: 20000
quick_log: null
progression_step: 500
default_days: null        # every day
default_time: null
---
# Daily steps

Walk a number of steps per day, as counted by the user's phone or watch.

## Why it helps
Walking is the easiest movement to fit into a day, and a step counter gives a number without effort. The
target is an example: a good one is a bit more than what the user does now. Anyone with a condition that
limits walking adapts it with a professional, or picks a different habit.

## Start small
- Ask for a typical daily count from the last week and start a little above it.
- Add walks to routines: a stop earlier, the stairs, a short walk after lunch.

## How to log
- Value: steps. The device shows a running total, but logs add up: log the difference since the last
  report. If `today` shows 4000 and the user now says 6500, log 2500.
- If the user reports only once a day, log the total once.

## Messages
Fill the numbers from `today`.
- start: "{target} steps is today's example target."
- midway: "{value} of {target} steps so far today."
- almost there: "{remaining} steps to go for today's {target}."
