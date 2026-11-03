# JobBot Rules

Hard constraints for every application. Do not violate these.

## Visa / sponsorship + early screening

1. **Do not apply to roles that do not sponsor visas.**
2. **Scout order (hard — before resume_editor / apply):**
   1. On **Jobright recommend**: pick the **first card at the current top** of the feed (rule 2a) → **click it** so detail / `/jobs/info/...` opens. Keep this Jobright tab/detail **open** for the rest of this job (needed later for “Yes, I applied!”). Do **not** pre-check applied on the recommend list (avoid double work) — check on detail after the click.
   2. On **Jobright detail only**: if **already applied** (Applied / Submitted / applied badge / history) → **skip** (do **not** open Original Job Post) → rule **2b** (log + Remove From List) → next job via rule 2a on the **same** Jobright tab. Do not call resume_editor. Do **not** use Jobright “H1B Sponsor Likely” (or similar) for any decide — ignore it.
   3. If not already applied → **click “Original Job Post”** (MCP click). Opens ATS/JD in a **new tab**. Do **not** open the ATS via fetch + `new_page` as the default. **Fallback only:** if Original Job Post click fails after 1–2 tries, resolve `href` and `new_page`. **Start this job’s 15-min timer at ATS/JD open** (not at card click).
   4. On the **original ATS / JD page**, before keywords or resume_editor, check **in this order**:
      - **Already applied (ATS):** already applied / application submitted, Apply disabled, or application-status view → **close the ATS tab only** (leave Jobright detail open) → rule **2b** → next job via rule 2a. Do not call resume_editor.
      - **Hard-req screen:** skip if the JD has a **must-have** Elgine clearly fails vs `PROFILE.md` (expected grad **Jun 2027**, earliest start **06/01/2027**, new-grad / ~0 YOE). Examples: required start or degree **before** those dates; **N+ years** experience when N≥2 unless the role is explicitly new-grad / university / campus hire; citizenship-only or other hard blockers stated as required. Soft “nice to have” / preferred skills do **not** skip. On skip → close ATS if open → rule **2b**.
      - **Sponsorship (original JD only):** decide solely from the ATS/JD text. Skip if it says no sponsorship, must be authorized without sponsorship, or equivalent. Do **not** read or rely on Jobright H1B badges. On skip → close ATS if open → rule **2b**.
   5. Only if Jobright already-applied, ATS already-applied, hard-req, and sponsorship all pass → extract keywords / scan JD → resume_editor → apply (Jobright detail stays open meanwhile).
2a. **Jobright feed / filters (hard — always current top card; do not invent “no jobs”):**
   1. **Never change Jobright filters** (date, role, location, seniority, “All Filters”, saved filters, etc.) unless the user explicitly asks. Do **not** widen Past 24 hours → Past week (or similar) on your own.
   2. **Always pick the first card at the current top** of the recommend feed. Before picking: put the **list scroller at the top**, then click that top card. After a skip or finished apply (non-park): on the **same** Jobright tab, return to recommend (back or `/jobs/recommend`), scroll to top, pick the **first card at the current top** again. Do **not** resume a mid-feed “next after last tried” cursor. Do **not** scroll past the top hunting for a deeper untried ID.
   3. **Do not jump ahead.** Never pick a lower/further card while a higher/earlier card at the current top should be chosen first. Scraping `querySelectorAll` and taking “any” untried ID from mid-list is forbidden.
   4. **Track tried job IDs** this session (`/jobs/info/<id>`). Mark an ID tried when you open its Jobright detail (including intentional early skips: Applied, hard-req, sponsorship, user hard-skips like TikTok/ByteDance). If the current top card’s ID is **already tried**, do not re-open it — take the first **untried** card counting strictly **from the current top downward** (still top-first; not a deep cursor).
   5. The recommend list is often **virtualized**. Always return the list scroller to the **top** before choosing. Scroll **down** only when the top visible cards are all already tried and you need the next untried immediately below, or when loading more after that. Do **not** decide the feed is empty from one DOM snapshot or the first screen only.
   6. **Scroll to load more:** only after every currently revealed card from the top is already tried — scroll the **job list scroller** (prefer the list container, not only `window`) → wait briefly for new `/jobs/info/` links → continue picking the first untried from the top. Treat the feed as temporarily exhausted under **current** filters only after **3 consecutive scrolls with zero new job IDs**.
   7. A streak of Applied / hard-req / other intentional skips is **not** “no more jobs.” Keep returning to the current top (rule 2a.2). **Do not** change filters.
   8. **Feed exhausted → refresh and restart (hard):** After 3 consecutive scrolls with zero new job IDs: on the **same** working Jobright tab, **reload** recommend (`reload` or navigate to `https://jobright.ai/jobs/recommend`). Wait for the feed to load. Clear `session_tried_ids` → `[]` in `handoff.json` (this walk starts fresh; keep `parked_tabs` / `do_not_touch_pages`). Scroll the list to the top → pick the **first card at the current top** (rule 2a.2) and continue the apply loop. Do **not** stop solely because the prior walk exhausted.
