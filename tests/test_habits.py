"""Tests for good-habits/scripts/habits.py. Standard library only: python -m unittest discover tests"""
import importlib.util
import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("habits", ROOT / "good-habits" / "scripts" / "habits.py")
habits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(habits)

MON = date(2026, 11, 9)  # a Monday
D = lambda n: MON + timedelta(days=n)  # noqa: E731


def ev(habit, day, event="log", value=None, until=None):
    e = {"habit": habit, "event": event, "date": day.isoformat()}
    if value is not None:
        e["value"] = value
    if until is not None:
        e["until"] = until.isoformat()
    return e


def track(habit, events):
    habits.check_habit(habit)
    return habits.Track(habit, events)


WATER = {"id": "water", "key": "hydration", "goal_type": "quantity", "period": "day", "unit": "ml",
         "target": 2000, "created": "2026-10-01"}
BED = {"id": "bed", "key": "bedtime", "goal_type": "time", "period": "day", "target": "22:00", "created": "2026-10-01"}
GYM = {"id": "gym", "key": "workout", "goal_type": "count", "period": "week", "target": 2, "created": "2026-10-01"}
PLAN = {"id": "plan", "key": "plan-day", "goal_type": "check", "period": "day",
        "days": ["mon", "tue", "wed", "thu", "fri"], "created": "2026-10-01"}


class CompletionRules(unittest.TestCase):
    def test_sum_at_least(self):
        t = track(WATER, [ev("water", D(0), value=1250), ev("water", D(0), value=750), ev("water", D(1), value=500)])
        self.assertEqual(t.evaluate(D(0), D(1)), {"status": "done", "value": 2000})
        s = t.snapshot(D(1))
        self.assertEqual((s["status"], s["value"], s["remaining"]), ("open", 500, 1500))

    def test_time_before(self):
        tb, m = habits.time_before, habits.parse_hhmm
        self.assertTrue(tb(m("21:40"), m("22:00")))
        self.assertTrue(tb(m("22:00"), m("22:00")))
        self.assertFalse(tb(m("22:10"), m("22:00")))
        self.assertFalse(tb(m("00:15"), m("23:30")))  # after midnight is late
        self.assertTrue(tb(m("23:50"), m("00:30")))   # before a post-midnight target is on time
        t = track(BED, [ev("bed", D(0), value="21:45"), ev("bed", D(1), value="22:30")])
        self.assertEqual(t.evaluate(D(0), D(2))["status"], "done")
        self.assertEqual(t.evaluate(D(1), D(2))["status"], "missed")
        self.assertEqual(t.evaluate(D(1), D(1))["status"], "missed")  # late today is final, not "open"
        self.assertEqual(track(BED, []).evaluate(D(1), D(1))["status"], "open")

    def test_time_last_value_corrects(self):
        late = [ev("bed", D(0), value="21:50"), {**ev("bed", D(0), value="00:15"), "at": "2026-11-10T08:00"}]
        self.assertEqual(track(BED, late).evaluate(D(0), D(1)), {"status": "missed", "value": "00:15"})
        early = [ev("bed", D(0), value="23:30"), {**ev("bed", D(0), value="21:30"), "at": "2026-11-10T08:00"}]
        self.assertEqual(track(BED, early).evaluate(D(0), D(1)), {"status": "done", "value": "21:30"})

    def test_count_at_least(self):
        t = track(GYM, [ev("gym", D(0)), ev("gym", D(3), value=45)])
        self.assertEqual(t.evaluate(MON, D(6)), {"status": "done", "value": 2})
        t = track(GYM, [ev("gym", D(0))])
        self.assertEqual(t.evaluate(MON, D(2)), {"status": "open", "value": 1})
        self.assertEqual(t.evaluate(MON, D(7))["status"], "missed")

    def test_checked(self):
        t = track(PLAN, [ev("plan", D(0))])
        self.assertEqual(t.evaluate(D(0), D(1))["status"], "done")
        self.assertEqual(t.evaluate(D(1), D(2))["status"], "missed")
        self.assertEqual(t.evaluate(D(5), D(6))["status"], "not_scheduled")  # Saturday


