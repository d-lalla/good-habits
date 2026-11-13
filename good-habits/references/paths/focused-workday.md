---
key: focused-workday
anchor: start of work
default_anchor: "09:00"   # example value, user-adjustable
---
# Focused workday

A workday shape: plan first, protect a focus block, take breaks, review the week at its end.

## Steps
| Offset (min) | Habit | Overrides |
|---|---|---|
| 0 | `plan-day` | — |
| 15 | `focus-time` | — |
| — | `active-breaks` | — |
| 480 | `weekly-review` | days=fri |

## Notes
- The anchor is when the user starts working. 09:00 is an example.
- `active-breaks` has no fixed time: breaks happen when they fit.
- `weekly-review` moves to Friday, at the end of the working week (anchor + 8 hours). The user can keep
  Sunday instead.
