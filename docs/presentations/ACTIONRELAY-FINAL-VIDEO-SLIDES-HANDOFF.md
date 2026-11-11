# ActionRelay final video and slides handoff

**Snapshot:** 2026-11-11
**Purpose:** Preserve the accepted creative and interface decisions before producing the final slide deck and revised video. Treat this as a production brief; it does not claim the final revisions have been rendered.

## Current files and what they are

- `ActionRelay-v2/actionrelay-demo.mp4` is the earlier MP4 walkthrough. It is not the final revised video with all latest pacing, paired-account, playback, credits, and app changes.
- `ActionRelay-review/actionrelay-demo.html` and `ActionRelay-review/actionrelay-demo-beats.html` are the current HTML review walkthroughs (continuous and presenter editions). They are useful source material, not the revised final MP4.
- The Storyboard is currently embedded in the authenticated app through `src/cdit_support_mao/static/actionrelay-presentation.js`; it is an in-interface story/slide sequence, not a standalone PowerPoint/PDF slide deck. The Codex working-copy source is under `ActionRelay Final Build/src/cdit_support_mao/static/actionrelay-presentation.js`.
- Codex’s `ActionRelay Final Build` working copy also contains the HTML Storyboard/app and review demos. It does not contain a separate `.pptx`/`.ppt` slide deck. Copy final deliverables into the project `docs/presentations/` folder; do not treat duplicate Codex working copies as the published project source.
- See [`ACTIONRELAY-REVIEW.md`](./ACTIONRELAY-REVIEW.md) for current app and review-demo checks. Final video and standalone slides are still pending.

## Story that opens the slides and leads into the Demo

1. **Who CDIT is:** summarize only facts supported by the current CDIT site and the replacement Customer Support Specialist posting at `docs/artifacts/CDIT-JD.txt` / the current ATS link. State the organization’s mission and history only with a linked, checked official source. If a founding date cannot be verified, omit it or label it unverified; do not infer it.
2. **Why this problem matters:** connect the job posting’s real support duties (intake, Salesforce case work, Tier 1 troubleshooting, SLA monitoring, escalation, customer training, and knowledge contributions) to the proposed workflow. Clearly distinguish job-posting facts from our design inference.
3. **External context statistic:** include a credible published statistic specifically about HR/support ticket volume, unanswered requests, backlog, or time-to-response only after verifying the source, date, population, and metric definition. Link the source on the slide. It is external context, not CDIT data. If no defensible unanswered/limbo-ticket number is found, say so rather than substitute a fabricated number. Do not imply a public API exists unless a real dataset/API is verified.
4. **Why six agents:** explain the distinct responsibilities and handoffs: Coordinator, Triage, Knowledge, Troubleshooting, Escalation, and Documentation. Show the loop between stages, version/evidence checks, parallel Knowledge/Escalation where permitted, human pause/resume, and the final application gate. Do not imply every current app path already runs as one automatic six-stage live call.
5. **What should be faster:** contrast a synthetic, timed example with a manual path and routine automation path only when both timings are measured in the demo. Baseline CDIT ticket volume, backlog, SLA performance, and time saved remain unknown. Label any timing comparison illustrative; never claim hours became seconds for CDIT without evidence.
6. **Lead into the interface:** Storyboard comes before the Demo. The Demo then follows User, Staff, Auditor, and Admin perspectives and shows the request being entered, routed, reviewed, and answered. The presenter does not interact with the recording; cursor, scroll, typing, agent activity, and screen transitions perform the walkthrough.

## Slide/storyboard content to carry forward

- Begin with the CDIT story and job-description problem, then explain ActionRelay’s design choice and six responsibilities before opening the live interface Demo.
- Use the approved ActionRelay frosted-glass identity and logo. Keep the shared app Storyboard/Demo divider in the same position across roles, after the longest Admin navigation with the agreed spacing. Use distinct colors for Storyboard and Demo while keeping role navigation consistent.
- Use compact universal symbols for playback and common actions, with accessible names/tooltips and concise words where a symbol alone could be ambiguous.
- Show the current app’s dynamic copyright year, footer links to the PRD, architecture, and other links already listed by the PRD artifact. Forms & Resources belongs in the footer, with the synthetic contact sheet and display-only CDIT address clearly identified as illustrative.
- Distinguish documented behavior from proposed or unverified behavior. Synthetic case counts are not CDIT service statistics. Do not use the old unmatched 961 figure or present the 80 development examples as a real distribution.

