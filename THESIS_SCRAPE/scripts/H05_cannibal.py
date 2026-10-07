"""H05: cannibalisation check - legacy DSG listings near HoS that opened between Apr-Sep25 and Apr-Sep26 vs other legacy listings.
Rerun: python THESIS_SCRAPE/scripts/H05_cannibal.py (after H05_groups.py). Distances approximate (lat/lng from Google Maps).
"""
import csv
r = {x['placeId']: x for x in csv.DictReader(open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\H05_store_velocity.csv', encoding='utf-8'))}
near = {'ChIJ2T8s1_yfToYRJoccGhlFpak': 'Dallas N Central ~10km from Dallas HoS (9/25)', 'ChIJpa10zCRoK4cRgafgLR4kzpU': 'Arrowhead ~13km from Glendale AZ HoS (9/25)',
        'ChIJ6Wh992GKOIgRpSSDIowuBb0': 'Easton ~11km from Polaris HoS (8/25)', 'ChIJz5MLa3j6rIkRuvYNeR3P0Yo': 'Brier Creek ~20km from Durham HoS (10/25)',
        'ChIJqzvBaP6tw4kRxDkwUxhQp8M': 'Union NJ ~20km from Jersey City HoS (9/25)', 'ChIJoS7Bl-T6wokR3PcDhc_9crY': 'Paramus ~25km from Jersey City HoS',
        'ChIJw3ownRFewokR7h02leAcSTI': 'Glendale NY ~15km from Jersey City HoS', 'ChIJz0mczZDqwogRyd4HXBmDX7g': 'Citrus Park ~30km from Brandon HoS (11/25)',
        'ChIJQzvbL0-wwogRhVjS1BOglsA': 'Wesley Chapel ~35km from Brandon HoS'}
excl = {'ChIJoQK4GqTRNIgRT57dnDqpbt8', 'ChIJexFU3OuaQIYRZXB7k75C-ao', 'ChIJQzvbL0-wwogRhVjS1BOglsA', 'ChIJc4PDnFKv2YgRYvmmGYIPQfg'}
a = [0, 0]; b = [0, 0]
for p, x in r.items():
    if x['group'] != 'LEG' or p in excl:
        continue
    w25, w26 = int(x['W25']), int(x['W26'])
    if p in near:
        print('%-50s %3d -> %3d' % (near[p], w25, w26)); a[0] += w25; a[1] += w26
    else:
        b[0] += w25; b[1] += w26
print('near-new-HoS legacy %s y/y %+.0f%% | other legacy %s y/y %+.0f%%' % (a, (a[1] / a[0] - 1) * 100, b, (b[1] / b[0] - 1) * 100))
