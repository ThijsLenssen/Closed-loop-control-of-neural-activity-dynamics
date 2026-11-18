function report = verify_sigmoid_dynamic_iiqc
%VERIFY_SIGMOID_DYNAMIC_IIQC Numerical checks supplementing the analytic proof.
% The proof of hardness is in README.md; sampled tests alone do not prove it.
% Quadratic supply integrals are computed exactly for piecewise-constant
% sigmoid inputs by a block matrix exponential, rather than time stepping.

folder = fileparts(mfilename('fullpath'));
rng(3695);
report.description = 'Continuous-time rational hard incremental IQC; joint sigmoid pairs';
report.caseDescriptions = {'independent inputs','small increments and moving common input', ...
    'constant increments and switching common input','correlated inputs'};
report.tests = struct([]);
report.inverseChecks = struct([]);

for groups = 1:2
    rho = linspace(0.9,0.95,groups);
    iqc = sigmoid_dynamic_iiqc(rho,10,10);
    inverseCheck = check_inverse(iqc);
    if isempty(report.inverseChecks)
        report.inverseChecks = inverseCheck;
    else
        report.inverseChecks(end+1) = inverseCheck;
    end
    m = iqc.channels;
    MS = repmat([300;400],groups,1);
    BS = repmat([17;75],groups,1);
    midpoint = MS/4.*log((MS-BS)./BS);
    segments = 500;
    dt = 0.01;
    for kind = 1:4
        switch kind
            case 1
                z1 = midpoint+MS.*(4*rand(m,segments)-2);
                z2 = midpoint+MS.*(4*rand(m,segments)-2);
            case 2
                common = midpoint+MS.*(6*rand(m,segments)-3);
                v = 0.01*MS.*randn(m,segments);
                z1 = common+v/2;
                z2 = common-v/2;
            case 3
                common = midpoint+MS.*(6*rand(m,segments)-3);
                v = 0.1*MS.*ones(m,segments);
                v(2:2:end,:) = -v(2:2:end,:);
                z1 = common+v/2;
                z2 = common-v/2;
            case 4
                wave = sin(linspace(0,20*pi,segments));
                v = MS.*repmat(wave,m,1);
                v(2:2:end,:) = -v(2:2:end,:);
                common = midpoint+MS.*repmat(cos(linspace(0,7*pi,segments)),m,1);
                z1 = common+v/2;
                z2 = common-v/2;
        end
        sigmoid = @(q) MS/2.*(1+tanh(2*(q-midpoint)./MS));
        v = z1-z2;
        w = sigmoid(z1)-sigmoid(z2);
        staticSupply = sum(w.*(v-w),1);
        assert(min(staticSupply)>-1e-8, 'Generated sigmoid pair violates its slope bound.');
        prefix = exact_prefix_integrals(iqc,[v;w],dt);
        energy = dt*sum(v.^2+w.^2,'all');
        tolerance = 1e-9*max(1,energy);
        assert(min(prefix)>=-tolerance,'A hard-IQC prefix test failed.');
        item.channels = m;
        item.caseDescription = report.caseDescriptions{kind};
        item.minPrefixSupply = min(prefix);
        item.finalSupply = prefix(end);
        item.inputEnergy = energy;
        item.relativeMinimum = min(prefix)/max(1,energy);
        if isempty(report.tests)
            report.tests = item;
        else
            report.tests(end+1) = item;
        end
        fprintf('%d channels, %s: min prefix %.9g, final %.9g\n', ...
            m,item.caseDescription,item.minPrefixSupply,item.finalSupply);
    end
end

% A delay-free continuous-time Lur'e example where this dynamic certificate
% succeeds but every diagonal static [0,1] sector multiplier fails.
rho = 0.95; order = 10; pole = 1; directRatio = 0.5;
iqc = sigmoid_dynamic_iiqc(rho,pole,order,directRatio);
omega = pole/8;
h = ((directRatio*1i*omega+pole)/(1i*omega+pole))^order;
obstruction = 1-rho*real(h)-rho^2*imag(h)^2;
assert(obstruction < -5e-4);
report.example.rho = rho;
report.example.order = order;
report.example.pole = pole;
report.example.directRatio = directRatio;
report.example.frequency = omega;
report.example.diagonalSectorObstruction = obstruction;
report.example.dynamicStrictness = min(iqc.eta);

