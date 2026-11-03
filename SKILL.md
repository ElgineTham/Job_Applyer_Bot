---
name: jobbot-apply
description: >-
  Jobright → visa check → keywords → resume_editor (Additional Skills + tectonic)
  → resume.pdf → Simplify autofill → submit. Use when applying to jobs from
  Jobright for Elgine.
---

# JobBot Apply Skill

Read and follow `RULES.md` and `PROFILE.md` in this folder before every apply.

## Agents

- **job_applyer** — Chrome scout + apply (MCP → AX → screenshot); calls resume_editor and waits. **No separate scout agent.**
- **resume_editor** — local only: patch Additional Skills in `resume.tex`, `tectonic` → `resume.pdf`.
- No Overleaf.

## Visibility

- **Chrome** (user can watch): Jobright scout, apply URL, Simplify, resume upload, submit.
- **Chrome DevTools MCP** on that Chrome (autoConnect) is the **default** control channel.
- Do **not** use Cursor’s separate browser MCP for Jobright **SSO login**.
- **resume_editor:** file edit + tectonic only.

## Channels / speed

- **Order:** Chrome DevTools MCP → Computer Use AX → screenshot (not sticky).
- **Scout:** recommend → scroll to top → **first card at the current top** (rule 2a; **never change Jobright filters**) → **click card** (keep detail open) → Jobright already-applied → if clear, **click Original Job Post** (timer) → ATS screens from original JD only. After skip/success on same Jobright: back to recommend → top → first card again. After 3 scrolls with zero new IDs → **reload recommend**, clear `session_tried_ids`, start again from the first card (rule 2a.8). Fetch/`new_page` only if OJP click fails.
- **Apply:** MCP Simplify + batch **`fill` / `fill_form`** leftovers; AX for native file dialog / MCP failures. See `RULES.md`.
- **React ATS text fields:** never `evaluate_script` / DOM `.value=` for leftovers — looks filled, fails submit. Use MCP fill (cheap; batch via `fill_form`).

## Workflow (fast path)

1. **job_applyer (MCP on Chrome):** Jobright (SSO session). Scroll recommend to top → **first card at the current top** (rule 2a; never change filters). **Click the job card** (detail opens; keep Jobright open). On detail: if **already applied** → skip (no ATS) → rule **2b** (log `skips_before` + Remove From List by id) → rule 2a. If clear → **click Original Job Post** (ATS tab; start per-job timer). Fallback fetch/`new_page` only if that click fails. Ignore Jobright H1B chips.
2. On the **original** JD/ATS page, **before** resume_editor: **already applied** → **hard-req** (must-haves vs `PROFILE.md` — grad Jun 2027 / start 06/01/2027 / ~0 YOE; skip N+ years when N≥2 unless new-grad/campus) → **sponsorship from original JD only**.
   - Any fail → **close the ATS tab only** → rule **2b** → rule 2a on the **same** Jobright tab. Do not call resume_editor.
   - All pass → continue (Jobright detail stays open).
3. **Extract keywords** (~8–15). Write `handoff.json` `"pending_resume"`.
4. **Call resume_editor** (subagent, wait — do not background):
   - Diff keywords against all of `resume.tex`
   - Update **Additional Skills** only (text after `:` until `\\`)
   - Keep **one page** (trim lowest-priority extras if needed)
   - Run `tectonic resume.tex` → `resume.pdf`
   - Set `handoff.json` to `"status": "ready"` (or `failed`) and return result
5. **job_applyer:** Open apply URL. Each form page: **Autofill This Page** first (MCP, else AX) → else Simplify toolbar → Autofill → if unsupported, PROFILE for this page only → else verify → batch leftovers. Restart that order after every page change.
6. **After verified autofill (or confirmed unsupported on this page):** batch still-empty fields with MCP **`fill_form` / `fill`** (one verify per batch) — **not** DOM value sets:
   - **Personal / account** → `PROFILE.md` (never invent; skip or ask if `TODO`)
   - **Work auth** → Yes (3 years OPT) now without sponsorship; Yes need sponsorship now or in the future
   - **Role/company questions** → JD + company + resume; not `PROFILE.md`. Human prose (no colon/dash outlines); pick resume experiences that best match this job’s keywords.
7. **Resume upload:** autofill first, then **AX only** on the normal **Resume** field (not “Autofill from resume”) with local **`resume.pdf`**. If `resume.pdf` is in AX → **select/`press` → `open` only** — never `show-menu`, search, or Go to Folder while visible; Escape if a context menu appears. Path search only when truly missing. **Ashby Yes/No:** **AX `press` first**; else one batched `evaluate_script` (React handler if present + verify `aria-pressed` in same return); not MCP uid click. Confirm pressed before Submit. Verify URL stays on `/application`. **State:** PROFILE **WA**; **Washington** is the same correct option. **Current location:** type Bellevue / Bellevue, WA → **click exact suggestion only if a list appears**; else keep typed text.
8. **Submit** (repeat Simplify-first on any further pages before final submit). On confirmed success → **close that apply tab first** (keep Jobright detail / parked tabs) → return to **same Jobright detail** → click **“Yes, I applied!”** **if present**; if missing, skip → then continue if looping.
9. **Captcha:** park the ATS tab (do not close/refresh/navigate away) → note `awaiting_user_captcha` + page_id in `do_not_touch_pages` → rule 26: reuse existing Jobright → first card at current top. Do not grind captcha. (No “I applied” mark.)
9a. **OTP:** prefer **email**. SMS/authenticator-only → park (`awaiting_user_otp`) → rule 26 continue. After send email code → **raise Mail** → AX match → **raise Chrome + select ATS tab** → fill code (memory only; never save) → continue apply. No match in **90s** → park → rule 26. (No “I applied” mark.)
10. **Per-job timer:** start when opening that job’s JD; if **>15 min** before submit → park tab (`awaiting_user_timeout`) → rule 26 continue. **Reset the clock for every new application.**
11. If applying to more jobs (non-park): **close that job’s ATS tab(s) first**, then **same** working Jobright → “Yes, I applied!” if shown after success → recommend → top → first card (rule 2a). Do **not** open another Jobright tab.

## Profile vs open questions

- `PROFILE.md` = fixed personal facts only.
- Open-ended / company-specific prompts are composed per job from the posting and resume: natural human prose, keyword-fit experiences, no colon/dash bullet-style answers.

## Handoff

- Live notify = resume_editor subagent **return** (job_applyer waits).
- `handoff.json` mirrors status for recovery: `idle` → `pending_resume` → `ready` | `failed` | `awaiting_user_captcha` | `awaiting_user_otp` | `awaiting_user_timeout`.
- **New agent run:** clear `parked_tabs` / `do_not_touch_pages` / `skips_before` / `session_tried_ids` first (rule 14a). Only parks/skips/tried IDs from the **current** run count.
- **Eligibility skip (rule 2b):** append `{id, company, title, reason}` to `skips_before` → recommend → find card by `/jobs/info/<id>` → that card’s `more-options` → **Remove From List** → then rule 2a top card.

## Stop rules

- Never customize resume or apply before Jobright already-applied, ATS already-applied, hard-req, and visa checks all pass.
- Never apply unless resume_editor returned ready / `handoff.json` is `ready`.
- Do **not** hand off UI blockers to the user — keep grinding (MCP → AX → screenshot) until submitted or truly stuck (e.g. PROFILE TODO). **Exceptions:** captcha (rule 26), **OTP park** (rule 26a), or **15-min timeout** (rule 28) → park tab + next job.
- Do **not** rely on Cursor browser MCP for Jobright SSO login.
