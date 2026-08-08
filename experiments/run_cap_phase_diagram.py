"""Generate the turnover-cap phase diagram."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from affine_diversification.affine_fibre import critical_pulled_scale, no_external_point_bounds

ROOT = Path(__file__).resolve().parents[1]
OUT, FIG, DATA = ROOT / "outputs", ROOT / "figures", ROOT / "figure_data"
for p in (OUT, FIG, DATA): p.mkdir(exist_ok=True)

TEAL = "#168C8C"; RASPBERRY = "#B23A6F"; VIOLET = "#6750A4"; SLATE = "#415A77"


def main() -> None:
    rho = 0.8
    x = np.linspace(1.0, 10.0, 700)
    lp = np.full_like(x, 0.2)
    caps = [(0.5, TEAL), (1.0, VIOLET), (1.2, RASPBERRY)]
    rows=[]
    plt.figure(figsize=(8.5, 5.2))
    for c, colour in caps:
        out = no_external_point_bounds(x, lp, rho=rho, turnover_cap=c)
        plot_width = np.minimum(out.width_factor, 30.0)
        plt.plot(x, plot_width, linewidth=2, color=colour, label=f"c={c:g} ({out.regime})")
        for xx, w, q, attained in zip(x, out.width_factor, out.q_infimum, out.lower_endpoint_attained):
            rows.append({"rho":rho,"turnover_cap":c,"x":float(xx),"width_factor":float(w),"q_infimum":float(q),"lower_attained":bool(attained)})
    xc = critical_pulled_scale(rho=rho, turnover_cap=1.2)
    plt.axvline(xc, color=SLATE, linestyle="--", linewidth=1.3, label=rf"$x_{{crit}}={xc:g}$ for c=1.2")
    plt.ylim(1, 30)
    plt.xlabel(r"Pulled scale $x=F(\tau)$")
    plt.ylabel("Pointwise multiplicative width (display capped at 30)")
    plt.title("Turnover-cap phase transition at c=1")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "figure7_turnover_cap_phase.png", dpi=220)
    plt.close()
    with (DATA / "figure7_turnover_cap_phase.csv").open("w", newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={"rho":rho,"supercritical_cap":1.2,"critical_pulled_scale":xc,"interpretation":"For c>1 the speciation supremum becomes infinite at and beyond xcrit; the zero survival-scale endpoint is an infimum, not an attained history."}
    (OUT / "turnover_cap_phase.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__": main()