class Continuity(unittest.TestCase):
    READ = {"id": "read", "goal_type": "check", "period": "day", "created": "2026-10-19"}

    def scenario(self):
        # Mon, Tue, Thu, Sun done; Wed skipped; Fri missed; Sat paused
        return track(self.READ, [
            ev("read", D(0)), ev("read", D(1)), ev("read", D(2), "skip"), ev("read", D(3)),
            ev("read", D(5), "pause", until=D(6)), ev("read", D(6)),
        ])

    def test_windows_7_and_28(self):
        t = self.scenario()
        self.assertEqual(t.window(7, D(6)), {"done": 4, "scheduled": 5})
        # 28 days back from Sunday 15.11 start on 19.10 (creation): 21 empty days before this week
        self.assertEqual(t.window(28, D(6)), {"done": 4, "scheduled": 26})

    def test_today_counts_only_when_done(self):
        t = track(self.READ, [ev("read", D(0))])
        self.assertEqual(t.window(7, D(1)), {"done": 1, "scheduled": 6})  # 03..08.11 missed, Mon done, Tue open

    def test_before_creation_not_counted(self):
        t = track(dict(self.READ, created=D(4).isoformat()), [ev("read", D(4))])
        self.assertEqual(t.window(28, D(4)), {"done": 1, "scheduled": 1})

    def test_longest_streak_is_not_broken_by_skips_or_pauses(self):
        p = self.scenario().progress(D(6))
        self.assertEqual(p["longest_streak"], 3)  # Mon, Tue, (skip), Thu; Fri breaks
        self.assertEqual(p["completed_periods"], 4)
        self.assertEqual(p["logs"], 4)

    def test_this_week(self):
        t = track(PLAN, [ev("plan", D(i)) for i in range(4)])
        self.assertEqual(t.snapshot(D(5))["week"], {"done": 4, "scheduled": 5})  # Fri missed, weekend unplanned
        self.assertEqual(t.snapshot(D(5))["status"], "not_scheduled")


class TargetHistory(unittest.TestCase):
    def test_change_does_not_regrade_the_past(self):
        bed = {**BED, "target": "22:45", "history": [{"until": D(6).isoformat(), "target": "23:00"}]}
        t = track(bed, [ev("bed", D(0), value="23:00"), ev("bed", D(1), value="22:50"), ev("bed", D(6), value="22:50")])
        self.assertEqual([t.evaluate(D(i), D(6))["status"] for i in (0, 1, 6)], ["done", "done", "missed"])
        self.assertEqual(t.snapshot(D(6))["target"], "22:45")

    def test_quantity_history_and_validation(self):
        water = {**WATER, "target": 2500, "history": [{"until": D(1).isoformat(), "target": 2000}]}
        t = track(water, [ev("water", D(0), value=2000), ev("water", D(1), value=2000)])
        self.assertEqual([t.evaluate(D(i), D(2))["status"] for i in (0, 1)], ["done", "missed"])
        with self.assertRaises(habits.UsageError):
            habits.check_habit({**WATER, "history": [{"until": "2026-11-01", "target": "lots"}]})

    def test_transcribed_facts_before_created_count_when_done(self):
        # moving from level 0: created = the day files start; remembered facts are logged on their own dates
        t = track({**PLAN, "created": D(3).isoformat()}, [ev("plan", D(0)), ev("plan", D(2))])
        self.assertEqual(t.window(7, D(3)), {"done": 2, "scheduled": 2})  # unreported 10.11 is not a miss

    def test_week_counts_so_far(self):
        t = track(PLAN, [])
        self.assertEqual(t.snapshot(D(0))["week"], {"done": 0, "scheduled": 0})  # Monday, still open
        t = track(PLAN, [ev("plan", D(0))])
        self.assertEqual(t.snapshot(D(1))["week"], {"done": 1, "scheduled": 1})


class SkipsAndPauses(unittest.TestCase):
    R = {"id": "r", "goal_type": "check", "period": "day", "created": "2026-10-01"}

    def test_skip_excluded_but_done_wins(self):
        t = track(self.R, [ev("r", D(0), "skip"), ev("r", D(1), "skip"), ev("r", D(1))])
        self.assertEqual(t.evaluate(D(0), D(3))["status"], "skipped")
        self.assertEqual(t.evaluate(D(1), D(3))["status"], "done")

    def test_pause_until_resume(self):
        t = track(self.R, [ev("r", D(0), "pause"), ev("r", D(3), "resume")])
        self.assertEqual([t.evaluate(D(i), D(5))["status"] for i in range(5)],
                         ["paused", "paused", "paused", "missed", "missed"])

    def test_pause_with_until_and_early_resume(self):
        t = track(self.R, [ev("r", D(0), "pause", until=D(5)), ev("r", D(2), "resume")])
        self.assertEqual([t.evaluate(D(i), D(6))["status"] for i in range(6)],
                         ["paused", "paused", "missed", "missed", "missed", "missed"])

    def test_open_pause_covers_today(self):
        t = track(self.R, [ev("r", D(0), "pause")])
        self.assertEqual(t.snapshot(D(4))["status"], "paused")
        self.assertEqual(t.window(7, D(4)), {"done": 0, "scheduled": 2})  # 07..08.11, before the pause

    def test_weekly_skip_skips_the_week(self):
        t = track(GYM, [ev("gym", D(2), "skip")])
        self.assertEqual(t.evaluate(MON, D(7))["status"], "skipped")


