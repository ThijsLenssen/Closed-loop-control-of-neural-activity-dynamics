function [results, programs, simulations] = relu_iqc_example(solver,mode,runSimulations)
%RELU_IQC_EXAMPLE Compare the paper's ReLU QCs and COP approximations.
% Run: results = relu_iqc_example;
% Run incremental primal and dual: relu_iqc_example('mosek','incremental')
% Use 'incremental-primal' or 'incremental-dual' for one side only.
% Pass false as the third argument to skip the incremental simulations.
% Requires SOSTOOLS 4 (included with PIETOOLS) and an SDP solver.
if nargin < 1, solver = 'mosek'; end
if nargin < 2, mode = 'ordinary'; end
mode = validatestring(mode,{'ordinary','incremental','incremental-primal','incremental-dual'});

%% System: xdot = A*x + B*w + E*d, w = max(C*x,0), z = x
A = [-1 .4; -.2 -1.2];
B = 0.8*[.5 -.4 .2; .1 .3 -.5];
C = [1 0; 0 1; 1 -1];
E = [1; .5];
plant = {A,B,C,E,eye(size(A,1))};

%% Settings: edit this list to choose which comparisons to run
cases = { ...
    'M1',  'none';
    'M2',  'matrix';
    'M2',  'sos0';
    'M2',  'sos1';
    'M3',  'none';
    'M12', 'matrix';
    'M12', 'sos0';
    'M12', 'sos1';
    'Mc',  'matrix';
    'Mc',  'sos0';
    'Mc',  'sos1'};

sides = {'primal'};
if ~strcmp(mode,'ordinary')
    cases = {'M1inc','none'; 'M2inc','none'; 'M12inc','none'; ...
        'M2inc4','none'; 'M12inc4','none'; ...
        'Mcinc','matrix'; 'Mcinc','sos0'; 'Mcinc','sos1'};
    switch mode
        case 'incremental'
            sides = {'primal','dual'};
        case 'incremental-dual'
            sides = {'dual'};
    end
end

sideColumn = repelem(sides,size(cases,1));
comparison = [sideColumn(:) repmat(cases,numel(sides),1)];

[results, programs] = relu_iqc_solve_cases(plant,comparison,solver);
incremental = ~strcmp(mode,'ordinary');
if ~incremental, results.Side = []; end
disp(results);

simulations = [];
if nargin < 3, runSimulations = incremental; end
if runSimulations && incremental
    sys = struct('A',A,'B',B,'C',C,'E',E,'b',zeros(size(C,1),1), ...
        'f',zeros(size(A,1),1),'xeq',zeros(size(A,1),1));
    simulations = iqc_incremental_simulations(sys,results);
end
end
