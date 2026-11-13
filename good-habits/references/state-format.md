# State format

Read this when you create or change the user's state files (levels 1 and 2).

## Where the files live

One folder chosen by the user, default `~/good-habits`. Never the skill folder, never a code repository.
It holds exactly two files: `habits.json` and `log.jsonl`. Nothing derived is stored: progress, continuity,
streaks and milestones are always recomputed by `scripts/habits.py` from the log.

## habits.json

Configuration. You write it; the script only reads it. Rewrite the whole file on every change and keep it
valid JSON.

```json
{
  "version": 1,
  "preferences": { "checkin_time": "20:30", "summary_day": "sun", "timezone": "Europe/Rome",
                   "paths": { "sleep-better": "22:00" } },
  "habits": [
    {
      "id": "hydration",
      "key": "hydration",
      "title": "Water",
      "goal_type": "quantity",
      "period": "day",
      "unit": "ml",
      "target": 2000,
      "target_min": 500,
      "target_max": 4000,
      "step": null,
      "days": null,
      "time": null,
      "status": "active",
      "path": null,
      "created": "2026-11-01"
    },
    {
      "id": "bedtime",
      "key": "bedtime",
      "title": "In bed by",
      "goal_type": "time",
      "period": "day",
      "target": "22:00",
      "step": -15,
      "time": "21:30",
      "status": "active",
      "path": null,
      "created": "2026-11-01"
    },
    {
      "id": "workout",
      "key": "workout",
      "title": "Workout",
      "goal_type": "count",
      "period": "week",
      "unit": "sessions",
      "target": 3,
      "target_min": 1,
      "target_max": 7,
      "step": 1,
      "days": ["mon", "wed", "fri"],
      "time": "18:00",
      "status": "active",
      "path": null,
      "created": "2026-11-01"
    }
  ]
}
```

### Habit fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | unique, lowercase, used in every command and log line. Default: the catalog `key`; a second habit from the same key gets a suffix (`daily-reading-2`); a custom habit is `custom-<short-name>` |
| `key` | yes | catalog key it came from, or `custom` |
| `title` | no | short name in the user's language; shown in calendar files. Without it the key is used |
| `goal_type` | yes | `quantity`, `time`, `count` or `check` |
| `period` | yes | `day` or `week` (`time` goals are always `day`) |
| `unit` | quantity, count | e.g. `ml`, `pages`, `minutes`, `sessions` |
| `target` | all but `check` | a positive number; for `time` an `HH:MM` limit (`22:00` = by 22:00) |
| `target_min`, `target_max` | no | bounds for progression proposals |
| `step` | no | progression step; `null` = never propose a change. For `time`, minutes: negative = earlier |
| `days` | no | planned weekdays `mon`…`sun`; `null` = every day. For weekly habits only the calendar uses it |
| `time` | no | `HH:MM` local time of the habit; used for calendar files and path schedules |
| `status` | no | `active` (default) or `archived`. **Pauses are not stored here**: they are facts in the log |
| `path` | no | key of the path that created it, or `null` |
| `created` | yes | local date `YYYY-MM-DD` of activation; days before it count only when done, never as missed |
| `history` | no | earlier targets: `[{"until": "YYYY-MM-DD", "target": ...}]`, each valid for the days before `until` |

Activating a catalog habit copies its defaults once: `default_target` → `target`, `progression_step` → `step`,
`default_days` → `days`, `default_time` → `time`, `unit`, `target_min`, `target_max` as they are. From then on
the habit belongs to the user: later catalog changes never touch it.

Optional fields may be left out or set to `null`: both mean "not set". `version` and `preferences` are
optional. `preferences` are for you, not for the script: the time of the daily check-in and the day of the
weekly summary (`mon`…`sun`), once agreed, `timezone` (IANA name, e.g. `Europe/Rome`, needed by scheduled
runs) and `paths`, the anchor time `HH:MM` of each activated path.

### Changes

- **Edit** (days, time, title): change the field. Changing `days` re-evaluates past days.
- **Change the target** (by request, an accepted proposal, or a moved path anchor for a `time` goal):
  append the old one to `history` with `until` = today's date, then set the new `target`. Past days keep
  the target they had: `{"until": "2026-11-22", "target": "23:00"}` keeps 23:00 for every day before 22.11.
- **Archive**: `"status": "archived"`. History stays in the log; the habit disappears from `today` and `progress`.
- **Delete**: only after the user confirms that the history goes too. Remove the habit from `habits.json` and
  rewrite `log.jsonl` without its lines. This is the only case where the log is rewritten.

## log.jsonl

Facts, one JSON object per line, append only. Write it through `habits.py log`, never by hand, so dates and
values are validated.

```jsonl
{"habit": "hydration", "event": "log", "date": "2026-11-13", "at": "2026-11-13T09:12:40+01:00", "value": 250}
{"habit": "bedtime", "event": "log", "date": "2026-11-13", "at": "2026-11-13T21:58:03+01:00", "value": "21:55"}
{"habit": "workout", "event": "log", "date": "2026-11-13", "at": "2026-11-13T19:02:11+01:00", "value": 40}
{"habit": "workout", "event": "skip", "date": "2026-11-16", "at": "2026-11-13T19:03:00+01:00"}
{"habit": "hydration", "event": "pause", "date": "2026-11-20", "at": "2026-11-13T19:04:00+01:00", "until": "2026-11-27"}
{"habit": "hydration", "event": "resume", "date": "2026-11-24", "at": "2026-11-24T08:00:00+01:00"}
```

| Field | Meaning |
|---|---|
| `habit` | habit `id` |
| `event` | `log`, `skip`, `pause` or `resume` |
| `date` | the user's **local** date the fact belongs to, set with `--date`: today, an earlier day the user reports, or the future day of a planned skip or pause. Always pass it: the machine clock may not be the user's (remote environments often run in UTC) |
| `at` | moment of writing, with offset |
| `value` | `log` only: a number for `quantity` (a negative number corrects an earlier entry), `HH:MM` for `time`, optional number for `count` (e.g. minutes), absent for `check` |
| `until` | `pause` only, optional: the resume date. Without it the pause lasts until a `resume` |

### What the events mean

- **log**: something happened. `quantity` sums values in the period, `count` counts lines, `check` needs one
  line. For `time` the **last** value of the day counts (log again to correct it); it is on time when it is
  at or up to 12 hours before the target, so 00:15 is late for a 23:00 target. A late time is final for
  that day (`missed`), not `open`.
- **skip**: a planned rest for that day (for weekly habits: that week). Not counted as missed.
- **pause** / **resume**: the habit is on hold from the pause date up to, not including, the resume date.
  Paused days are not counted. For a weekly habit, a pause on any day leaves the whole week out.
- A completed period always counts, even on a skipped, paused or unplanned day.

## Moving from level 0

When files become available, offer to transcribe what you remember:

1. Set each habit's `created` to the day the files start (today). Earlier facts still count when done,
   and days the user never reported are not counted as missed.
2. List the remembered facts with their dates and ask the user to confirm them once; drop any they don't.
3. Write each confirmed fact with `habits.py log … --date <that day>`. Never estimates, never "not done"
   days: they need no line.
