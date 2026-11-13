---
key: workout
category: activity
goal_type: count          # quantity | time | count | check
period: week              # day | week
unit: sessions
default_target: 3         # sessions per week; example value, user-adjustable
target_min: 1
target_max: 7
quick_log: null
progression_step: 1       # one session more (or less) per week
default_days: [mon, wed, fri]  # suggested days for the calendar; any day counts
default_time: "18:00"
---
# Workout

A number of exercise sessions per week, of any kind the user enjoys.

## Why it helps
Regular movement supports energy, mood and sleep for many people. The kind of exercise matters less than
doing it often enough to become routine. Anyone with a health condition, an injury, or who has not been
active for a while checks with a professional before starting; the skill does not prescribe exercises.

## Start small
- Start with fewer sessions than planned: two that happen beat four that don't.
- Short counts: a 15-minute session is a session.
- Pick fixed days and a time; the user can still move them within the week.

## How to log
- One log per session. Optional value: duration in minutes.
- The type of activity is not stored; ask only if the user wants to talk about it.
- The week runs Monday to Sunday; sessions on any day count toward it.

## Messages
Fill the numbers from `today` / `progress`. A week below target is simply a week, not a failure.
- start: "New week: {target} sessions is the plan."
- midway: "{value} of {target} sessions this week."
- almost there: "{remaining} more and this week's {target} sessions are done."
