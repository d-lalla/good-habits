---
key: sleep-better
anchor: bedtime
default_anchor: "22:00"   # example value, user-adjustable
---
# Sleep better

An evening sequence that leads up to a regular bedtime.

## Steps
| Offset (min) | Habit | Overrides |
|---|---|---|
| -60 | `no-screens-before-bed` | — |
| -45 | `daily-reading` | — |
| -20 | `meditation` | — |
| 0 | `bedtime` | — |

## Notes
- The anchor is the time the user wants to be in bed. Ask for the usual one too: if the wanted time is
  much earlier, suggest starting closer to the usual one (bedtime "Start small"). 22:00 is an example.
- The earlier steps already work as cues, so `bedtime` may need no cue of its own (`time: null`); ask.
- Each step is a normal habit: skipping one never affects the others.
- Offer to start with two steps (e.g. screens away and bedtime) and add the rest later.
