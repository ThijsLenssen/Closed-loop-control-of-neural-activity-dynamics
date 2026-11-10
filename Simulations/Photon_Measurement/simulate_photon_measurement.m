function results = simulate_photon_measurement(makePlots)
%SIMULATE_PHOTON_MEASUREMENT Compare a finite-domain PDE and convolution.
% Run from this folder:
%   results = simulate_photon_measurement;
% Pass false to calculate without making figures.
%
% Derived mean measurement model (not a PDE proposed in Wilt et al., 2013):
%   z_t + z_a = -z/tau,       0 < a < L,
%   z(t,0) = r(t) + z(t,L),   z(0,a) = 0,
%   S_PDE(t) = F0 + A * integral_0^L z(t,a) da.
%
% Independent reference:
%   S_conv(t) = F0 + A * integral_0^t exp(-(t-s)/tau) r(s) ds.
%
% The PDE is solved using explicit conservative upwind finite volumes.
% The reference is an FFT convolution with analytically integrated weights
% for the same piecewise-constant rate input. It is not calculated from
% the PDE state or by integrating the equivalent scalar ODE.
%
% All simulated inputs are ordinary locally square-integrable signals.
% The single-spike exponential is a reference curve, not a Dirac input.
% Outputs are MEAN photon fluxes; this comparison does not add shot noise.

if nargin < 1
    makePlots = true;
end

% Parameters: tau is an example from the paper; the other values below
% illustrate the model and have not been fitted to experimental data.
p.tau = 0.15;                % Indicator decay time [s].
p.A = 200;                   % Photon-flux increment per spike [photons/s].
p.F0 = 1000;                 % Baseline photon flux [photons/s].
p.L = 0.10;                  % Fixed memory-coordinate interval [s].
p.duration = 2.0;            % Simulation duration [s].
p.cells = 160;               % Fine spatial grid.
p.requestedDt = 0.000125;    % Fine time step [s], further reduced for CFL.
p.cflSafety = 0.45;          % Keeps transport + decay update positive.
p.pulseStart = 0.05;         % Finite-pulse onset [s].
p.pulseWidth = 0.005;        % Unit-area pulse duration [s].

% Replace this handle with firing-rate output from your population model.
% For sampled data, for example:
%   populationRate = @(t) interp1(tPopulation, rPopulation, t, 'linear', 0);
% Here the example remains nonnegative and is not a fitted neural model.
populationRate = @(t) 8 + 18*exp(-((t-0.55)/0.12).^2) ...
    + 14*exp(-((t-1.25)/0.18).^2) + 3*sin(2*pi*1.4*t).^2;

assert(p.tau > 0 && p.L > 0 && p.duration > 0);
assert(p.cells >= 2 && mod(p.cells, 1) == 0);
assert(p.requestedDt > 0 && p.pulseWidth > 0);
assert(p.pulseStart >= 0 && ...
    p.pulseStart + p.pulseWidth < p.duration);

fine = solveCases(p, populationRate, true);
coarseParameters = p;
coarseParameters.cells = p.cells/2;
coarseParameters.requestedDt = 2*p.requestedDt;
coarse = solveCases(coarseParameters, populationRate, false);

% Meaningful checks: pulse area, analytic finite-pulse response, constant
% rate response, positivity, and improvement under time/grid refinement.
results.parameters = p;
results.cases = fine;
results.coarseCases = coarse;
for j = 1:numel(fine)
    scale = max(1, max(abs(fine(j).fluorescenceConvolution-p.F0)));
    assert(fine(j).relativeMaxError < 0.005, ...
        'PDE/convolution discrepancy exceeds 0.5%%.');
    assert(fine(j).minimumState >= -1e-10, ...
        'The upwind solution lost positivity.');
    assert(fine(j).maxAbsError < 0.65*coarse(j).maxAbsError, ...
        'Refinement did not reduce the output discrepancy as expected.');
    fprintf('%s\n', fine(j).name);
    fprintf('  fine dt = %.6g s, CFL including decay = %.4f\n', ...
        fine(j).dt, fine(j).combinedCfl);
    fprintf('  max PDE/convolution error = %.6g photons/s (%.4f%% of increment)\n', ...
        fine(j).maxAbsError, 100*fine(j).maxAbsError/scale);
    fprintf('  coarse/fine error ratio = %.3f\n', ...
        coarse(j).maxAbsError/fine(j).maxAbsError);
end