class WeeklyGoals(unittest.TestCase):
    def test_week_boundary(self):
        events = [ev("gym", D(-7)), ev("gym", D(-4)), ev("gym", D(1))]  # previous week done, this week 1 of 2
        t = track(GYM, events)
        # Wednesday: 7-day window reaches back into the previous week; current week still open
        self.assertEqual(t.window(7, D(2)), {"done": 1, "scheduled": 1})
        # Sunday: only the current week is in the window, and it is still open
        self.assertEqual(t.window(7, D(6)), {"done": 0, "scheduled": 0})
        t = track(GYM, events + [ev("gym", D(6))])
        self.assertEqual(t.window(7, D(6)), {"done": 1, "scheduled": 1})
        # next Monday: the closed week counts
        self.assertEqual(track(GYM, events).window(7, D(7)), {"done": 0, "scheduled": 1})

    def test_logs_on_sunday_and_monday_belong_to_different_weeks(self):
        t = track(GYM, [ev("gym", D(-1)), ev("gym", D(0))])
        self.assertEqual(t.evaluate(D(-7), D(0))["value"], 1)
        self.assertEqual(t.evaluate(MON, D(0))["value"], 1)

    def test_snapshot_reports_week_progress(self):
        s = track(GYM, [ev("gym", D(0))]).snapshot(D(3))
        self.assertEqual((s["status"], s["value"], s["remaining"]), ("open", 1, 1))
        self.assertNotIn("week", s)


class Progression(unittest.TestCase):
    def habit(self, **kw):
        return {**WATER, "step": 250, "target_max": 2100, "created": D(-20).isoformat(), **kw}

    def test_up_with_clamp(self):
        t = track(self.habit(), [ev("water", D(-i), value=2000) for i in range(14)])
        self.assertEqual(t.proposal(D(0)), {"direction": "up", "target": 2100})

    def test_down(self):
        self.assertEqual(track(self.habit(), []).proposal(D(0)), {"direction": "down", "target": 1750})

    def test_middle_or_too_early_or_no_step(self):
        half = [ev("water", D(-i), value=2000) for i in range(0, 14, 2)]
        self.assertIsNone(track(self.habit(), half).proposal(D(0)))
        self.assertIsNone(track(self.habit(created=D(-5).isoformat()), []).proposal(D(0)))
        self.assertIsNone(track(dict(WATER), []).proposal(D(0)))

    def test_time_step(self):
        bed = dict(BED, step=-15, created=D(-20).isoformat())
        self.assertEqual(track(bed, [ev("bed", D(-i), value="21:30") for i in range(14)]).proposal(D(0)),
                         {"direction": "up", "target": "21:45"})
        self.assertEqual(track(bed, []).proposal(D(0)), {"direction": "down", "target": "22:15"})

    def test_milestones(self):
        t = track(dict(WATER, created=D(-40).isoformat()), [ev("water", D(-i), value=2000) for i in range(30)])
        self.assertEqual(t.progress(D(0))["milestones"], ["first_week", "30_days"])


