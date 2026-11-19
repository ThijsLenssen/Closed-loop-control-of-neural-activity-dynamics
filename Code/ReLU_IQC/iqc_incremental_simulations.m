function simulations = iqc_incremental_simulations(sys,results,lower,upper)
%IQC_INCREMENTAL_SIMULATIONS Compare pairs of actual closed-loop trajectories.
% Without limits, simulate ReLU. With limits, simulate direct clipping.
% In both examples the performance output difference is the state difference.
saturated = nargin >= 4;
if saturated
    lower = lower(:).';
    upper = upper(:).';
    name = 'Saturation';
else
    name = 'ReLU';
end
n = size(sys.A,1);
nd = size(sys.E,2);
direction = ones(nd,1);
time = (0:.05:60).';
pulse = @(t) .5*(1-cos(pi*min(max(min(t,40-t),0),1)));
commonInput = @(t) (1+.3*sin(.65*t))*pulse(t)*direction;
addedInput = @(t) (3*pulse(t))*direction;
zeroInput = @(t) zeros(nd,1);
initialOffset = linspace(1.4,-.7,n).';
odeOptions = odeset('RelTol',1e-8,'AbsTol',1e-10,'MaxStep',.05);

simulations.common = simulatePair(sys.xeq+initialOffset,sys.xeq-initialOffset,zeroInput);
simulations.forced = simulatePair(sys.xeq,sys.xeq,addedInput);
valid = isfinite(results.Gamma) & results.pinf==0 & results.dinf==0 & results.numerr==0;
simulations.gainBound = NaN;
if any(valid), simulations.gainBound = min(results.Gamma(valid)); end
fprintf('%s, common disturbance: state gap %.4g -> %.4g.\n', ...
    name,simulations.common.gap(1),simulations.common.gap(end));
fprintf('%s, different disturbances: final incremental energy ratio %.6g.\n', ...
    name,simulations.forced.energyRatio(end));

simulations.figure = figure('Name',[name ' incremental simulations'], ...
    'Color','w','Position',[100 100 1100 680]);
tiledlayout(2,2,'TileSpacing','compact','Padding','compact');
nexttile;
semilogy(time,max(simulations.common.gap,1e-12),'LineWidth',1.5);
grid on; xlim([time(1) 25]); xlabel('Time'); ylabel('||x - xhat||_2');
title('Same disturbance, different initial states');

response = simulations.forced;
nexttile; hold on;
plot(time,vecnorm(response.deltaD,2,2),':','LineWidth',1.5,'DisplayName','Input difference');
plot(time,response.gap,'LineWidth',1.5,'DisplayName','State difference');
grid on; xlabel('Time'); ylabel('Euclidean norm');
title('Same initial state, different disturbances'); legend('Location','best');

nexttile; hold on;
if saturated
    shownSlopes = response.slopes(:,[1 size(sys.C,1)+1]);
    plot(time,shownSlopes(:,1),'LineWidth',1.6,'DisplayName','Lower threshold');
    plot(time,shownSlopes(:,2),'--','LineWidth',1.6,'DisplayName','Upper threshold');
    title('Actuator 1: upper secant never exceeds lower');
else
    for k = 1:size(response.slopes,2)
        plot(time,response.slopes(:,k),'LineWidth',1.4,'DisplayName',sprintf('ReLU %d',k));
    end
    title('ReLU secant slopes along the two trajectories');
end
grid on; ylim([-.08 1.08]); xlabel('Time'); ylabel('Secant slope'); legend('Location','best');

nexttile; hold on;
plot(time,response.energyRatio,'LineWidth',1.5,'DisplayName','Measured ratio');
if saturated
    withoutOrdering = valid & strcmp(results.QC,'M12inc4');
    if any(withoutOrdering)
        baseline = min(results.Gamma(withoutOrdering));
        yline(baseline,':','Color',[.55 .3 .16],'LineWidth',1.4, ...
            'DisplayName',sprintf('Without slope ordering %.4f',baseline));
    end
end
if isfinite(simulations.gainBound)
    yline(simulations.gainBound,'k--','LineWidth',1.4, ...
        'DisplayName',sprintf('IQC bound %.4f',simulations.gainBound));
end
grid on; xlabel('Horizon T'); ylabel('||\Delta z||_{L_2} / ||\Delta d||_{L_2}');
title('Incremental gain from equal initial states'); legend('Location','best');

simulations.trajectoryFigure = figure('Name',[name ' state trajectories'], ...
    'Color','w','Position',[120 120 1080 660]);
layout = tiledlayout(n,2,'TileSpacing','compact','Padding','compact');
columnTitles = {'Shared disturbance, different initial states', ...
    'Different disturbances, same initial state'};
runs = {simulations.common,simulations.forced};
for k = 1:n
    for column = 1:2
        ax = nexttile(layout);
        pair = runs{column};
        hold(ax,'on');
        plot(ax,pair.t,pair.x(:,k),'-','Color',[0 .32 .66],'LineWidth',1.7, ...
            'DisplayName','Trajectory x');
        plot(ax,pair.t,pair.reference(:,k),'--','Color',[.76 .29 .06],'LineWidth',1.5, ...
            'DisplayName','Trajectory xhat');
        grid(ax,'on');
        xlim(ax,[pair.t(1) pair.t(end)]);
        ylabel(ax,sprintf('State %d',k));
        if k == 1
            title(ax,columnTitles{column});
            if column == 1, legendAxes = ax; end
        end
    end
end
key = legend(legendAxes,'Orientation','horizontal');
key.Layout.Tile = 'south';
xlabel(layout,'Time');
title(layout,[name ' state trajectories']);

    function data = simulatePair(initialX,initialReference,deltaInput)
        [~,q] = ode45(@derivative,time,[initialX;initialReference;0;0],odeOptions);
        data.t = time;
        data.x = q(:,1:n);
        data.reference = q(:,n+1:2*n);
        data.gap = vecnorm(data.x-data.reference,2,2);
        data.deltaD = zeros(numel(time),nd);
        for j = 1:numel(time), data.deltaD(j,:) = deltaInput(time(j)).'; end
        data.inputEnergy = max(q(:,2*n+1),0);
        data.outputEnergy = max(q(:,2*n+2),0);
        data.energyRatio = NaN(size(time));
        active = data.inputEnergy>1e-10;
        data.energyRatio(active) = sqrt(data.outputEnergy(active)./data.inputEnergy(active));

        v = data.x*sys.C.'+sys.b.';
        vReference = data.reference*sys.C.'+sys.b.';
        if saturated
            v = [v-lower v-upper];
            vReference = [vReference-lower vReference-upper];
        end
        deltaV = v-vReference;
        deltaW = max(v,0)-max(vReference,0);
        data.slopes = NaN(size(deltaV));
        measurable = abs(deltaV)>1e-8;
        data.slopes(measurable) = deltaW(measurable)./deltaV(measurable);

        function dq = derivative(t,q)
            x = q(1:n);
            reference = q(n+1:2*n);
            d = commonInput(t);
            dd = deltaInput(t);
            e = x-reference;
            dq = [rhs(x,d+dd); rhs(reference,d); dd.'*dd; e.'*e];
        end
    end

    function dx = rhs(x,d)
        v = sys.C*x+sys.b;
        if saturated
            u = min(max(v,lower.'),upper.');
        else
            u = max(v,0);
        end
        dx = sys.A*x+sys.B*u+sys.E*d+sys.f;
    end
end
