function report=verify_sigmoid_dual_iiqc
%VERIFY_SIGMOID_DUAL_IIQC Primal admissibility and the dual-first algebra.
% The analytic proof, rather than numerical sampling, establishes hardness.
folder=fileparts(mfilename('fullpath'));
rng(3695);
report.tests=struct([]); report.factorChecks=struct([]);
descriptions={'independent inputs','small increments and moving common input', ...
    'constant increments and switching common input','correlated inputs', ...
    'arbitrary switching diagonal slopes, including sector endpoints'};
for directRatio=[0,0.5]
    for groups=1:2
        rho=linspace(0.9,0.95,groups);
        weights=1:groups;
        iqc=sigmoid_dual_iiqc(rho,10,10,directRatio,weights);
        check=check_factors(iqc);
        if isempty(report.factorChecks), report.factorChecks=check;
        else, report.factorChecks(end+1)=check; end
        m=iqc.channels;
        MS=repmat([300;400],groups,1); BS=repmat([17;75],groups,1);
        midpoint=MS/4.*log((MS-BS)./BS);
        segments=500; dt=0.01;
        for kind=1:5
            if kind==5
                z_Delta=MS.*randn(m,segments);
                slopes=rand(m,segments);
                slopes(:,1:4:end)=0; slopes(:,2:4:end)=1;
                slopes(1:2:end,3:4:end)=1; slopes(2:2:end,3:4:end)=0;
                slopes(1:2:end,4:4:end)=0; slopes(2:2:end,4:4:end)=1;
                w_Delta=slopes.*z_Delta;
            elseif kind==1
                z1=midpoint+MS.*(4*rand(m,segments)-2);
                z2=midpoint+MS.*(4*rand(m,segments)-2);
            else
                common=midpoint+MS.*(6*rand(m,segments)-3);
                if kind==2
                    v=0.01*MS.*randn(m,segments);
                elseif kind==3
                    v=0.1*MS.*ones(m,segments); v(2:2:end,:)=-v(2:2:end,:);
                else
                    v=MS.*repmat(sin(linspace(0,20*pi,segments)),m,1);
                    v(2:2:end,:)=-v(2:2:end,:);
                    common=midpoint+MS.*repmat(cos(linspace(0,7*pi,segments)),m,1);
                end
                z1=common+v/2; z2=common-v/2;
            end
            if kind~=5
                sigmoid=@(q) MS/2.*(1+tanh(2*(q-midpoint)./MS));
                z_Delta=z1-z2; w_Delta=sigmoid(z1)-sigmoid(z2);
            end
            assert(min(sum(w_Delta.*(z_Delta-w_Delta),1))>-1e-8);
            prefix=prefix_integrals(iqc.Theta_Delta,[z_Delta;w_Delta],dt);
            lowerBound=held_energy(z_Delta,diag(iqc.Y_Delta),dt);
            energy=dt*sum(z_Delta.^2+w_Delta.^2,'all');
            assert(min(prefix)>=-1e-9*max(1,energy));
            assert(min(prefix-lowerBound)>=-1e-9*max(1,energy));
            item.channels=m; item.directRatio=directRatio;
            item.description=descriptions{kind}; item.minPrefix=min(prefix);
            item.minPropositionResidual=min(prefix-lowerBound);
            item.minPositiveTimeSupply=min(prefix(2:end));
            item.prefixCount=numel(prefix);
            item.finalSupply=prefix(end); item.energy=energy;
            if isempty(report.tests), report.tests=item;
            else, report.tests(end+1)=item; end
            fprintf('beta=%.1f, %d channels, %s: min primal prefix %.9g\n', ...
                directRatio,m,item.description,item.minPrefix);
        end
    end
end

