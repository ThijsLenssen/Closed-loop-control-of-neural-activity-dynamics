function [K,design,simulations] = saturation_iqc_dual_synthesis(solver,runSimulations)
%SATURATION_IQC_DUAL_SYNTHESIS Design K for a scalar saturated actuator.
% Uses the ordered incremental ReLU QCs on the dual side and K=Z'/Q.
% Equations (4)-(6) of saturation_iqc.tex give the difference system.
% The guarantee is for an outer trajectory and a reference in an inner set.
% Run: [K,design,simulations] = saturation_iqc_dual_synthesis;
if nargin < 1, solver = 'mosek'; end
if nargin < 2, runSimulations = true; end

% T*xdot = A*x + B*sat_[-limit,limit](K*x). T is an invertible matrix.
T = diag([1 1.2]);
A = [0 1; .5 -.35];
B = [0;1];
limit = 1;
commandBound = 1.8;                  % allows clipping inside x'*inv(Q)*x <= 1
referenceCommandBound = .4;          % strict interior of the linear range
referenceLevel = (referenceCommandBound/commandBound)^2;
alpha = (limit-referenceCommandBound)/(commandBound-referenceCommandBound);
decay = .15;
epsilon = 1e-6;
n = size(A,1);

% Equations (4)-(6) have input [1;1]*K*x_delta to the incremental
% ReLU block and injection B*[1 -1]*w_delta into the state equation.
% On the dual side these become v_d=[1;-1]*B'*x_d and K'*[1 1]*w_d.
% The diagonal secant block is self-adjoint. Q is the dual storage
% weight for T'*x_d. Z=Q*K' makes the synthesis LMI affine.
H = [B.' zeros(1,2);-B.' zeros(1,2);zeros(2,n) eye(2)];
aggregate = [1 0 0 0;0 0 1 1];       % [p; w_d,lower + w_d,upper]
sector = [-2*alpha 1+alpha;1+alpha -2];
y = pvar('y');
prog = sosprogram(y);
[prog,Q] = sospolymatrixvar(prog,polynomial(1),[n n],'symmetric');
[prog,Z] = sospolymatrixvar(prog,polynomial(1),[n 1]);
[prog,scale] = sospolyvar(prog,polynomial(1));
[prog,radiusSquared] = sospolyvar(prog,polynomial(1));
[prog,M1] = qc_M1_inc(prog,2);
[prog,M2] = qc_M2_inc(prog,2,4);
[prog,Morder] = qc_saturation_order_inc(prog,1,'dual');

