#!/usr/bin/env python3
"""Good Habits state engine: the only source of numbers for the skill.

State lives in a folder chosen by the user (default ~/good-habits), never in the skill folder:
  habits.json  active habits and their configuration
  log.jsonl    append-only facts, one per line: log, skip, pause, resume

Every command prints JSON. There is no user-facing text here: the assistant phrases it.
Options go after the command, e.g. `habits.py today --data DIR --date 2026-11-13`.
"""
import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
GOAL_TYPES = ("quantity", "time", "count", "check")
PERIOD_DAYS = {"day": 1, "week": 7}
EVENTS = ("log", "skip", "pause", "resume")
UP, DOWN = 0.8, 0.4  # progression thresholds on the last 14 days


class UsageError(Exception):
    pass


def parse_date(s):
    try:
        return date.fromisoformat(str(s))
    except ValueError:
        raise UsageError(f"invalid date {s!r}, expected YYYY-MM-DD")


def parse_hhmm(s):
    try:
        h, m = (int(x) for x in str(s).split(":"))
    except ValueError:
        raise UsageError(f"invalid time {s!r}, expected HH:MM")
    if not (0 <= h < 24 and 0 <= m < 60):
        raise UsageError(f"invalid time {s!r}, expected HH:MM")
    return h * 60 + m


def hhmm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def num(x):
    return int(x) if isinstance(x, float) and x.is_integer() else x


def time_before(value, target):
    """`time_before` rule, on minutes since midnight. Works across midnight:
    target 23:30, logged 00:15 is late; target 00:30, logged 23:50 is on time."""
    # ponytail: assumes the logged time is within 12 h of the target, true for any bedtime-like habit
    return (target - value) % 1440 < 720


def check_target(hid, gt, t):
    if gt == "time":
        parse_hhmm(t)
    elif gt != "check" and (isinstance(t, bool) or not isinstance(t, (int, float)) or t <= 0):
        raise UsageError(f"habit {hid!r}: target must be a positive number")


def check_habit(h):
    for f in ("id", "goal_type", "period"):
        if f not in h:
            raise UsageError(f"habit {h.get('id', '?')!r}: missing field {f!r}")
    hid, gt = h["id"], h["goal_type"]
    if gt not in GOAL_TYPES:
        raise UsageError(f"habit {hid!r}: goal_type must be one of {', '.join(GOAL_TYPES)}")
    if h["period"] not in PERIOD_DAYS:
        raise UsageError(f"habit {hid!r}: period must be day or week")
    if gt == "time" and h["period"] != "day":
        raise UsageError(f"habit {hid!r}: time goals are daily")
    check_target(hid, gt, h.get("target"))
    history = h.get("history") or []
    if not isinstance(history, list):
        raise UsageError(f"habit {hid!r}: history must be a list")
    for old in history:
        if not isinstance(old, dict) or "until" not in old:
            raise UsageError(f"habit {hid!r}: history entries need until and target")
        parse_date(old["until"])
        check_target(hid, gt, old.get("target"))
    days = h.get("days")
    if days is not None and (not isinstance(days, list) or not days or any(d not in WEEKDAYS for d in days)):
        raise UsageError(f"habit {hid!r}: days must be null or a non-empty list of {', '.join(WEEKDAYS)}")
    if h.get("time") is not None:
        parse_hhmm(h["time"])
    if h.get("status") not in (None, "active", "archived"):
        raise UsageError(f"habit {hid!r}: status must be active or archived (pauses live in the log)")