% Transposition changes the polyhedral norm from a sum to a difference.
x=randn(2,20000); D=rand(2,20000); R=[1 1;-1 0];
Nminus=@(z) max([abs(z);abs(z(1,:)-z(2,:))],[],1);
report.normIdentityError=max(abs(Nminus(R'*x)-Nminus(x)));
report.diagonalContractionResidual=max(Nminus(D.*x)-Nminus(x));
assert(report.normIdentityError<1e-12 && report.diagonalContractionResidual<=1e-12);

% Matching example: primal P=Hprime, dual P'=H. Compare both choices of h.
report.examples=struct([]);
for directRatio=[0,0.5]
    iqc=sigmoid_dual_iiqc(0.95,1,10,directRatio);
    if directRatio==0
        omega=tan(acos(1/(2*0.95))/10);
    else
        omega=1/8;
    end
    h=((directRatio*1i*omega+1)/(1i*omega+1))^10;
    example.directRatio=directRatio; example.frequency=omega;
    example.diagonalSectorObstruction=1-0.95*real(h)-0.95^2*imag(h)^2;
    example.primalInputStrictness=min(iqc.eta);
    example.dualInputStrictness=1;
    example.incrementalIOStrictness=min(iqc.eta)/(1+0.95^2*norm(R,2)^2);
    assert(example.diagonalSectorObstruction < -5e-4);
    if isempty(report.examples), report.examples=example;
    else, report.examples(end+1)=example; end
end
report.passed=true;
save(fullfile(folder,'dual_verification_results.mat'),'report');
fprintf('%d signal cases, %d total prefixes; stronger proposition bound passed.\n', ...
    numel(report.tests),sum([report.tests.prefixCount]));
fprintf('DUAL_VERIFICATION_PASSED\n');
end

function check=check_factors(iqc)
m=iqc.channels; J=iqc.hatJ;
Theta_Delta=iqc.Theta_Delta; N_Delta=iqc.N_Delta;
Theta_Delta_underlined=iqc.Theta_Delta_underlined;
N_Delta_underlined=iqc.N_Delta_underlined;
assert(min(eig(iqc.X_Delta))>0 && min(eig(iqc.Y_Delta))>0);
assert(norm(N_Delta-blkdiag(iqc.X_Delta,-iqc.Y_Delta),'fro')<1e-12);
assert(rank(Theta_Delta.D)==2*m && rank(Theta_Delta_underlined.D)==2*m);
check.channels=m; check.directRatio=iqc.directRatio;
check.maxDualityError=0; check.maxFactorInverseError=0;
check.maxComplementError=0;
for omega=iqc.pole*[0,logspace(-5,5,100)]
    dual=response(Theta_Delta_underlined,omega); primal=response(Theta_Delta,omega);
    % .' is intentional: the paper's prime is a causal LTI dual, not a
    % conjugate-transpose frequency-domain adjoint.
    recovered=(J'*dual.'*J)\eye(2*m);
    check.maxDualityError=max(check.maxDualityError,norm(primal-recovered,'fro'));
    for data={ {iqc.dual,iqc.dualInverse}, {iqc.primal,iqc.primalInverse} }
        pair=data{1}; F=response(pair{1},omega); Finv=response(pair{2},omega);
        check.maxFactorInverseError=max([check.maxFactorInverseError, ...
            norm(F*Finv-eye(2*m),'fro'),norm(Finv*F-eye(2*m),'fro')]);
    end
    assert(norm(primal(m+1:end,1:m),'fro')<1e-12);
    assert(norm(primal(m+1:end,m+1:end)-eye(m),'fro')<1e-12);
    Hp=response(iqc.Hprime,omega); H=response(iqc.H,omega);
    expectedPrimal=-diag(iqc.eta./kron(iqc.pairWeights,ones(2,1)));
    expectedDual=-diag(kron(iqc.pairWeights,ones(2,1)));
    primalSupply=[Hp;eye(m)]'*primal'*N_Delta*primal*[Hp;eye(m)];
    dualSupply=[H;eye(m)]'*dual'*N_Delta_underlined*dual*[H;eye(m)];
    check.maxComplementError=max([check.maxComplementError, ...
        norm(primalSupply-expectedPrimal,'fro'),norm(dualSupply-expectedDual,'fro')]);
end
expectedWeight=-(J'*N_Delta_underlined'*J)\eye(2*m);
check.weightDualityError=norm(N_Delta-expectedWeight,'fro');
assert(check.maxDualityError<1e-9 && check.maxFactorInverseError<1e-9);
assert(check.weightDualityError<1e-10 && check.maxComplementError<1e-9);
assert(max(real(eig(iqc.primal.A)))<0 && max(real(eig(iqc.dual.A)))<0);
assert(norm(iqc.primal22-eye(m),'fro')==0);
check.HFeedthroughRank=rank(iqc.H.D);
if iqc.directRatio==0, assert(check.HFeedthroughRank==0); end

% Finite-horizon complementary inequalities: P=Hprime and P'=H.
% Compose independent realizations to check cancellation in the time domain.
input=randn(m,200); dt=0.05;
primalGraph=compose_graph(Theta_Delta,iqc.Hprime);
dualGraph=compose_graph(Theta_Delta_underlined,iqc.H);
primalPrefix=prefix_integrals(primalGraph,input,dt);
dualPrefix=prefix_integrals(dualGraph,input,dt);
primalExpected=-held_energy(input,diag(iqc.Y_Delta),dt);
dualExpected=-held_energy(input,kron(iqc.pairWeights,ones(2,1)),dt);
check.maxPrimalTimeComplementError=max(abs(primalPrefix-primalExpected));
check.maxDualTimeComplementError=max(abs(dualPrefix-dualExpected));
scale=max(1,dt*sum(input.^2,'all'));
assert(check.maxPrimalTimeComplementError<1e-9*scale);
assert(check.maxDualTimeComplementError<1e-9*scale);
fprintf('  finite-horizon complementary errors: primal %.3g, dual %.3g\n', ...
    check.maxPrimalTimeComplementError,check.maxDualTimeComplementError);
fprintf('beta=%.1f, %d channels: D-map error %.3g, square-factor inverse error %.3g\n', ...
    iqc.directRatio,m,check.maxDualityError,check.maxFactorInverseError);
end

function graph=compose_graph(Theta,P)
% Zero-state map from w to Theta*[P*w;w]. The dual case uses underlined w.
m=size(P.D,1); np=size(P.A,1); nf=size(Theta.A,1);
Bz=Theta.B(:,1:m); Bw=Theta.B(:,m+1:end);
Dz=Theta.D(:,1:m); Dw=Theta.D(:,m+1:end);
graph.A=[P.A,zeros(np,nf);Bz*P.C,Theta.A];
graph.B=[P.B;Bz*P.D+Bw];
graph.C=[Dz*P.C,Theta.C]; graph.D=Dz*P.D+Dw;
graph.M=Theta.M;
end

function prefix=held_energy(inputs,weights,dt)
% Exact weighted energy at the same half-segment prefixes as the filter.
increment=dt/2*sum(weights.*inputs.^2,1);
prefix=[0;cumsum(repelem(increment(:),2))];
end

function value=response(system,omega)
value=system.D+system.C*((1i*omega*eye(size(system.A))-system.A)\system.B);
end

function prefix=prefix_integrals(filter,inputs,dt)
n=size(filter.A,1); k=size(inputs,1);
A=[filter.A,filter.B;zeros(k,n+k)];
output=[filter.C,filter.D]; Q=output'*filter.M*output;
dimension=n+k;
vanLoan=expm([-A',Q;zeros(dimension),A]*(dt/2));
transition=vanLoan(dimension+1:end,dimension+1:end);
gramian=transition'*vanLoan(1:dimension,dimension+1:end);
gramian=(gramian+gramian')/2;
x=zeros(n,1); prefix=zeros(2*size(inputs,2)+1,1); index=1;
for segment=1:size(inputs,2)
    for half=1:2
        state=[x;inputs(:,segment)];
        increment=state'*gramian*state; state=transition*state;
        x=state(1:n); prefix(index+1)=prefix(index)+increment; index=index+1;
    end
end
end