% On G=H, the first IQC output v-Hw vanishes exactly. Check the
% state-space realization against the resulting negative supply identity.
maxIdentityError = 0;
for omega = [0,logspace(-4,4,100)]
    H = response(iqc.H,omega);
    Psi = iqc.D+iqc.C*((1i*omega*eye(size(iqc.A))-iqc.A)\iqc.B);
    graph = [H;eye(iqc.channels)];
    supply = graph'*Psi'*iqc.M*Psi*graph;
    expected = -H'*diag(iqc.eta)*H-diag(iqc.eta);
    maxIdentityError = max(maxIdentityError,norm(supply-expected,'fro'));
end
assert(maxIdentityError < 1e-9);
report.example.maxRealizationIdentityError = maxIdentityError;

% Check the polyhedral norm identities used in the analytic proof.
x = randn(2,10000);
gain = rand(2,10000);
N = @(q) max([abs(q);abs(sum(q,1))],[],1);
R = [1 1;-1 0];
report.maxNormIdentityError = max(abs(N(R*x)-N(x)));
report.maxDiagonalContractionResidual = max(N(gain.*x)-N(x));
assert(report.maxNormIdentityError < 1e-12);
assert(report.maxDiagonalContractionResidual <= 1e-12);
report.passed = true;
save(fullfile(folder,'verification_results.mat'),'report');
fprintf('Static sector obstruction %.9g; dynamic strictness %.9g\n', ...
    report.example.diagonalSectorObstruction,report.example.dynamicStrictness);
fprintf('VERIFICATION_PASSED\n');
end

function check = check_inverse(iqc)
% Verify analytic pole locations, high-frequency invertibility, and both
% inverse products over DC through high frequencies. No toolboxes needed.
check.channels = iqc.channels;
check.directRatio = iqc.directRatio;
check.maxRealPoleH = max(real(eig(iqc.H.A)));
check.maxRealPoleInverse = max(real(eig(iqc.Hinv.A)));
assert(check.maxRealPoleH < 0 && check.maxRealPoleInverse < 0);
assert(abs(check.maxRealPoleH+iqc.pole) < 1e-10*max(1,iqc.pole));
assert(abs(check.maxRealPoleInverse+iqc.inversePole) < 1e-10*max(1,iqc.inversePole));
check.maxInverseProductError = 0;
check.maxFormulaError = 0;
for omega = iqc.pole*[0,logspace(-5,5,120)]
    H = response(iqc.H,omega);
    Hinv = response(iqc.Hinv,omega);
    check.maxInverseProductError = max([check.maxInverseProductError, ...
        norm(H*Hinv-eye(iqc.channels),'fro'), ...
        norm(Hinv*H-eye(iqc.channels),'fro')]);
    scalar = ((iqc.directRatio*1i*omega+iqc.pole)/(1i*omega+iqc.pole))^iqc.order;
    exact = scalar*kron(diag(iqc.rho),[1 1;-1 0]);
    check.maxFormulaError = max(check.maxFormulaError,norm(H-exact,'fro'));
end
check.feedthroughInverseError = max( ...
    norm(iqc.H.D*iqc.Hinv.D-eye(iqc.channels),'fro'), ...
    norm(iqc.Hinv.D*iqc.H.D-eye(iqc.channels),'fro'));
assert(check.maxInverseProductError < 1e-8);
assert(check.maxFormulaError < 1e-10);
assert(check.feedthroughInverseError < 1e-10);
fprintf('%d channels: H/Hinv pole bounds %.6g / %.6g, inverse error %.3g\n', ...
    check.channels,check.maxRealPoleH,check.maxRealPoleInverse,check.maxInverseProductError);
end

function value = response(system,omega)
value = system.D+system.C*((1i*omega*eye(size(system.A))-system.A)\system.B);
end

function prefix = exact_prefix_integrals(iqc,inputs,dt)
% Two half-interval checks per segment. The input holds each value for dt.
n = size(iqc.A,1);
k = size(inputs,1);
extendedA = [iqc.A,iqc.B;zeros(k,n+k)];
output = [iqc.C,iqc.D];
Q = output'*iqc.M*output;
dimension = n+k;
vanLoan = expm([-extendedA',Q;zeros(dimension),extendedA]*(dt/2));
transition = vanLoan(dimension+1:end,dimension+1:end);
gramian = transition'*vanLoan(1:dimension,dimension+1:end);
gramian = (gramian+gramian')/2;
x = zeros(n,1);
prefix = zeros(2*size(inputs,2)+1,1);
index = 1;
for segment = 1:size(inputs,2)
    for half = 1:2
        state = [x;inputs(:,segment)];
        increment = state'*gramian*state;
        state = transition*state;
        x = state(1:n);
        prefix(index+1) = prefix(index)+increment;
        index = index+1;
    end
end
end
