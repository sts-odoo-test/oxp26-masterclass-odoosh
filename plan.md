# Odoo.sh Masterclass — Day 2 Plan

> **Context:** Second day of a two-day masterclass (Odoo Experience 2026, Sep 22-23).
> Day 1 covered on-premise architecture and performance.
> Students fork `github.com/sts-odoo/oxp26-masterclass-odoosh` at the start of the day to get
> their own Odoo.sh project — this is not pre-provisioned by the instructor.
> Exercise numbers below match the student handout (`README.md`) — 1 through 7, no gaps.
> Slide deck: `slides.md` (31 slides, timing-free by design — this file is the only place
> timing lives, since only the instructor sees it).

**Venue schedule (fixed anchors):** 09:00 start · ~10:30 short break · 12:00–13:00 lunch ·
~15:00 short break · 17:00 end. The blocks below are resynced to this, but two anchors don't
land exactly on the stated time — flagged inline where that happens, with the reason. Both
breaks are assumed 15 min (not stated by the venue, worth confirming).

---

## Morning

### 09:00 – 09:15 · Intro & the deployment landscape *(15 min, talk)*

- Title, logistics (pad link, today's schedule), and the first action of the day: students
  fork the repo and start creating their Odoo.sh project — happens in parallel while you talk,
  provisioning takes a few minutes
- Agenda at a glance: exercise numbers only (1–3 morning, 4–7 afternoon), no explanations —
  students read `README.md` for the actual instructions
- Odoo Online vs. Odoo.sh vs. On-Premise: where Odoo.sh sits, and why — move quickly through
  this, it's dense (6 slides' worth: the three options, a deep-dive on each, the comparison
  table, when to choose which)
- Bridge from day 1: map yesterday's topics (workers, nginx, postgres, backups) to "who
  manages it on Odoo.sh." Sets the framing for the rest of the day

---

### 09:15 – 10:30 · Platform overview & branches *(75 min, demo)*

Bumped from 45 to 75 min — this block now also covers Workers and Hosting (new content, see
`slides.md` 12–16), which didn't exist when the block was first timed at 45 min.

- The three branch types and what each is for; what a build is: container + DB + code,
  rebuilt on every push
- Workers: the two models (On-Premise/Online's pre-fork vs. Odoo.sh's multithreaded-process
  architecture) and what you can actually scale (production only)
- Hosting types: shared vs. dedicated, and how that gates worker count
- Major version upgrades, briefly: it's not automatic, here's the actual flow (request test →
  staging upgrade mode → test → request production → downtime) — full depth comes back later
  with Exercise 7, this is just enough context for "upgrade" to mean something before the day
  goes on
- Live demo (~20 min of this block): builds list, inside a build (logs, shell, editor),
  branch settings — a checklist for the presenter lives in `slides.md` (12–19)

**🏋 Exercise 1 — 15 min (embedded) · "Deploy production"**
> 1. Warm-up (2 min): find the build log for your main branch. What version is running? How long
>    did the last build take? Where are the daily backups listed?
> 2. Create a production instance from your `prod` branch: open its branch settings and mark it
>    as the Production branch. Watch the first production build run to completion.

`prod` currently only holds the README — a clean, low-risk canvas. This is the first
consequential action students take on their own project; Exercise 2 (13:00, right after lunch)
is what actually puts something in it.

---

### 10:30 – 10:45 · Break

---

### 10:45 – 11:30 · The development workflow *(45 min, demo)*

- Dev branch lifecycle: push → rebuild → test
- Shell access & online editor — when to use which
- `requirements.txt` for Python dependencies (persistent across rebuilds)
- What survives a rebuild, what doesn't

**🏋 Exercise — 15 min (embedded)**
> On your dev branch: add a field to the Sessions form view, push, wait for the rebuild,
> verify it appears.

Teaches the core push → rebuild loop. First time students touch their own project.

---

### 11:30 – 12:00 · Tests & CI on Odoo.sh *(30 min, demo + exercise)*

Trimmed from 45 to 30 min to fit the new schedule's tighter morning (venue lunch moved from
12:30 to 12:00). The 25-min exercise below is untouched — the concept portion is what's
compressed, down to ~5 min. Move fast through the bullets; most of it is a one-liner each.

- How tests run automatically on every push (show the red build badge)
- How to read the test output in the build log
- Running tests manually in the shell

**🏋 Exercise 3 — 25 min · "Add new field and deploy (computed)"**