class Track:
    """One habit plus its events. Planned occurrences are computed, never stored."""

    def __init__(self, habit, events):
        self.h = habit
        self.weekly = habit["period"] == "week"
        self.days = set(habit.get("days") or WEEKDAYS)
        # earlier targets, so that changing a target never re-grades the past
        # ponytail: only the target is versioned; changing `days` still re-evaluates past days
        self.history = sorted((parse_date(x["until"]), x["target"]) for x in habit.get("history") or [])
        self.logs = defaultdict(list)
        self.skips = set()
        self.pauses = []  # [start, end_exclusive or None]
        self.n_logs = 0
        mine = sorted((e for e in events if e.get("habit") == habit["id"]),
                      key=lambda e: (e["date"], e.get("at", "")))
        for e in mine:
            d = parse_date(e["date"])
            kind = e.get("event")
            if kind == "log":
                self.logs[d].append(e.get("value"))
                self.n_logs += 1
            elif kind == "skip":
                self.skips.add(d)
            elif kind == "pause":
                self.pauses.append([d, parse_date(e["until"]) if e.get("until") else None])
            elif kind == "resume" and self.pauses:
                last = self.pauses[-1]
                if last[1] is None or last[1] > d:
                    last[1] = d
        if habit.get("created"):
            self.created = parse_date(habit["created"])
        else:
            self.created = parse_date(mine[0]["date"]) if mine else None

    def target_on(self, d):
        return next((t for until, t in self.history if d < until), self.h.get("target"))

    def paused(self, d):
        return any(s <= d and (e is None or d < e) for s, e in self.pauses)

    def period_start(self, d):
        return d - timedelta(days=d.weekday()) if self.weekly else d

    def evaluate(self, start, today):
        """Status of the period starting at `start`, as seen on `today`.
        A completed period always counts; otherwise skips, pauses and unplanned days are left out."""
        h, gt = self.h, self.h["goal_type"]
        span = [start + timedelta(days=i) for i in range(PERIOD_DAYS[h["period"]])]
        values = [v for d in span for v in self.logs.get(d, [])]
        target = self.target_on(start)
        if gt == "quantity":
            value = num(sum(v for v in values if isinstance(v, (int, float))))
            done = value >= target
        elif gt == "time":  # the last value of the day wins: logging again corrects a mistake
            value = values[-1] if values else None
            done = value is not None and time_before(parse_hhmm(value), parse_hhmm(target))
        else:  # count, check: number of registrations
            value = len(values)
            done = value >= (target if gt == "count" else 1)
        end = span[-1]
        if done:
            status = "done"
        elif self.created and end < self.created:
            status = "before_start"
        elif not self.weekly and WEEKDAYS[start.weekday()] not in self.days:
            status = "not_scheduled"
        elif any(d in self.skips for d in span):
            status = "skipped"
        elif any(self.paused(d) for d in span):
            status = "paused"
        elif end >= today and not (gt == "time" and values):  # a late time is final, not still open
            status = "open"
        else:
            status = "missed"
        return {"status": status, "value": value}

    def statuses(self, first, last, today):
        d = self.period_start(first)
        step = timedelta(days=PERIOD_DAYS[self.h["period"]])
        while d <= last:
            yield self.evaluate(d, today)["status"]
            d += step

    def window(self, days, today):
        """Rolling window: periods ending in the last `days` days. The current period counts only once done."""
        c = Counter(self.statuses(today - timedelta(days=days - 1), today, today))
        return {"done": c["done"], "scheduled": c["done"] + c["missed"]}

    def snapshot(self, today):
        h, gt = self.h, self.h["goal_type"]
        r = self.evaluate(self.period_start(today), today)
        s = {k: h[k] for k in ("id", "key", "title", "goal_type", "period", "unit", "time", "path")
             if h.get(k) is not None}
        s.update(r)
        if gt != "check":
            s["target"] = self.target_on(self.period_start(today))
        if gt in ("quantity", "count"):
            s["remaining"] = num(max(0, s["target"] - r["value"]))
        if not self.weekly:  # so far this week (Monday first); today counts once done
            monday = today - timedelta(days=today.weekday())
            c = Counter(self.statuses(monday, today, today))
            s["week"] = {"done": c["done"], "scheduled": c["done"] + c["missed"]}
        s["last_7"] = self.window(7, today)
        return s

    def proposal(self, today):
        """Progression is only ever proposed: >= 80 % over two weeks -> one step up, < 40 % -> one step down."""
        h, gt, step = self.h, self.h["goal_type"], self.h.get("step")
        if not step or gt == "check" or not self.created or (today - self.created).days < 13:
            return None
        w = self.window(14, today)
        if not w["scheduled"]:
            return None
        rate = w["done"] / w["scheduled"]
        sign = 1 if rate >= UP else -1 if rate < DOWN else 0
        if not sign:
            return None
        direction = "up" if sign > 0 else "down"
        if gt == "time":  # step in minutes, negative = earlier
            return {"direction": direction, "target": hhmm((parse_hhmm(h["target"]) + sign * step) % 1440)}
        new = h["target"] + sign * step
        if h.get("target_min") is not None:
            new = max(new, h["target_min"])
        if h.get("target_max") is not None:
            new = min(new, h["target_max"])
        if new <= 0 or new == h["target"]:
            return None
        return {"direction": direction, "target": num(new)}

    def progress(self, today):
        p = self.snapshot(today)
        p["last_28"] = self.window(28, today)
        longest = run = completed = 0
        for st in self.statuses(self.created or today, today, today):
            if st == "done":
                run += 1
                completed += 1
                longest = max(longest, run)
            elif st == "missed":
                run = 0  # skips, pauses, unplanned days and today neither break nor extend
        p["longest_streak"] = longest
        p["completed_periods"] = completed
        p["logs"] = self.n_logs
        thresholds = [(1, "first_week")] if self.weekly else [(7, "first_week"), (30, "30_days")]
        p["milestones"] = [name for n, name in thresholds if completed >= n]
        if self.n_logs >= 100:
            p["milestones"].append("100_logs")
        p["proposal"] = self.proposal(today)
        return p


