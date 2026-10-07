# DIGEST SPEC (stage 1): condense core notes into a digest section

ROOT = C:\Users\palaz\Downloads\DKS_RESEARCH
Purpose: CORE_NOTES/00_CORE_DIGEST.md will be read IN FULL by Claude at the start of every response in future research chats about DKS (Dick's Sporting Goods). It is the always-loaded layer; the full core notes and working notes are swept by agents afterwards. So the digest must carry the highest-value facts densely and point to where details live.

Your input: the core notes file(s) named in your prompt. Read each one in full (sequential Read chunks, line 1 to last line).
Your output: ROOT\_PREP\digest\<YOUR_ID>.md, target 18,000-30,000 characters (hard cap 35,000).

Content priorities (keep exact numbers, units, periods, dates; no rounding):
1. Financial trajectory: revenue, comps, GM, SG&A, op margin, EPS (GAAP and non-GAAP) by period; segment data (DICK'S banner vs Foot Locker); balance sheet/FCF/capex/buyback/dividend/leverage key figures.
2. Guidance: every guidance range and how it changed over time (date → old → new), with management's stated reasons.
3. Foot Locker deal: terms, price, financing, synergies, integration progress, FL profit/loss trajectory and guidance.
4. Street: rating/PT/EPS-estimate history by firm and date (compact table), consensus estimates, valuation methods/multiples, bull vs bear debate, catalysts, risks.
5. Management voice: the most decision-relevant verbatim quotes (short) with speaker/date.
6. Expert-call and alt-data signals: each expert's role and key quantified claims; alt data/survey/channel datapoints; insider buying; market data facts (price reactions, 52w range, etc.).
7. Contradictions between sources (flag them).
Format: dense bullets and compact pipe tables, finance shorthand, for a machine reader. After each fact or block add a pointer like `→C02B` (core file id) so a reader knows where full detail lives. Keep markers [d], [r], [sic] where relevant.
Do not add opinions. Do not modify any input file. Do not spawn sub-agents.
Final reply: output path + char count, ≤3 lines.
