"""R9: batch ZipNum CDX lookups (no index server). Rerun: python R9_zipnum_batch.py
Edit JOBS for new crawls. Skips outputs that already exist."""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
G = ["CC-MAIN-2025-51", "CC-MAIN-2026-04", "CC-MAIN-2026-08", "CC-MAIN-2026-12", "CC-MAIN-2026-17", "CC-MAIN-2026-21",
     "CC-MAIN-2026-25", "CC-MAIN-2026-30", "CC-MAIN-2026-34", "CC-MAIN-2026-39"]
P = ["CC-MAIN-2025-33", "CC-MAIN-2025-38", "CC-MAIN-2025-43", "CC-MAIN-2025-47", "CC-MAIN-2025-51", "CC-MAIN-2026-04",
     "CC-MAIN-2026-17", "CC-MAIN-2026-25", "CC-MAIN-2026-34", "CC-MAIN-2026-39"]
C = ["CC-MAIN-2023-06", "CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10", "CC-MAIN-2024-30", "CC-MAIN-2025-33"]
JOBS = [(c, "com,golfgalaxy)/f/", "gg_f") for c in G] + [(c, "com,publiclands)/f/", "pl_f") for c in P] + \
       [(c, "com,calia)/", "calia_z") for c in C]
for c, pre, tag in JOBS:
    subprocess.run([sys.executable, os.path.join(HERE, "R9_cc_zipnum.py"), c, pre, tag])
