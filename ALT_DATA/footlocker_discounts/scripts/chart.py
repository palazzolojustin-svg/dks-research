"""Chart monthly Foot Locker discount metrics (output/monthly_metrics.csv + pages_per_month.csv)
-> output/fl_discount_chart.png. Months with < MIN_PAGES pages are left as gaps."""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "output"))
MIN_PAGES = 100
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
DEAL = "2025-09"  # DKS closed the Foot Locker acquisition 2025-09-08


def load():
    met = {}
    for r in csv.DictReader(open(os.path.join(OUT, "monthly_metrics.csv"))):
        if r["segment"] == "all":
            met[(r["region"], r["month"])] = r
    pages = {(r["region"], r["month"]): int(r["pages_with_products"])
             for r in csv.DictReader(open(os.path.join(OUT, "pages_per_month.csv")))}
    months = sorted({m for _, m in pages})
    return met, pages, months


def lab(m):
    import calendar
    y, mo = m.split("-")
    return "%s-%s" % (calendar.month_abbr[int(mo)], y[2:])


def main():
    met, pages, months = load()
    x = list(range(len(months)))
    fig, axes = plt.subplots(4, 1, figsize=(13, 10), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1, 3, 1]}, facecolor=SURF)
    for i, reg in enumerate(("NA", "EMEA")):
        ax, axp = axes[2 * i], axes[2 * i + 1]
        for a in (ax, axp):
            a.set_facecolor(SURF)
            for s in ("top", "right"):
                a.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                a.spines[s].set_color(GRID)
            a.tick_params(colors=INK2, labelsize=9)
            a.grid(axis="y", color=GRID, lw=0.8)
            a.set_axisbelow(True)
            if DEAL in months:
                a.axvline(months.index(DEAL), color=INK2, lw=1, ls=(0, (4, 3)))
        for key, color, name in (("pct_on_sale", BLUE, "% of products on sale"),
                                 ("avg_disc_all", ORANGE, "Avg discount, all products")):
            ys = [float(met[(reg, m)][key]) * 100 if (reg, m) in met and pages.get((reg, m), 0) >= MIN_PAGES
                  else float("nan") for m in months]
            ax.plot(x, ys, color=color, lw=2, marker="o", ms=5, label=name,
                    markeredgecolor=SURF, markeredgewidth=1.5)
            pts = [(xi, y) for xi, y in zip(x, ys) if y == y]
            for xi, y in pts:
                ax.annotate("%.0f%%" % y, (xi, y), textcoords="offset points", xytext=(0, 7),
                            ha="center", fontsize=7.5, color=INK2)
        ax.set_ylim(0, max([v for v in ax.get_ylim()[1:]] + [10]) * 1.22)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: "%d%%" % v))
        ax.set_title("Foot Locker %s" % ("North America (footlocker.com / .ca)" if reg == "NA"
                                         else "EMEA (European country sites)"),
                     loc="left", fontsize=12, color=INK, fontweight="bold")
        if i == 0:
            ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=2, labelcolor=INK)
            if DEAL in months:
                ax.annotate("DKS closes FL deal (Sep-25)", (months.index(DEAL), ax.get_ylim()[1]),
                            xytext=(4, -12), textcoords="offset points", fontsize=8, color=INK2)
        pv = [pages.get((reg, m), 0) for m in months]
        axp.bar(x, pv, color=["#9ec5f4" if v >= MIN_PAGES else GRID for v in pv], width=0.75)
        for xi, v in zip(x, pv):
            axp.annotate("{:,}".format(v), (xi, v), textcoords="offset points", xytext=(0, 2),
                         ha="center", fontsize=6.5, color=INK2)
        axp.set_ylabel("pages", fontsize=8, color=INK2)
        axp.set_ylim(0, max(pv + [1]) * 1.3)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels([lab(m) for m in months], rotation=45, ha="right")
    fig.text(0.01, 0.005, "Source: Common Crawl archives of Foot Locker category/listing pages; list vs. selling price "
             "per product, unique products per month. Months with <%d pages left blank. Discount = 1 - price/list."
             % MIN_PAGES, fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(os.path.join(OUT, "fl_discount_chart.png"), dpi=150, facecolor=SURF)
    print("wrote", os.path.join(OUT, "fl_discount_chart.png"))


if __name__ == "__main__":
    main()
