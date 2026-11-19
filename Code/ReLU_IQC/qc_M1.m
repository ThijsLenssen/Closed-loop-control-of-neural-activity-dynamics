function [prog,M] = qc_M1(prog,m)
%QC_M1 Complementarity QC: 2*w'*Q1*(v-w) = 0 (paper, Eq. 3).
% Q1 is diagonal and its diagonal entries are unrestricted.
[prog,q] = sospolymatrixvar(prog,polynomial(1),[m 1]);
Q1 = dpvar(zeros(m));
for i = 1:m, Q1(i,i) = q(i); end
M = [zeros(m) Q1; Q1 -2*Q1];
end
