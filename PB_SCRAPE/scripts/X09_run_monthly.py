"""X09: run the full set of monthly (2021-01 -> 2026-10) US Google Trends batches.
Rerun: python X09_run_monthly.py   (skips batches whose CSV already exists; delete raw/X09_gt_m_*.csv to refresh)
Anchors: 'calia' in apparel batches, 'maxfli' in golf batches, 'dicks sporting goods' links both.
"""
from X09_gtrends import run_batches

TF = '2021-01-01 2026-10-06'
B = {
    'app1': ['calia', 'vrst', 'dsg leggings', 'dsg joggers', 'dsg jacket'],
    'app2': ['calia', 'calia leggings', 'vrst shorts', 'dsg shorts', 'dsg hoodie'],
    'golf1': ['maxfli', 'maxfli golf balls', 'maxfli tour', 'walter hagen golf', 'titleist pro v1'],
    'golf2': ['maxfli', 'top flite', 'tommy armour', 'kirkland golf balls', 'vice golf'],
    'bench1': ['calia', 'vuori', 'nike leggings', 'under armour', 'lululemon'],
    'link1': ['calia', 'maxfli', 'dicks sporting goods', 'dicks sporting goods brand', 'golf galaxy'],
    'other1': ['calia', 'alpine design', 'nishiki bike', 'quest canopy', 'fitness gear'],
    'dupe1': ['calia', 'lululemon dupe', 'dsg dupe', 'dicks dupe', 'align dupe'],
}
if __name__ == '__main__':
    run_batches(B, TF, prefix='m_', pause=45)
