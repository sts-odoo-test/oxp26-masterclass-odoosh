# Project Context — Odoo.sh Masterclass

This document gives a fresh agent everything needed to continue work on this project.

---

## What this is

A two-day masterclass at Odoo Experience 2026 (Sep 22-23, Brussels).

- **Day 1** (not our concern): on-premise Odoo architecture and performance.
- **Day 2** (this project): Odoo.sh — platform overview, dev workflow, testing, CI,
  performance debugging, and upgrades. Delivered by Stanislas (sts@odoo.com).

**Audience:** Developers and QA engineers, advanced level (Python, SQL, Linux, Odoo dev).
**Format:** 30 students max, each with their own Odoo.sh project. Instructor-led demos
alternating with hands-on exercises.

Three docs, three audiences:
- `README.md` — student-facing exercise handout (the only place exercise instructions live)
- `plan.md` — instructor's timed run of show (the only place timing lives)
- `slides.md` — the 31-slide deck (deliberately timing-free and instruction-free; points back
  to `README.md`/`plan.md` rather than repeating either)

---

## The repository

**GitHub:** `github.com/sts-odoo/oxp26-masterclass-odoosh`
**Local path:** `/home/odoo/src/user/`

### Branch map (SHAs verified against GitHub 2026-09-21, end of session)

| Branch | Odoo | Commit | Purpose |
|---|---|---|---|
| `origin/main` | — | `eb83f75` | **Class docs only** — README.md / context.md / plan.md / slides.md / images/. No module code here. Moves with nearly every doc edit — don't trust this SHA, check `git log origin/main` or the GitHub API before assuming it's current. |
| `origin/17.0` | 17.0 | `ccbb891` | Original clean `conference_session` module |
| `origin/17.0-failed-test` | 17.0 | `fef23bb` | Module + tests + **intentional bug** (`/ 100.0` instead of `/ 60.0`) |
| `origin/17.0-perf-issue` | 17.0 | `19af4a6` | **Perf exercise base** — slow `room_session_count` field + populate factories |
| `origin/19.0-upgrade` | 19.0 | `3001cff` | Upgraded module + migration scripts for the upgrade exercise |
| `origin/prod` | — | `a272bab` | Initial empty commit (README only) — the class's production target branch |

### Branch state (all pushed)

All branches are pushed to GitHub. **Note:** this local checkout's working tree currently only
has the docs (README/context/plan/slides/images) — it is on the `main` line, detached. The
module code lives on the other branches above, not here. To work on the module locally,
`git checkout` the relevant branch first.

**Operational note:** `origin/main` has been reset/rewritten from outside this session at least
once (someone edited `README.md` directly on GitHub, which landed as a new commit with a
different SHA than what this session had pushed — a plain `git push`/`odoosh-push` retry will
fail with "fetch first" when that happens). Before pushing, it's worth checking the actual
remote tip via the GitHub API rather than assuming local history matches — see the git log at
the end of this session for how the reconciliation was done (fetch the real tip over HTTPS
since this container has no direct SSH access for plain `git fetch`, diff content to confirm
nothing was lost, then reapply the delta on top and push).

---

## The module: `conference.session`

Lives on the `17.0`, `17.0-failed-test`, `17.0-perf-issue`, `19.0-upgrade` branches (not on
`main`). Field list below is the `17.0-perf-issue` state (base fields + the deliberately slow
computed field).

### Model fields (17.0-perf-issue state)

| Field | Type | Notes |
|---|---|---|
| `name` | Char (required) | Session title |
| `speaker` | Char | Speaker name — becomes Many2one in v19 |
| `duration` | Integer | Duration in **minutes** — becomes Float (hours) in v19 |
| `room` | Char | Room name |
| `notes` | Text | Free notes |
| `date` | Date | Session date |
| `room_session_count` | Integer (computed) | **Deliberately slow** — uses `search_count` in a loop (N+1) |

### The slow field — for the performance exercise

