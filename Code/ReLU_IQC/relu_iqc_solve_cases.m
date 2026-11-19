function [results,programs] = relu_iqc_solve_cases(plant,comparison,solver)
%RELU_IQC_SOLVE_CASES Solve primal and dual dissipation LMIs for one plant.
% plant contains {A,B,C,E,Cz}. comparison rows contain {side,QC,COP}.
m = size(plant{3},1);
epsilon = 1e-5;
options.solver = solver;
y = polynomial(zeros(2*m,1));
for j = 1:2*m, y(j) = pvar(sprintf('y%d',j)); end
programs = cell(size(comparison,1),1);
rows = cell(size(comparison,1),8);

%% Solve the same L2-gain problem with each QC
for k = 1:size(comparison,1)
    [side,family,method] = comparison{k,:};
    if strcmp(side,'dual')
        % Adjoint plant swaps input/output roles and transposes each block.
        % The diagonal slope family is invariant under transpose and time
        % reversal, so its QCs apply directly to the dual uncertainty pair.
        [A,B,C,E,Cz] = deal(plant{1}.',plant{3}.',plant{2}.',plant{5}.',plant{4}.');
    else
        [A,B,C,E,Cz] = plant{:};
    end
    n = size(A,1);
    nd = size(E,2);
    H = [C zeros(m,m+nd); zeros(m,n) eye(m) zeros(m,nd)];
    fprintf('\n--- %s / %s / %s ---\n',side,family,method);
    timer = tic;
    prog = sosprogram(y);
    [prog,P] = sospolymatrixvar(prog,polynomial(1),[n n],'symmetric');
    [prog,rho] = sospolyvar(prog,polynomial(1)); % rho = gamma^2

    switch family
        case 'M1'
            [prog,M] = qc_M1(prog,m);
        case 'M2'
            [prog,M] = qc_M2(prog,m,method,y);
        case 'M3'
            [prog,M] = qc_M3(prog,m);
        case 'M12'
            [prog,M1] = qc_M1(prog,m);
            [prog,M2] = qc_M2(prog,m,method,y);
            M = M1+M2;
        case 'Mc'
            [prog,M] = qc_Mc(prog,m,method,y);
        case 'M1inc'
            [prog,M] = qc_M1_inc(prog,m);
        case 'M2inc'
            [prog,M] = qc_M2_inc(prog,m);
        case 'M2inc4'
            [prog,M] = qc_M2_inc(prog,m,4);
        case {'M12inc','M12inc4','M12inc4Ordered'}
            [prog,M1] = qc_M1_inc(prog,m);
            coefficient = 2;
            if ~strcmp(family,'M12inc'), coefficient = 4; end
            [prog,M2] = qc_M2_inc(prog,m,coefficient);
            M = M1+M2;
            if strcmp(family,'M12inc4Ordered')
                [prog,Morder] = qc_saturation_order_inc(prog,m/2,side);
                M = M+Morder;
            end
        case 'Mcinc'
            [prog,M] = qc_Mc_inc(prog,m,method,y);
        otherwise
            error('Unknown QC family: %s',family);
    end

    % V=x'*P*x. Require Vdot + z'*z - rho*d'*d + [v;w]'*M*[v;w] < 0.
    L = [A.'*P+P*A+Cz.'*Cz, P*B,        P*E;
         B.'*P,           zeros(m),   zeros(m,nd);
         E.'*P,           zeros(nd,m), -rho*eye(nd)] + H.'*M*H;

    prog = sosmatrixineq(prog,P-epsilon*eye(n));
    prog = sosmatrixineq(prog,-L-epsilon*eye(n+m+nd));
    prog = sosineq(prog,rho);
    prog = sossetobj(prog,rho);
    prog = sossolve(prog,options);

    % Report the raw solver diagnostics and optimized gain.
    programs{k} = prog;
    info = prog.solinfo.info;
    gamma = NaN;
    if info.pinf == 0 && info.dinf == 0 && isfield(prog.solinfo,'RRx') ...
            && ~isempty(prog.solinfo.RRx)
        gamma = sqrt(double(sosgetsol(prog,rho)));
    end
    rows(k,:) = {side,family,method,gamma,info.pinf,info.dinf,info.numerr,toc(timer)};
end

results = cell2table(rows,'VariableNames', ...
    {'Side','QC','COP','Gamma','pinf','dinf','numerr','Seconds'});
end