def ics_text(habits, events, today, now):
    def esc(s):
        return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    def fold(line):  # RFC 5545: at most 75 octets per line, never splitting a UTF-8 character
        parts, cur = [], ""
        for ch in line:
            if len((cur + ch).encode()) > (74 if parts else 75):
                parts.append(cur)
                cur = ""
            cur += ch
        return "\r\n ".join(parts + [cur])

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//good-habits//habits.py//EN", "CALSCALE:GREGORIAN"]
    count = 0
    for h in habits:
        if (h.get("status") or "active") != "active" or not h.get("time") or Track(h, events).paused(today):
            continue
        days = [d for d in WEEKDAYS if d in (h.get("days") or WEEKDAYS)]
        start = next(today + timedelta(days=i) for i in range(7) if WEEKDAYS[(today.weekday() + i) % 7] in days)
        t = parse_hhmm(h["time"])
        title = h.get("title") or h.get("key") or h["id"]
        if h["goal_type"] == "time":  # the event is the cue: show the limit it leads to
            title = f"{title} {h['target']}"
        title = esc(title)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{h['id']}@good-habits",
            f"DTSTAMP:{now:%Y%m%dT%H%M%SZ}",
            # floating local time: the calendar shows it at that hour wherever the user is
            f"DTSTART:{start:%Y%m%d}T{t // 60:02d}{t % 60:02d}00",
            "DURATION:PT15M",
            "RRULE:FREQ=WEEKLY;BYDAY=" + ",".join(d[:2].upper() for d in days),
            f"SUMMARY:{title}",
            "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{title}", "TRIGGER:PT0M", "END:VALARM",
            "END:VEVENT",
        ]
        count += 1
    lines.append("END:VCALENDAR")
    return "".join(fold(line) + "\r\n" for line in lines), count


def load_habits(data):
    path = data / "habits.json"
    if not path.exists():
        raise UsageError(f"habits.json not found in {data}")
    try:
        habits = json.loads(path.read_text(encoding="utf-8")).get("habits", [])
    except (json.JSONDecodeError, AttributeError) as e:
        raise UsageError(f"habits.json is not valid: {e}")
    for h in habits:
        check_habit(h)
    ids = [h["id"] for h in habits]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise UsageError(f"duplicate habit id: {', '.join(sorted(dup))}")
    return habits


