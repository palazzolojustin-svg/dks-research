# ORCHESTRATOR PROCEDURE: DKS two-thesis overnight scrape (THESIS_SCRAPE)
(For the main session, or any watchdog session that takes over. Working dir C:\Users\palaz\Downloads\DKS_RESEARCH. Everything lives in THESIS_SCRAPE\. Do NOT touch PB_SCRAPE\: that is a separate owned-brand run with its own watchdog.)

## User's request (verbatim intent)
Thesis #1 = House of Sport / Field House comp floor (the user's choice among the long points already found; it excludes buybacks, closures, FL exits and owned brands). Thesis #2 = a NEW long thesis not already found, picked from the wave-1 discovery. For each, gather HARD, NOVEL evidence (the full corpus first: expert calls, alt data, earnings calls, broker notes; then web alt data) that shows (1) clear variance vs Bloomberg consensus and (2) a novel "smoking gun". The user does NOT want data we already have. Scrape for as long as is productive. Final deliverable: ONE readable research memo (HTML Artifact).

## Files
- STATE.md: run status, wave table, heartbeat, dry-wave counter, Apify total, thesis #2 choice. Update the heartbeat every time you act.
- AGENT_RULES.md + KNOWN_BRIEF.md: every sub-agent reads these first. After thesis #2 is chosen, append a "THESIS #2" known section to KNOWN_BRIEF.md and an updated mission line to AGENT_RULES.md.
- PROMPTS_WAVE<N>.md: assignments. wave<N>\<ID>.md: outputs (complete when the last line is `STATUS: COMPLETE`).
- LEDGER.md: consolidated, de-duplicated findings (grades A/B/C/X).
- APIFY_LEDGER.md: hard cap $25 total.

## Takeover check (watchdog / cron)
1. Read STATE.md. If `STATUS: DONE` → exit (the watchdog also deletes its own scheduled task `dks-thesis-scrape-watchdog`).
2. If HEARTBEAT is < 75 min old, OR any file in THESIS_SCRAPE\wave*\ was modified < 45 min ago → orchestrator/agents are alive → exit without action. (Exception: the in-session cron of the owning main session always proceeds to the Loop.)
3. Otherwise take over: write a new HEARTBEAT with `owner: watchdog <time>`, then continue with the Loop.

## Loop
A. For the current wave: list agent IDs from STATE.md. Any ID whose output file is missing, or lacks `STATUS: COMPLETE` and has not been modified for 60+ min, and is not still running in this session → relaunch it (Agent tool, subagent_type general-purpose, run_in_background true). Prompt: "Read C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\AGENT_RULES.md and KNOWN_BRIEF.md first and follow them exactly. You are agent <ID>, wave <N>. Your assignment is section <ID> of THESIS_SCRAPE\PROMPTS_WAVE<N>.md. If THESIS_SCRAPE\wave<N>\<ID>.md already exists, it is your own partial work from a crashed run: read it, keep it, and continue from where it stopped." Max 20 concurrent.
B. When the wave is complete (or ≥17/20 complete and the rest are stale for 60+ min): consolidate into LEDGER.md. Keep only NEW/BURIED, grade them A/B/C/X, and spot-verify the top A findings (re-fetch the source, or Read the SOURCE file).
C. AFTER WAVE 1 ONLY: choose thesis #2. Score each D-agent candidate on novelty × evidence × size, and check that it is not in KNOWN_BRIEF's known list and is not owned brands/buybacks/closures/FL exit/HoS. Record the choice and the reasoning in STATE.md, add the thesis #2 sections to KNOWN_BRIEF/AGENT_RULES, and keep the runner-up as a fallback.
D. Wave verdict: "productive" if ≥2 new A-grade or ≥5 new B-grade findings across the two theses; otherwise "dry". Update DRY_STREAK (reset to 0 on a productive wave).
E. If DRY_STREAK < 3 and good leads remain → write PROMPTS_WAVE<N+1>.md and launch it (20 agents, roughly 9-10 per thesis). Follow up the strongest leads, deepen productive avenues, verify A findings, open new avenues from "Leads for next wave". WAVE 2 MUST also include working-notes sweep agents reading IN FULL (for both theses): (W01 + W02 + W09), (W03 + W06 + W08), (W05_A + W05_B), (W05_C + W20_SECTOR_MACRO), (P_ASO_10K + P_ASO_10Q + P_ADIDAS_PUMA_ASO_FL_RESEARCH), (W21 alone), plus peer research (P_NKE_RESEARCH_1-4, P_DECK_*, P_ONON_*) if thesis #2 touches brands/competition. Also add one agent to pull relevant raw SOURCE\ files (expert-call transcripts, alt-data files) and re-read them for thesis #2.
F. If DRY_STREAK ≥ 3, OR leads are exhausted, OR the time is past ~09:30 local on 2026-10-07 with at least 4 waves done → FINAL (below).

## FINAL: the research memo
Load the `artifact-design` skill first. Write the memo in the user's readable style (plain English, bottom line first, each idea = one plain sentence, then context, then a few bullets; at most one short quote per idea; acronyms defined; tables trimmed, with a one-line "what this shows"; no internal tags like NEW/BURIED/D/E/X). Save it at THESIS_SCRAPE\DKS_thesis_memo.html. Structure:
1. Bottom line (both theses, the variance in one line each, the smoking gun in one line each).
2. Consensus base line (Bloomberg, pulled 2026-10-04).
3. Thesis #1 HoS/FH: the claim; why consensus is wrong; the variance (comp bps vs consensus revenue, margin bps vs consensus margin → $/share, arithmetic shown, labelled as our estimate); THE SMOKING GUN (boxed); supporting evidence ranked (number, period, source link); charts of any time series; what cuts against it.
4. Thesis #2: same structure, plus one paragraph on why it was chosen over the other candidates.
5. How to keep tracking it (repeatable data sources and scripts).
6. Appendix: all findings, with sources.
Publish via the Artifact tool (icon "chart", title "DKS Long Thesis Memo"). Save the URL in STATE.md, set `STATUS: DONE`, delete the scheduled task `dks-thesis-scrape-watchdog` and any session cron, and send a PushNotification with the link. Also add a memory file (project type) recording the run and the URL.
