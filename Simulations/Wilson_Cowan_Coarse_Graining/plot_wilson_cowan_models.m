function results = plot_wilson_cowan_models(overrides, makePlots)
%PLOT_WILSON_COWAN_MODELS Compare WC Eq. (9), Eq. (10), and a transport PDE.
%
% Run from this folder:
%   results = plot_wilson_cowan_models;
%
% Optional parameter overrides, for example:
%   results = plot_wilson_cowan_models(struct('tau', 1.5, 'nAge', 600));
%
% Source: Wilson and Cowan (1972), Eqs. (9)-(10), pp. 8-10.
% Figure 3 specifies r=3 ms but does not give its complete numerical setup.
% These defaults are ILLUSTRATIVE; they are not an exact reproduction of Fig. 3.
% All times below are in milliseconds.
%
% Eq. (9), with histories retained:
%   tau*E_dot = -E + (1-R)*S(U)
%   R(t) = integral_{t-r}^t E(s) ds
%   U(t) = integral_{-inf}^t exp(-alpha*(t-s))*(c1*E(s)+P(s)) ds
% The exponential convolution is realized EXACTLY as
%   U_dot = -alpha*U + c1*E + P.
%
% Eq. (10), after temporal coarse graining:
%   tau*Ebar_dot = -Ebar + (1-r*Ebar)*S(k*(c1*Ebar+P))
% We choose k=1/alpha to match the exponential filter's constant-input gain.
%
% Transport realization of Eq. (9):
%   z_t + z_a = 0,  a in [0,r],  z(t,0)=E(t)
%   R(t) = integral_0^r z(t,a) da
% coupled to the SAME E and U ODEs as Eq. (9).
% z is a history-age field, not a physical spatial field.
%
% Numerics:
% - Eq. (9): trapezoidal quadrature of the simulated activity history.
% - PDE: conservative first-order upwind finite volumes in age.
% - All time integrations: explicit second-order Heun method.
% - Zero prehistory E(t)=P(t)=0 for t<0; E(0)=U(0)=z(0,a)=0.
% No additional toolboxes are required.

if nargin < 1 || isempty(overrides), overrides = struct(); end
if nargin < 2, makePlots = true; end

% ---------------- Editable model and numerical parameters -----------------
p.r = 3;                  % Absolute refractory duration [ms]; Fig. 3 caption.
p.tau = 2.5;              % Population response constant [ms]; illustrative.
p.alpha = 0.25;           % Exponential decay RATE [1/ms]; illustrative.
p.c1 = 1;                 % Recurrent excitatory coupling; illustrative.
p.P0 = 1;                 % Step-input amplitude; illustrative.
p.slope = 6;              % Logistic response slope; illustrative.
p.theta = 1;              % Logistic response midpoint; illustrative.
p.k = [];                 % [] -> DC-matched gain 1/alpha [ms].
p.tf = 25;                % Simulation duration [ms].
p.nHistory = 1200;        % r/dt: makes the history window an integer length.
p.nAge = 300;             % Number of finite-volume cells on a in [0,r].
p.snapshotDt = 0.1;        % History-field snapshot interval [ms].

names = fieldnames(overrides);
for j = 1:numel(names)
    assert(isfield(p,names{j}), 'Unknown parameter: %s', names{j});
    p.(names{j}) = overrides.(names{j});
end
if isempty(p.k), p.k = 1/p.alpha; end
assert(p.r > 0 && p.tau > 0 && p.alpha > 0, ...
    'r, tau and alpha must be positive.');
assert(p.nHistory >= 1 && p.nHistory == round(p.nHistory));
assert(p.nAge >= 1 && p.nAge == round(p.nAge));

dt = p.r/p.nHistory;
da = p.r/p.nAge;
assert(dt/da <= 1, 'Upwind CFL condition requires nAge <= nHistory.');
time = (0:round(p.tf/dt))'*dt;
nSteps = numel(time);
input = p.P0*ones(nSteps,1);       % P(t)=P0 for t>=0; zero for t<0.
S = @(u) 0.5*(1+tanh(0.5*p.slope*(u-p.theta))); % Stable logistic.

