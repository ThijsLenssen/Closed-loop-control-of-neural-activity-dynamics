function [prog,M] = qc_M1_inc(prog,m)
%QC_M1_INC Diagonal incremental sector multipliers (Eq. 9).
[prog,t] = sospolymatrixvar(prog,polynomial(1),[m 1]);
T = dpvar(zeros(m));
for i = 1:m
    T(i,i) = t(i);
    prog = sosineq(prog,t(i));
end
M = [zeros(m) T; T -2*T];
end