`room_session_count` fires one `search_count` SQL query per record.
With 65,000 records in the DB (~13,000 per room, after `populate --size=large`), loading the
list view still only triggers 80 queries — one per *visible* record (list view page size),
regardless of total DB size. Clearly visible in the profiler.

**The fix** (to show after the exercise):
```python
def _compute_room_session_count(self):
    groups = self.env['conference.session'].read_group(
        domain=[('room', 'in', self.mapped('room'))],
        fields=['room'],
        groupby=['room'],
    )
    counts = {g['room']: g['conference_session_count'] for g in groups}
    for session in self:
        session.room_session_count = counts.get(session.room, 0)
```
One query instead of N.

### Populate factories

```bash
odoo-bin populate --size=large --models=conference.session -d $PGDATABASE --stop-after-init --no-http
```

Sizes (from `_populate_sizes` in the model, `17.0-perf-issue` branch): small=500,
medium=10,000, large=65,000. The perf exercise (plan.md) uses `large` — ~65,000 sessions,
~13,000 per room (5 rooms: Hall A–E, 20 rotating speakers).

### Current DB state (this container)

As of this check, this container's working tree is on the docs-only `main` line and its
database has **no `conference_session` tables installed** — the module isn't checked out here.
The 10,005-row state described in earlier notes was from prep work on a different branch/build
and is no longer current; don't rely on it. To reproduce a populated DB for testing, check out
`17.0-perf-issue`, install the module, and run the `populate` command above. Reset with:

```bash
# Empty the DB
python3 -c "
import psycopg2
conn = psycopg2.connect('')
conn.autocommit = True
cr = conn.cursor()
cr.execute(\"SELECT tablename FROM pg_tables WHERE schemaname = 'public'\")
for (t,) in cr.fetchall():
    cr.execute(f'DROP TABLE IF EXISTS public.\"{t}\" CASCADE')
cr.execute(\"SELECT relname FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid WHERE c.relkind='S' AND n.nspname='public'\")
for (s,) in cr.fetchall():
    cr.execute(f'DROP SEQUENCE IF EXISTS public.\"{s}\" CASCADE')
print('Done')
"
# Reinstall clean
odoo-bin -i conference_session --stop-after-init --no-http
```

---

## The exercises

Numbering matches the student handout (`README.md`) — 1 through 7, no gaps.
Full timed walkthrough is in `plan.md`.

### Exercise 1 — Deploy production (`prod` branch)

Students mark their `prod` branch (currently just a README) as the project's Production
branch in the Odoo.sh UI and watch the first production build run. Low-risk since the
branch has no module code yet.

### Exercise 2 — New module and deploy (`17.0` → `prod`)

Confirm `17.0` is healthy on staging, merge it into `prod`, then in the production build go
to Apps → Update Apps List and install `conference_session` manually. First full
dev → staging → production promotion students run end to end.

### Exercise 3 — Add new field and deploy, computed (dev branch: `17.0-failed-test`)

The `duration_in_hours` computed field divides by `100.0` instead of `60.0`.
4 out of 5 tests fail. Students must:
1. Read the red build log in the Odoo.sh UI
2. Run tests manually: `odoo-bin -u conference_session --test-tags /conference_session --stop-after-init --no-http`
3. Read `AssertionError: 0.9 != 1.5`, find the divisor in the model
4. Fix it (`100.0` → `60.0`), re-run, confirm green, push
5. Optionally merge to `prod` the same way as Exercise 2.

Teaching point: `test_duration_in_hours_zero` passes even with the bug (0/anything = 0).

### Exercise 4 — Secret in production + `data/neutralize.sql`

Add a value to System Parameters on `prod`, create a staging branch and confirm the value
leaks into it, then add `data/neutralize.sql` on `prod` to clear/mask it, and rebuild staging
to confirm it's now neutralized.

### Exercise 5 — Performance (dev branch: `17.0-perf-issue`, populated DB)

