function results = simulate_cortical_disturbance(options, makePlots)
%SIMULATE_CORTICAL_DISTURBANCE Exogenous cortex in the PNAS firing-rate model.
%   results = simulate_cortical_disturbance;
%   results = simulate_cortical_disturbance(struct('duration', 5), false);
%
% Open loop: stimulation u(t) = 0. All times are in SECONDS.
%   tauS*Sdot = FS(-wGS*G(t-delayGS) + wCS*Ctx(t)) - S
%   tauG*Gdot = FG(wSG*S(t-delaySG) - wGG*G(t-delayGG) - wXG*Str) - G
%
% Ctx(t) is prescribed independently of S and G. For each sampled Ctx(t),
% solve the two static equations for the FROZEN-INPUT equilibrium. This is
% a reference curve, not generally a trajectory of the nonautonomous DDE.
% Delays disappear from the frozen equilibrium equations, but remain in
% the actual firing-rate simulation, integrated by MATLAB's dde23.
%
% Custom cortex (a scalar input handle, in spikes/s):
%   cfg.cortex = @(t) 27 + 5*sin(2*pi*2*t);
%   results = simulate_cortical_disturbance(cfg);
% For measured input: use interp1 with interpolation and explicit endpoint
% handling. A discontinuous input also needs its jump times in cfg.jumps.

if nargin < 1, options = struct; end
if nargin < 2, makePlots = true; end

% Diseased-case parameters from main.tex, Table 1. Time units converted to s.
p.wSG = 20; p.wGS = 10.7; p.wGG = 12.3;
p.wCS = 9.2; p.wXG = 139.4;
p.tauS = 6e-3; p.tauG = 14e-3;
p.delayGS = 6e-3; p.delaySG = 6e-3; p.delayGG = 4e-3;
p.MS = 300; p.MG = 400; p.BS = 17; p.BG = 75;
p.Ctx = 27; p.Str = 2;

% Illustrative disturbances; these are not fitted cortical recordings.
cfg.duration = 3;
cfg.samplePeriod = 5e-4;
cfg.onset = 0.5;
cfg.transition = 0.2;
cfg.rampDuration = 0.75;
cfg.rampAmplitude = 15;          % Smooth increase from 27 to 42 spikes/s.
cfg.amplitude = 5;               % Same amplitude for slow and beta inputs.
cfg.slowFrequency = 1;           % Hz.
cfg.betaFrequency = 20;          % Hz.
cfg.initialPerturbation = [0.1; -0.1]; % Constant history offset, spikes/s.
cfg.relTol = 1e-7; cfg.absTol = 1e-9; cfg.maxStep = 2.5e-4;
cfg.cortex = [];                 % Optional user-supplied scalar function.
cfg.jumps = [];                  % Known input discontinuity times, seconds.
cfg.outputDirectory = fullfile(fileparts(mfilename('fullpath')), 'output');
names = fieldnames(options);
for k = 1:numel(names)
    assert(isfield(cfg, names{k}), 'Unknown option: %s', names{k});
    cfg.(names{k}) = options.(names{k});
end
validateattributes(cfg.duration, {'numeric'}, {'scalar','real','finite','positive'});
validateattributes(cfg.samplePeriod, {'numeric'}, {'scalar','real','finite','positive'});
validateattributes(cfg.transition, {'numeric'}, {'scalar','real','finite','positive'});
validateattributes(cfg.rampDuration, {'numeric'}, {'scalar','real','finite','positive'});
validateattributes(cfg.maxStep, {'numeric'}, {'scalar','real','finite','positive'});
validateattributes(cfg.initialPerturbation, {'numeric'}, {'real','finite','numel',2});

t = (0:cfg.samplePeriod:cfg.duration).';
if t(end) < cfg.duration, t(end+1) = cfg.duration; end
[lags, ~, lagIndex] = unique([p.delayGS, p.delaySG, p.delayGG]);
solverOptions = ddeset('RelTol', cfg.relTol, 'AbsTol', cfg.absTol, ...
    'MaxStep', cfg.maxStep);
