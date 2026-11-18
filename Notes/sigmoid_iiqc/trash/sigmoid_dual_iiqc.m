function iqc = sigmoid_dual_iiqc(rho,pole,order,directRatio,pairWeights)
%SIGMOID_DUAL_IIQC Dual-first square factors for paired sigmoid increments.
%   iqc = sigmoid_dual_iiqc(0.95,100,10); % Strictly proper H is allowed.
%   iqc = sigmoid_dual_iiqc([0.9 0.95],100,10,0,[1 2]);
%
% Define the DUAL factor first:
%   underline(Theta_Delta) = [I -H;0 I],
%   underline(N_Delta) = diag(W*inv(E),-W),
%   H = blockdiag(rho(j)*R)*((directRatio*s+pole)/(s+pole))^order,
%   R=[1 1;-1 0], E=diag(kron((1-rho).^2/8,[1;1])),
%   W=diag(kron(pairWeights,[1;1])).
%
% Recover the PRIMAL factor with the paper's map D(Theta):
%   Theta_Delta = boldD(underline(Theta_Delta)) = [I -Hprime;0 I],
%   N_Delta = -boldD(underline(N_Delta)) = diag(inv(W),-E*inv(W)).
% N_Delta is the paper's calligraphic N_Delta; its positive blocks are
% X_Delta=inv(W) and Y_Delta=E*inv(W). Dual quantities are UNDERLINED.
% Here Hprime is the CAUSAL LTI dual (A',C',B',D'), not the
% generally anticausal Hilbert-space adjoint on the half-line.
% The primal factor acts on [z_Delta;w_Delta], where
% z_Delta=q-qtilde and w_Delta=F(q)-F(qtilde).
%
% Theta_Delta, underline(Theta_Delta) and their 22 blocks have stable
% causal inverses independently of invertibility of H.
% Theta_Delta,21*P+Theta_Delta,22 = I.
% Proposition 1 in multipliers.tex and dual_first.md proves hardness.
%
% iqc.dual: use A,B,C,D,M in the dual analysis/synthesis inequality.
% iqc.primal: use A,B,C,D,M for primal uncertainty admissibility.
% Pair weights are positive scalar weights per STN/GPe pair. With the
% filters fixed, the dual weight matrix is affine in these weights.
% No toolbox is required to construct the numeric realizations.

if nargin<1, rho=0.95; end
if nargin<2, pole=100; end
if nargin<3, order=10; end
if nargin<4, directRatio=0; end
rho=rho(:);
if nargin<5, pairWeights=ones(size(rho)); end
if isscalar(pairWeights), pairWeights=repmat(pairWeights,size(rho)); end
pairWeights=pairWeights(:);
validateattributes(rho,{'numeric'},{'real','finite','vector','nonempty','>',0,'<',1});
validateattributes(pole,{'numeric'},{'real','finite','scalar','positive'});
validateattributes(order,{'numeric'},{'real','finite','scalar','integer','positive'});
validateattributes(directRatio,{'numeric'},{'real','finite','scalar','>=',0,'<',1});
validateattributes(pairWeights,{'numeric'},{'real','finite','vector','positive','numel',numel(rho)});
m=2*numel(rho);
R=[1 1;-1 0];
iqc.H=lead_lag_cascade(directRatio,pole,order,kron(diag(rho),R));
iqc.Hprime=lti_dual(iqc.H);
iqc.eta=kron((1-rho).^2/8,ones(2,1));
weights=kron(pairWeights,ones(2,1));

% Choose underline(Theta_Delta), then recover Theta_Delta via boldD.
iqc.dual=triangular_factor(iqc.H,-1);
iqc.dual.M=blkdiag(diag(weights./iqc.eta),-diag(weights));
iqc.primal=triangular_factor(iqc.Hprime,-1);
iqc.primal.M=blkdiag(diag(1./weights),-diag(iqc.eta./weights));
iqc.dualInverse=triangular_factor(iqc.H,1);
iqc.primalInverse=triangular_factor(iqc.Hprime,1);
% Named fields follow the supplied paper; legacy descriptive aliases remain.
iqc.Theta_Delta=iqc.primal;
iqc.N_Delta=iqc.primal.M;
iqc.Theta_Delta_underlined=iqc.dual;
iqc.N_Delta_underlined=iqc.dual.M;
iqc.X_Delta=diag(1./weights);
iqc.Y_Delta=diag(iqc.eta./weights);
iqc.rho=rho;
iqc.pole=pole;
iqc.order=order;
iqc.directRatio=directRatio;
iqc.pairWeights=pairWeights;
iqc.channels=m;
iqc.J=[zeros(m),eye(m);-eye(m),zeros(m)];
iqc.hatJ=iqc.J;
iqc.primal22=eye(m);
iqc.dual22=eye(m);
iqc.inputCoordinateIsIdentity=true;
iqc.primalInputOrdering='[z_Delta;w_Delta]=[q-qtilde;F(q)-F(qtilde)]';
end

function factor=triangular_factor(H,sign)
% [I sign*H;0 I]; the inverse has the opposite sign.
m=size(H.D,1);
n=size(H.A,1);
factor.A=H.A;
factor.B=[zeros(n,m),H.B];
factor.C=[sign*H.C;zeros(m,n)];
factor.D=[eye(m),sign*H.D;zeros(m),eye(m)];
factor.initialState=zeros(n,1);
end

function dual=lti_dual(system)
dual.A=system.A'; dual.B=system.C';
dual.C=system.B'; dual.D=system.D';
end

function system=lead_lag_cascade(d,p,order,mixing)
m=size(mixing,1); n=order*m;
system.A=-p*eye(n);
system.B=zeros(n,m); system.C=zeros(m,n);
for stage=1:order
    rows=(stage-1)*m+(1:m);
    system.B(rows,:)=p*d^(stage-1)*eye(m);
    system.C(:,rows)=(1-d)*d^(order-stage)*mixing;
    for previous=1:stage-1
        cols=(previous-1)*m+(1:m);
        system.A(rows,cols)=p*(1-d)*d^(stage-1-previous)*eye(m);
    end
end
system.D=d^order*mixing;
end