2b. **Skip → log + Remove From List (hard — every eligibility / abandon skip):**
   1. **When:** Jobright already-applied, ATS already-applied, hard-req fail, sponsorship fail, or user hard-skip (e.g. TikTok/ByteDance). **Not** for captcha/OTP/timeout parks, and **not** after a successful submit.
   2. **Remember** the Jobright job `id` from `/jobs/info/<id>` plus company, title, and skip `reason`.
   3. **Append** to `handoff.json` `skips_before`: `{ "id", "company", "title", "reason" }` (current-run list only; cleared on fresh start — rule 14a).
   4. **Close ATS** tab(s) for this job if open (rule 27). Stay on the **same** working Jobright tab.
   5. **Return to recommend** (back or `/jobs/recommend`). Find the card whose link `href` contains that exact `id`. Scope to that card’s container; cross-check title/company. Open that card’s **`more-options`** (⋮) → click **`Remove From List`**. Do **not** click another card’s ⋮. If the card is not in the DOM, scroll until the id appears or give up after a short search — then continue rule 2a.
   6. Then continue: scroll to top → **first card at the current top** (rule 2a).
3. If it does **not** sponsor (or fails already-applied / hard-req) → **close the ATS / original-post tab only**, leave Jobright open, do rule **2b**, then next job via rule 2a on the **same** Jobright tab. Do not call resume_editor for that role. Do **not** open a second Jobright tab for ordinary skips.
4. **Sponsorship source of truth = original job post only.** Ignore Jobright “H1B Sponsor Likely” / “H1B Sponsored” chips entirely for pass/fail.

## Work authorization answers (forms)

5. **Currently authorized to work in the US without employer sponsorship?** → **Yes** (3 years OPT).
6. **Will you now or in the future require employer sponsorship?** → **Yes**.

## Agents / resume pipeline

7. **job_applyer** owns the full loop (no separate scout agent): **Chrome scout via DevTools MCP** (Jobright card → Original Job Post → JD/visa/keywords; AX/screenshot fallback) → call resume_editor → **Chrome apply** (Simplify → upload `resume.pdf` → submit) → **Jobright “Yes, I applied!”** (rule 27a) → next Jobright job in Chrome.
8. **resume_editor** owns: missing-keyword diff vs `resume.tex` → update **Additional Skills only** → `tectonic resume.tex` → `resume.pdf`.
9. job_applyer must **wait** for resume_editor (subagent return / `handoff.json` `"status": "ready"`) before applying. Do not apply with a stale PDF if status is `failed`.
10. **Overleaf is not used.** PDF comes from local `tectonic` only.

## Resume / Additional Skills

11. Keep the resume **one page**.
12. **Additional Skills edit (resume_editor only — fast path):**
    - Near end of `resume.tex`, find `\textbf{Additional Skills}:`
    - Replace **only** the content after the colon up to (but not including) the `\\`
    - Add keywords from job_applyer that are **missing anywhere** in `resume.tex`
    - If the line would break the one-page limit, prioritize caller/JD order and drop lower-priority terms
    - Do not edit other sections of `resume.tex`

