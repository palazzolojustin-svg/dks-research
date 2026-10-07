# ORCHESTRATOR PROCEDURE: DKS owned-brand overnight scrape
(For the main session, or any watchdog session that takes over. Working dir C:\Users\palaz\Downloads\DKS_RESEARCH. Everything lives in PB_SCRAPE\.)

## Files
- STATE.md: run status, wave table, heartbeat, dry-wave counter, Apify total. The orchestrator updates the heartbeat line every time it acts.
- AGENT_RULES.md + KNOWN_BRIEF.md: every sub-agent reads these first.
- PROMPTS_WAVE<N>.md: assignments per wave. wave<N>\<ID>.md: agent outputs (complete when the last line is `STATUS: COMPLETE`).
- LEDGER.md: consolidated, de-duplicated findings across waves (orchestrator maintains).
- APIFY_LEDGER.md: hard cap $25.

## Takeover check (watchdog / cron)
1. Read STATE.md. If `STATUS: DONE` → exit (the watchdog also deletes its own scheduled task `dks-pb-scrape-watchdog`).
2. If HEARTBEAT is < 75 min old, OR any file in PB_SCRAPE\wave*\ was modified < 60 min ago → another orchestrator/agents are alive → exit without action.
3. Otherwise take over: write a new HEARTBEAT with `owner: watchdog <time>`, then continue below.

## Loop
A. For the current wave: list agent IDs from STATE.md. Any ID whose output file is missing or lacks `STATUS: COMPLETE` and has not been modified for 60+ min → relaunch it (Agent tool, subagent_type general-purpose, run_in_background true). Use the prompt: "Read C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\AGENT_RULES.md and KNOWN_BRIEF.md first and follow them exactly. You are agent <ID>, wave <N>. Your assignment is section <ID> of PB_SCRAPE\PROMPTS_WAVE<N>.md. If PB_SCRAPE\wave<N>\<ID>.md already exists, it is your own partial work from a crashed run: read it, keep it, and continue from where it stopped." Max 20 agents concurrently.
B. When all agents in the wave are complete: consolidate into LEDGER.md. De-duplicate, keep only NEW/BURIED findings, grade them A (quantified, sourced, clearly supports acceleration/mix-up), B (supporting but qualitative or partial), C (weak), X (against). Spot-verify the top A findings by re-fetching the source.
C. Wave verdict: a wave is "productive" if it added ≥2 new A-grade findings, or ≥5 new B-grade ones. Otherwise it is "dry". Update DRY_STREAK in STATE.md (reset to 0 on a productive wave).
D. If DRY_STREAK < 3 and good leads remain → write PROMPTS_WAVE<N+1>.md (follow-ups on the strongest leads, deeper pulls on productive avenues, verification of A findings, new avenues from "Leads for next wave") and launch it. Wave 2 must also include working-notes sweep agents reading in full: (W01_DKS_10K_FY2024-FY2025.md + W02_DKS_10K_FY2022-FY2023.md + W09_DKS_ANNUAL_REPORTS_TO_SHAREHOLDERS.md), (W05_DKS_8K_PRESSRELEASES_A/B/C.md), (P_ASO_10K.md + P_ASO_10Q.md + P_ADIDAS_PUMA_ASO_FL_RESEARCH.md + W20_SECTOR_MACRO.md), (W03 + W04 10-Qs + W06 + W08).
E. If DRY_STREAK ≥ 3, or leads are exhausted → FINAL: build the artifact (below), set `STATUS: DONE` in STATE.md, delete the scheduled task `dks-pb-scrape-watchdog` (mcp__scheduled-tasks__delete_scheduled_task) and any session cron, then send a PushNotification.

## Final artifact
Load the `artifact-design` skill first. Build an easily readable HTML page at PB_SCRAPE\DKS_owned_brand_evidence.html, written in plain English with the bottom line first. Sections: bottom line (is there evidence owned-brand mix is accelerating, and how strong); modelling implication (a mix path vs the implied flat ~13%, GM bps and EPS effect, labelled as inference, with the arithmetic shown); the top evidence ranked (each with number, period, source link, confidence); charts of any time series (reviews, search, imports, catalog counts); evidence against; best scraping avenues ranked (how to rerun weekly, script paths); appendix of all findings. Publish via the Artifact tool (icon "chart"), then give the user the link. Save the URL into STATE.md.