% The three models are integrated independently.
E9 = zeros(nSteps,1); U9 = E9; R9 = E9; cumulativeE = E9;
E10 = E9;
EPde = E9; UPde = E9; RPde = E9;
z = zeros(p.nAge,1);              % Cell averages of E(t-a).
age = ((1:p.nAge)'-0.5)*da;
stride = max(1,round(p.snapshotDt/dt));
snapshotIndices = unique([1:stride:nSteps,nSteps]);
history = zeros(p.nAge,numel(snapshotIndices));
snapshotNumber = 2;

for n = 1:nSteps-1
    % ----- Eq. (9): moving-window history quadrature + filter ODE -----------
    lower = n-p.nHistory;
    if lower >= 1, previousIntegral = cumulativeE(lower);
    else, previousIntegral = 0; end
    R9(n) = cumulativeE(n)-previousIntegral;

    eDot = (-E9(n)+(1-R9(n))*S(U9(n)))/p.tau;
    uDot = -p.alpha*U9(n)+p.c1*E9(n)+input(n);
    ePred = E9(n)+dt*eDot;
    uPred = U9(n)+dt*uDot;

    lowerNext = n+1-p.nHistory;
    if lowerNext >= 1, previousIntegralNext = cumulativeE(lowerNext);
    else, previousIntegralNext = 0; end
    rPred = cumulativeE(n)+0.5*dt*(E9(n)+ePred)-previousIntegralNext;
    eDotPred = (-ePred+(1-rPred)*S(uPred))/p.tau;
    uDotPred = -p.alpha*uPred+p.c1*ePred+input(n+1);
    E9(n+1) = E9(n)+0.5*dt*(eDot+eDotPred);
    U9(n+1) = U9(n)+0.5*dt*(uDot+uDotPred);
    cumulativeE(n+1) = cumulativeE(n)+0.5*dt*(E9(n)+E9(n+1));

    % ----- Eq. (10): temporal coarse-grained ODE ---------------------------
    q = p.k*(p.c1*E10(n)+input(n));
    eDot = (-E10(n)+(1-p.r*E10(n))*S(q))/p.tau;
    ePred = E10(n)+dt*eDot;
    qPred = p.k*(p.c1*ePred+input(n+1));
    eDotPred = (-ePred+(1-p.r*ePred)*S(qPred))/p.tau;
    E10(n+1) = E10(n)+0.5*dt*(eDot+eDotPred);

    % ----- Transport PDE coupled to E and U -------------------------------
    % Flux at a=0 is the current E; the distal boundary is pure outflow.
    RPde(n) = da*sum(z);
    zDot = ([EPde(n);z(1:end-1)]-z)/da;
    eDot = (-EPde(n)+(1-RPde(n))*S(UPde(n)))/p.tau;
    uDot = -p.alpha*UPde(n)+p.c1*EPde(n)+input(n);
    zPred = z+dt*zDot;
    ePred = EPde(n)+dt*eDot;
    uPred = UPde(n)+dt*uDot;
    rPred = da*sum(zPred);
    zDotPred = ([ePred;zPred(1:end-1)]-zPred)/da;
    eDotPred = (-ePred+(1-rPred)*S(uPred))/p.tau;
    uDotPred = -p.alpha*uPred+p.c1*ePred+input(n+1);
    z = z+0.5*dt*(zDot+zDotPred);
    EPde(n+1) = EPde(n)+0.5*dt*(eDot+eDotPred);
    UPde(n+1) = UPde(n)+0.5*dt*(uDot+uDotPred);

    if snapshotNumber <= numel(snapshotIndices) && n+1 == snapshotIndices(snapshotNumber)
        history(:,snapshotNumber) = z;
        snapshotNumber = snapshotNumber+1;
    end
end

R9(end) = cumulativeE(end)-cumulativeE(max(1,nSteps-p.nHistory));
RPde(end) = da*sum(z);
results.parameters = p;
results.time = time;
results.input = input;
results.eq9 = struct('E',E9,'U',U9,'R',R9);
results.eq10 = struct('E',E10);
results.transport = struct('E',EPde,'U',UPde,'R',RPde, ...
    'age',age,'snapshotTimes',time(snapshotIndices),'history',history);
results.dt = dt;
results.da = da;
results.maxDifference = max(abs(E9-EPde));
results.relativePeakDifference = results.maxDifference/max(max(abs(E9)),eps);

fprintf('Illustrative parameters; not an exact reproduction of published Fig. 3.\n');
fprintf('dt = %.5g ms, da = %.5g ms, CFL = %.3f\n',dt,da,dt/da);
fprintf('Maximum |Eq. (9) - transport| = %.6g (%.3f%% of Eq. (9) peak)\n', ...
    results.maxDifference,100*results.relativePeakDifference);

if makePlots
    folder = fullfile(fileparts(mfilename('fullpath')),'output');
    if ~exist(folder,'dir'), mkdir(folder); end
    fig = figure('Color','w','Name','Wilson-Cowan: memory, coarse graining and transport', ...
        'Position',[100,100,1050,700]);
    layout = tiledlayout(fig,2,1,'TileSpacing','compact','Padding','compact');
    ax = nexttile(layout);
    plot(ax,time,E9,'Color',[0 .45 .70],'LineWidth',1.7); hold(ax,'on');
    plot(ax,time,E10,'Color',[.80 .15 .10],'LineWidth',1.7);
    plot(ax,time,EPde,'--','Color',[.1 .1 .1],'LineWidth',1.3);
    xlabel(ax,'Time (ms)'); ylabel(ax,'Population activity E(t)');
    legend(ax,'Eq. (9): explicit temporal memory','Eq. (10): coarse grained', ...
        'Transport PDE realization of Eq. (9)','Location','best');
    title(ax,'Illustrative comparison: same input and zero prehistory');
    grid(ax,'on'); xlim(ax,[time(1),time(end)]);
    ax = nexttile(layout);
    plot(ax,time,abs(E9-EPde),'Color',[0 .45 .70],'LineWidth',1.4);
    xlabel(ax,'Time (ms)'); ylabel(ax,'|E_9 - E_{PDE}|');
    title(ax,'Numerical discrepancy: refine the age grid to reduce upwind error');
    grid(ax,'on'); xlim(ax,[time(1),time(end)]);
    exportgraphics(fig,fullfile(folder,'wilson_cowan_comparison.png'),'Resolution',180);
    exportgraphics(fig,fullfile(folder,'wilson_cowan_comparison.pdf'),'ContentType','vector');
    savefig(fig,fullfile(folder,'wilson_cowan_comparison.fig'));
    save(fullfile(folder,'wilson_cowan_comparison.mat'),'results');
end
end
