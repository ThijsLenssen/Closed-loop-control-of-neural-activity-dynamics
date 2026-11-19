function [prog,Q] = cop_matrix(prog,q,Q)
%COP_MATRIX Q=S+N, S positive semidefinite, N entrywise nonnegative.
% This sufficient condition for copositivity is also the SOS level K^0.
% Optional third input: constrain an existing symmetric matrix expression Q.
if nargin < 3
    [prog,Q] = sospolymatrixvar(prog,polynomial(1),[q q],'symmetric');
end
[prog,N] = sospolymatrixvar(prog,polynomial(1),[q q],'symmetric');
prog = sosmatrixineq(prog,Q-N);              % S = Q-N is PSD
for i = 1:q
    for j = i:q
        prog = sosineq(prog,N(i,j));         % scalar, NOT a PSD constraint
    end
end
end
