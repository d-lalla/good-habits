---
key: no-screens-before-bed
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
default_time: "21:00"     # screens away about an hour before bed; example value, user-adjustable
---
# No screens before bed

Put phone, laptop and TV away for a while before going to bed.

## Why it helps
Screens keep the mind busy and can push bedtime later without noticing. A screen-free stretch before bed
leaves room for slower activities like reading or a routine. How long is a personal choice; an hour is an
example, fifteen minutes is a real start.

## Start small
- Start with 15-30 minutes before the usual bedtime and lengthen only if it feels easy.
- Charge the phone outside the bedroom, or at least out of reach.
- Decide in advance what replaces the screen (a book, music, a chat, stretching).

## How to log
- One log when the screens went away at the planned time, more or less. No value.
- `time` is when screens go away; if the bedtime changes, propose moving it too.

## Messages
Fill the numbers from `today`. Leave out the numbers while `week.scheduled` is 0.
- before: "Screens away around {time} tonight."
- after: "Screens away. This week {week.done} of {week.scheduled} evenings."
