function [prog,M] = qc_M3(prog,m)
%QC_M3 Repeated slope-restriction QC (paper, Eq. 6).
% Q3 is doubly hyperdominant; it need not be symmetric.
[prog,Q3] = sospolymatrixvar(prog,polynomial(1),[m m]);
for i = 1:m
    prog = sosineq(prog,sum(Q3(i,:),2));     % nonnegative row sum
    prog = sosineq(prog,sum(Q3(:,i),1));     % nonnegative column sum
    for j = 1:m
        if i ~= j
            prog = sosineq(prog,-Q3(i,j));  % nonpositive off-diagonal
        end
    end
end
M = [zeros(m) Q3.'; Q3 -(Q3+Q3.')];
end
