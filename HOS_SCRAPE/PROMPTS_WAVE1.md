# Wave 1 assignments (20 agents). Read AGENT_RULES.md first. Output HOS_SCRAPE/wave1/<ID>.md.
Note: THESIS_SCRAPE/raw now holds B5_hos_events.csv, B5_event_summary.csv, B5_NY_sporting_latest.csv, B5_CO_naics459_cities.csv (NY/CO state data was partly used), B8_cmbs_store_panel.csv, B9_*.csv, B10_*.csv, H04_*.csv, H07_*.csv.

## Jobs (HoS only; other job sources)
- J01 HoS MASTER LIST: build HOS_SCRAPE/data/J01_hos_master.csv of every House of Sport opened or announced (store #, mall/center, city, county FIPS, open date, type relocation/net-new/conversion, replaced store #), from B5_hos_events.csv, THESIS_SCRAPE H02/B9, DKS store locator pages and news. Flag which are in the 34 QCEW events and which are missing/after 2026Q1. Others will use it; finish fast (≤25 calls), then use remaining budget to spot data gaps.
- J02 STATE LMI DATA: state labor-market sources faster or finer than QCEW (state QCEW/ES-202 portals with 2026Q2 county or city data, state CES metro sporting-goods series, state "new hires" or UI establishment data, Census QWI by county × NAICS 4511/4591). Target counties of HoS opened 2025Q3-2026Q3 and the 2 dropped events. Skip NY/CO county work already in B5 unless you extend it to newer quarters.
- J03 QCEW EXTENSIONS: for HoS opened 2025Q3-2026Q1 that have only k=0 or k=1 in B5, pull monthly employment (month1/2/3) from QCEW 2026Q1 and any 2026Q2 preliminary release; also NAICS 459110 establishment counts and size changes. Report per-store jobs increments and implied sales ($215K/$70K).
- J04 CAREERS POSTINGS, cohort 2021-2023 openings: Wayback snapshots of DICK'S careers pages (jobs.dickssportinggoods.com and any ATS host such as Workday/iCIMS/Avature) filtered to each HoS store/city; count postings in the 6 months before and after opening; compare to the legacy store it replaced where possible.
- J05 CAREERS POSTINGS, cohort 2024 openings (same method).
- J06 CAREERS POSTINGS, cohort 2025 openings (same method).
- J07 CAREERS POSTINGS, cohort 2026 openings + 2027 pipeline (live careers site today + Wayback): hiring for upcoming HoS (headcount targets, "hiring event" pages).
- J08 JOB BOARDS: Indeed/LinkedIn/Glassdoor/ZipRecruiter/SimplyHired public pages (live + Wayback/Common Crawl) for "DICK'S House of Sport" by city: posting counts by month, roles (store size signal), any stated headcount.
- J09 LOCAL NEWS HIRING, stores A-L by city: news/TV/press-release statements of HoS hiring ("hiring 150 teammates", job fairs), opening-day staffing, store size; compare to replaced store headcount.
- J10 LOCAL NEWS HIRING, stores M-Z by city (same method).
- J11 INCENTIVE / ECONOMIC-DEVELOPMENT FILINGS: city council/county minutes, TIF/abatement/PILOT agreements, state incentive databases (e.g. Good Jobs First Subsidy Tracker, state EDC reports) with HoS job-creation commitments, payroll, projected sales or sales-tax.
- J12 $/JOB CALIBRATION: find stores (HoS or large DKS) where both headcount and sales are publicly known (municipal sales-tax by vendor, CMBS sales + news headcount, Bass Pro/Scheels analogs) to pin $/job between $70K and $215K. Show each calibration point.
- J13 NET-JOBS CHECK: WARN notices, closures and transfers of the legacy DKS stores replaced by HoS (staff moved vs cut), to turn gross HoS hiring into net jobs.
- J14 CENSUS ESTABLISHMENT-SIZE DATA: Census County Business Patterns / ZIP Business Patterns (latest years, API api.census.gov) for NAICS 451110/459110 by ZIP or county: appearance of a 100-249 or 250-499 employee establishment in HoS ZIPs after opening (2021-2024 openings); also Nonemployer/Business Dynamics if useful.
- J15 OTHER JOB SIGNALS: LinkedIn/Glassdoor store-level employee counts ("Dick's House of Sport <city>" employees), Indeed company reviews by location, Reddit/TikTok staff posts about HoS staffing levels; quantify where possible.

## Mall loans (HoS only, SEC EDGAR CMBS first; FL store sales in a separate section)
- M01 EDGAR FTS phrase sweep: "House of Sport", "DICK'S House of Sport", "Dick's Sporting Goods House of Sport" across all forms 2021-2026 (with and without forms filter; handle HTTP 500). Compare with B9_fts_HOS*.csv / B10 hits; fetch only NEW accessions; extract HoS sales, rent, underwriting, sales psf, lease dates.
- M02 EDGAR FTS by HoS center names, first half of J01's/B5's store list (alphabetical by mall): each mall/center name + "Dick's" → new CMBS deals (SASB/conduit 424B2/424H/FWP, also 10-D exhibits). Extract HoS sales.
- M03 same as M02 for the second half of the list.
- M04 NEW CMBS DEALS since 2026-07: any CMBS prospectus/FWP filed Jul-Oct 2026 (EDGAR daily index or FTS "Dick's Sporting Goods" with recent dates) not in the B8/B9/B10 cache; extract DKS HoS sales; also any DKS legacy-store sales that serve as the replaced-store base for an HoS.
- M05 FOOT LOCKER STORE SALES in CMBS: FTS "Foot Locker" / "Champs Sports" / "Kids Foot Locker" + "sales" in CMBS prospectuses 2019-2026; build a store panel (store, mall, year, sales, sales psf) and y/y for the latest deals (2025-2026 underwriting) vs earlier; note occupancy cost and lease terms. This feeds the separate FL section.
