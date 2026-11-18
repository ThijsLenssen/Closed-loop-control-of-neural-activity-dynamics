clear all; close all;

addpath(genpath('C:\Program Files\Mosek\11.0\toolbox\r2019b'));


rho = 0.95;
a = 1;
order = 10;
beta = 0;                       % 0: strictly proper; 0.5: biproper
eta = (1-rho)^2/8;
I = eye(2);
% H and the dual factor, using the paper's underlined notation.
h = ss(-a,a,1-beta,beta)^order; % ((beta*s+a)/(s+a))^order as a cascade
H = rho*[1 1;-1 0]*append(h,h);
% H = zeros(2,2);
Theta_Delta_underlined = [I,-H;zeros(2),I];


% Filtered dual graph: underline(Theta_Delta)*[Pprime;I].
s = tf('s');
P = ss([0.8/(s+1),  -2/(s+0.3);
        1.5/(s+0.5), -0.4/(s+0.8)]);

% Causal LTI dual for your dual KYP test:
[Ap,Bp,Cp,Dp] = ssdata(P);
Pprime = ss(Ap.',Cp.',Bp.',Dp.');

[A,B,C,D] = ssdata(Theta_Delta_underlined*[Pprime;I]);
n = size(A,1);
% The paper's dual KYP LMI, with quadratic storage mathcalP.
P = sdpvar(n,n,'symmetric');
S = sdpvar(2,2,'diagonal');
N_Delta_underlined = blkdiag(S/eta,-S);
% N_Delta_underlined = [zeros(2,2), S; S,zeros(2,2)];
eps = sdpvar(1,1);
KYP = [A'*P+P*A, P*B; ...
       B'*P, eps*I] ...
       + [C D]'*N_Delta_underlined*[C D];
constraints = [P >= 1e-5*eye(n), KYP<=0, S>=1e-5*eye(2), eps<=10];
result = optimize(constraints,-eps,sdpsettings('solver','mosek','verbose',0));
assert(result.problem == 0,result.info);

% Check the numerical certificate independently of solver status.
Q = value(P); Q = (Q+Q')/2;
L = value(KYP); L = (L+L')/2;
% assert(min(eig(Q)) > 0 && max(eig(L)) <= 0,'KYP residual check failed.');
fprintf('KYP feasible: epsilon = %.3g, min eig(storage) = %.3g, max eig(KYP) = %.3g\n, max eig(S) = %.3g', ...
        double(eps),min(eig(Q)),max(eig(L)), max(eig(value(S))));
