"""X01: monthly ALL-BRAND review totals per dicks.com category (denominator for owned-brand share).

Uses the Bazaarvoice front-door API (see X01_bv_reviews.py docstring). reviews.json accepts a single
CategoryAncestorId EQ filter plus SubmissionTime range filters; Limit=1 and read TotalResults.
Two variants per category-month: ALL native reviews, and PIE = CampaignId ESP_PIE_INCENTIVE
(DSG's post-purchase incentive email = purchase-triggered, the cleanest unit proxy).
Output: raw/X01_category_month_totals_<client>.csv (category, month, variant, total)
RERUN: python X01_bv_category_totals.py dsg   (golfgalaxy also works with its own category ids)
"""
import csv, os, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW

CATS = {"dsg": ["WomensApparel-129841", "MensApparel-129824", "Apparel-129823", "Golf-129239", "GolfBalls-129255",
                "GolfClubs-132413", "GolfAccessories-129273", "WomensPantsTightsCapris-129846", "WomensShirtsTops-129842",
                "MensShirtsTops-129825", "MensShorts-129829", "MensPants-129830", "WomensShorts-129845",
                "WomensSwimsuits-129848", "BoysApparel-129859", "girls-apparel-footwear", "Socks-129981", "Hats-129973",
                "ExerciseFitness-128988", "Weights-131314", "CampingHiking-128904", "BikesCycling-128852",
                "Outdoor-236211", "ShopBySport-128771", "Baseball-128772", "WomensSportsBras-129849",
                "MensHoodiesSweatshirts-129827", "WomensHoodiesSweatshirts-129843", "WomensJacketsVests-129844"]}


def months(start=(2023, 1), end=None):
    y, m = start
    end = end or (datetime_now().year, datetime_now().month)
    out = []
    while (y, m) <= end:
        a = int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp())
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        b = int(dt.datetime(ny, nm, 1, tzinfo=dt.timezone.utc).timestamp())
        out.append((f"{y}-{m:02d}", a, b))
        y, m = ny, nm
    return out


def datetime_now():
    return dt.datetime.now(dt.timezone.utc)


def main(client, cats=None):
    s = session_for(client)
    cats = cats or CATS[client]
    jobs = [(c, mo, a, b, v) for c in cats for (mo, a, b) in months() for v in ("ALL", "PIE")]
    path = os.path.join(RAW, f"X01_category_month_totals_{client}.csv")
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            done = {(r["category"], r["month"], r["variant"]) for r in csv.DictReader(f)}
    jobs = [j for j in jobs if (j[0], j[1], j[4]) not in done]
    new = not os.path.exists(path)
    f = open(path, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["category", "month", "variant", "total"])

    def q(j):
        c, mo, a, b, v = j
        p = [("Filter", f"CategoryAncestorId:eq:{c}"), ("Filter", f"SubmissionTime:gte:{a}"),
             ("Filter", f"SubmissionTime:lt:{b}"), ("Limit", "1")]
        if v == "PIE":
            p.append(("Filter", "CampaignId:eq:ESP_PIE_INCENTIVE"))
        r = get(s, client, "reviews", p)
        return c, mo, v, r.get("TotalResults")
    with ThreadPoolExecutor(6) as ex:
        for i, row in enumerate(ex.map(q, jobs)):
            if row[3] is not None:
                w.writerow(row)
            if i % 100 == 0:
                f.flush(); print(i, len(jobs), flush=True)
    f.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or None)
