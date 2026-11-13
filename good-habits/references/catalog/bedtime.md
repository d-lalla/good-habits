---
key: bedtime
category: sleep
goal_type: time           # quantity | time | count | check
period: day               # day | week
unit: null
default_target: "22:00"   # in bed by this time; example value, user-adjustable
target_min: null
target_max: null
quick_log: null
progression_step: -15     # minutes: a proposal moves the target 15 minutes earlier (or later when reducing)
default_days: null        # every day; weekends can be left out
default_time: "21:30"     # gentle cue before the target
---
# Bedtime

Go to bed by a chosen time.

## Why it helps
A regular bedtime is one of the simplest levers on rest: the body tends to settle into a rhythm when
evenings look alike. The right time depends on when the user needs to get up and how much sleep suits them;
22:00 is only an example. Persistent trouble sleeping is something to discuss with a professional, not to
fix with a target.

## Start small
- Ask about the usual bedtime of the last few nights and start from there, not from an ideal one.
- Move it in small steps (about 15 minutes) and only when the current time feels easy.
- A cue about 30 minutes before (dim lights, put the phone away) helps more than the target itself.
  When the target changes, propose moving the cue (`time`) with it.

## How to log
- Value: the local time the user went to bed, `HH:MM`. "Going to bed now" means the user's current
  local time; if you are not sure of it, ask.
- The day it belongs to is the evening it started: after midnight, log it on the previous date.
- On time means at or before the target (any time up to 12 hours earlier). Later is simply late.
- A wrong time is corrected by logging the right one for the same date: the last value counts.

## Messages
Fill the numbers from `today`. Describe, never judge a late night. Leave out the numbers while
`last_7.scheduled` is 0.
- before: "Bedtime tonight: {target}."
- after: "In bed at {value}. Last 7 days: {last_7.done} of {last_7.scheduled} evenings by {target}."
