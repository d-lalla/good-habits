---
key: daily-reading
category: learning
goal_type: quantity       # quantity | time | count | check
period: day               # day | week
unit: pages
default_target: 10        # example value, user-adjustable
target_min: 1
target_max: 100
quick_log: [5, 10]
progression_step: 2
default_days: null        # every day
default_time: "21:00"
---
# Daily reading

Read a number of pages each day, of any book the user chooses.

## Why it helps
Reading a little every day adds up to several books a year, and it is a calm way to end the day away from
screens. Pages are easy to count; the target is an example.

## Start small
- Five or ten pages, at a fixed moment (commute, before bed).
- Keep the book where that moment happens.
- Any book counts. Changing book is fine.

## How to log
- Value: pages read. Quick amounts: 5, 10. Several logs per day add up.
- If the user prefers minutes, make it a custom habit with unit `minutes` instead.

## Messages
Fill the numbers from `today`.
- start: "{target} pages is today's example."
- midway: "{value} of {target} pages so far today."
- almost there: "{remaining} pages to go for today's {target}."
