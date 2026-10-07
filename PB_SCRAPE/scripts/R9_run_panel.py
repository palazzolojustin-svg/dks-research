"""R9 runner: python R9_run_panel.py [AB|G]  -> runs R9_panel_analyze for the chosen panels.
AB = dicks.com panels (outputs raw/R9_panel_*.csv); G = golfgalaxy.com panel (raw/R9_panel_*_G.csv)."""
import sys
which = sys.argv[1] if len(sys.argv) > 1 else "AB"
sys.argv = ["x"]
import R9_panel_analyze as M
M.PANELS = {k: v for k, v in M.PANELS.items() if k in which}
M.OUT_SUFFIX = "" if which == "AB" else "_" + which
M.main()