## Browser / input channels

13. **Scout + apply = Google Chrome** with the user’s logged-in profile (Jobright Google/SSO). Use **Chrome DevTools MCP** (`chrome-devtools` / `user-chrome-devtools`, `--autoConnect`) attached to that Chrome. Do **not** use Cursor’s separate browser MCP for Jobright login (SSO/pwd unsupported there).
14. Keep **one working Jobright tab** for the active scout/apply loop while resume_editor / apply run (do not close it; do not open extra Jobright tabs). Keep parked captcha/OTP/timeout **ATS** tabs open and listed in `handoff.json` (`parked_tabs` / `do_not_touch_pages`) so they are never selected or navigated **during this agent run only**.
14a. **Fresh agent start (hard):** When a **new** job_applyer run begins (user stopped the prior agent and starts another, or any new invoke that is not an in-run resume of the same live loop), **clear** in `handoff.json` immediately: `parked_tabs` → `{}`, `do_not_touch_pages` → `[]`, `skips_before` → `[]`, and `session_tried_ids` → `[]`. Do **not** treat prior-run parks, skips, or tried IDs as still active — the user may have already solved/closed parked tabs / changed the feed, and those lists are **per run only**.
15. **Channel fallback (hard order — every step):**
    1. **Chrome DevTools MCP** (DOM snapshot / click / fill / `evaluate_script` / `upload_file`)
    2. **Computer Use AX** if MCP fails that step (tab missing, CDP disconnect, control not in DOM, native OS UI)
    3. **Screenshot** only if AX is empty/wrong or you need a one-shot diagnose — **not sticky**; return to MCP/AX next step
    - **One channel per step** — never MCP + AX on the same control.
    - Fail fast: **1–2 MCP retries** max on a step, then AX for that step.

16. **JD text vs UI controls:**
    - **Scout (default UI path):** Jobright recommend → **first card at the current top** (rule 2a) → **click job card** → Jobright already-applied on detail → if clear, **click “Original Job Post”** → ATS already-applied + hard-req + sponsorship (original JD only) → then keywords. Read JD from the live ATS page (snapshot / `evaluate_script`).
    - **Fallback only** if Original Job Post click fails: resolve `href` (detail link or same-origin `fetch` of Jobright info) → `new_page`. Prefer UI click so Jobright can show “Yes, I applied!” later.
    - **JD text** (ATS already-applied / hard-req / sponsorship + keywords): **source of truth = original ATS page in MCP** (Ashby, Greenhouse, Lever, ZipRecruiter, etc.). Dismiss overlays (Escape) if needed. Do **not** rely on bare shell/`curl` of SPA ATS pages (often empty “enable JavaScript”). Do **not** `fetch` the ATS URL from inside the Jobright tab (cross-origin blocked) as the primary open path.
    - **Jobright detail UI:** OK for title/company/pay, rough keywords, and **already-applied** status only. **Never** use Jobright H1B chips for sponsorship (rule 4).
    - **Simplify, form leftovers, resume upload, submit:** MCP first; AX fallback. Follow Simplify order in rule 22.

## Speed (Chrome MCP + AX fallback)

17. **Fast scout (Jobright → JD):** MCP select working Jobright recommend → scroll list to top → **first card at the current top** (rule 2a; **never change filters**) → click card → click **Original Job Post** → read JD from ATS DOM. Fetch/`new_page` only as fallback (rule 2 / 16). AX/screenshot scout only if MCP cannot reach Chrome.
18. **Apply forms / Simplify:**
    - **MCP first** (snapshot / click / fill / `fill_form`). Simplify order in rule 22 (Autofill This Page before extension icon).
    - **AX** (`computer_app_state` + `press` / `set_value`) when MCP cannot act.
    - **Screenshot** only when both MCP and AX are weak, for file-dialog focus checks, or risky verify — not sticky.