% For |K*x| <= commandBound and |K*xhat| <= referenceCommandBound,
% the effective incremental slope lambda_lower-lambda_upper is in
% [alpha,1], even when x clips. If the positive command clips, the
% smallest ratio occurs at u=commandBound and uhat=referenceCommandBound.
% Negative clipping gives the same result by symmetry. The extra IIQC
% excludes zero slope, which otherwise exposes the unstable open loop.
Mrange = scale*(aggregate.'*sector*aggregate);
M = M1+M2+Morder+Mrange;

AQ = T*Q*A.';
Zlift = T*Z*[1 1];
L = [AQ+AQ.'+2*decay*T*Q*T.' Zlift; Zlift.' zeros(2)] + H.'*M*H;
prog = sosmatrixineq(prog,-L-epsilon*eye(n+2));
prog = sosmatrixineq(prog,Q-radiusSquared*eye(n));
prog = sosmatrixineq(prog,25*eye(n)-Q); % keep the ellipsoid axis lengths bounded
prog = sosmatrixineq(prog,[commandBound^2 Z.';Z Q]);
prog = sosineq(prog,radiusSquared-epsilon);
prog = sosineq(prog,scale-epsilon);
prog = sossetobj(prog,-radiusSquared); % largest enclosed ball for this SDP
options.solver = solver;
prog = sossolve(prog,options);
info = prog.solinfo.info;
assert(info.pinf==0 && info.dinf==0 && info.numerr==0, ...
    'No numerical solution. Inspect the solver output or adjust the example settings.');

Q = double(sosgetsol(prog,Q));
Z = double(sosgetsol(prog,Z));
K = Z.'/Q;
P = Q\eye(n);
Acl = (T\A)+(T\B)*K;
design = struct('T',T,'A',A,'B',B,'Q',Q,'P',P,'Z',Z, ...
    'limit',limit,'commandBound',commandBound,'sectorLower',alpha,'decay',decay);
design.referenceCommandBound = referenceCommandBound;
design.referenceLevel = referenceLevel;
design.dualQC = struct('M1inc',double(sosgetsol(prog,M1)), ...
    'M2inc4',double(sosgetsol(prog,M2)),'ordering',double(sosgetsol(prog,Morder)), ...
    'restrictedSlope',double(sosgetsol(prog,Mrange)));
design.ballRadius = sqrt(double(sosgetsol(prog,radiusSquared)));
design.openLoopPoles = eig(T\A);
design.linearClosedLoopPoles = eig(Acl);
design.maxCommand = sqrt(K*Q*K.');
design.unsaturatedEntryTime = log(commandBound/limit)/decay;
Lv = double(sosgetsol(prog,L));
design.maxDualLmiEigenvalue = max(eig((Lv+Lv.')/2));
design.solverInfo = prog.solinfo;
fprintf('Recovered K:'); fprintf(' % .6f',K); fprintf('\n');
fprintf('Open-loop max real pole %.4f. Closed-loop max real pole %.4f.\n', ...
    max(real(design.openLoopPoles)),max(real(design.linearClosedLoopPoles)));
fprintf('Certified x''*P*x <= 1 encloses a ball of radius %.4f.\n',design.ballRadius);
fprintf('Incremental decay >= %.2f for x''*P*x <= 1 and xhat''*P*xhat <= %.4f.\n', ...
    decay,referenceLevel);

simulations = [];
if runSimulations
    sys = struct('A',T\A,'B',T\B,'C',K,'E',zeros(n,1));
    open = sys;
    open.C = zeros(size(K));          % disable controller, same initial state
    initialDirection = Q*K.'/design.maxCommand;
    initial = .97*initialDirection;
    reference = .9*sqrt(referenceLevel)*initialDirection;
    time = (0:.02:18).';
    zero = @(t) 0;
    simulations.controlled = saturation_simulate(sys,-limit,limit,zero,initial,time);
    simulations.reference = saturation_simulate(sys,-limit,limit,zero,reference,time);
    simulations.uncontrolled = saturation_simulate(open,-limit,limit,zero,initial,time);
    simulations = checkAndPlot(simulations,design);
end
end

function simulations = checkAndPlot(simulations,design)
x = simulations.controlled;
xhat = simulations.reference;
xOpen = simulations.uncontrolled;
e = x.x-xhat.x;
limit = design.limit;
t = x.t;

% Equations (4)-(6): differences of the raw pairs, followed by J=[1 -1].
z = [x.v+limit x.v-limit];
zhat = [xhat.v+limit xhat.v-limit];
wDelta = max(z,0)-max(zhat,0);
simulations.stateDifference = e;
simulations.reluInputDifference = z-zhat;
simulations.reluOutputDifference = wDelta;
simulations.saturationDifference = wDelta(:,1)-wDelta(:,2);
simulations.storage = sum((x.x*design.P).*x.x,2);
simulations.referenceStorage = sum((xhat.x*design.P).*xhat.x,2);
simulations.incrementalStorage = sum((e*design.P).*e,2);
simulations.incrementalBound = simulations.incrementalStorage(1)*exp(-2*design.decay*t);
simulations.liftResidual = norm(simulations.saturationDifference-(x.u-xhat.u),inf);
simulations.entryTime = design.unsaturatedEntryTime;
fprintf('Initial command %.4f is clipped to %.4f. Reference command %.4f.\n', ...
    x.v(1),x.u(1),xhat.v(1));
fprintf('ReLU difference residual %.3g.\n',simulations.liftResidual);

simulations.figure = figure('Name','Dual synthesis with input saturation', ...
    'Color','w','Position',[100 100 1100 690]);
tiledlayout(2,2,'TileSpacing','compact','Padding','compact');

nexttile; hold on;
semilogy(t,max(vecnorm(xOpen.x,2,2),1e-12),'--','LineWidth',1.5,'DisplayName','Open loop');
semilogy(t,max(vecnorm(x.x,2,2),1e-12),'LineWidth',1.5,'DisplayName','Saturated feedback');
set(gca,'YScale','log'); grid on;
xlabel('Time'); ylabel('State norm'); title('Same initial state with and without feedback');
legend('Location','best');

nexttile; hold on;
colors = lines(size(x.x,2));
for j = 1:size(x.x,2)
    plot(t,x.x(:,j),'Color',colors(j,:),'LineWidth',1.5, ...
        'DisplayName',sprintf('x_%d',j));
    plot(t,xhat.x(:,j),'--','Color',colors(j,:),'LineWidth',1.3, ...
        'DisplayName',sprintf('xhat_%d',j));
end
grid on; xlabel('Time'); ylabel('State'); title('Two trajectories with saturated feedback');
legend('Location','best');

nexttile; hold on;
plot(t,x.v,':','LineWidth',1.6,'DisplayName','Command Kx');
plot(t,x.u,'LineWidth',1.5,'DisplayName','Applied input');
yline(limit,'k--','DisplayName','Actuator limits');
yline(-limit,'k--','HandleVisibility','off');
grid on; xlabel('Time'); ylabel('Scalar input'); title('Actuator clipping');
legend('Location','best');

nexttile; hold on;
semilogy(t,max(simulations.incrementalStorage,1e-12), ...
    'LineWidth',1.5,'DisplayName','Incremental storage');
semilogy(t,simulations.incrementalBound,'k--','LineWidth',1.3, ...
    'DisplayName','Certified upper bound');
set(gca,'YScale','log'); grid on;
xlabel('Time'); ylabel('(x-xhat)^T P (x-xhat)'); title('Incremental convergence from time zero');
legend('Location','best');
end
