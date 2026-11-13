---
key: regular-sleep-schedule
category: sleep
goal_type: time           # quantity | time | count | check
period: day               # day | week
unit: null
default_target: "07:30"   # up by this time, every day; example value, user-adjustable
target_min: null
target_max: null
quick_log: null
progression_step: null    # regularity matters, not getting up ever earlier
default_days: null        # every day, weekends included: that is the point
default_time: null
---
# Regular sleep schedule

Get up at about the same time every day, weekends included.

## Why it helps
A steady wake-up time is often what sets the body's daily rhythm, more than the bedtime. Many people find
evenings get easier once mornings are regular. The right time depends on the user's life; 07:30 is only an
example. Persistent trouble sleeping or staying awake is something to discuss with a professional.

## Start small
- Ask when the user usually gets up on workdays and use that, so weekends are the only change.
- If weekdays and weekends differ a lot, start with a time in between that works for both, then narrow it.
- Pair it with daylight or a glass of water right after getting up.

## How to log
- Value: the local time the user got up, `HH:MM`. "I'm up now" means the user's current local time.
- On time means at or before the target. A wrong time is corrected by logging the right one: the last
  value of the day counts.

## Messages
Fill the numbers from `today`. Leave out the numbers while `last_7.scheduled` is 0.
- before: "Today's wake-up time: {target}."
- after: "Up at {value}. Last 7 days: {last_7.done} of {last_7.scheduled} mornings by {target}."