## Final video editions and playback

Produce two synchronized editions from the approved final interface:

- **Continuous:** plays through all chapters unless the presenter pauses, navigates, or replays.
- **Presenter/clicker:** supports deliberate next/previous chapter navigation, with automatic continuation available and a remaining-seconds timer for each chapter.

Both editions must show an end-to-end human-speed walkthrough of the full approved story, even when a live integration is unavailable during recording. Label scripted/simulated behavior truthfully. Target up to 180 seconds, with enough time to read and follow each action; slow typing, pointer movement, and scrolling to natural human pace. Avoid long stalls. Explanatory captions sit at the left without covering controls, fields, or data. Use gentle transitions and maintain continuity between chapters.

Use compact icon buttons for **Previous, Play/Pause, Next, Replay**, plus **0.5×, 0.75×, and 1×** playback. Keep keyboard/clicker navigation and accessible labels. Playback speed changes the walkthrough timing, not the truth of the displayed result.

Use the selected **Open Circuit R4** music in the beat/presenter version. Keep the continuous edition unobtrusive and loop the selected track seamlessly from ending to beginning, with no audible gap or restart hit. Music should have the approved rock rhythm/instrumentation and level; it must not overpower narration or screen actions. Confirm the final music master exists and is the selected R4 asset before rendering.

## Walkthrough sequence

1. Establish the CDIT support context and introduce ActionRelay.
2. Show the User entering a supported blank-form request. Show the approved file itself becoming available in the ticket, then Resolved; explain that delivery does not submit the form and Resolved is not Closed.
3. Show an exception such as a personal W-2 or unexpected payroll withholding staying open for human review; do not expose personal records or claim an employee record was changed.
4. Show Staff queue filters including status, urgency band, category, and date; show assigned-only scope and a useful flag such as **Close out or Review**.
5. Show Auditor reviewing all queue tickets but editing only their own assignments; record a reasoned decision and revision history.
6. For cross-account actions, first show the acting account alone, then slowly shrink into split screen. Example: Admin leaves feedback/flags the exact Auditor decision; show that feedback appear in the Auditor account. Use the same transition pattern for any other linked account action. Do not force a logout/login sequence when simultaneous split-screen demonstrates the same action more clearly.
7. Show Admin analytics and account/assignment controls, with all-case scope and Product Health. Keep all charts synthetic and avoid claiming verified CDIT distributions.
8. End on the credits as a full-screen closing page.

## Credits and opening/closing technology

The ending is one full-screen credits page, not a left rail or a small credits card. Use an eye-catching dark/black treatment or translucent version of the approved motion background, with readable contrast. Place the supplied Pursuit wordmark above the credits, recolored to harmonize with the background, and include **“Special thanks to Pursuit”** and **“Support: Pursuit.”**

Credit lines exactly as approved:

- Emmanuel De Jesus (Manny) | Coordinator, Triage, Escalation, and SQL
- Shawn Bi | Knowledge, Troubleshooting, and Documentation
- ChatGPT 6.1 Sol | Video and audio

Show the technology stack at both the opening and the end/credits. Match names and technologies to what is actually in the build (Python, FastAPI, SQLite, HTML/CSS/JavaScript, and Claude Sonnet 5.5 for explicitly authorized synthetic Triage calls). Do not imply live CDIT/Salesforce integration.

## Final slide/video acceptance checks

- Verify all official CDIT facts and job responsibilities against linked sources; put slide-level citations beside each statistic or historical claim.
- No unsupported claim about CDIT ticket counts, unanswered tickets, measured savings, or service outcomes.
- Show realistic, varied synthetic cases and dates; status and category/band filters work in the app example.
- Keep all four personas’ access distinctions accurate, especially Auditor visibility vs. assigned-only editing.
- Demonstrate the exact file delivery and ticket status behavior; separate personal-record human handoff from blank-form fulfillment.
- Readable at presentation size; no overlay blocks an input, chart, or key state.
- Continuous and presenter editions have matching events, credits, tech stack, controls, timers, and usable keyboard/clicker support.
- Credits occupy the final full screen and include Pursuit, both contributors, and ChatGPT 6.1 Sol exactly as listed.
- File the final slide deck/storyboard source, both runnable HTML editions, final audio master, and both requested video editions under `docs/presentations/` with a short README naming the final versions.