area = sum(fine(1).rate)*fine(1).dt;
assert(abs(area-1) < 1e-12, 'Finite pulse must have unit area.');
t = fine(1).time;
t0 = fine(1).actualPulseStart;
width = fine(1).actualPulseWidth;
% Stable analytic convolution for a finite-width rectangular pulse.
u = max(t-t0, 0);
v = min(u, width);
analyticPulse = p.F0 + p.A*p.tau/width ...
    .* exp(-(u-v)/p.tau) .* (-expm1(-v/p.tau));
pulseReferenceError = max(abs(analyticPulse-fine(1).fluorescenceConvolution));
assert(pulseReferenceError < 1e-9*max(1,max(analyticPulse)), ...
    'FFT convolution disagrees with the analytic finite-pulse response.');
constantRate = 12;
constantReference = integratedConvolution( ...
    constantRate*ones(numel(t)-1,1), fine(1).dt, p.tau, p.A);
constantAnalytic = p.A*constantRate*p.tau*(-expm1(-t/p.tau));
assert(max(abs(constantReference-constantAnalytic)) < ...
    1e-9*max(1,max(abs(constantAnalytic))), ...
    'FFT convolution disagrees with the analytic constant-rate response.');
results.pulseArea = area;
results.analyticPulseReferenceError = pulseReferenceError;
fprintf('Unit-pulse area = %.12f spikes; analytic reference check passed.\n', area);

outputFolder = fullfile(fileparts(mfilename('fullpath')), 'output');
if ~isfolder(outputFolder)
    mkdir(outputFolder);
end
if makePlots
    makeComparisonFigure(fine, p, outputFolder);
    makeStateFigure(fine, p, outputFolder);
    makeStepComparisonFigure(fine(1), p, outputFolder);
end
save(fullfile(outputFolder, 'photon_measurement_results.mat'), 'results');
fprintf('Results saved in %s\n', outputFolder);
end

