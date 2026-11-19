function [results,fig] = sigmoid_gain_placement_comparison
%SIGMOID_GAIN_PLACEMENT_COMPARISON Gain outside versus inside saturation.
% Normalized coordinates: r=(q-c)/h, y=(F(q)-h)/h=tanh(r), h=M/2.
% Applies to both paper sigmoids. No SDP solver or extra toolbox required.
r = linspace(-4,4,1601);
y = tanh(r);
s = saturation_relu(r,-1,1);
alpha = tanh(1);
theta = ones(size(r));
kappa = ones(size(r));
nonzero = r~=0;
theta(nonzero) = y(nonzero)./s(nonzero);
kappa(nonzero) = y(nonzero)./r(nonzero);
outside = theta.*s;
inside = saturation_relu(kappa.*r,-1,1);

% These are global envelopes for arbitrary gains in the stated intervals.
outsideLo = min(alpha*s,s);
outsideHi = max(alpha*s,s);
insideLo = min(0,s);
insideHi = max(0,s);
outsideError = max(abs(outside-y));
insideError = max(abs(inside-y));
assert(max([outsideError insideError])<1e-12,'Exact reconstruction failed.');
assert(all(y>=outsideLo-1e-12 & y<=outsideHi+1e-12),'Outside envelope failed.');
assert(all(y>=insideLo-1e-12 & y<=insideHi+1e-12),'Inside envelope failed.');
assert(all(theta>=alpha-1e-12 & theta<=1+1e-12),'Outside gain bounds failed.');
assert(all(kappa>=0 & kappa<=1+1e-12),'Inside gain bounds failed.');

blue = [0 .35 .7];
orange = [.85 .32 .08];
fig = figure('Name','Gain outside versus inside saturation','Color','w', ...
    'Position',[50 100 1500 490]);
tiledlayout(1,3,'TileSpacing','compact','Padding','compact');
sample = 1:80:numel(r);

nexttile; hold on;
fill([r fliplr(r)],[outsideLo fliplr(outsideHi)],[.85 .92 .98], ...
    'EdgeColor','none','DisplayName','All allowed output values');
plot(r,s,'--','Color',[.45 .45 .45],'DisplayName','Saturation');
plot(r,alpha*s,'--','Color',blue,'DisplayName','tanh(1) times saturation');
plot(r,y,'k','LineWidth',1.8,'DisplayName','Sigmoid tanh(r)');
plot(r(sample),outside(sample),'o','Color',blue,'MarkerSize',4, ...
    'DisplayName','Exact reconstruction');
grid on; xlim([-4 4]); ylim([-1.12 1.12]);
xlabel('Normalized input r = (q-c)/h'); ylabel('Normalized output (F-h)/h');
title({'Gain outside saturation','y = \theta sat(r),  \theta \in [tanh(1),1]'});
legend('Location','southeast','FontSize',8);

nexttile; hold on;
fill([r fliplr(r)],[insideLo fliplr(insideHi)],[.99 .89 .82], ...
    'EdgeColor','none','DisplayName','All allowed output values');
plot(r,s,'--','Color',[.45 .45 .45],'DisplayName','Saturation (gain = 1)');
plot(r,zeros(size(r)),'--','Color',orange,'DisplayName','Zero output (gain = 0)');
plot(r,y,'k','LineWidth',1.8,'DisplayName','Sigmoid tanh(r)');
plot(r(sample),inside(sample),'o','Color',orange,'MarkerSize',4, ...
    'DisplayName','Exact reconstruction');
grid on; xlim([-4 4]); ylim([-1.12 1.12]);
xlabel('Normalized input r = (q-c)/h'); ylabel('Normalized output (F-h)/h');
title({'Gain inside saturation','y = sat(\kappa r),  \kappa \in [0,1]'});
legend('Location','southeast','FontSize',8);

nexttile; hold on;
plot(r,theta,'Color',blue,'LineWidth',1.8,'DisplayName','Outside: \theta(r)');
plot(r,kappa,'Color',orange,'LineWidth',1.8,'DisplayName','Inside: \kappa(r)');
yline(alpha,'--','Color',blue,'DisplayName','Outside lower bound tanh(1)');
yline(0,'--','Color',orange,'DisplayName','Inside lower bound 0');
yline(1,':','Color',[.4 .4 .4],'HandleVisibility','off');
grid on; xlim([-4 4]); ylim([-.04 1.05]);
xlabel('Normalized input r = (q-c)/h'); ylabel('Gain');
title({'Gains that recover the exact sigmoid','Both equal 1 at the common midpoint'});
legend('Location','south','FontSize',8);

results = table({'Outside';'Inside'},[alpha;0],[1;1], ...
    [outsideError;insideError],'VariableNames', ...
    {'GainPlacement','GlobalGainLower','GlobalGainUpper','MaxReconstructionError'});
disp(results);
fprintf('Shading shows arbitrary-gain envelopes; markers reconstruct the exact sigmoid.\n');
fprintf('Both models use the same ReLU saturation function.\n');
end
