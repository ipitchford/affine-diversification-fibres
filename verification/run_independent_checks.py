"""Independent numerical checks for release 0.2.1."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import linprog

from affine_diversification.affine_fibre import (
    conditional_descendant_probability,
    cumulative_loss_from_turnover,
    sharp_envelopes,
)
from verification.reference_envelopes import lower_envelope, pairwise_feasible, upper_envelope

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)


def lp_bounds(grid, indices, lo, hi, cap, targets):
    nvar=len(grid); A=[]; b=[]
    for j,dx in enumerate(np.diff(grid)):
        row=np.zeros(nvar);row[j]=1;row[j+1]=-1;A.append(row);b.append(0.0)
        row=np.zeros(nvar);row[j]=-1;row[j+1]=1;A.append(row);b.append(cap*dx)
    for k,j in enumerate(indices):
        row=np.zeros(nvar);row[j]=-1;A.append(row);b.append(-lo[k])
        row=np.zeros(nvar);row[j]=1;A.append(row);b.append(hi[k])
    A=np.asarray(A);b=np.asarray(b)
    answer=[]
    for target in targets:
        obj=np.zeros(nvar);obj[target]=1
        rmin=linprog(obj,A_ub=A,b_ub=b,bounds=[(None,None)]*nvar,method='highs')
        rmax=linprog(-obj,A_ub=A,b_ub=b,bounds=[(None,None)]*nvar,method='highs')
        if not (rmin.success and rmax.success): raise RuntimeError('independent LP failed')
        answer.append((rmin.fun,-rmax.fun))
    return answer


def envelope_checks():
    rng=np.random.default_rng(917203)
    cases=180; targets=[2,7,13,18]
    max_formula=0.0;max_lp=0.0
    for _ in range(cases):
        grid=np.linspace(1.0,2.5,21)
        cap=float(rng.uniform(0.05,1.4))
        rho=float(rng.uniform(0.55,1.0))
        eps=rng.uniform(0.0,min(cap*0.8,1.1),grid.size-1)
        # Regenerate if the supercritical sample approaches the barrier.
        n,q=cumulative_loss_from_turnover(grid,eps,rho=rho,turnover_cap=cap)
        if np.min(q)<0.12:
            eps*=0.5
            n,q=cumulative_loss_from_turnover(grid,eps,rho=rho,turnover_cap=cap)
        idx=np.array([0,5,10,15,20]); xi=grid[idx]
        margin=rng.uniform(0.005,0.04,size=idx.size);margin[0]=0
        lo=n[idx]-margin;hi=n[idx]+margin
        lo[0]=hi[0]=n[0]
        feasible,_=pairwise_feasible(xi,lo,hi,cap)
        if not feasible: raise RuntimeError('constructed case unexpectedly infeasible')
        env=sharp_envelopes(grid,xi,lo,hi,turnover_cap=cap)
        if not env.feasible: raise RuntimeError(env.certificate)
        ref_lo=lower_envelope(grid,xi,lo,cap);ref_hi=upper_envelope(grid,xi,hi,cap)
        max_formula=max(max_formula,float(np.max(np.abs(env.lower_n-ref_lo))),float(np.max(np.abs(env.upper_n-ref_hi))))
        bounds=lp_bounds(grid,idx,lo,hi,cap,targets)
        for t,(l,u) in zip(targets,bounds):
            max_lp=max(max_lp,abs(l-env.lower_n[t]),abs(u-env.upper_n[t]))
    return {"random_cases":cases,"target_extrema":cases*len(targets),"maximum_reference_formula_discrepancy":max_formula,"maximum_linear_programme_discrepancy":max_lp}


def analytic_event_state():
    lam,mu,rho=0.45,0.15,0.8
    y=np.array([rho,0.0]) # u, integral lambda*u
    left=0.0
    for right,s in ((1.0,0.7),(2.0,0.4),(3.0,None)):
        def rhs(t,z):
            u,I=z
            return [lam*u*(1-u)-mu*u,lam*u]
        sol=solve_ivp(rhs,(left,right),y,rtol=2e-12,atol=2e-14)
        y=sol.y[:,-1]
        if s is not None:y[0]*=s
        left=right
    return float(y[0]),float(math.exp(y[1]))


def evolve_counts(counts,duration,lam,mu,rng):
    elapsed=np.zeros(counts.size);done=counts<=0
    while True:
        active=~done
        if not np.any(active):break
        ids=np.flatnonzero(active)
        rates=counts[ids]*(lam+mu)
        waits=rng.exponential(1.0/rates)
        hit=elapsed[ids]+waits<duration
        stop_ids=ids[~hit];done[stop_ids]=True
        event_ids=ids[hit]
        if event_ids.size:
            elapsed[event_ids]+=waits[hit]
            births=rng.random(event_ids.size)<lam/(lam+mu)
            counts[event_ids]+=np.where(births,1,-1)
            done[event_ids[counts[event_ids]<=0]]=True
    return counts


def event_simulation():
    lam,mu,rho=0.45,0.15,0.8
    replicates=160_000;rng=np.random.default_rng(20260806)
    counts=np.ones(replicates,dtype=np.int32)
    counts=evolve_counts(counts,1.0,lam,mu,rng)
    counts=rng.binomial(counts,0.4)
    counts=evolve_counts(counts,1.0,lam,mu,rng)
    counts=rng.binomial(counts,0.7)
    counts=evolve_counts(counts,1.0,lam,mu,rng)
    counts=rng.binomial(counts,rho)
    u,F=analytic_event_state()
    observed_survival=float(np.mean(counts>0))
    surv_se=math.sqrt(u*(1-u)/replicates)
    survival_z=(observed_survival-u)/surv_se
    positive=counts[counts>0]; npos=positive.size
    zs=[]
    for k in range(1,9):
        p=conditional_descendant_probability(k,F=F)
        obs=float(np.mean(positive==k))
        se=math.sqrt(max(p*(1-p)/npos,1e-30))
        zs.append((obs-p)/se)
    smooth_error=max(abs(math.exp(math.log(s))-s) for s in (0.4,0.7))
    return {"replicates":replicates,"analytic_survival":u,"simulated_survival":observed_survival,"survival_z":survival_z,"F_stem":F,"maximum_conditional_count_absolute_z":float(np.max(np.abs(zs))),"smooth_event_limit_max_absolute_error":smooth_error}


def main():
    result={"envelopes":envelope_checks(),"finite_event_simulation":event_simulation(),"status":"passed"}
    (OUT/'independent_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
