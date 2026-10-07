"""X09: control batches to test whether the Apr-Jun 2026 Google Trends spike is real demand or a data artifact.
Rerun: python X09_run_controls.py
"""
from X09_gtrends import run_batches

B_month = {
    'ctl1': ['calia', 'sourdough starter', 'hoka', 'patagonia', 'carhartt'],
    'ctl2': ['calia', 'crochet pattern', 'tire pressure', 'costco membership', 'pizza hut'],
    'ctl3': ['maxfli', 'callaway', 'taylormade', 'golf balls', 'golf clubs'],
}
B_week = {
    'wk1': ['calia', 'maxfli', 'titleist pro v1', 'under armour', 'sourdough starter'],
    'wk2': ['calia', 'vrst', 'dsg leggings', 'dsg shorts', 'dsg jacket'],
}
if __name__ == '__main__':
    run_batches(B_month, '2021-01-01 2026-10-06', prefix='m_', pause=45)
    run_batches(B_week, '2025-01-01 2026-10-06', prefix='w_', pause=45)