19. **Batch UI work (minimize tree reads — main speed lever on forms):**
    - On a form page: **one** MCP snapshot (or one AX read) → fill a **batch** of text fields → **one** verify re-read.
    - Prefer larger text batches (**5–10** fields) when controls are plain text. Dropdowns/dates need a re-read after open (menu appears = tree changed).
    - Do **not** observe→act→verify per field. Do **not** re-read only to “be safe” after a successful text fill.
    - Skip optional long waits when Simplify says unsupported; avoid waits except for real navigation/load.
    - After a page navigation or major UI change → **Simplify autofill first** (rules 21–22), then **one** fresh read, then batch again.
19a. **Text leftovers — MCP `fill` / `fill_form`, not DOM value writes (React ATS):**
    - Ashby / Greenhouse / similar use **controlled React inputs**. Setting `el.value = "..."` via `evaluate_script` updates the DOM only; React state often stays empty → submit shows “Missing …” even though the field looks filled.
    - **Required for still-empty text / textarea leftovers:** MCP **`fill_form`** (preferred batch) or **`fill`** / type into a focused field so real `input`/`change` events fire. Click/focus alone is not enough.
    - **`evaluate_script` is OK for:** reads (empty check, error banners, URL), and Ashby Yes/No **fallback** after AX (rule 20). **Not** for typing profile/essay answers into text fields.
    - **AX `set_value` alone** is unreliable on the same React controls — prefer MCP fill; AX type only after focus if MCP cannot target the field.
    - **Runtime:** `fill_form` is one MCP call for many fields — seconds, not a new stage. Failed DOM writes + resubmit cost more than fill once.
20. **Dropdowns & date pickers (open → select — not raw text set when it won’t stick):**
    - Applies to **Degree** (e.g. A.A. / Associate / B.S.), country/state, phone type, source, and similar popup/menu fields.
    - Correct path: **click/press to open** → re-read → **click/press the matching option** from `PROFILE.md` (closest label OK, e.g. Associate → **A.A.**). Same idea in MCP (`click` / `fill`) or AX (`press` / `show-menu`).
    - **Dates — two kinds:**
      1. **Plain text / typeable date** (`MM/DD/YYYY` etc.): fill/type from `PROFILE.md` / resume.
      2. **Popup date picker**: open → select month/year (or Previous/Next Year). Work dates often `MM/YYYY`; education may be year-only. Do **not** grind text-set on this kind.
      - If unsure: try fill/set once; if empty / doesn’t stick, switch to **open→select**. Do not loop.
    - Also **click/press (not text-set)**: radios, checkboxes, tabs, primary buttons (Next / Continue / Submit).
    - **Combobox / typeahead**: type, then **if a suggestion list appears**, click/press the matching option — typing alone often does not stick. If **no suggestions appear**, leave the typed value (plain text field).
    - **Current location / city:** type `Bellevue` or `Bellevue, WA` from `PROFILE.md`. **Only if suggestions appear** → click the exact matching option (e.g. Bellevue, WA, USA). If there is no dropdown/suggestion list, keep the typed text. If the form says “Please select a location from the dropdown…” → suggestions exist and were not chosen; open the list again and pick one before Submit.
    - **Ashby Yes/No (and similar custom option buttons) — do not use MCP `click` by snapshot uid.** Playwright uid-click can miss and hit the company logo / header link (leaves `/application`, wipes the form). Synthetic DOM `click()` / fake mouse events often **do not update React state** (looks pressed, submit still fails). Prefer in order:
      1. **AX `press`** on the Yes/No control for that question (real activation; usually updates React). Batch several Yes/Nos with AX without extra snapshot loops when the tree is already fresh.
      2. Else **one** MCP `evaluate_script` (same call): find each question by label → Yes/No inside that container → prefer invoking the control’s **React handler** if present (`__reactProps$…` / fiber `onClick` / `onChange`) else a full pointerdown/up + `click()` → return each `aria-pressed` / selected class. If not pressed, **one** in-script retry. Do not add per-question snapshot round-trips.
      3. MCP uid `click` only as last resort, **one control at a time** (never parallel clicks on the same form).
      - Before Submit: confirm required Yes/Nos show pressed/selected (from that script return or one quick read). If not → fix those answers; do not park as captcha when the real issue is unset toggles.
    - **After every form click/press that could navigate:** confirm URL still on the ATS application path (e.g. still contains `/application`). If it left (e.g. company homepage): **`history.back()` / navigate back immediately** — prefer back over a fresh application URL load when possible so field state may survive; then re-check. Never click company wordmark / logo links while applying.
    - Do **not** hand off to the user — keep going until the field sticks or the apply finishes.