def load_events(data):
    path = data / "log.jsonl"
    if not path.exists():
        return []
    events = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                raise UsageError(f"log.jsonl line {n} is not valid JSON")
    return events


def parse_value(h, raw):
    gt = h["goal_type"]
    if gt == "check":
        return None
    if gt == "time":
        if raw is None:
            raise UsageError(f"habit {h['id']!r} needs a time value HH:MM")
        return hhmm(parse_hhmm(raw))
    if raw is None:
        if gt == "quantity":
            raise UsageError(f"habit {h['id']!r} needs a numeric value")
        return None
    try:
        v = float(raw)
    except ValueError:
        v = math.nan
    if not math.isfinite(v) or v == 0:
        raise UsageError(f"invalid value {raw!r}, expected a non-zero number")
    # ponytail: the log is append-only, so a quantity is corrected with a negative entry
    return num(v)


def run(a):
    data = Path(a.data).expanduser()
    today = parse_date(a.date) if a.date else date.today()
    habits = load_habits(data)
    events = load_events(data)
    by_id = {h["id"]: h for h in habits}

    if a.cmd == "log":
        h = by_id.get(a.habit)
        if h is None:
            raise UsageError(f"unknown habit {a.habit!r}")
        if a.until and a.event != "pause":
            raise UsageError("--until is only valid with --event pause")
        row = {"habit": h["id"], "event": a.event, "date": today.isoformat(),
               "at": datetime.now().astimezone().isoformat(timespec="seconds")}
        if a.event == "log":
            value = parse_value(h, a.value)
            if value is not None:
                row["value"] = value
        if a.until:
            until = parse_date(a.until)
            if until <= today:
                raise UsageError("--until must be after the pause date")
            row["until"] = until.isoformat()
        with open(data / "log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return {"logged": row, "habit": Track(h, events + [row]).snapshot(today)}

    active = [h for h in habits if (h.get("status") or "active") == "active"]
    if a.cmd == "today":
        items = [Track(h, events).snapshot(today) for h in active]
        due = [i for i in items if i["status"] in ("open", "done")]
        return {"date": today.isoformat(), "weekday": WEEKDAYS[today.weekday()], "habits": items,
                "summary": {"due": len(due), "done": sum(i["status"] == "done" for i in due)}}

    if a.cmd == "progress":
        chosen = active
        if a.habit:
            if a.habit not in by_id:
                raise UsageError(f"unknown habit {a.habit!r}")
            chosen = [by_id[a.habit]]
        return {"date": today.isoformat(), "habits": [Track(h, events).progress(today) for h in chosen]}

    # ics
    text, count = ics_text(habits, events, today, datetime.now(timezone.utc))
    out = Path(a.out).expanduser()
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return {"file": str(out), "events": count}


def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data", default=str(Path.home() / "good-habits"), help="folder with habits.json and log.jsonl")
    common.add_argument("--date", help="the user's local date YYYY-MM-DD, when the machine clock may differ (e.g. UTC)")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log", parents=[common], help="append a fact to log.jsonl")
    lg.add_argument("habit")
    lg.add_argument("value", nargs="?")
    lg.add_argument("--event", choices=EVENTS, default="log")
    lg.add_argument("--until", help="with --event pause: resume date YYYY-MM-DD")
    sub.add_parser("today", parents=[common], help="what is planned today, done and remaining")
    pr = sub.add_parser("progress", parents=[common], help="continuity, streak, milestones, proposals")
    pr.add_argument("habit", nargs="?")
    ic = sub.add_parser("ics", parents=[common], help="write a calendar file with the habits' times")
    ic.add_argument("--out", default="good-habits.ics")
    a = p.parse_args(argv)
    try:
        result = run(a)
    except UsageError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