class Calendar(unittest.TestCase):
    def test_ics(self):
        hs = [
            {"id": "read", "goal_type": "check", "period": "day", "time": "21:00", "title": "Read, then; sleep"},
            {"id": "review", "goal_type": "check", "period": "week", "time": "18:00", "days": ["sun"]},
            {"id": "long", "goal_type": "check", "period": "day", "time": "07:00", "title": "Lettura è " * 12},
            {"id": "paused", "goal_type": "check", "period": "day", "time": "08:00"},
            {"id": "gone", "goal_type": "check", "period": "day", "time": "08:00", "status": "archived"},
            {"id": "notime", "goal_type": "check", "period": "day"},
            {"id": "bed", "goal_type": "time", "period": "day", "target": "23:00", "time": "22:30", "title": "In bed by"},
        ]
        for h in hs:
            habits.check_habit(h)
        now = datetime(2026, 11, 13, 10, 0, tzinfo=timezone.utc)
        text, n = habits.ics_text(hs, [ev("paused", D(0), "pause")], D(4), now)  # Friday 13.11
        self.assertEqual(n, 4)
        self.assertIn("SUMMARY:In bed by 23:00\r\n", text)
        self.assertTrue(text.startswith("BEGIN:VCALENDAR\r\n") and text.endswith("END:VCALENDAR\r\n"))
        self.assertNotIn("\n", text.replace("\r\n", ""))
        self.assertIn("SUMMARY:Read\\, then\\; sleep\r\n", text)
        self.assertIn("DTSTART:20261113T210000\r\nDURATION:PT15M\r\nRRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU", text)
        self.assertIn("DTSTART:20261115T180000\r\nDURATION:PT15M\r\nRRULE:FREQ=WEEKLY;BYDAY=SU", text)
        self.assertIn("DTSTAMP:20261113T100000Z", text)
        for uid in ("paused", "gone", "notime"):
            self.assertNotIn(f"UID:{uid}@", text)
        self.assertTrue(all(len(line.encode()) <= 75 for line in text.split("\r\n")))
        unfolded = text.replace("\r\n ", "")
        self.assertIn("SUMMARY:" + "Lettura è " * 12 + "\r\n", unfolded)


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        (self.data / "habits.json").write_text(json.dumps({"habits": [WATER, BED, PLAN, GYM]}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = habits.main([*args, "--data", str(self.data)])
        return code, json.loads(buf.getvalue())

    def test_log_today_progress(self):
        code, out = self.cli("log", "water", "250", "--date", "2026-11-13")
        self.assertEqual(code, 0)
        self.assertEqual((out["logged"]["value"], out["habit"]["value"], out["habit"]["remaining"]), (250, 250, 1750))
        self.cli("log", "bed", "21:5", "--date", "2026-11-13")
        rows = [json.loads(line) for line in (self.data / "log.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([r["date"] for r in rows], ["2026-11-13", "2026-11-13"])
        self.assertEqual(rows[1]["value"], "21:05")
        self.assertIn("at", rows[0])
        code, out = self.cli("today", "--date", "2026-11-13")
        self.assertEqual((code, out["weekday"]), (0, "fri"))
        by_id = {h["id"]: h for h in out["habits"]}
        self.assertEqual(by_id["bed"]["status"], "done")
        self.assertEqual(out["summary"], {"due": 4, "done": 1})
        code, out = self.cli("progress", "water", "--date", "2026-11-13")
        self.assertEqual([h["id"] for h in out["habits"]], ["water"])

    def test_errors(self):
        for args, msg in [
            (("log", "nope"), "unknown habit"),
            (("log", "bed"), "needs a time"),
            (("log", "water", "abc"), "non-zero number"),
            (("log", "water", "--event", "skip", "--until", "2026-12-01"), "only valid"),
            (("log", "water", "--event", "pause", "--until", "2026-11-01", "--date", "2026-11-13"), "after"),
            (("today", "--date", "13.11.2026"), "invalid date"),
        ]:
            code, out = self.cli(*args)
            self.assertEqual(code, 2, args)
            self.assertIn(msg, out["error"])
        self.assertFalse((self.data / "log.jsonl").exists())

    def test_invalid_config(self):
        (self.data / "habits.json").write_text(json.dumps({"habits": [dict(WATER, goal_type="sum")]}), encoding="utf-8")
        code, out = self.cli("today")
        self.assertEqual(code, 2)
        self.assertIn("goal_type", out["error"])

    def test_ics_file(self):
        out_file = self.data / "cal.ics"
        code, out = self.cli("ics", "--out", str(out_file), "--date", "2026-11-13")
        self.assertEqual((code, out["events"]), (0, 0))
        self.assertIn(b"\r\nEND:VCALENDAR\r\n", out_file.read_bytes())


SKILL = ROOT / "good-habits"
CATEGORIES = {"sleep", "nutrition", "activity", "mind", "learning", "productivity", "relationships"}
CATALOG_FIELDS = {"key", "category", "goal_type", "period", "unit", "default_target", "target_min",
                  "target_max", "quick_log", "progression_step"}
OPTIONAL_FIELDS = {"default_days", "default_time"}
SECTIONS = ["## Why it helps", "## Start small", "## How to log", "## Messages"]
FORBIDDEN = re.compile(r"calorie|body weight|\bweigh yourself|\bbmi\b|\bkg\b|medication|diagnos", re.I)


def scalar(v):
    """The small YAML subset used by catalog headers: null, numbers, quoted or bare strings, [a, b] lists."""
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [scalar(x) for x in v[1:-1].split(",") if x.strip()]
    if v in ("null", "~", ""):
        return None
    if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    return v


def front_matter(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---", f"{path.name}: no header"
    end = lines.index("---", 1)
    meta = {}
    for line in lines[1:end]:
        line = line.split(" #")[0].strip()
        if line:
            k, _, v = line.partition(":")
            assert k.strip() not in meta, f"{path.name}: duplicate {k}"
            meta[k.strip()] = scalar(v)
    return meta, "\n".join(lines[end + 1:])


def as_habit(meta):
    """What activation writes into habits.json (see state-format.md)."""
    return {"id": meta["key"], "key": meta["key"], "goal_type": meta["goal_type"], "period": meta["period"],
            "unit": meta["unit"], "target": meta["default_target"], "target_min": meta["target_min"],
            "target_max": meta["target_max"], "step": meta["progression_step"],
            "days": meta.get("default_days"), "time": meta.get("default_time"), "created": "2026-11-01"}


class Catalog(unittest.TestCase):
    files = sorted((SKILL / "references" / "catalog").glob("*.md"))

    def test_not_empty(self):
        self.assertTrue(self.files)

    def test_every_file(self):
        for path in self.files:
            with self.subTest(path.name):
                meta, body = front_matter(path)
                self.assertEqual(CATALOG_FIELDS - meta.keys(), set(), "missing fields")
                self.assertEqual(meta.keys() - CATALOG_FIELDS - OPTIONAL_FIELDS, set(), "unknown fields")
                self.assertEqual(meta["key"], path.stem)
                self.assertRegex(meta["key"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
                self.assertIn(meta["category"], CATEGORIES)
                self.assertIn(meta["goal_type"], habits.GOAL_TYPES)
                self.assertIn(meta["period"], habits.PERIOD_DAYS)
                gt, target = meta["goal_type"], meta["default_target"]
                lo, hi = meta["target_min"], meta["target_max"]
                if gt in ("quantity", "count"):
                    self.assertIsInstance(meta["unit"], str)
                    self.assertTrue(all(isinstance(x, (int, float)) for x in (target, lo, hi)))
                    self.assertTrue(0 < lo <= target <= hi)
                else:
                    self.assertIsNone(lo)
                    self.assertIsNone(hi)
                if gt == "check":
                    self.assertIsNone(target)
                    self.assertIsNone(meta["progression_step"])
                if gt == "count":
                    self.assertIsInstance(target, int)
                quick = meta["quick_log"]
                if quick is not None:
                    self.assertEqual(gt, "quantity")
                    self.assertTrue(quick and all(isinstance(x, (int, float)) and x > 0 for x in quick))
                step = meta["progression_step"]
                self.assertTrue(step is None or (isinstance(step, (int, float)) and step != 0))
                habits.check_habit(as_habit(meta))  # same rules as the script: types, HH:MM, days
                self.assertRegex(body.lstrip(), r"^# \S")
                for section in SECTIONS:
                    self.assertIn(section, body)
                messages = body.split("## Messages", 1)[1]
                variants = ("- start:", "- midway:", "- almost there:") if gt in ("quantity", "count") \
                    else ("- before:", "- after:")
                for variant in variants:
                    self.assertIn(variant, messages)
                self.assertIsNone(FORBIDDEN.search(body), "asks for health data")


def path_steps(path):
    """Rows of the Steps table: (offset or None, habit key, {field: value})."""
    meta, body = front_matter(path)
    table = body.split("## Steps", 1)[1].split("\n## ", 1)[0]
    steps = []
    for off, key, over in re.findall(r"^\| *(-?\d+|—) *\| *`([a-z0-9-]+)` *\| *(.+?) *\|$", table, re.M):
        fields = {}
        if over != "—":
            for item in over.split(";"):
                k, _, v = item.strip().partition("=")
                fields[k] = None if v == "null" else v.split(",") if k == "days" else scalar(v)
        steps.append((None if off == "—" else int(off), key, fields))
    return meta, body, steps


class Paths(unittest.TestCase):
    files = sorted((SKILL / "references" / "paths").glob("*.md"))
    OVERRIDABLE = {"target", "days", "step"}

    def test_not_empty(self):
        self.assertTrue(self.files)

    def test_every_path(self):
        catalog = {p.stem: front_matter(p)[0] for p in Catalog.files}
        for path in self.files:
            with self.subTest(path.name):
                meta, body, steps = path_steps(path)
                self.assertEqual(set(meta), {"key", "anchor", "default_anchor"})
                self.assertEqual(meta["key"], path.stem)
                anchor = habits.parse_hhmm(meta["default_anchor"])
                self.assertRegex(body.lstrip(), r"^# \S")
                self.assertGreaterEqual(len(steps), 2)
                self.assertEqual(len({k for _, k, _ in steps}), len(steps), "habit twice")
                for off, key, fields in steps:
                    self.assertIn(key, catalog)
                    self.assertEqual(set(fields) - self.OVERRIDABLE, set())
                    h = {**as_habit(catalog[key]), **fields}  # activation as described in SKILL.md
                    if off is not None:
                        at = habits.hhmm((anchor + off) % 1440)
                        if h["goal_type"] == "time":
                            lead = habits.parse_hhmm(h["target"]) - habits.parse_hhmm(h["time"] or h["target"])
                            h["target"], h["time"] = at, habits.hhmm((anchor + off - lead) % 1440)
                        else:
                            h["time"] = at
                    habits.check_habit(h)


class SkillFile(unittest.TestCase):
    """Agent Skills spec (agentskills.io/specification); claude.ai uploads reject any other header key."""
    ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

    def setUp(self):
        self.meta, self.body = front_matter(SKILL / "SKILL.md")

    def test_header(self):
        self.assertEqual(self.meta.keys() - self.ALLOWED, set())
        self.assertEqual(self.meta["name"], SKILL.name)
        self.assertRegex(self.meta["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(self.meta["name"]), 64)
        self.assertTrue(0 < len(self.meta["description"]) <= 1024)
        self.assertLessEqual(len(self.meta.get("compatibility", "")), 500)
        for k, v in self.meta.items():  # plain YAML scalars: no ": " or " #" inside
            self.assertNotRegex(str(v), r": | #", k)

    def test_short(self):
        self.assertLess(len(self.body.splitlines()), 300)

    def test_catalog_index_matches_files(self):
        index = self.body.split("## Catalog index", 1)[1]
        listed = {}
        for cat, cell in re.findall(r"^\| (\w+) \| (.+) \|$", index, re.M):
            for key in re.findall(r"`([a-z0-9-]+)`", cell):
                listed[key] = cat
        files = {p.stem: front_matter(p)[0]["category"] for p in Catalog.files}
        self.assertEqual(listed, files)

    def test_paths_index_matches_files(self):
        index = self.body.split("## Paths", 1)[1]
        listed = {key: re.findall(r"`([a-z0-9-]+)`", cell)
                  for key, cell in re.findall(r"^\| `([a-z0-9-]+)` \| [^|]+ \| (.+) \|$", index, re.M)}
        files = {p.stem: [k for _, k, _ in path_steps(p)[2]] for p in Paths.files}
        self.assertEqual(listed, files)


class Marketplace(unittest.TestCase):
    """.claude-plugin/marketplace.json must point at the skill folder (Claude Code plugins, npx skills)."""

    def test_points_at_the_skill(self):
        data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        [plugin] = data["plugins"]
        self.assertEqual(plugin["skills"], ["./good-habits"])
        self.assertEqual(plugin["name"], front_matter(SKILL / "SKILL.md")[0]["name"])
        self.assertTrue((ROOT / plugin["skills"][0] / "SKILL.md").is_file())


class StateFormatDoc(unittest.TestCase):
    """The examples in state-format.md must be accepted by the script."""

    def test_examples_run(self):
        doc = (SKILL / "references" / "state-format.md").read_text(encoding="utf-8")
        config = re.search(r"```json\n(.*?)```", doc, re.S).group(1)
        log = re.search(r"```jsonl\n(.*?)```", doc, re.S).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "habits.json").write_text(config, encoding="utf-8")
            (Path(tmp) / "log.jsonl").write_text(log, encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = habits.main(["progress", "--data", tmp, "--date", "2026-11-22"])
        out = json.loads(buf.getvalue())
        self.assertEqual(code, 0, out)
        by_id = {h["id"]: h for h in out["habits"]}
        self.assertEqual(by_id["hydration"]["status"], "paused")
        self.assertEqual(by_id["workout"]["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