The `conference_session` module on the `17.0-failed-test` branch has a deliberate bug:
`duration_in_hours` divides by 100 instead of 60. The build is red. Students must:

1. Read the failure in the build log
2. Run the tests themselves in the shell to see what command line CI actually uses:
   ```bash
   odoo-bin -u conference_session --test-tags /conference_session --stop-after-init --no-http
   ```
3. Read the assertion error (`0.9 != 1.5`) and find the bug in the model
4. Fix it (`/ 100.0` → `/ 60.0`), run tests again, confirm green, push
5. If time allows: merge the fixed branch to `prod` the same way as Exercise 2, so the new
   computed field actually reaches production.

**Debrief:** Why does `test_duration_in_hours_zero` pass even with the bug?
(Because 0 / anything = 0 — good moment to discuss test coverage.)

---

### 12:00 – 13:00 · Lunch

---

## Afternoon

### 13:00 – 13:45 · Staging & the path to production *(45 min, demo)*

Moved to right after lunch (was the pre-lunch block when the venue's lunch was 12:30–14:00).
Works fine as an afternoon-opener too — nothing here depends on being before lunch.

- Staging as a copy of production — why it matters
- The merge flow: dev → staging → production
- What Odoo.sh validates automatically vs what is your responsibility
- Backups: daily automatic, one-click restore to staging

**🏋 Exercise 2 — 20 min (embedded) · "New module and deploy"**
> 1. Confirm `17.0` is healthy on your staging branch (green build, spot-check the Sessions menu).
> 2. Merge `17.0` into `prod`.
> 3. In the production build, go to Apps → Update Apps List, then install `conference_session`
>    manually.
> 4. Confirm the Sessions menu and demo data show up and work.

This is the first full dev → staging → production promotion students run end-to-end — the same
pattern they'll reuse for Exercises 3, 5c and 7.

---

### 13:45 – 14:30 · Production operations *(45 min, demo + exercise)*

Connect explicitly to day 1:

| Day 1 topic | On Odoo.sh |
|---|---|
| Workers & longpolling | Configured in project settings |
| Nginx / SSL | Fully managed, custom domains supported |
| PostgreSQL tuning | Managed; you can read slow query logs |
| Filestore | Managed, included in backups |
| Backups | Daily automatic, downloadable, one-click restore |

- Reading logs: `odoo.log`, build log, error alerts
- What to do when production is down: the restore + staging workflow

**🏋 Exercise 4 — 15 min (embedded) · "Add some secret in production"**
> 1. In production, add a value in Settings → Technical → System Parameters (stand-in for a
>    real secret, e.g. an API key).
> 2. Create a staging branch from `prod` and check whether that value shows up there.
> 3. Back on `prod`, add a `data/neutralize.sql` script that clears/masks it.
> 4. Rebuild the staging branch and confirm the value is now neutralized.

Direct follow-on from the backups/restore table above: staging is a copy of production data, so
anything sensitive needs an explicit neutralization step before it lands on a non-production
build.

---

### 14:30 – 15:30 · Performance debugging *(60 min)* · Exercise 5

**Branch:** `17.0-perf-issue` (dev, with demo data). Make sure students are on this branch,
not `main` — `main` only holds these class docs, the module code lives on `17.0-perf-issue`.

**Setup — before the exercise starts (students do this themselves, ~3 min):**

Students must populate their dev database first. The module ships with only 4 demo
records — not enough to see the slowness. They run this once in the shell:

```bash
odoo-bin populate --size=large --models=conference.session \
  -d $PGDATABASE --stop-after-init --no-http
```

This inserts **65,000 sessions** (~13,000 per room). Takes about 20 seconds.
The data persists in the dev DB until the next rebuild — students must not push
any commit during the exercise or the DB resets.

> **Why this works on dev:** `populate` only inserts records into the existing DB.
> It does not rebuild anything. The data is safe as long as no push triggers a rebuild.

Expected result after populate: loading the Sessions list takes **2–3 seconds**.
That is the starting point for the flamegraph exercise.

---

**Teach — 15 min: how to read a flamegraph**

Two patterns to recognise:
- Wide flat bar → one slow function
- Many thin repeated bars → N+1 (same query fired once per record)

Show one pre-recorded example before students open their own profiler.

Connect to day 1: "Yesterday we looked at slow queries in pg_activity. The flamegraph
shows you *which Python code* triggered those queries."

---

**🏋 Exercise 5a — 20 min: "Find it"**

> 1. Go to Conference → Sessions in your dev build
> 2. Enable debug mode (add `?debug=1` to the URL)
> 3. Add `?profile=1` to activate the profiler
> 4. Reload the page — it will be slow
> 5. Open the profiler viewer, read the flamegraph
>
> Deliverable: write down *what* is slow and *why*, before looking at the code.

What they will see: `_compute_room_session_count` repeated 80 times (one per visible
record), each with a thin `search_count` SQL bar underneath it.

---

**🏋 Exercise 5b — 20 min: "Confirm and fix it in the shell"**

Open `odoo-bin shell` and follow these steps:

```python
import time

# Step 1 — time one page (what the list view loads)
records = env['conference.session'].search([], limit=80)
t = time.time()
_ = records.mapped('room_session_count')
print(f"Slow: {time.time() - t:.2f}s")   # expect ~1-2s

# Step 2 — see every query firing
import logging
logging.getLogger('odoo.sql_db').setLevel(logging.DEBUG)
_ = records.mapped('room_session_count')  # watch the flood of identical SELECT count(*)

# Step 3 — the fix: one read_group instead of N search_counts
groups = env['conference.session'].read_group(
    domain=[('room', 'in', records.mapped('room'))],
    fields=['room'],
    groupby=['room'],
)
counts = {g['room']: g['conference_session_count'] for g in groups}
t = time.time()
_ = {s: counts.get(s.room, 0) for s in records}
print(f"Fast: {time.time() - t:.4f}s")   # expect <0.01s
```

**Debrief:** The fix is not about the number of records — it is about the number of
*round-trips to the database*. 80 queries × 14ms each = ~1.1s. One GROUP BY = 18ms.
Speedup: ~60×. This is the most common performance bug in Odoo custom code.

**🏋 Exercise 5c — 5 min: "Ship it"**
> Apply the `read_group` fix to the model, rebase `17.0-perf-issue` on `prod`, push, confirm
> the staging build is green, then merge to production the same way as Exercise 2.

---

### 15:30 – 15:45 · Break

Later than the venue's ~15:00 anchor by about 30 min — Exercise 5 needs an uninterrupted
60-min block, and exercise order has to stay 4 → 5 → 6 → 7 so numbering matches what students
read in `README.md`. Diagnose the graph (20 min, the natural small block) is what would
otherwise sit next to this break, but it can't jump ahead of Exercise 5 in sequence. If this
30-min drift from the anchor is a problem, the fix is trimming Performance debugging itself,
not moving the break.

---

### 15:45 – 16:05 · Diagnose the graph *(20 min)* · Exercise 6

Zoom out from code-level profiling to platform-level monitoring. Students see this as
"Graph A" – "Graph I" in `README.md` (deliberately shuffled, not in `image1`–`image9` file
order, so nobody reads a numeric sequence into it) — each one is a different, standalone
situation captured from a different instance.

**🏋 Exercise 6 — 15 min: "Pick your strategy"**
> For each graph: what's happening, is it a problem, and what would you actually do about it?

Deliberately open-ended — no menu of options is given to students. They have to reason from
first principles (what they've seen on Odoo.sh so far: scaling, code fixes, rollback, restore,
monitoring) rather than pattern-match a letter. **Each graph is a standalone situation from a
different instance** — they are not related to each other and do not share a common incident;
don't let students (or yourself) over-fit a story that spans several images. Individually or in
pairs, ~1–2 min per graph, then group debrief on 3–4 of them (5 min).

**Instructor notes (do not show to students) — the strategy space they should arrive at:**
scale up · ship a code fix (dev → staging → prod) · roll back the last deploy · restore from
backup · it's normal, just monitor · not enough information, investigate further.

| Shown as | File | Pattern | Likely read | Suggested strategy |
|---|---|---|---|---|
| Graph A | image6 | IOPS: quiet, then a large sustained write spike for hours | Heavy write workload — a big import/export, a backup, or an inefficient write-heavy query | Investigate the source; ship a code fix if it's inefficient application code, otherwise likely expected |
| Graph B | image2 | CPU steady 60–80%, one sharp "Other" spike | One-off unidentified process (backup? script? manual job?) | Investigate what "Other" was; if non-recurring, no action needed |
| Graph C | image9 | Memory: steady climb, no plateau yet | Could be a leak or expected growth — can't tell from one graph alone | Investigate further before concluding either way |
| Graph D | image4 | Concurrent requests: calm baseline → sustained wild spikes | Either real new traffic, or requests piling up because something is slow to respond | Investigate first (check response times/logs on this instance) before deciding scale vs. fix |
| Graph E | image1 | CPU, recurring day/night rhythm, red markers at a few specific timestamps | Normal daily traffic rhythm; the markers are worth a quick look at the build log, but the load pattern itself isn't a regression | Normal, no action — check the markers out of curiosity |
| Graph F | image7 | Response time: repeated spikes to 30–50s | Real, user-facing slowness on this instance | Ship a fix if the cause is known, or roll back the last deploy if it isn't — not a restore, no data was lost |
| Graph G | image3 | CPU pinned ~90–100% continuously, never drops | Sustained saturation, no headroom, at any time of day | Scale up or fix the code — not "do nothing" |
| Graph H | image8 | Memory: single sharp spike, returns to baseline | Transient, one-off heavy job | Normal, monitor |
| Graph I | image5 | Disk: flat with two step-changes | A one-off jump in storage, not organic gradual growth | Investigate what caused each step (import? migration? log growth?); likely no urgent action if explained |

**Debrief:** the teaching point is that each graph must be diagnosed on its own — resist the
urge to assume separate graphs describe the same event just because the time windows overlap
(most of these default to a "last 3 days" view). The right first move is almost always more
investigation, not an immediate scale/rollback/restore.

---

### 16:05 – 16:50 · Upgrade on Odoo.sh *(45 min)* · Exercise 7

**Teach — 5 min (recap, not new material):** the three actors / upgrade mode / `upgrade.log`
were already covered in the morning's Platform overview block (09:15). This is just a reminder
plus the module-specific bit: why `pre_migration.py` vs `post_migration.py` (ORM has/hasn't
run yet).

**🏋 Exercise 7 — 35 min: "Run the upgrade (staging, then production)"**

Students already have a `19.0-upgrade` branch. Walk through:
1. Trigger the test upgrade from the Odoo.sh UI (staging)
2. While waiting — read a pre-loaded upgrade.log example together
3. Push the 19.0 code **without** migration scripts → observe the damage in the DB
   (speaker names lost, duration values wrong)
4. Push **with** migration scripts → verify data preserved and correctly transformed on staging
5. Once staging is green and the data looks right, promote the upgrade to production the same
   way as Exercises 2 and 5c.

The two migration issues in the module:
- `speaker` (Char) → `presenter_id` (Many2one res.partner): handled by **post_migration.py**
- `duration` (Integer, minutes) → `duration` (Float, hours): handled by **pre_migration.py**

**Debrief — 5 min:**
- Why pre vs post matters (ORM has/hasn't run yet)
- What the platform does vs what you own

---

### 16:50 – 17:00 · Wrap-up & Q&A *(10 min)*

- What Odoo.sh still does not do for you (code quality, test coverage, downtime planning)
- Resources: docs, release notes, upgrade-util repo
- Open floor

---

## Branch map for the class

| Branch | Content | Used for |
|---|---|---|
| `main` | Class docs only (README/context/plan/images) — no module code | Exercise 6 (diagnose the graph) |
| `17.0` | Clean `conference_session` module | Exercise 2 (new module and deploy) |
| `17.0-failed-test` | Module + tests + `/ 100.0` bug | Exercise 3 (test & CI) |
| `17.0-perf-issue` | Module + slow `room_session_count` + populate factories | Exercise 5 (performance) |
| `19.0-upgrade` | Upgraded module + `pre_migration.py` / `post_migration.py` | Exercise 7 (upgrade) |
| `prod` | Empty (README only) at class start | Exercises 1, 2, 4, 5c, 7 (production target) |

---

## Pre-class checklist

| Item | Status |
|---|---|
| `conference_session` module with 4 demo sessions | ✅ Done |
| `duration_in_hours` computed field + 5 tests | ✅ Done |
| Bug committed (`/ 100.0` instead of `/ 60.0`) on `17.0-failed-test` | ✅ Done |
| `room_session_count` slow computed field | ✅ Done |
| `_populate_factories` with `large=65000` | ✅ Done |
| `19.0-upgrade` branch with `pre_migration.py` + `post_migration.py` | ✅ Done |
| Push perf exercise commits to `17.0-perf-issue` branch | ✅ Done |
| `prod` branch pushed (empty, README only) | ✅ Done |
| Flamegraph example screenshot(s) for the "how to read a flamegraph" demo | ⬜ TODO |
| Repo is public/forkable and README is current, so students can self-provision on the day | ⬜ TODO (verify) |
