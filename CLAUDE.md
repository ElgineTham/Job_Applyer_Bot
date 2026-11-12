# JobBot

JobBot finds new-grad software jobs on Jobright, reads each original job posting, and
scores the user's resume against it like an ATS would. Jobs that score 75 or higher (45
or higher at a target company in `target_companies.json`) are saved with the keywords the resume is missing, so the user can tailor the resume and
apply by hand. **Nothing in this repo ever applies to a job.**

## The team

| Who | Where | Job |
|---|---|---|
| **orchestrator** | `.claude/agents/orchestrator.md` (run `claude --agent orchestrator`) | Starts one job_finder and two ats_scorers, keeps the scorers running while the queue has jobs, and reports back. |
| **job_finder** | `.claude/agents/job_finder.md` | Walks the Jobright recommendations feed in Chrome, reads each job's Original Job Post URL, and pushes new jobs onto the queue. |
| **ats_scorer** | `.claude/agents/ats_scorer.md` | Pops one job at a time, reads the description on the original post, checks the knockout gates, scores the resume with the rubric, and saves jobs that reach their pass line (75, or 45 at a target company). Several can run at once. |

Start a run with `claude --agent orchestrator`. That makes the orchestrator the main
session, so it can start job_finder and the scorers as subagents. Subagents cannot start
other subagents, so the orchestrator does not work when launched as a subagent (for
example, by asking a normal session to "use the orchestrator agent").

### Flow

```
Jobright feed ──job_finder──▶ job_links.json (queue) ──ats_scorer ×2──▶ ats_passed.json
                    │                                      │
                    └──▶ job_history.json (permanent)      └── knocked out / below pass line: report only
```

1. job_finder resets `job_links.json` and `ats_passed.json`, then walks the feed. For each
   card on the screen it checks history, opens the Jobright detail page, and pushes the
   job right away, before it scrolls on.
2. The scorers pop jobs while job_finder is still walking. Each scorer finishes one job
   (read, gates, score, save) before popping the next. A scorer stops after 1 minute
   with an empty queue.
3. Passing jobs land in `ats_passed.json`, sorted by score.

## Files

| File | What it is | How to change it |
|---|---|---|
| `jobqueue.py` | Locked FIFO queue plus permanent history | `reset`, `seen <id>`, `push '<json>'`, `pop`, `peek`, `history-reset` |
| `passed.py` | Locked results writer, pass line 75 (45 for target companies) | `reset`, `add` (JSON argument or heredoc on stdin), `count` |
| `target_companies.json` | Target companies (big tech, AI labs, chips) whose jobs pass at 45, with the names each may appear under | Edit by hand to add or remove companies. Agents only read it. |
| `job_links.json` | Queue of jobs waiting to be scored | Only through `jobqueue.py` |
| `job_history.json` | Every job ever pushed, across runs (gitignored) | Only through `jobqueue.py push`. Never clear it unless the user asks (`history-reset`). |
| `ats_passed.json` | Jobs that reached their pass line, with `target_company`, breakdown, matched, and missing keywords | Only through `passed.py`. Only job_finder resets it, at startup. |
| `resume.tex` / `resume.pdf` | The resume (gitignored) | Edit `resume.tex`, compile with `tectonic` |
| `PROFILE.md` | Private applicant details used by the knockout gates (gitignored) | Read only |

Both scripts lock their file with `fcntl` and write atomically (temp file, then
`os.replace`), so any number of agents can use them at once. Never edit the JSON files
with Write or Edit while agents may be running.

### Duplicates

`jobqueue.py push` refuses a job (prints `duplicate of <id>`) when its id is already in
history, or when its original post URL matches a job in history after normalizing it:
tracking parameters dropped, Greenhouse embed URLs mapped to the board URL, and trailing
`/application` or `/apply` removed. Jobs with no URL match on company plus title.
`push --force` re-queues a job by hand. Agents never use it.

## Scoring (summary)

The full rubric is in `ats_scorer.md`, step 4. In short:

- **Knockout gates** (checked first, no score): not full-time, work authorization or
  sponsorship limits, citizenship or clearance required, graduation or start timing,
  2+ years required unless the role is new grad, Master's or PhD required. The
  applicant's own details for these gates live in `PROFILE.md`.
- **Score** = 70% hard skills + 5% title + 5% education + 10% experience level + 10%
  responsibilities. If a JD has fewer than 3 hard skills, skills is `null` and the other
  four parts are rescaled.
- **Pass line:** 75. Jobs at a target company listed in `target_companies.json` pass at
  45 instead. The score itself is never raised, and the knockout gates still apply.
- **Missing keywords:** up to 12, in priority order: required hard skills, preferred hard
  skills, flagged examples, responsibility terms, experience items, then soft skills.
  The full list is in `missing_all`.

## Rules for every agent and session

- Never click Apply, "Yes, I applied!", or Remove; never fill or submit forms; never sign
  in or create accounts; never solve captchas or bot checks. Stop and report instead.
- `PROFILE.md` holds private data. Never type anything from it into a website, and never
  copy it into tracked files.
- Never invent URLs. Record `null` with a note if one can't be read.
- Score only from the description on the original post, never from Jobright's summary
  or from memory.
- Use the Claude in Chrome tools. Load them in one ToolSearch call, open your own tabs,
  never touch tabs you did not create, and close yours when done.
- Read long pages with chunked `javascript_tool` reads (store `innerText` in
  `window.__jd`, read 900-character slices). The tool truncates around 1,000 characters.
- Keep personal files out of git (see `.gitignore`). Commit or push only when the user asks.

## Common commands

```bash
python3 jobqueue.py peek             # jobs waiting in the queue
python3 passed.py count              # jobs saved in ats_passed.json
python3 jobqueue.py seen <id>        # was this Jobright job collected before?
tectonic resume.tex                  # rebuild resume.pdf
```