## Autofill / resume upload

21. Let **Simplify autofill run first on every new page**. Multi-step portals (iCIMS, Workday, etc.) often support Autofill on later pages even when an earlier page (e.g. login) does not. Only fill fields that are still empty after autofill **and** after you have verified autofill ran (or is unsupported **on this page**).
22. **Simplify trigger order (every new page — MCP → AX → screenshot):**
    1. Search for **“Autofill This Page”** (or Autofill / Autofill page) on the page or already-open Simplify panel (**MCP snapshot first**). If found → click/press it. Do **not** open the extension icon first.
    2. **Only if that button is missing:** open toolbar **`Simplify Copilot Has access to this site`** (MCP click, else AX `press`), then search again for **Autofill This Page** and click it.
    3. **Unsupported check:** if Simplify shows autofill **isn’t supported** on this page → stop waiting; use `PROFILE.md` for **this page only**. Do not treat that as successful autofill.
    4. After a successful Autofill trigger → **verify once**: at least one previously empty profile field filled. If not → one retry, then `PROFILE.md` leftovers.
    - **Unsupported is not sticky across pages** — on each new page, restart at step 1.
    - Never start bulk manual fill while Autofill This Page is visible and unclicked.
23. **Still-empty personal / account fields** (name, email, phone, address, LinkedIn, GitHub, education basics, work auth, demographics, passwords if stored, etc.) → fill from **`PROFILE.md`**. Never invent profile facts. If a needed `PROFILE.md` value is `TODO` / blank → ask the user or skip that field. Use **batch fill** (rule 19). For dropdowns/dates use rule 20 (open → select).
    - **State / province:** PROFILE **WA**; **Washington** is the same correct answer. Type `WA` or `Washington` to filter; select **Washington** if that’s the option. If Simplify already left **WA** or **Washington**, leave it. Do not change a correct WA/Washington to the job’s office state.
    - **Current location:** PROFILE city/state (Bellevue, WA). Type it; **select an exact suggestion only when the field shows options** (rule 20).
24. **Still-empty role/company questions** (e.g. “Why this company?”, “Why this role?”, “project you’re proud of,” technical challenge, cover-letter style prompts) → answer from the **job post + company + resume**. Do **not** look these up in `PROFILE.md` and do **not** use a generic canned blurb.
    - **Pick experiences that best match this job’s keywords** (and the question). Prefer concrete work from the resume over vague claims.
    - **Sound human and natural** — short paragraphs or a few flowing sentences, like a real applicant writing quickly. Promote Elgine as a strong fit without sounding robotic or résumé-paste.
    - **No outline formatting in the answer text:** do **not** use colons as label separators (e.g. `Challenge: …`) or dash/bullet lists (`- …`, `• …`). Write plain prose. Avoid stacked `Title — detail` lines.
