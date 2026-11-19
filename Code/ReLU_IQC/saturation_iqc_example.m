function [results, programs, simulations] = saturation_iqc_example(solver,runSimulations,mode)
%SATURATION_IQC_EXAMPLE Edit the plant, limits, and options, then run.
% Use saturation_iqc_example('mosek',true,'incremental') for the ordered-QC
% primal/dual comparison and paired simulations.
if nargin < 1, solver = 'mosek'; end
if nargin < 2, runSimulations = true; end
if nargin < 3, mode = 'ordinary'; end
mode = validatestring(mode,{'ordinary','incremental'});

%% Plant: xdot=A*x+B*u+E*d+f, v=C*x+D*d+b, u=clip(v,lower,upper)
sys.A = [-1 .4; -.2 -1.2];
sys.B = [.5 -.2; .2 .3];
sys.C = [1 -.5; .4 1];
sys.E = [1; .5];
lower = [-1; -.4];                         % different, asymmetric limits
upper = [.7; 1.2];
sys.b = [.1; -.2];
sys.xeq = [.2; -.1];                       % chosen operating point
% Pick a constant drive that makes this operating point an equilibrium.
ueq = saturation_relu(sys.C*sys.xeq+sys.b,lower,upper);
sys.f = -sys.A*sys.xeq-sys.B*ueq;

if strcmp(mode,'incremental')
    p = size(sys.C,1);
    J = [eye(p) -eye(p)];
    plant = {sys.A,sys.B*J,[sys.C;sys.C],sys.E,eye(size(sys.A,1))};
    cases = {'M1inc';'M12inc';'M12inc4';'M12inc4Ordered'};
    sides = [repmat({'primal'},numel(cases),1);repmat({'dual'},numel(cases),1)];
    comparison = [sides repmat(cases,2,1) repmat({'none'},numel(sides),1)];
    [results,programs] = relu_iqc_solve_cases(plant,comparison,solver);
    disp(results);
    simulations = [];
    if runSimulations
        simulations = iqc_incremental_simulations(sys,results,lower,upper);
    end
    return
end

% Optional fields: D (d to v), Cz/Dz/Ez (performance output).
% z=Cz*(x-xeq)+Dz*(u-ueq)+Ez*d. Defaults: D=0, Cz=I, Dz=0, Ez=0.

%% Analysis options
options.solver = solver;
options.center = true;                     % centered auxiliary ReLU outputs
options.epsilon = 1e-5;
options.cases = {'M1','none'; 'M2','matrix'; 'M2','sos0'; 'M2','sos1';
    'M3','none'; 'M12','matrix'; 'M12','sos0'; 'M12','sos1';
    'Mc','matrix'; 'Mc','sos0'; 'Mc','sos1'};

[results, programs] = saturation_iqc_analysis(sys,lower,upper,options);
simulations = [];
if runSimulations
    valid = isfinite(results.Gamma) & results.pinf==0 & results.dinf==0 & results.numerr==0;
    gamma = min(results.Gamma(valid));
    if isempty(gamma), gamma = NaN; end
    simulations = saturation_iqc_simulations(sys,lower,upper,gamma);
end
end
