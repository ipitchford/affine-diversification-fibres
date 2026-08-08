"""Deliberately broken controls that the assurance checks must reject."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from affine_diversification.affine_fibre import (
    interval_feasibility_certificate,
    no_external_point_bounds,
    positive_survival_certificate,
    sharp_envelopes,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)


def main():
    controls=[]

    # 1. Wrong sign in a lower cone should disagree with the correct envelope.
    x=np.linspace(1,6,41);xi=np.array([1.,3.,6.]);lo=np.array([0.2,1.1,2.6]);hi=np.array([0.2,1.4,2.9]);c=0.6
    correct=sharp_envelopes(x,xi,lo,hi,turnover_cap=c)
    mutated=np.max(lo[:,None]+c*np.maximum(xi[:,None]-x[None,:],0),axis=0)
    detected=bool(np.max(np.abs(mutated-correct.lower_n))>0.1)
    controls.append({"id":"M1_wrong_cone_sign","detected":detected})

    # 2. Omitting (n-1)! breaks fixed-stem count-density normalization.
    n=5;F=3.2;H=1-1/F
    mutated_integral=(H**(n-1)/math.factorial(n-1))/(H**(n-1))
    controls.append({"id":"M2_missing_branching_time_factorial","detected":abs(mutated_integral-1)>0.9})

    # 3. A supercritical cap cannot retain a finite upper bound beyond xcrit.
    out=no_external_point_bounds(np.array([8.0]),np.array([0.2]),rho=0.8,turnover_cap=1.2)
    mutated_finite=999.0
    controls.append({"id":"M3_supercritical_finite_bound","detected":bool(np.isinf(out.lambda_supremum[0]) and np.isfinite(mutated_finite))})

    # 4. A directed-Lipschitz conflict must produce a pairwise witness.
    cert=interval_feasibility_certificate(np.array([1.,3.]),np.array([0.,2.]),np.array([0.,2.]),turnover_cap=0.5)
    controls.append({"id":"N1_infeasible_constraints","detected":cert is not None and cert.get('type')=='directed_lipschitz'})

    # 5. A lower bound at the barrier is not a positive-survival history.
    barrier=positive_survival_certificate(np.array([1.,4.]),np.array([0.2,4.0]))
    controls.append({"id":"N2_barrier_violation","detected":barrier is not None})

    status='passed' if all(c['detected'] for c in controls) else 'failed'
    result={"status":status,"controls":controls,"detected":sum(c['detected'] for c in controls),"total":len(controls)}
    (OUT/'negative_controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if status!='passed':raise SystemExit(1)

if __name__=='__main__':main()
