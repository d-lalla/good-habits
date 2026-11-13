---
key: hydration
category: nutrition
goal_type: quantity       # quantity | time | count | check
period: day               # day | week
unit: ml
default_target: 2000      # example value, user-adjustable
target_min: 500
target_max: 4000
quick_log: [250, 500]
progression_step: null    # no automatic proposals: more is not better
default_days: null        # every day
default_time: null
---
# Hydration

Drink water regularly through the day, logged in millilitres.

## Why it helps
Many people simply forget to drink while busy. Spreading water across the day can make it easier to stay
focused and comfortable. How much a person needs varies with body, climate, activity and health, so the
target is an example to adjust, not a rule. Anyone with a condition that limits fluids follows their
doctor's guidance instead.

## Start small
- Ask roughly how much the user drinks now; start from that plus one glass, rather than jumping to the
  example target.
- Tie it to moments that already exist: a glass after waking, one with each meal.
- Keep a bottle in sight; a known size (e.g. 500 ml) makes logging one tap.

## How to log
- Value: millilitres drunk, any amount. Quick amounts: 250 (a glass), 500 (a bottle). Use 250 for "a
  glass" unless the user has told you their glass size.
- Several logs per day add up; one log of the total is the same. A wrong entry is corrected with a
  negative amount.
- Water, unsweetened tea and similar count; the user decides what counts for them.

## Messages
Fill the numbers from `today` / `progress`. Never point at what is missing in a reproachful way.
- start: "A new day for water: {target} {unit} is today's example target."
- midway: "{value} of {target} {unit} so far today."
- almost there: "{remaining} {unit} to go for today's {target}."
