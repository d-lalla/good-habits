# Good Habits

**An Agent Skill that helps people build habits that last — without streak anxiety.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-8A2BE2.svg)](https://agentskills.io/specification)
[![Python](https://img.shields.io/badge/python-3%20·%20stdlib%20only-3776AB.svg)](good-habits/scripts/habits.py)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#how-it-works)

Good Habits turns your AI assistant into a calm habit coach. It helps you pick a few habits from a curated
catalog, start small, log what you did in plain words, and see how it's going — "this week 4 of 7" — with
no points, no badges and no "your streak is at risk".

Works with any assistant that loads [Agent Skills](https://agentskills.io/specification) (`SKILL.md`):
Claude Code, the Claude apps, Codex and others.

---

## Why

Most habit trackers punish you for missing a day. Anxiety and guilt are exactly what make people quit.
Good Habits is built on the opposite idea:

- **Describes, never judges.** "4 sessions so far", never "you failed".
- **Rest is not failure.** Planned skips and pauses are left out of every count.
- **Small steps.** Every default is an example to adjust. Raising or lowering a target is only ever a
  proposal you accept or decline.
- **Exact numbers.** Progress is computed by a small script, not guessed by the model.
- **Your data stays yours.** Two plain files in a folder you choose. Journal habits record only *that* you
  wrote, never *what*.

## Example

> **You:** I drank two glasses and a 500 ml bottle today, and I'm skipping Sunday, I'll be travelling.
>
> **Assistant:** Logged: 1000 of 1500 ml so far today. Sunday is marked as a rest day for water.
>
> **You:** Going to bed now.
>
> **Assistant:** In bed at 22:50. Last 7 days: 5 of 6 evenings by 23:00.

And on Sunday, if you like, a short weekly summary: what went well, what changed, and at most one
suggestion.

## Features

- **21 habits** across sleep, nutrition, activity, mind, learning, productivity and relationships, plus
  fully custom habits.
- **3 ready-made paths** that set up several habits around one anchor time (e.g. *Sleep better*: screens
  away 60 min before bed, read, meditate, in bed by your chosen time).
- **Four goal types**: amounts (2000 ml, 10 pages), times (in bed by 22:30), counts (3 workouts a week)
  and simple check-offs.
- **Contextual check-ins** that know your progress, instead of bare reminders.
- **Weekly summaries** with continuity over 7 and 28 days and progression proposals after two steady weeks.
- **Calendar export** (`.ics`) for habits with a fixed time.
- **Graceful degradation**: works in plain chat, gets exact with files, gets proactive with scheduled
  tasks (see [Levels](#levels)).
- **Any language**: the skill is written in English; the assistant answers in yours.

## Install

Every option below installs the skill for **you only** (user scope), available in all your projects.

**Claude Code** — as a plugin, in one step (Claude Code 2.1.275 or later), inside a session:

```
/plugin install good-habits --marketplace d-lalla/good-habits
```

Or from your shell, in two steps:

```bash
claude plugin marketplace add d-lalla/good-habits
```

```bash
claude plugin install good-habits@good-habits
```

Updates come from this repository. As a plugin skill it is listed as `good-habits:good-habits`; it still
activates on its own when you talk about habits
([plugin docs](https://code.claude.com/docs/en/plugin-marketplaces)).

**Claude Code, Codex, Cursor, opencode and 70+ other agents** — with the
[`skills`](https://github.com/vercel-labs/skills) CLI, which asks which agents to install to:

```bash
npx skills add d-lalla/good-habits -g
```

**Manual copy** — the skill is the [`good-habits/`](good-habits) folder (the one containing `SKILL.md`),
not the whole repository. Keep the folder name `good-habits`: it must match the skill's `name`.

```bash
git clone https://github.com/d-lalla/good-habits.git
```

```bash
cp -r good-habits/good-habits ~/.claude/skills/good-habits
```

For Codex the manual target is `~/.agents/skills/good-habits`
([docs](https://learn.chatgpt.com/docs/build-skills)).

**Claude apps (claude.ai, desktop)** — turn on *Settings › Capabilities › Code execution and file
creation*, then *Customize › Skills › + › Upload a skill* and upload a ZIP with the `good-habits` folder at
its root ([help center](https://support.claude.com/en/articles/12512180-use-skills-in-claude)):

```bash
cd good-habits && zip -r good-habits.zip good-habits
```

On Windows: `Compress-Archive -Path good-habits -DestinationPath good-habits.zip`. No command can install
a skill into a claude.ai account: the upload is the only way, and it stays private to you.

**ChatGPT** — according to OpenAI's docs, standalone skills are available in the desktop app (*Skills*
sidebar) and, packaged as plugins, on web and mobile. See [Known limitations](#known-limitations).

**Other Agent Skills hosts** — copy the folder wherever your assistant loads skills from.

## Usage

There are no commands to learn. Just talk:

- "I want to sleep better. Where do I start?"
- "Set up the morning routine path, I wake up at 7."
- "Drank 500 ml." · "Read 12 pages." · "Worked out, 40 minutes."
- "Skip reading tonight, I'm tired." · "Pause everything from Thursday to Saturday."
- "How did this week go?"
- "Make the water target 1500." · "Archive the stretching habit."

On first use the assistant asks which areas you care about, proposes two or three habits per area,
suggests starting with one or two, and asks where to keep your data (default `~/good-habits`).

## Levels

The skill checks what your assistant can do and tells you in one line.

| Level | Your assistant can | You get |
|---|---|---|
| 0 | only chat | help choosing and configuring, check-ins in conversation; no exact counts |
| 1 | write persistent files and run Python 3 | exact records and numbers, calendar file |
| 2 | also schedule tasks | one daily check-in and one weekly summary, automatically |

Nothing is lost when moving up: the assistant offers to write down what it already knows.

## Catalog

| Category | Habits |
|---|---|
| Sleep | `bedtime`, `regular-sleep-schedule`, `evening-routine`, `no-screens-before-bed` |
| Nutrition | `hydration`, `fruit-and-vegetables`, `less-sugary-drinks` |
| Activity | `workout`, `daily-steps`, `stretching`, `active-breaks` |
| Mind | `meditation`, `breathing`, `gratitude-journal` |
| Learning | `daily-reading`, `language-study`, `learning-15-min` |
| Productivity | `plan-day`, `weekly-review`, `focus-time` |
| Relationships | `reach-out` |

| Path | Anchor | Habits |
|---|---|---|
| `sleep-better` | bedtime | no screens → reading → meditation → bedtime |
| `morning-start` | wake-up time | water → stretching → plan the day |
| `focused-workday` | start of work | plan the day → focus time → active breaks → weekly review |

## How it works

```
good-habits/                 the skill: this is the folder you install
  SKILL.md                   when to activate, levels, flows, tone, limits
  references/
    catalog/<key>.md         one habit per file, loaded only when needed
    paths/<key>.md           one path per file
    state-format.md          format of habits.json and log.jsonl
  scripts/habits.py          log, today, progress, ics (Python 3, standard library only)
.claude-plugin/
  marketplace.json           makes the repo installable as a Claude Code plugin and via `npx skills`
tests/test_habits.py         tests for the script, the catalog, the paths, SKILL.md and the manifest
```

- **The assistant is the interface; the script is the source of truth for numbers.** `habits.py` prints
  JSON and contains no user-facing text, so the assistant phrases everything in your language.
- **State is two files** in your folder: `habits.json` (configuration) and `log.jsonl` (an append-only
  list of facts: logs, skips, pauses, resumes). Progress, continuity and milestones are always recomputed,
  never stored.
- **Progressive disclosure.** Only the short `SKILL.md` is loaded when the skill activates; habit and path
  files are read on demand.

You can also run the script yourself:

```bash
python3 good-habits/scripts/habits.py today --data ~/good-habits --date 2026-11-13
```

## Privacy and safety

- Data lives only in the folder you choose, never in the skill folder or in a repository
  ([`.gitignore`](.gitignore) excludes it here too).
- No weight, calories, diagnoses or medication are ever asked for. Diary-style habits store only the fact
  that you wrote; contacts in `reach-out` are never recorded.
- **Not medical advice.** Defaults are examples, not recommendations valid for everyone. For anything
  medical, the skill suggests talking to a professional.

## Known limitations

Checked against the official documentation in November 2026; where that wasn't possible, it says so.

- **File persistence.** Level 1 needs files that survive between conversations. Claude Code, Codex CLI and
  desktop apps working on a local folder have them. For claude.ai and ChatGPT it is not documented that the
  execution environment keeps files across conversations; there the skill runs at level 0. *Not verified.*
- **ChatGPT and scripts.** OpenAI's docs allow a `scripts/` folder in skills but don't say whether ChatGPT
  runs bundled Python scripts. *Not verified.*
- **Scheduled tasks in Claude Desktop** ([docs](https://claude.com/docs/third-party/claude-desktop/scheduled-tasks)):
  they run on your computer, which must be awake with the app open. Missed runs collapse into one when the
  app reopens; runs missed more than seven days ago don't run.
- **Scheduled tasks in ChatGPT** ([help center](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)):
  3 to 15 active tasks depending on the plan, at most daily on the free plan, and each run uses your plan's
  allowance. Whether a scheduled task can use a skill and run its script: *not verified*.
- **Claude Code cloud routines**: daily run limits appear only in third-party sources. *Not verified.*
- **Level 2 testing** used a session-scoped scheduled task in Claude Code (one check-in, run on time).
  Durable scheduled tasks in Claude Desktop and ChatGPT have not been tested.
- **Memory at level 0**: how reliable an assistant's memory is across conversations can't be verified,
  which is why the skill gives no exact counts at level 0.
- **Time zones**: remote environments often run in UTC. The script takes the local date via `--date`, and
  scheduled prompts carry the user's time zone.
- **Corrections**: amounts are corrected with a negative entry and times by logging again (the last value
  wins). A wrong `count` or `check` entry can't be undone yet.
- **Changing planned days** (`days`) re-evaluates past days; changing a target doesn't (old targets are
  kept in `history`).
- **Times past midnight**: a time counts as on time if it falls within the 12 hours before the target.

## Contributing

Issues and pull requests are welcome.

- **New habit**: add `good-habits/references/catalog/<key>.md` following an existing file (header with
  defaults, then *Why it helps*, *Start small*, *How to log*, *Messages*) and list it in the catalog index
  of `SKILL.md`.
- **New path**: add `good-habits/references/paths/<key>.md` and list it in the paths table of `SKILL.md`.
- Keep the tone rules: descriptive language, no gamification, no health data, defaults as examples.
- Run the tests; they validate every catalog and path file and check that `SKILL.md` matches them:

```bash
python -m unittest discover -s tests
```

Design notes (in Italian): [approved decisions](docs/decisioni.md) ·
[original analysis](docs/analisi-good-habits.md).

## License

[MIT](LICENSE)
