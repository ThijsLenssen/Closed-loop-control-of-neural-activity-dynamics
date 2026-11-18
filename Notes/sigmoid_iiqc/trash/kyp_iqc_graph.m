function certificate = kyp_iqc_graph(P,Theta,N,epsilon,solver)
%KYP_IQC_GRAPH State-space SDP for a complementary hard IQC inequality.
% P,Theta are numeric real continuous-time A,B,C,D structures. N is the
% paper's calligraphic signature weight, not a feedthrough matrix.
%
% Primal: kyp_iqc_graph(P,iqc.Theta_Delta,iqc.N_Delta,epsilon)
% Dual:   kyp_iqc_graph(Pprime,iqc.Theta_Delta_underlined, ...
%                                      iqc.N_Delta_underlined,epsilon)
% Pprime=(A.',C.',B.',D.') is the paper's causal LTI dual.
%
% For G = Theta*[P;I] = (A_g,B_g,C_g,D_g), solve
%   mathcalP >= 0,
%   [A_g'*mathcalP+mathcalP*A_g, mathcalP*B_g;
%    B_g'*mathcalP, epsilon*I] + [C_g D_g]'*N*[C_g D_g] <= 0.
% This is the ODE specialization (T=I) of the paper's dual KYP LPI.
% Integration proves the finite-horizon complementary inequality from
% zero initial state. It does not establish sigmoid IQC admissibility.
%
% Requires YALMIP and an SDP solver (default SeDuMi). No frequency sampling
% or minimal-realization cancellation is used. Failed solver status and
% eigenvalue residuals are returned; certificate.passed must be inspected.

if nargin<5 || isempty(solver), solver='sedumi'; end
validateattributes(epsilon,{'numeric'},{'real','finite','scalar','positive'});
assert(exist('sdpvar','file')~=0,'YALMIP is required for the KYP SDP.');
m=size(P.D,1); k=size(P.D,2);
assert(size(Theta.D,2)==m+k,'Theta must act on [P*w;w].');
assert(isequal(size(N),[size(Theta.D,1),size(Theta.D,1)]));
assert(norm(N-N.','fro')<1e-10,'The IQC weight must be symmetric.');
np=size(P.A,1); nf=size(Theta.A,1);
Bz=Theta.B(:,1:m); Bw=Theta.B(:,m+1:end);
Dz=Theta.D(:,1:m); Dw=Theta.D(:,m+1:end);
G.A=[P.A,zeros(np,nf);Bz*P.C,Theta.A];
G.B=[P.B;Bz*P.D+Bw];
G.C=[Dz*P.C,Theta.C]; G.D=Dz*P.D+Dw;
n=size(G.A,1);

% Divide the supply and storage by epsilon so the input margin is one.
% This keeps the much smaller primal margin numerically comparable to
% the dual margin. It changes neither feasibility nor the recovered SDP.
mathcalP_scaled=sdpvar(n,n,'symmetric');

CD=[G.C,G.D];

L_scaled=[G.A.'*mathcalP_scaled+mathcalP_scaled*G.A,mathcalP_scaled*G.B; ...
          G.B.'*mathcalP_scaled,eye(k)] + CD.'*(N/epsilon)*CD;
L_scaled=(L_scaled+L_scaled.')/2;
numericalSlack=1e-5;
constraints=[mathcalP_scaled>=numericalSlack*eye(n), ...
             L_scaled<=-numericalSlack*eye(n+k)];
options=sdpsettings('solver',solver,'verbose',0);
diagnostics=optimize(constraints,[],options);
certificate.solver=solver; certificate.problem=diagnostics.problem;
certificate.info=diagnostics.info; certificate.epsilon=epsilon;
certificate.G=G; certificate.N=N;
certificate.passed=false;
if diagnostics.problem~=0
    return
end
Q=value(mathcalP_scaled); Q=(Q+Q.')/2;
certificate.mathcalP=epsilon*Q;
L=[G.A.'*Q+Q*G.A,Q*G.B;G.B.'*Q,eye(k)] + CD.'*(N/epsilon)*CD;
L=(L+L.')/2;
certificate.kypMatrix=epsilon*L;
certificate.minStorageEigenvalue=min(eig(certificate.mathcalP));
certificate.maxKypEigenvalue=max(eig(certificate.kypMatrix));
certificate.minScaledStorageEigenvalue=min(eig(Q));
certificate.maxScaledKypEigenvalue=max(eig(L));
certificate.passed=certificate.minStorageEigenvalue>0 ...
                      && certificate.maxKypEigenvalue<0;
end
