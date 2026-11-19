function [results,programs,multipliers] = relu_iqc_dual_example(solver,methods,steps)
%RELU_IQC_DUAL_EXAMPLE Dual LMI with recovered primal multiplier in M1+M2.
% Same homogeneous ReLU system as relu_iqc_example; no affine saturation lift.
% Run: [results,programs,multipliers] = relu_iqc_dual_example;
% methods may be {'matrix'}, {'sos0'}, {'sos1'}, or a list of these.
% steps is the number of convex solves per COP method (default 6).
if nargin < 1, solver = 'mosek'; end
if nargin < 2, methods = {'matrix','sos0','sos1'}; end
if nargin < 3, steps = 6; end
validateattributes(steps,{'numeric'},{'scalar','integer','positive'});
A = [-1 .4;-.2 -1.2];
B = 0.8*[.5 -.4 .2;.1 .3 -.5];
C = [1 0;0 1;1 -1];
E = [1;.5];
n = size(A,1); m = size(C,1); nd = size(E,2); nz = n;
epsilon = 1e-5;

% Seed is the ordinary complementarity QC, with Q1=I and Q2=0.
% Each solve can update all blocks of K. The seed is not a fixed IQC factor.
I = eye(m);
seed = [zeros(m) I;I -2*I];

% G: [w;d] -> [v;z]. Its dual has Ad=A', Bd=[C' I], Cd=[B';E'].
% xi_dual=[xd;v_dual;z_dual], uncertainty graph pair=[w_dual;v_dual].
Ad = A.'; Bd = [C.' eye(n)];
Hdelta = [B.' zeros(m,m+nz);zeros(m,n) eye(m) zeros(m,nz)];
Hp = [E.' zeros(nd,m+nz);zeros(nz,n+m) eye(nz)];
y = polynomial(zeros(2*m,1));
for j=1:2*m, y(j)=pvar(sprintf('y%d',j)); end
options.solver = solver;
programs = cell(numel(methods),1);
multipliers = cell(numel(methods),1);
rows = cell(numel(methods),10);

for k=1:numel(methods)
    M0 = seed;
    timer = tic;
    gamma=NaN; minGap=NaN; maxL=NaN; maxM22=NaN; accepted=0;
    for step = 1:steps
        fprintf('\n--- dual M1+M2 / %s / step %d ---\n',methods{k},step);
        prog = sosprogram(y);
        [prog,P] = sospolymatrixvar(prog,polynomial(1),[n n],'symmetric');
        [prog,eta] = sospolyvar(prog,polynomial(1)); % eta=1/gamma^2
        [prog,Vdual,K,M12] = qc_M12_dual(prog,M0,methods{k},y,epsilon);
        Vperformance = blkdiag(eta*eye(nd),-eye(nz));
        L = [Ad.'*P+P*Ad P*Bd;Bd.'*P zeros(m+nz)] ...
            + Hdelta.'*Vdual*Hdelta + Hp.'*Vperformance*Hp;
        prog = sosmatrixineq(prog,P-epsilon*eye(n));
        prog = sosmatrixineq(prog,-L-epsilon*eye(n+m+nz));
        prog = sosineq(prog,eta-epsilon);
        prog = sossetobj(prog,-eta);
        prog = sossolve(prog,options);
        info = prog.solinfo.info;
        if accepted==0, programs{k}=prog; end
        if info.pinf~=0 || info.dinf~=0 || info.numerr~=0 ...
                || ~isfield(prog.solinfo,'RRx') || isempty(prog.solinfo.RRx)
            break
        end

        Kv = double(sosgetsol(prog,K));
        M = Kv\eye(2*m);
        M = (M+M.')/2;
        gap = M-double(sosgetsol(prog,M12));
        candidateGap = min(eig((gap+gap.')/2));
        Lv = double(sosgetsol(prog,L));
        candidateL = max(eig((Lv+Lv.')/2));
        candidateM22 = max(eig(M(m+1:end,m+1:end)));
        candidateGamma = 1/sqrt(double(sosgetsol(prog,eta)));
        if candidateGap < -1e-7 || candidateL >= 0 || candidateM22 >= 0
            warning('Dual step failed the recovered matrix checks.');
            break
        end
        if accepted>0 && candidateGamma >= gamma, break; end
        gamma = candidateGamma;
        minGap = candidateGap;
        maxL = candidateL;
        maxM22 = candidateM22;
        multipliers{k} = M;
        programs{k} = prog;
        accepted = step;
        M0 = M;
    end
    info = programs{k}.solinfo.info;
    rows(k,:) = {methods{k},gamma,info.pinf,info.dinf,info.numerr, ...
        minGap,maxL,maxM22,accepted,toc(timer)};
end
results = cell2table(rows,'VariableNames',{'COP','Gamma','pinf','dinf','numerr', ...
    'MinPrimalGapEig','MaxDualLMIEig','MaxPrimalM22Eig','AcceptedSteps','Seconds'});
disp(results);
fprintf('The recovered primal multiplier belongs to M1+M2. Each convex step uses a fixed expansion point.\n');
end