if ~isempty(cfg.jumps), solverOptions = ddeset(solverOptions, 'Jumps', cfg.jumps); end

envelope = @(time) smooth_step((time-cfg.onset)/cfg.transition);
if isempty(cfg.cortex)
    caseNames = {'Constant cortex', 'Ramping cortex', 'Slow cortex', 'Beta cortex'};
    cortexFunctions = {
        @(time) p.Ctx;
        @(time) p.Ctx + cfg.rampAmplitude* ...
            smooth_step((time-cfg.onset)/cfg.rampDuration);
        @(time) p.Ctx + cfg.amplitude*envelope(time)* ...
            sin(2*pi*cfg.slowFrequency*(time-cfg.onset));
        @(time) p.Ctx + cfg.amplitude*envelope(time)* ...
            sin(2*pi*cfg.betaFrequency*(time-cfg.onset))};
else
    assert(isa(cfg.cortex, 'function_handle'), 'cortex must be a function handle.');
    caseNames = {'Custom cortex'};
    cortexFunctions = {cfg.cortex};
end

results.parameters = p;
results.configuration = cfg;
results.referenceType = 'Frozen-input open-loop equilibrium, stimulation u=0';
for k = 1:numel(caseNames)
    cortex = cortexFunctions{k};
    ctx = arrayfun(cortex, t);
    validateattributes(ctx, {'numeric'}, {'real','finite','nonnegative','numel',numel(t)});
    equilibriumAtStart = frozen_equilibrium(cortex(0), p);
    history = equilibriumAtStart + cfg.initialPerturbation(:);
    assert(all(history >= 0 & history <= [p.MS;p.MG]), ...
        'The initial firing-rate history must lie within the sigmoid bounds.');
    rhs = @(time, rates, delayed) model_rhs(time, rates, delayed, cortex, p, lagIndex);
    solution = dde23(rhs, lags, history, [0 cfg.duration], solverOptions);
    rates = deval(solution, t).';

    % Reuse identical inputs, e.g. the constant part before disturbance onset.
    [uniqueCtx, ~, inputIndex] = unique(ctx);
    equilibriumTable = zeros(numel(uniqueCtx), 2);
    for j = 1:numel(uniqueCtx)
        equilibriumTable(j,:) = frozen_equilibrium(uniqueCtx(j), p).';
    end
    equilibrium = equilibriumTable(inputIndex,:);
    error = rates-equilibrium;
    residual = equilibrium - [ ...
        activation(-p.wGS*equilibrium(:,2)+p.wCS*ctx, p.MS, p.BS), ...
        activation(p.wSG*equilibrium(:,1)-p.wGG*equilibrium(:,2) ...
            -p.wXG*p.Str, p.MG, p.BG)];
    maxResidual = max(abs(residual), [], 'all');
    assert(maxResidual < 1e-7, 'Frozen-equilibrium root residual is too large.');
    assert(all(isfinite(rates), 'all'), 'DDE returned nonfinite rates.');

    item.name = caseNames{k};
    item.t = t;
    item.cortex = ctx;
    item.rates = rates;             % Columns: STN, GPe [spikes/s].
    item.equilibrium = equilibrium; % Columns: STN*, GPe* [spikes/s].
    item.trackingError = error;
    item.initialHistory = history;
    item.solution = solution;
    item.maxEquilibriumResidual = maxResidual;
    item.rmsTrackingError = sqrt(trapz(t, error.^2, 1)/cfg.duration);
    item.finalRates = rates(end,:);
    item.finalEquilibrium = equilibrium(end,:);
    results.cases(k) = item;
    fprintf('%s: final equilibrium [%.6f %.6f], rates [%.6f %.6f] spikes/s\n', ...
        item.name, item.finalEquilibrium, item.finalRates);
    fprintf('  RMS difference [STN GPe] = [%.6g %.6g]; equilibrium residual %.3g\n', ...
        item.rmsTrackingError, maxResidual);
end

