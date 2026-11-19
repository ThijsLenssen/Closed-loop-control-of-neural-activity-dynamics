function simulations = saturation_iqc_simulations(sys,lower,upper,gamma)
%SATURATION_IQC_SIMULATIONS Free decay, forced responses, and a gain comparison.
% gamma is an optional IQC upper bound; use NaN to omit it.
if nargin < 4, gamma = NaN; end
n = size(sys.A,1); p = size(sys.C,1); nd = size(sys.E,2);
if ~isfield(sys,'xeq'), sys.xeq = zeros(n,1); end
xeq = sys.xeq(:);
lower = lower(:).*ones(p,1); upper = upper(:).*ones(p,1);

%% Simulation settings
time = (0:0.01:30).';
initialDirection = linspace(2,-1.5,n).';
initialStates = [xeq+initialDirection, xeq-initialDirection];
amplitudes = [0.1 3];                       % weak and strongly saturating input
burstDuration = 12;
zeroInput = @(t) zeros(nd,1);

%% Free decay: nonzero initial deviation, d=0
simulations.free = cell(1,size(initialStates,2));
for k = 1:size(initialStates,2)
    simulations.free{k} = saturation_simulate(sys,lower,upper,zeroInput,initialStates(:,k),time);
    response = simulations.free{k};
    fprintf('Free run %d: state-error norm %.4g -> %.4g at t=%.1f.\n', ...
        k,response.errorNorm(1),response.errorNorm(end),response.t(end));
end

%% Forced response: x(0)=xeq, as required for the induced-gain comparison
simulations.forced = cell(1,numel(amplitudes));
for k = 1:numel(amplitudes)
    amplitude = amplitudes(k);
    disturbance = @(t) amplitude*(sin(0.8*t)+0.4*sin(1.7*t)) ...
        *sin(pi*t/burstDuration)^2*(t<=burstDuration)*ones(nd,1);
    simulations.forced{k} = saturation_simulate(sys,lower,upper,disturbance,xeq,time);
    fprintf('Forced run, amplitude %.2g: measured finite-horizon ratio %.6g.\n', ...
        amplitude,simulations.forced{k}.energyRatio(end));
end
simulations.gainBound = gamma;
simulations.amplitudes = amplitudes;

%% Plots: simulations illustrate the bound; they do not prove stability/gain
simulations.figure = figure('Name','Saturation simulations','Color','w', ...
    'Position',[100 100 1200 760]);
tiledlayout(2,2,'TileSpacing','compact','Padding','compact');

nexttile; hold on;
for k = 1:numel(simulations.free)
    response = simulations.free{k};
    semilogy(response.t,max(response.errorNorm,1e-12),'LineWidth',1.4, ...
        'DisplayName',sprintf('Initial state %d',k));
end
set(gca,'YScale','log'); grid on;
xlabel('Time'); ylabel('||x-x_{eq}||_2');
title('No disturbance: convergence to equilibrium'); legend('Location','best');

response = simulations.forced{end};
nexttile; hold on;
for j = 1:nd
    plot(response.t,response.d(:,j),'LineWidth',1.2,'DisplayName',sprintf('d_%d',j));
end
plot(response.t,sqrt(sum(response.z.^2,2)),'k','LineWidth',1.5,'DisplayName','||z||_2');
grid on; xlabel('Time'); ylabel('Amplitude');
title('Large disturbance: input and performance output'); legend('Location','best');

nexttile; hold on;
colors = lines(p);
for j = 1:p
    plot(response.t,response.v(:,j),':','Color',colors(j,:),'LineWidth',1.1, ...
        'DisplayName',sprintf('v_%d (before saturation)',j));
    plot(response.t,response.u(:,j),'-','Color',colors(j,:),'LineWidth',1.5, ...
        'DisplayName',sprintf('u_%d (after saturation)',j));
    yline(lower(j),'--','Color',colors(j,:),'HandleVisibility','off');
    yline(upper(j),'--','Color',colors(j,:),'HandleVisibility','off');
end
grid on; xlabel('Time'); ylabel('Saturation input / output');
title('Actual clipping; dashed lines are the limits'); legend('Location','best');

nexttile; hold on;
for k = 1:numel(amplitudes)
    response = simulations.forced{k};
    plot(response.t,response.energyRatio,'LineWidth',1.5, ...
        'DisplayName',sprintf('Measured, amplitude %.2g',amplitudes(k)));
end
if isfinite(gamma)
    yline(gamma,'k--','LineWidth',1.5,'DisplayName',sprintf('IQC bound %.4f',gamma));
end
grid on; xlabel('Horizon T'); ylabel('sqrt(E_z(T) / E_d(T))');
title('Finite-horizon energy ratios, x(0)=x_{eq}'); legend('Location','best');
end
