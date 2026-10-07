# STATE: FL inventory-shift overnight scrape (FL_INVENTORY_SCRAPE)
STATUS: RUNNING
STARTED: 2026-10-07 ~21:10 UTC (user said "go")
CURRENT_WAVE: 0+1 (30 agents: F01-F15 folder sweep, W01-W15 web)
DRY_STREAK: 0 (stop after 2 consecutive dry waves; dry = <2 new A and <4 new B findings)
WATCHDOG: routine trig_01R4GrWXWepd17D2UtBM5txz (hourly at :41 UTC) fires into this session

## User requirements (verbatim intent)
- 30 agents; comprehensive web scrape of consumer data points + full scrape of the research folder.
- Thesis: FL is shifting its underlying inventory; the new inventory gets significantly higher consumer uptake and needs significantly less discounting.
- Then definitively show whether estimates reflect this in the timeline of the inventory shift, and quantify the variance vs FL segment consensus (FL comp, revenue, GM, OI), showing the gap to consensus.
- Focus only on Foot Locker. Decide the best scrape avenues.
- NOVEL data only (nothing already in the folder or found earlier).
- Stop after a couple of waves with no meaningful new evidence → summary Artifact with findings, plus old evidence as a bullet appendix at the bottom.

## Launch plan
Max 20 concurrent background agents. First launch: W01-W15 + F01-F05 (20). As slots free: F06-F15.

## Wave log
(wave | productive/dry | #A #B new | notes)
