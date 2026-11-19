function [prog,Q] = cop_sos(prog,y,r,Q)
%COP_SOS Parrilo's SOS inner approximation K^r of the copositive cone.
% Enforce (sum_i y_i^2)^r * (y.^2)'*Q*(y.^2) to be SOS.
% r=0: quartic, equivalent to PSD+nonnegative. r=1: sextic, larger cone.
% Optional fourth input: constrain an existing symmetric matrix expression Q.
q = length(y);
if nargin < 4
    [prog,Q] = sospolymatrixvar(prog,polynomial(1),[q q],'symmetric');
end
u = y.^2;
prog = sosineq(prog,sum(u)^r * (u.'*Q*u));
end
