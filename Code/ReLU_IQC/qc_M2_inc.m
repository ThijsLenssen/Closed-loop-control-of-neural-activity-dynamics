function [prog,M] = qc_M2_inc(prog,m,coefficient)
%QC_M2_INC Pairwise incremental multipliers (Theorem 4).
% Each pair contributes (dv_i-dv_j)^2 + coefficient*dw_i*dw_j.
% The paper uses 2. The inequality remains valid up to the sharp value 4.
if nargin < 3, coefficient = 2; end
validateattributes(coefficient,{'numeric'},{'real','scalar','>=',0,'<=',4});
T = dpvar(zeros(m));
U = dpvar(zeros(m));
I = eye(m);
for i = 1:m-1
    for j = i+1:m
        [prog,weight] = sospolyvar(prog,polynomial(1));
        prog = sosineq(prog,weight);
        difference = I(:,i)-I(:,j);
        T = T + weight*(difference*difference.');
        U(i,j) = coefficient*weight/2;
        U(j,i) = U(i,j);
    end
end
M = [T zeros(m); zeros(m) U];
end