function cases = solveCases(p, populationRate, keepState)
da = p.L/p.cells;
dtLimit = p.cflSafety/(1/da + 1/p.tau);
steps = ceil(p.duration/min(p.requestedDt, dtLimit));
dt = p.duration/steps;
t = (0:steps)'*dt;
a = ((1:p.cells)'-0.5)*da;
saveEvery = max(1, ceil(steps/700));
snapshotSteps = unique([0:saveEvery:steps, steps]);

for j = 1:2
    if j == 1
        first = round(p.pulseStart/dt);
        pulseSteps = max(1, round(p.pulseWidth/dt));
        width = pulseSteps*dt;
        rate = zeros(steps,1);
        rate(first+(1:pulseSteps)) = 1/width;
        caseName = 'Finite unit-area pulse';
    else
        rate = populationRate(t(1:end-1));
        rate = rate(:);
        caseName = 'Illustrative population firing rate';
    end
    assert(numel(rate) == steps && all(isfinite(rate)) && all(rate >= 0), ...
        'Rate must give one finite nonnegative value per time interval.');

    z = zeros(p.cells,1);
    cPde = zeros(steps+1,1);
    minimumState = 0;
    if keepState
        history = zeros(p.cells,numel(snapshotSteps));
        nextSnapshot = 2;
    end
    for k = 1:steps
        % Incoming left-face value includes recirculation from the right.
        upstream = [z(end)+rate(k); z(1:end-1)];
        z = z + dt*((upstream-z)/da-z/p.tau);
        cPde(k+1) = p.A*da*sum(z);
        minimumState = min(minimumState,min(z));
        if keepState && nextSnapshot <= numel(snapshotSteps) ...
                && k == snapshotSteps(nextSnapshot)
            history(:,nextSnapshot) = z;
            nextSnapshot = nextSnapshot+1;
        end
    end

    cConvolution = integratedConvolution(rate, dt, p.tau, p.A);
    error = cPde-cConvolution;
    record.name = caseName;
    record.time = t;
    record.rate = rate;
    record.dt = dt;
    record.combinedCfl = dt*(1/da+1/p.tau);
    record.fluorescencePde = p.F0+cPde;
    record.fluorescenceConvolution = p.F0+cConvolution;
    record.error = error;
    record.maxAbsError = max(abs(error));
    record.relativeMaxError = record.maxAbsError/max(1,max(abs(cConvolution)));
    record.minimumState = minimumState;
    record.singleSpikeReference = [];
    record.heavisideStep = [];
    record.actualPulseStart = [];
    record.actualPulseWidth = [];
    record.coordinate = a;
    record.stateTime = [];
    record.state = [];
    if j == 1
        record.actualPulseStart = first*dt;
        record.actualPulseWidth = width;
        elapsed = t-record.actualPulseStart;
        record.heavisideStep = double(elapsed >= 0);
        record.singleSpikeReference = p.F0 ...
            + p.A*exp(-max(elapsed,0)/p.tau).*record.heavisideStep;
    end
    if keepState
        record.stateTime = t(snapshotSteps+1);
        record.state = history;
    end
    cases(j) = record; %#ok<AGROW>
end
end

function c = integratedConvolution(rate, dt, tau, amplitude)
% For ZOH input, integrate the exponential kernel over each time cell.
n = numel(rate);
weights = tau*(-expm1(-dt/tau))*exp(-(0:n-1)'*dt/tau);
nFft = 2^nextpow2(2*n-1);
fullConvolution = real(ifft(fft(rate,nFft).*fft(weights,nFft)));
c = [0; amplitude*fullConvolution(1:n)];
end

function makeComparisonFigure(cases, p, outputFolder)
fig = figure('Name','PDE and exponential convolution', ...
    'Color','w','Position',[60 80 1450 780]);
layout = tiledlayout(fig,2,3,'TileSpacing','compact','Padding','compact');
title(layout,'Same firing-rate input: PDE versus exponential convolution');
subtitle(layout,sprintf('tau = %.3g s, L = %.3g s; mean fluorescence, zero initial state', ...
    p.tau,p.L));

for j = 1:numel(cases)
    d = cases(j);
    yTop = max([d.fluorescencePde;d.fluorescenceConvolution]);
    if j == 1
        yTop = max(yTop,max(d.singleSpikeReference));
    end
    limits = [p.F0-0.04*(yTop-p.F0), p.F0+1.08*(yTop-p.F0)];
    ax = nexttile(layout,(j-1)*3+1);
    plot(ax,d.time,d.fluorescencePde,'Color',[0 0.42 0.72],'LineWidth',1.6);
    title(ax,{d.name,'PDE output'});
    ylabel(ax,'Mean photon flux [photons/s]');
    xlabel(ax,'Time [s]'); grid(ax,'on'); ylim(ax,limits);

    ax = nexttile(layout,(j-1)*3+2);
    plot(ax,d.time,d.fluorescenceConvolution,'Color',[0.85 0.32 0.1],'LineWidth',1.6);
    title(ax,'Exponential convolution');
    ylabel(ax,'Mean photon flux [photons/s]');
    xlabel(ax,'Time [s]'); grid(ax,'on'); ylim(ax,limits);

    ax = nexttile(layout,(j-1)*3+3);
    plot(ax,d.time,d.fluorescencePde,'Color',[0 0.42 0.72],'LineWidth',1.8);
    hold(ax,'on');
    plot(ax,d.time,d.fluorescenceConvolution,'--', ...
        'Color',[0.85 0.32 0.1],'LineWidth',1.4);
    labels = {'PDE','Convolution'};
    if j == 1
        plot(ax,d.time,d.singleSpikeReference,':k','LineWidth',1.3);
        labels{end+1} = 'Paper: single-spike exponential';
    end
    title(ax,sprintf('Overlay; max numerical difference %.3g photons/s',d.maxAbsError));
    legend(ax,labels,'Location','northeast','FontSize',8);
    ylabel(ax,'Mean photon flux [photons/s]');
    xlabel(ax,'Time [s]'); grid(ax,'on'); ylim(ax,limits);
end
exportgraphics(fig,fullfile(outputFolder,'fluorescence_comparison.png'),'Resolution',160);
savefig(fig,fullfile(outputFolder,'fluorescence_comparison.fig'));
end

function makeStateFigure(cases, p, outputFolder)
fig = figure('Name','Rate inputs and PDE states', ...
    'Color','w','Position',[100 100 1150 760]);
layout = tiledlayout(fig,2,2,'TileSpacing','compact','Padding','compact');
title(layout,'Finite-energy inputs and distributed measurement states');
subtitle(layout,'The pulse has unit area; the population input is illustrative');
for j = 1:numel(cases)
    d = cases(j);
    ax = nexttile(layout,(j-1)*2+1);
    stairs(ax,d.time,[d.rate;d.rate(end)],'LineWidth',1.3);
    title(ax,d.name); xlabel(ax,'Time [s]');
    ylabel(ax,'Firing rate [spikes/s]'); grid(ax,'on');
    if j == 1
        xlim(ax,[max(0,d.actualPulseStart-2*d.actualPulseWidth), ...
            d.actualPulseStart+5*d.actualPulseWidth]);
    end
    ax = nexttile(layout,(j-1)*2+2);
    imagesc(ax,d.stateTime,d.coordinate,d.state);
    axis(ax,'xy'); ylim(ax,[0 p.L]);
    title(ax,'PDE state z(t,a)'); xlabel(ax,'Time [s]');
    ylabel(ax,'Memory coordinate a [s]'); colorbar(ax);
end
exportgraphics(fig,fullfile(outputFolder,'rate_inputs_and_pde_states.png'),'Resolution',160);
savefig(fig,fullfile(outputFolder,'rate_inputs_and_pde_states.fig'));
end

function makeStepComparisonFigure(d, p, outputFolder)
% Separate the Heaviside gate from the complete fluorescence response.
% The PDE receives a finite-width unit-area pulse, not the step shown in
% the first panel. Consequently its continuous rise approximates the
% paper's instantaneous onset rather than reproducing that jump exactly.
elapsed = d.time-d.actualPulseStart;
paperIncrement = d.singleSpikeReference-p.F0;
pdeIncrement = d.fluorescencePde-p.F0;
convolutionIncrement = d.fluorescenceConvolution-p.F0;
fullWindow = [-min(0.01,d.actualPulseStart), ...
    min(6*p.tau,p.duration-d.actualPulseStart)];
onsetWindow = [-min(0.01,d.actualPulseStart), ...
    min(max(5*d.actualPulseWidth,0.02),p.duration-d.actualPulseStart)];

fig = figure('Name','Heaviside gate, paper response, and PDE', ...
    'Color','w','Position',[140 120 1250 780]);
layout = tiledlayout(fig,2,2,'TileSpacing','compact','Padding','compact');
title(layout,'How the step function relates to the PDE response');
subtitle(layout,'The step gates the paper response; the PDE input is a finite unit-area pulse');

ax = nexttile(layout,1);
stairs(ax,elapsed,d.heavisideStep,'k','LineWidth',1.8);
title(ax,'Step function \theta(t-t_0)');
xlabel(ax,'Time since onset t-t_0 [s]');
ylabel(ax,'Dimensionless gate');
xlim(ax,onsetWindow); ylim(ax,[-0.05 1.15]); grid(ax,'on');

ax = nexttile(layout,2);
plot(ax,elapsed,paperIncrement,'k','LineWidth',1.8);
title(ax,'Paper: A exp(-(t-t_0)/\tau) \theta(t-t_0)');
xlabel(ax,'Time since onset t-t_0 [s]');
ylabel(ax,'Fluorescence above baseline [photons/s]');
xlim(ax,fullWindow); ylim(ax,[-0.04*p.A 1.12*p.A]); grid(ax,'on');

ax = nexttile(layout,3);
hold(ax,'on');
patch(ax,[0 d.actualPulseWidth d.actualPulseWidth 0], ...
    [-0.04 -0.04 1.12 1.12]*p.A,[0.6 0.6 0.6], ...
    'FaceAlpha',0.15,'EdgeColor','none','HandleVisibility','off');
plot(ax,elapsed,pdeIncrement,'Color',[0 0.42 0.72],'LineWidth',1.8);
plot(ax,elapsed,convolutionIncrement,'--','Color',[0.85 0.32 0.1],'LineWidth',1.4);
plot(ax,elapsed,paperIncrement,':k','LineWidth',1.5);
title(ax,sprintf('Onset zoom: shaded pulse lasts %.1f ms',1000*d.actualPulseWidth));
xlabel(ax,'Time since onset t-t_0 [s]');
ylabel(ax,'Fluorescence above baseline [photons/s]');
xlim(ax,onsetWindow); ylim(ax,[-0.04*p.A 1.12*p.A]); grid(ax,'on');
legend(ax,{'PDE: finite pulse','Convolution: finite pulse', ...
    'Paper: single-spike response'},'Location','southeast','FontSize',8);

ax = nexttile(layout,4);
plot(ax,elapsed,pdeIncrement,'Color',[0 0.42 0.72],'LineWidth',1.8);
hold(ax,'on');
plot(ax,elapsed,convolutionIncrement,'--','Color',[0.85 0.32 0.1],'LineWidth',1.4);
plot(ax,elapsed,paperIncrement,':k','LineWidth',1.5);
title(ax,'Full fluorescence response');
xlabel(ax,'Time since onset t-t_0 [s]');
ylabel(ax,'Fluorescence above baseline [photons/s]');
xlim(ax,fullWindow); ylim(ax,[-0.04*p.A 1.12*p.A]); grid(ax,'on');
legend(ax,{'PDE: finite pulse','Convolution: finite pulse', ...
    'Paper: single-spike response'},'Location','northeast','FontSize',8);

exportgraphics(fig,fullfile(outputFolder,'theta_exponential_and_pde.png'),'Resolution',160);
savefig(fig,fullfile(outputFolder,'theta_exponential_and_pde.fig'));
end