The `room_session_count` field loads slowly. Students must:
1. Activate profiler (`?profile=1`) on the Sessions list
2. Read the flamegraph: many thin repeated bars → N+1
3. Open `odoo-bin shell`, reproduce and measure:
   ```python
   import time, logging
   logging.getLogger('odoo.sql_db').setLevel(logging.DEBUG)
   t = time.time()
   env['conference.session'].search([], limit=80).mapped('room_session_count')
   print(f"{time.time()-t:.2f}s")
   ```
4. Apply the `read_group` fix, measure again
5. Rebase on `prod`, test in staging, deploy to production (same pattern as Exercise 2).

### Exercise 6 — Diagnose the graph (`main` branch, `images/image1.png`–`image9.png`, embedded in README.md)

Platform-monitoring diagnosis exercise, distinct from Exercise 5's code-level profiling —
reads Odoo.sh's built-in CPU/memory/IOPS/concurrency/response-time graphs instead of a
flamegraph. 9 images, shown in README.md as "Graph A"–"Graph I" in shuffled order (not
`image1`–`image9` file order, so nobody reads a numeric sequence into it — see the mapping
table in `plan.md`'s instructor notes). **Each a standalone situation from a different
instance** — they are *not* related to each other or part of a shared incident, even though
several time windows happen to overlap (most default to a "last 3 days" view). Deliberately
open-ended: students are **not** given a menu of strategies — they must reason out for
themselves what's happening and what they'd do about it (scale up / ship a fix / roll back /
restore / just monitor / investigate further), drawing on what they've learned earlier in the
day.

Key teaching point: diagnose each graph on its own merits — don't assume separate images
describe the same event just because timestamps overlap. Full per-image answer key is in
`plan.md` (instructor notes, not shown to students).

### Exercise 7 — Upgrade (`17.0` → `19.0-upgrade`, staging then production)

Students trigger a test upgrade via the Odoo.sh UI. They:
1. Push 19.0 code **without** migration scripts → see data loss
2. Push **with** migration scripts → data preserved
3. Once staging looks right, promote to production.

The two migration issues:
- `speaker` (Char) → `presenter_id` (Many2one res.partner): needs **post_migration.py**
- `duration` (Integer, minutes) → `duration` (Float, hours): needs **pre_migration.py**

Migration scripts **are committed** in
`conference_session/migrations/19.0.1.0.0/pre_migration.py` and `post_migration.py` on the
`19.0-upgrade` branch (verified on GitHub) — no need to hand-write or reveal them separately
during class, they're already in the branch students check out.

---

## What still needs to be done

**Done:**

| Item | Detail |
|---|---|
| Perf exercise commits pushed | `19af4a6` on `origin/17.0-perf-issue` |
| `README.md`/`plan.md` exercise numbering aligned | 1–7, no gaps |
| Slide deck scripted | `slides.md`, 31 slides, fact-checked against odoo.sh docs, timing-free |
| `plan.md` resynced to the real venue schedule | 09:00 start / ~10:30 break / 12:00–13:00 lunch / ~15:00 break / 17:00 end |

**Still open:**

| Item | Notes |
|---|---|
| Export populated DB from outside container | Instructor handles this, not something this session can do |
| Reset DB to clean state after export | Follows the export above |
| Flamegraph example screenshot(s) for the "how to read a flamegraph" demo | Referenced in `plan.md`'s Performance debugging block, not sourced yet |
| Confirm repo is public/forkable ahead of class | Students self-provision by forking at 09:00 (see `plan.md`) — this only works if the repo is actually open to them |
| Confirm both venue "short breaks" are really 15 min | `plan.md` assumed this; the venue only gave start times, not durations |

---

## Git identity

```
user.name  = Stanislas
user.email = sts@odoo.com
```

## Key commands

```bash
odoo-bin -i conference_session --stop-after-init --no-http   # fresh install
odoo-bin -u conference_session --stop-after-init --no-http   # update
odoo-bin -u conference_session --test-tags /conference_session --stop-after-init --no-http  # tests
odoo-bin populate --size=medium --models=conference.session -d $PGDATABASE --stop-after-init --no-http
odoo-bin shell --no-http
odoosh-push   # never use git push directly
echo $ODOO_BACKEND_URL
```
