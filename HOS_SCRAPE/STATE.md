# STATE: House of Sport jobs + mall-loan scrape (HOS_SCRAPE)
STATUS: DONE 2026-10-08 — memo https://claude.ai/artifact/7MMyjjEkp5MrF5rueWHjDJ (wave 2 dry; mall loans dry x2)
Method: cost-conserving — Sonnet agents, ~40 tool calls each, scripts print compact tables, no watchdog routine.
Wave 1: 20 agents J01-J15 (jobs, HoS only, other job sources), M01-M05 (EDGAR CMBS HoS sales; M05 = Foot Locker store sales, separate section).
Later waves: 6-10 agents from leads. If EDGAR mall-loan search finds nothing new → rating-agency presale reports (KBRA/Moody's/Fitch), servicer reports, mall REIT disclosures, Trepp/CRED iQ.
Stop: 2 consecutive dry waves (dry = <2 new A and <4 new B).
Output: summary Artifact (HoS store productivity) + FL section + appendix of all existing evidence (34 QCEW events, 22 CMBS stores, Tampa/Empire/Washington Square/Ridgedale).
Raw from earlier run: THESIS_SCRAPE/raw/*.csv (B5/B8/B9/B10/H04/H07) streamed from release raw-data.

## Wave log
- 2026-10-08: user said credits too fast. Stopped J04-J09 (low yield/heavy). Kept J02, J13, M01, M03, M05. Plan: no big wave 2; at most 3-4 targeted agents (Haiku/Sonnet, ~25 calls), then memo. Orchestrator stays terse.
- Wave 1 done: jobs PRODUCTIVE (new B: QWI Kennesaw/Freehold/Leawood/Live Oak; QCEW monthly Jersey City/Polaris/Freehold/Live Oak; calibration $155-210K/head; relocation vs net-new split; Davenport 120; Knoxville plan). Mall loans DRY (M01-M04 EDGAR) and DRY again (M06 non-EDGAR). FL: Northwoods + Prince George's FL sales flat/down 2025.
- Wave 2 (small): K1 QWI large-firm cut, K2 opening headcounts. If both dry → memo.