25. **Resume upload / replace (keep this short):**
    - Run Simplify autofill first, then attach/replace project-root **`resume.pdf`** (absolute path: JobBot folder `/Users/elginetham/Downloads/JobBot/resume.pdf` or the workspace `resume.pdf`).
    - **Ashby (and similar) often has two upload controls** — do **not** use the top **“Autofill from resume” / “Upload your resume here to autofill”** chooser. Use the form’s normal **Resume** field (**Upload File** / **Replace**). Verify the filename sits on that Resume control, not only on the autofill block.
    - **Resume file dialog = AX only.** Use Computer Use **`computer_app_state` + `computer_app_action`** on the native open panel. Do **not** use screenshot clicks, OCR coords, `computer_click` on the dialog, or MCP `upload_file` / DOM file-input injection for resume. (MCP may still click the page’s Upload/Replace **button** to open the dialog.)
    - **AX open panel — hard allowlist when `resume.pdf` is visible:**
      - **Allowed actions only:** select / `press` the **`resume.pdf`** row → **`open`** (or press the dialog’s **Open** button).
      - **Forbidden (even if listed in AX `actions=`):** `show-menu`, Quick Look, rename, duplicate, `set_value` / filename search / typeahead filter, Go to Folder, sidebar browsing. Picking `show-menu` opens a context menu and wastes the dialog — never do it for resume.
      - If a context menu appears by mistake → **Escape** once → select `resume.pdf` → Open (no improvising).
    - **AX open panel steps:**
      1. Open Attach / Upload / Replace → confirm the **file dialog / sheet** is focused (raise it if Chrome/Find stole focus).
      2. **Look in the AX tree first:** if **`resume.pdf`** is already listed/selected — AX **select/`press` it → `open`** only (allowlist above). Do **not** fall back to screenshot while it is in AX.
      3. **If Open fails / attach doesn’t stick** but `resume.pdf` is still in AX: cancel/re-open the dialog if needed → select/`press` `resume.pdf` → Open again (**1–2 retries max**). Still allowlist-only.
      4. **Only if `resume.pdf` is truly missing** from the AX dialog listing: focus the sheet, then **Go to Folder** (`Cmd+Shift+G`) → full JobBot `resume.pdf` path → Open (still AX keys/actions, not screenshot). If Chrome Find opens instead, cancel Find, focus the sheet, retry. Do not browse folders click-by-click.
    - **One** verify of the new file name on the Resume field. Keep retrying with AX — do **not** hand off to the user.

## Captcha (park tab → continue)

26. **CAPTCHA / human-verification gate (hCaptcha, reCAPTCHA, “verify you are human”, etc.):**
    - Do **not** spend the loop trying to solve image puzzles (MCP/AX/screenshot). Quick check only: checkbox / “I’m not a robot” if it’s a simple click; otherwise treat as blocked.
    - **Park that apply tab:** leave it **open**. Do **not** `close_page`, navigate away, refresh, or dismiss the challenge. Form should already be filled + resume attached so the user can solve captcha and hit Submit later.
    - Note in `handoff.json` (or report): `"status": "awaiting_user_captcha"`, company, title, apply URL, and that the tab is parked.
    - **Continue after park (hard):** Do **not** close parked tabs **from this run**. Record the parked ATS `page_id` (+ URL) in `handoff.json` `parked_tabs` / `do_not_touch_pages` (current-run only; see rule 14a). **Do not** open a new Jobright tab — reuse the **existing working Jobright** already in Chrome: select it → recommend (back or `/jobs/recommend`) → scroll to top → **first card at the current top** (rule 2a) → continue. Never `select_page` / navigate / close a parked ATS tab listed for **this run**. Disambiguation: working Jobright = scout/apply loop; parked = ATS tabs in `do_not_touch_pages`; active ATS = only the non-parked apply tab for the job in progress.
    - Captcha, **OTP park** (rule 26a), and the **15-minute timeout park** (rule 28) share this continue path. Other blockers still grind (MCP → AX → screenshot) unless PROFILE `TODO` / user abort.

