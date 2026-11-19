function [prog,Vdual,K,M12] = qc_M12_dual(prog,M0,method,y,epsilon)
%QC_M12_DUAL Convex step for primal M1+M2 membership on the dual side.
% M0 is a fixed symmetric, nonsingular primal expansion matrix. Its inverse
% must have m positive and m negative eigenvalues and positive leading block.
% K is the free symmetric inverse primal multiplier. Recover M with K\I.
m = size(M0,1)/2;
I = eye(m);
Iall = eye(2*m);
K0 = M0\Iall;
K0 = (K0+K0.')/2;
K011 = K0(1:m,1:m);
S = [-(K011\K0(1:m,m+1:end)); I];
assert(min(eig(K011))>0 && max(eig(S.'*K0*S))<0, ...
    'The expansion matrix must satisfy the stated inertia and block conditions.');

[prog,K] = sospolymatrixvar(prog,polynomial(1),[2*m 2*m],'symmetric');
[prog,M1] = qc_M1(prog,m);
[prog,M2] = qc_M2(prog,m,method,y);
M12 = M1+M2;

% K is positive on the first m coordinates and negative on range(S).
W = -S.'*K*S;
prog = sosmatrixineq(prog,K(1:m,1:m)-epsilon*I);
prog = sosmatrixineq(prog,W-epsilon*I);

% K^-1 >= 2*M0-M0*K*M0 - F*inv(W)*F', with F=(I-M0*K)*S.
% A Schur complement puts M12 below this lower bound, so K^-1 is
% M12 plus a PSD matrix. M2 already contains every PSD matrix.
F = (Iall-M0*K)*S;
lower = 2*M0-M0*K*M0-M12;
prog = sosmatrixineq(prog,[lower F;F.' W]);

J = [zeros(m) I;-I zeros(m)];
Vdual = -J.'*K*J;
end
