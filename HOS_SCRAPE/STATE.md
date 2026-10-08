# STATE: House of Sport jobs + mall-loan scrape (HOS_SCRAPE)
STATUS: RUNNING (user "go" 2026-10-08)
Method: cost-conserving — Sonnet agents, ~40 tool calls each, scripts print compact tables, no watchdog routine.
Wave 1: 20 agents J01-J15 (jobs, HoS only, other job sources), M01-M05 (EDGAR CMBS HoS sales; M05 = Foot Locker store sales, separate section).
Later waves: 6-10 agents from leads. If EDGAR mall-loan search finds nothing new → rating-agency presale reports (KBRA/Moody's/Fitch), servicer reports, mall REIT disclosures, Trepp/CRED iQ.
Stop: 2 consecutive dry waves (dry = <2 new A and <4 new B).
Output: summary Artifact (HoS store productivity) + FL section + appendix of all existing evidence (34 QCEW events, 22 CMBS stores, Tampa/Empire/Washington Square/Ridgedale).
Raw from earlier run: THESIS_SCRAPE/raw/*.csv (B5/B8/B9/B10/H04/H07) streamed from release raw-data.

## Wave log