26a. **OTP / email verification (during apply):**
    - If the form offers a channel choice → prefer **email** OTP (PROFILE apply email / Mail inbox).
    - If **only SMS or authenticator** is available → **park** the apply tab (leave open; no close/refresh). Set `handoff.json` `"status": "awaiting_user_otp"` (company, title, apply URL, reason: sms/authenticator-only). Continue via rule **26** park-continue (reuse existing Jobright; first card at current top). No “I applied” mark.
    - **After sending an email code:**
      1. Note send time. **Raise Apple Mail first** (`open -a Mail` / AX activate) — AX fails if Mail is not forward.
      2. Poll Mail AX **message list** (sender, subject, preview). Prefer list preview; do **not** use screenshot for OTP if AX works after raise. Do not dig the whole mailbox.
      3. **Match** (all must pass): (a) arrived **after** send (or within last **2 minutes** if no exact timestamp); (b) OTP-ish subject/preview (`verification code`, `one-time`, `security code`, `passcode`, `OTP`, `authenticate`, `sign-in code`, `login code`); (c) sender/subject/preview ties to **current company** or ATS/noreply patterns (`noreply`, `no-reply`, `careers`, `jobs`, `otp`, `verify`, ADP, Amazon, Workday, etc.); (d) extract a **4–8 digit** code (prefer labeled / next to OTP wording); (e) if several match → **newest wins**. Reject newsletters, Jobright alerts, LinkedIn, pre-send mail, or ambiguous multi-code messages.
      4. **Keep the code only in memory** — do **not** write it to `handoff.json`, PROFILE, disk, or logs.
      5. **Immediately raise Google Chrome** (`open -a "Google Chrome"` / AX activate) and **select the ATS apply tab** that requested the OTP (MCP `select_page` / bringToFront). Do **not** leave Mail in front when filling.
      6. **Fill the OTP** on that form (MCP `fill` / `fill_form`) → continue the apply workflow (autofill order, leftovers, resume, submit as usual).
      7. Optional: **one** resend if nothing useful yet and time remains.
      8. If **no match within 90 seconds** of send → **park** tab (same as captcha). `handoff.json` `"status": "awaiting_user_otp"` (reason: timeout; **no code stored**). Continue via rule **26** park-continue.
    - OTP park is separate from captcha; same “leave open + continue” behavior (rule 26).

27. **Close ATS tab(s) before moving on** (skip or finished apply):
    - **When:** you leave a candidate for the next Jobright job because of a **skip** (no sponsorship, hard eligibility mismatch, already applied, etc.) **or** a **finished apply** (confirmed successful submit — thanks / success / “application submitted”).
    - **What to close:** that job’s original-post / ATS / apply tab(s) (`close_page`). Close them **first**, then continue on Jobright.
    - **Do not close:** the Jobright tab (keep detail open through apply when possible), parked captcha/OTP/timeout tabs (rules 26 / 26a / 28), or unrelated tabs.
    - Captcha-, OTP-, and timeout-parked jobs are **not** “finished” for this rule — leave those tabs open.
    - After a **confirmed successful submit**, also do rule **27a** before scouting the next job.

27a. **Jobright “I applied” mark (after successful submit only):**
    - After closing the apply/ATS tab(s), return to the **same Jobright detail** you opened via card click (rule 2).
    - Look for the confirm prompt (typically **“Yes, I applied!”** / **“No, I didn't apply”**, or “I applied” / “Did you apply?”).
    - **If present** → click **“Yes, I applied!”** (or equivalent yes/confirm) via MCP, then proceed to find the next job.
    - **If not present** → do **not** grind; skip this step and proceed to find the next job.
    - Do **not** invent clicks on unrelated UI. Skips / captcha / OTP / timeout parks do **not** require this mark.

## Per-job time limit

28. **Track time per application (hard 15-minute cap):**
    - **Start** the clock when you **open that job’s original post / begin JD read** for the candidate you are pursuing (first click into that listing’s ATS/JD — not Jobright browsing, not prior jobs).
    - Clock covers JD/visa → keywords → resume_editor → apply → submit for **this job only**.
    - **If wall time exceeds 15 minutes** before confirmed submit: **park the tab** (same as captcha — leave open; no close/refresh/navigate away). Set `handoff.json` `"status": "awaiting_user_timeout"` (company, title, apply URL, elapsed note). Continue via rule **26** park-continue (do not close parked tabs; reuse existing Jobright; first card at current top).
    - **Reset the timer for every new application.** Do **not** carry elapsed time from a previous job, skip, or park. New job → new start timestamp at that job’s JD open.
    - Skips before committing (no-sponsor / hard mismatch after a quick JD peek) do not consume a 15-minute budget on the next job — still restart when you open the next chosen JD. **Close that skipped job’s ATS tab(s) first** (rule 27), then continue on the **same** working Jobright via rule 2a.
