function [prog,Vdual,Mlower,W,Z,U] = qc_Mc_dual(prog,Theta,method,y,X0,epsilon)
%QC_MC_DUAL Convex sufficient dual parameterization with primal M in Mc.
% Theta is a FIXED invertible static factor, with invertible Theta22.
% The actual primal multiplier is Theta'*diag(inv(Z),-inv(W))*Theta.
% W,Z,U are raw polynomial decision matrices; no matrix inverse is optimized.
% X0 is a fixed SPD expansion matrix for the lower bound on inv(Z).
m = size(Theta,1)/2;
if nargin < 5, X0 = eye(m); end
if nargin < 6, epsilon = 1e-5; end
assert(isequal(size(Theta),[2*m 2*m]) && m==floor(m),'Theta must be square of even order.');
assert(rcond(Theta)>1e-12 && rcond(Theta(m+1:end,m+1:end))>1e-12, ...
    'Theta and Theta22 must be invertible.');
assert(isequal(size(X0),[m m]) && norm(X0-X0.','fro')<1e-12 ...
    && min(eig(X0))>0,'X0 must be symmetric positive definite.');

[prog,W] = sospolymatrixvar(prog,polynomial(1),[m m],'symmetric');
[prog,Z] = sospolymatrixvar(prog,polynomial(1),[m m],'symmetric');
[prog,U] = sospolymatrixvar(prog,polynomial(1),[m m],'symmetric');
prog = sosmatrixineq(prog,W-epsilon*eye(m));
prog = sosmatrixineq(prog,Z-epsilon*eye(m));
prog = sosmatrixineq(prog,[U eye(m);eye(m) W]); % U >= inv(W)

% inv(Z) >= 2*X0-X0*Z*X0. Hence actual M >= Mlower.
Mlower = Theta.'*[2*X0-X0*Z*X0 zeros(m);zeros(m) -U]*Theta;
for k = 0:2^m-1
    D = diag(2*bitget(k,1:m)-1);
    R = [D;(eye(m)+D)/2];
    Q = R.'*Mlower*R;
    switch method
        case 'matrix'
            prog = cop_matrix(prog,m,Q);
        case 'sos0'
            prog = cop_sos(prog,y(1:m),0,Q);
        case 'sos1'
            prog = cop_sos(prog,y(1:m),1,Q);
        otherwise
            error('Unknown COP method: %s',method);
    end
end

J = [zeros(m) eye(m);-eye(m) zeros(m)];
ThetaDual = (J.'*Theta.'*J)\eye(2*m);
Vdual = ThetaDual.'*[W zeros(m);zeros(m) -Z]*ThetaDual;
% The plant feedthrough and well-posedness conditions remain caller checks.
end
