function iqc = sigmoid_dynamic_iiqc(rho, pole, order, directRatio)
%SIGMOID_DYNAMIC_IIQC Linear, causal, rational, hard incremental IQC.
%   iqc = sigmoid_dynamic_iiqc(0.95, 100, 10);
%   iqc = sigmoid_dynamic_iiqc([0.9 0.95], 100, 10);
%   iqc = sigmoid_dynamic_iiqc(0.95, 100, 10, 0.5);
%
% Input to the IQC filter is [v;w], with v=q-qtilde and
% w=F(q)-F(qtilde). Each component of F must be slope restricted in
% [0,1], as for the PNAS STN/GPe sigmoids. Components are paired:
% [STN,GPe] or [plant STN,plant GPe,observer STN,observer GPe].
%
% H(s) = blockdiag(rho(j)*R) * ((directRatio*s+pole)/(s+pole))^order,
% R = [1 1;-1 0]. The filter output is [v-Hw; v; w], and
% M = diag(I,-E,-E), E=diag(kron((1-rho).^2/8,[1;1])).
% With ZERO filter initial state, integral_0^T output'*M*output >= 0
% for every T>=0. README.md gives the finite-horizon proof.
% Both H and H^{-1} are causal, proper and stable. The inverse has poles
% -pole/directRatio; its numeric realization is returned in iqc.Hinv.
%
% All matrices are numeric. Base MATLAB suffices. No Control System
% Toolbox, YALMIP, or SDP solver is required to construct the filter.
% rho, pole, order and directRatio are fixed library choices, not joint SDP
% variables. Nonnegative conic combinations of library entries are valid.

if nargin < 1, rho = 0.95; end
if nargin < 2, pole = 100; end
if nargin < 3, order = 10; end
if nargin < 4, directRatio = 0.5; end
validateattributes(rho, {'numeric'}, {'real','finite','vector','nonempty','>',0,'<',1});
validateattributes(pole, {'numeric'}, {'real','finite','scalar','positive'});
validateattributes(order, {'numeric'}, {'real','finite','scalar','integer','positive'});
validateattributes(directRatio, {'numeric'}, {'real','finite','scalar','>',0,'<',1});
rho = rho(:);
m = 2*numel(rho);
R = [1 1;-1 0];

% Each scalar stage is d+(1-d)*p/(s+p). Cascade realizations keep the
% state matrices triangular, including for the inverse, whose d exceeds 1.
H = lead_lag_cascade(directRatio,pole,order,kron(diag(rho),R));
Hinv = lead_lag_cascade(1/directRatio,pole/directRatio,order, ...
    kron(diag(1./rho),R\eye(2)));
n = size(H.A,1);

iqc.A = H.A;
iqc.B = [zeros(n,m),H.B];
iqc.C = [-H.C;zeros(2*m,n)];
iqc.D = [eye(m),-H.D;eye(m),zeros(m);zeros(m),eye(m)];
iqc.eta = kron((1-rho).^2/8,ones(2,1));
iqc.M = blkdiag(eye(m),-diag(iqc.eta),-diag(iqc.eta));
iqc.H = H;
iqc.Hinv = Hinv;
iqc.rho = rho;
iqc.pole = pole;
iqc.order = order;
iqc.directRatio = directRatio;
iqc.inversePole = pole/directRatio;
iqc.channels = m;
iqc.initialState = zeros(n,1);
iqc.inputOrdering = '[q-qtilde; F(q)-F(qtilde)]';
end

function system = lead_lag_cascade(d,p,order,mixing)
% (d+(1-d)*p/(s+p))^order, followed by a constant mixing matrix.
m = size(mixing,1);
n = order*m;
system.A = -p*eye(n);
system.B = zeros(n,m);
system.C = zeros(m,n);
for stage = 1:order
    rows = (stage-1)*m+(1:m);
    system.B(rows,:) = p*d^(stage-1)*eye(m);
    system.C(:,rows) = (1-d)*d^(order-stage)*mixing;
    for previous = 1:stage-1
        cols = (previous-1)*m+(1:m);
        system.A(rows,cols) = p*(1-d)*d^(stage-1-previous)*eye(m);
    end
end
system.D = d^order*mixing;
end
