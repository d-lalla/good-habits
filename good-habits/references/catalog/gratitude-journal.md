---
key: gratitude-journal
category: mind
goal_type: check          # quantity | time | count | check
period: day               # day | week
unit: null
default_target: null
target_min: null
target_max: null
quick_log: null
progression_step: null
default_days: null        # every day
default_time: null
---
# Gratitude journal

Write down one to three things the user is grateful for.

## Why it helps
Noticing a few good things on purpose is a simple reflective habit that many people find pleasant at the
end of the day. It works on paper or in any notes app the user prefers.

## Start small
- One line is enough. Same moment every day, e.g. in bed or after dinner.
- Paper or the user's own app; never in this skill's files.

## How to log
- One log when the user has written. No value.
- **Only the fact is recorded, never the content.** Do not ask what they wrote. If they share it, respond
  kindly and do not store it anywhere.

## Messages
Fill the numbers from `today`. Leave out the numbers while `week.scheduled` is 0.
- before: "A line in the gratitude journal, if it suits today."
- after: "Journal written. This week {week.done} of {week.scheduled} days."