if makePlots
    if ~isfolder(cfg.outputDirectory), mkdir(cfg.outputDirectory); end
    fig = plot_cases(results.cases, [0 cfg.duration]);
    exportgraphics(fig, fullfile(cfg.outputDirectory, 'cortex_equilibrium_comparison.png'), ...
        'Resolution', 180);
    exportgraphics(fig, fullfile(cfg.outputDirectory, 'cortex_equilibrium_comparison.pdf'), ...
        'ContentType', 'vector');
    % Resolve the individual beta cycles in a second, short-time view.
    if isempty(cfg.cortex)
        zoomFigure = plot_cases(results.cases(end), [max(0,cfg.duration-0.25) cfg.duration]);
        exportgraphics(zoomFigure, fullfile(cfg.outputDirectory, 'beta_zoom.png'), 'Resolution', 180);
    end
    save(fullfile(cfg.outputDirectory, 'cortex_equilibrium_results.mat'), 'results');
end
end

function derivative = model_rhs(time, rates, delayed, cortex, p, lagIndex)
qS = -p.wGS*delayed(2,lagIndex(1)) + p.wCS*cortex(time);
qG = p.wSG*delayed(1,lagIndex(2)) - p.wGG*delayed(2,lagIndex(3)) - p.wXG*p.Str;
derivative = [(activation(qS,p.MS,p.BS)-rates(1))/p.tauS; ...
              (activation(qG,p.MG,p.BG)-rates(2))/p.tauG];
end

function rates = frozen_equilibrium(ctx, p)
% Eliminate S to solve a scalar equation for G. The residual is strictly
% increasing for these nonnegative weights, giving a unique bracketed root.
stn = @(g) activation(-p.wGS*g+p.wCS*ctx, p.MS, p.BS);
residual = @(g) g-activation(p.wSG*stn(g)-p.wGG*g-p.wXG*p.Str, p.MG, p.BG);
g = fzero(residual, [0 p.MG], optimset('TolX',1e-12,'Display','off'));
rates = [stn(g); g];
end

function rate = activation(input, maximum, baseline)
% Same logistic as main.tex. Tanh avoids exponential overflow.
midpoint = (maximum/4)*log((maximum-baseline)/baseline);
rate = (maximum/2)*(1+tanh(2*(input-midpoint)/maximum));
end

function value = smooth_step(s)
s = min(1, max(0, s));
value = s.^2.*(3-2*s);
end

function fig = plot_cases(cases, interval)
fig = figure('Color','w','Position',[50 50 420*numel(cases) 940]);
layout = tiledlayout(fig,4,numel(cases),'TileSpacing','compact','Padding','compact');
colors = [0.08 0.40 0.72; 0.80 0.28 0.12];
for k = 1:numel(cases)
    c = cases(k);
    ax = nexttile(layout,k);
    plot(ax,c.t,c.cortex,'Color',[0.2 0.5 0.25],'LineWidth',1.2);
    title(ax,c.name); ylabel(ax,'Cortex [spikes/s]');
    xlim(ax,interval); grid(ax,'on');
    for j = 1:2
        ax = nexttile(layout,j*numel(cases)+k);
        plot(ax,c.t,c.rates(:,j),'Color',colors(j,:),'LineWidth',1.1); hold(ax,'on');
        plot(ax,c.t,c.equilibrium(:,j),'k--','LineWidth',1.4);
        populations = {'STN','GPe'};
        ylabel(ax,sprintf('%s [spikes/s]',populations{j}));
        xlim(ax,interval); grid(ax,'on');
        if k == 1 && j == 1
            legend(ax,{'Firing rate','Frozen equilibrium'},'Location','best');
        end
    end
    ax = nexttile(layout,3*numel(cases)+k);
    plot(ax,c.t,c.trackingError(:,1),'Color',colors(1,:),'LineWidth',1); hold(ax,'on');
    plot(ax,c.t,c.trackingError(:,2),'Color',colors(2,:),'LineWidth',1);
    yline(ax,0,'k:'); xlim(ax,interval); grid(ax,'on');
    xlabel(ax,'Time [s]'); ylabel(ax,'Rate - equilibrium [spikes/s]');
    if k == 1, legend(ax,{'STN','GPe'},'Location','best'); end
end
title(layout,'Exogenous cortical drive; open loop (u = 0)');
end
