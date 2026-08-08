"""Independent, loop-based reference formulas used only for verification."""
from __future__ import annotations

import numpy as np


def lower_envelope(evaluation_x, constraint_x, lower_n, cap):
    out=[]
    for x in evaluation_x:
        out.append(max(float(l)-cap*max(float(xi)-float(x),0.0) for xi,l in zip(constraint_x,lower_n)))
    return np.asarray(out)


def upper_envelope(evaluation_x, constraint_x, upper_n, cap):
    out=[]
    for x in evaluation_x:
        out.append(min(float(u)+cap*max(float(x)-float(xi),0.0) for xi,u in zip(constraint_x,upper_n)))
    return np.asarray(out)


def pairwise_feasible(constraint_x, lower_n, upper_n, cap, tol=1e-12):
    for i,(xi,li) in enumerate(zip(constraint_x,lower_n)):
        for j,(xj,uj) in enumerate(zip(constraint_x,upper_n)):
            if li > uj + cap*max(xi-xj,0.0) + tol:
                return False,(i,j)
    return True,None
