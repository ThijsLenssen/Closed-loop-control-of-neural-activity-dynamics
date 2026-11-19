function [parameters,fig] = sigmoid_relu_uncertainty_example(Kd)
%SIGMOID_RELU_UNCERTAINTY_EXAMPLE Align saturation and sigmoid midpoints.
% Run: [parameters,fig] = sigmoid_relu_uncertainty_example;
% Kd selects the paper's operating point (default 1). No SDP solver needed.
% F(q) = M/2 + theta(q)*sat_[-M/2,M/2](q-c), theta in [tanh(1),1].
if nargin < 1, Kd = 1; end
here = fileparts(mfilename('fullpath'));
addpath(fullfile(here,'..','Controller Synthesis','Example_4'));
[~,~,~,operatingPoint] = stn_gpe_equilibrium(Kd);
M = [operatingPoint.MS operatingPoint.MG];
B = [operatingPoint.BS operatingPoint.BG];
q0 = [operatingPoint.uS0 operatingPoint.uG0];
names = {'STN','GPe'};
alpha = tanh(1);
rows = cell(2,10);
fig = figure('Name','Sigmoid and saturation with the same center','Color','w', ...
    'Position',[50 50 1500 820]);
tiledlayout(2,3,'TileSpacing','compact','Padding','compact');

for i = 1:2
    h = M(i)/2;
    c = M(i)/4*log((M(i)-B(i))/B(i));
    q = unique([c+linspace(-2*M(i),2*M(i),1601),c-h,c,c+h,q0(i)]);
    [f,s,theta] = sigmoid_saturation(q,0,M(i),c);
    [f0,s0,theta0] = sigmoid_saturation(q0(i),0,M(i),c);
    reconstructed = h+theta.*s;
    error = max(abs(f-reconstructed));
    assert(all(theta>=alpha-1e-12 & theta<=1+1e-12),'Gain outside bounds.');
    assert(error<1e-10*M(i),'Reconstruction failed.');
    % Compare against the original paper's logistic parameterization.
    original = M(i)./(1+((M(i)-B(i))/B(i))*exp(-4*q/M(i)));
    assert(max(abs(f-original))<1e-10*M(i),'Sigmoid parameterization mismatch.');

    nexttile; hold on;
    lo = h+min(alpha*s,s);
    hi = h+max(alpha*s,s);
    fill([q fliplr(q)],[lo fliplr(hi)],[.87 .92 .98], ...
        'EdgeColor','none','DisplayName','Gain uncertainty envelope');
    plot(q,h+s,'--','Color',[.4 .4 .4],'LineWidth',1.2, ...
        'DisplayName','Saturation with same center');
    plot(q,f,'Color',[0 .35 .7],'LineWidth',1.8,'DisplayName','Sigmoid F(q)');
    sample = 1:100:numel(q);
    plot(q(sample),reconstructed(sample),'o','Color',[.85 .3 .1], ...
        'MarkerSize',4,'DisplayName','Gain times ReLU + offset');
    plot(c,h,'kp','MarkerFaceColor','k','MarkerSize',8,'DisplayName','Shared midpoint');
    plot(q0(i),f0,'ks','MarkerFaceColor','w','DisplayName','Operating point');
    grid on; xlabel('Input q'); ylabel('Output');
    title(sprintf('%s: common center (%.2f, %.0f)',names{i},c,h));
    legend('Location','best','FontSize',8);

    nexttile; hold on;
    plot(q,theta,'LineWidth',1.7,'DisplayName','Exact gain');
    yline(alpha,'--','DisplayName','Global lower bound tanh(1)');
    yline(1,'k--','DisplayName','Global upper bound 1');
    plot(c,1,'kp','MarkerFaceColor','k','MarkerSize',8,'DisplayName','Gain at midpoint');
    plot(q0(i),theta0,'ks','MarkerFaceColor','w','DisplayName','Gain at operating point');
    grid on; xlabel('Input q'); ylabel('Multiplicative gain');
    ylim([.7 1.03]); title(sprintf('%s: gain between %.4f and 1',names{i},alpha));
    legend('Location','best','FontSize',8);

    t = linspace(0,30,1501);
    qt = q0(i)+M(i)*(sin(.6*t)+.25*sin(1.7*t));
    [ft,st,thetat] = sigmoid_saturation(qt,0,M(i),c);
    % Correct equilibrium subtraction: do not multiply s(t)-s0 by theta(t).
    delta = ft-f0;
    deltaReconstructed = thetat.*st-theta0*s0;
    assert(max(abs(delta-deltaReconstructed))<1e-10*M(i), ...
        'Equilibrium-shifted reconstruction failed.');
    nexttile;
    yyaxis left;
    plot(t,thetat,'LineWidth',1.6,'DisplayName','Gain');
    ylim([.7 1.03]); ylabel('Time-varying gain');
    yyaxis right;
    plot(t,qt,':','LineWidth',1.1,'DisplayName','Input q(t)');
    ylabel('Input q(t)'); xlabel('Time'); grid on;
    title(sprintf('%s: gain along an example input',names{i}));
    legend('Location','best','FontSize',8);
    rows(i,:) = {names{i},M(i),B(i),q0(i),f0,c,h,alpha,1,error};
end
parameters = cell2table(rows,'VariableNames', ...
    {'Channel','M','B','InputEquilibrium','OutputEquilibrium', ...
     'InputCenter','OutputCenter','GainLower','GainUpper','MaxReconstructionError'});
disp(parameters);
fprintf('F(q) = M/2 + theta(q)*saturation_relu(q-InputCenter,-M/2,M/2).\n');
fprintf('Global gain interval: [tanh(1),1] = [%.8f,1].\n',alpha);
fprintf('Shifted output: theta(q)*s(q) - theta(q0)*s(q0).\n');
end
