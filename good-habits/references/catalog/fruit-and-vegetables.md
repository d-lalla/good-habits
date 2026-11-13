---
key: fruit-and-vegetables
category: nutrition
goal_type: count          # quantity | time | count | check
period: day               # day | week
unit: portions
default_target: 3         # example value, user-adjustable
target_min: 1
target_max: 8
quick_log: null
progression_step: 1       # one portion more (or less) per day
default_days: null        # every day
default_time: null
---
# Fruit and vegetables

Eat a number of portions of fruit or vegetables each day.

## Why it helps
Fruit and vegetables add variety to meals, and counting portions is simpler than counting anything else.
The number is an example: what fits depends on the person, their tastes and any dietary needs. Anyone
with a dietary restriction or a health condition follows the advice of their doctor or dietitian.

## Start small
- Ask roughly how many portions the user eats on a normal day and start from one more.
- Add to meals that already exist: fruit at breakfast, vegetables with lunch.
- Keep something ready to eat in sight.

## How to log
- One log per portion. No value. A portion is roughly a handful or a small bowl; the user decides.
- Never ask about quantities in grams or about the rest of the diet.

## Messages
Fill the numbers from `today`.
- start: "{target} portions of fruit or vegetables is today's example."
- midway: "{value} of {target} portions so far today."
- almost there: "{remaining} more portion for today's {target}."
