function [results, programs] = saturation_iqc_analysis(sys,lower,upper,options)
%SATURATION_IQC_ANALYSIS Generic continuous-time saturation feedback analysis.
%   xdot = A*x + B*u + E*d + f
%   v    = C*x + D*d + b,       u = clip(v,lower,upper)
%   z    = Cz*(x-xeq) + Dz*(u-ueq) + Ez*d
% Required sys fields: A, B, C, E. Other fields have zero/identity defaults.
% lower/upper: scalars or one limit per saturation channel.
% options: solver, center (auxiliary ReLU outputs), epsilon, cases.
% Returns the gain table and raw SOSTOOLS programs; ordinary QCs only.
if nargin < 4, options = struct; end
A = sys.A; B = sys.B; C = sys.C; E = sys.E;
n = size(A,1); p = size(C,1); nd = size(E,2);
if ~isfield(sys,'D'),   sys.D = zeros(p,nd); end
if ~isfield(sys,'b'),   sys.b = zeros(p,1); end
if ~isfield(sys,'f'),   sys.f = zeros(n,1); end
if ~isfield(sys,'xeq'), sys.xeq = zeros(n,1); end
if ~isfield(sys,'Cz'),  sys.Cz = eye(n); end
nz = size(sys.Cz,1);
if ~isfield(sys,'Dz'), sys.Dz = zeros(nz,p); end
if ~isfield(sys,'Ez'), sys.Ez = zeros(nz,nd); end
if ~isfield(options,'solver'),  options.solver = 'mosek'; end
if ~isfield(options,'center'),  options.center = false; end
if ~isfield(options,'epsilon'), options.epsilon = 1e-5; end
if ~isfield(options,'cases')
    options.cases = {'M1','none'; 'M2','matrix'; 'M2','sos0'; 'M2','sos1';
        'M3','none'; 'M12','matrix'; 'M12','sos0'; 'M12','sos1';
        'Mc','matrix'; 'Mc','sos0'; 'Mc','sos1'};
end

assert(isequal(size(A),[n n]) && isequal(size(B),[n p]) ...
    && isequal(size(C),[p n]) && size(E,1)==n,'Inconsistent plant dimensions.');
assert(isequal(size(sys.D),[p nd]) && isequal(size(sys.Cz),[nz n]) ...
    && isequal(size(sys.Dz),[nz p]) && isequal(size(sys.Ez),[nz nd]), ...
    'Inconsistent feedthrough or performance-output dimensions.');
assert(numel(sys.b)==p && numel(sys.f)==n && numel(sys.xeq)==n, ...
    'b, f, and xeq must have one entry per input/state.');
assert((isscalar(lower) || numel(lower)==p) ...
    && (isscalar(upper) || numel(upper)==p),'Supply scalar limits or p limits.');
assert(isscalar(options.center) && ismember(options.center,[false true]), ...
    'options.center must be true or false.');
assert(isscalar(options.epsilon) && isfinite(options.epsilon) ...
    && options.epsilon>0,'epsilon must be positive and finite.');
lower = lower(:).*ones(p,1);
upper = upper(:).*ones(p,1);
assert(all(isfinite([lower;upper])) && all(lower<upper), ...
    'Limits must be finite and satisfy lower < upper.');
xeq = sys.xeq(:);
b = sys.b(:); f = sys.f(:);
v0 = C*xeq+b;
ueq = min(max(v0,lower),upper);
equilibriumResidual = A*xeq+B*ueq+f;
assert(norm(equilibriumResidual,inf) <= 1e-10*(1+norm(A*xeq,inf)+norm(B*ueq,inf)+norm(f,inf)), ...
    'xeq must satisfy A*xeq+B*clip(C*xeq+b,lower,upper)+f=0 at d=0.');

%% Exact affine ReLU lift
% e=x-xeq, a=[v-lower;v-upper], w=ReLU(a), u=lower+[I -I]*w.
% r=w-shift: shift=0 for raw outputs, shift=w0 for centered outputs.
% Append the known ReLU pair (1,1) to the QC. It fixes the ReLU orientation:
% homogeneous QCs alone also admit flipped ReLU, which matters with offsets.
nw = 2*p;                                  % unknown ReLU outputs
m = nw+1;                                  % include the known reference pair
J = [eye(p) -eye(p)];
a0 = [v0-lower; v0-upper];
w0 = max(a0,0);
shift = double(options.center)*w0;

% xi=[e;r;d;1]. The constant is not a state or an L2 input.
H = [C zeros(p,nw) sys.D a0(1:p);
     C zeros(p,nw) sys.D a0(p+1:end);
     zeros(1,n+nw+nd) 1;
     zeros(nw,n) eye(nw) zeros(nw,nd) shift;
     zeros(1,n+nw+nd) 1];                   % [a;1;w;1] = H*xi
X = [eye(n) zeros(n,nw+nd+1)];               % e = X*xi
W = [zeros(nd,n+nw) eye(nd) zeros(nd,1)];     % d = W*xi
F = [A B*J E A*xeq+B*(lower+J*shift)+f];     % edot = F*xi
Z = [sys.Cz sys.Dz*J sys.Ez sys.Dz*(lower+J*shift-ueq)];
eq = [zeros(n,1); w0-shift; zeros(nd,1); 1]; % equilibrium in chosen coordinates

%% Same optimization for every QC family
cases = options.cases;
epsilon = options.epsilon;
solverOptions.solver = options.solver;
y = polynomial(zeros(2*m,1));
for j = 1:2*m, y(j) = pvar(sprintf('y%d',j)); end
programs = cell(size(cases,1),1);
rows = cell(size(cases,1),7);

for k = 1:size(cases,1)
    family = cases{k,1}; method = cases{k,2};
    fprintf('\n--- Saturation: %s / %s (center=%d) ---\n',family,method,options.center);
    timer = tic;
    prog = sosprogram(y);
    [prog,P] = sospolymatrixvar(prog,polynomial(1),[n n],'symmetric');
    [prog,rho] = sospolyvar(prog,polynomial(1));
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
        otherwise
            error('Unknown QC family: %s',family);
    end

    % V=e'*P*e. The ordinary QC acts on raw [a;w], even if r is centered.
    L = X.'*P*F + F.'*P*X + Z.'*Z - rho*(W.'*W) + H.'*M*H;
    prog = sosmatrixineq(prog,P-epsilon*eye(n));
    prog = sosineq(prog,rho);
    prog = soseq(prog,L*eq);                % valid for raw AND centered outputs

    % With L*eq=0 and eq(end)=1, this principal-block inequality is equivalent
    % to the full affine inequality. Strictness is on e and d only.
    margin = epsilon*blkdiag(eye(n),zeros(nw),eye(nd));
    prog = sosmatrixineq(prog,-L(1:end-1,1:end-1)-margin);
    prog = sossetobj(prog,rho);
    prog = sossolve(prog,solverOptions);

    programs{k} = prog;
    info = prog.solinfo.info;
    gamma = NaN;
    if info.pinf == 0 && info.dinf == 0 && isfield(prog.solinfo,'RRx') ...
            && ~isempty(prog.solinfo.RRx)
        gamma = sqrt(double(sosgetsol(prog,rho)));
    end
    rows(k,:) = {family,method,gamma,info.pinf,info.dinf,info.numerr,toc(timer)};
end
results = cell2table(rows,'VariableNames', ...
    {'QC','COP','Gamma','pinf','dinf','numerr','Seconds'});
disp(results);
end
