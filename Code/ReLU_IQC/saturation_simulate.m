function data = saturation_simulate(sys,lower,upper,disturbance,x0,time)
%SATURATION_SIMULATE Simulate the same physical model as saturation_iqc_analysis.
% disturbance(t) returns an nd-by-1 vector; time is an increasing time grid.
% Energies are integrated with the ODE, not approximated from plotted samples.
n = size(sys.A,1); p = size(sys.C,1); nd = size(sys.E,2);
if ~isfield(sys,'D'),   sys.D = zeros(p,nd); end
if ~isfield(sys,'b'),   sys.b = zeros(p,1); end
if ~isfield(sys,'f'),   sys.f = zeros(n,1); end
if ~isfield(sys,'xeq'), sys.xeq = zeros(n,1); end
if ~isfield(sys,'Cz'),  sys.Cz = eye(n); end
nz = size(sys.Cz,1);
if ~isfield(sys,'Dz'), sys.Dz = zeros(nz,p); end
if ~isfield(sys,'Ez'), sys.Ez = zeros(nz,nd); end
lower = lower(:).*ones(p,1); upper = upper(:).*ones(p,1);
xeq = sys.xeq(:);
ueq = min(max(sys.C*xeq+sys.b(:),lower),upper);
assert(numel(x0)==n,'x0 must have one entry per state.');
assert(numel(time)>=2 && all(diff(time(:))>0),'time must be increasing.');

odeOptions = odeset('RelTol',1e-8,'AbsTol',1e-10,'MaxStep',0.02);
[t,Y] = ode45(@dynamics,time(:),[x0(:);0;0],odeOptions);
data.t = t;
data.x = Y(:,1:n);
data.d = zeros(numel(t),nd);
data.v = zeros(numel(t),p);
data.u = zeros(numel(t),p);
data.z = zeros(numel(t),nz);
for k = 1:numel(t)
    [d,v,u,z] = signals(t(k),data.x(k,:).');
    data.d(k,:) = d.';
    data.v(k,:) = v.';
    data.u(k,:) = u.';
    data.z(k,:) = z.';
end
data.error = data.x-xeq.';
data.errorNorm = sqrt(sum(data.error.^2,2));
data.inputEnergy = max(Y(:,n+1),0);          % remove tiny integration roundoff
data.outputEnergy = max(Y(:,n+2),0);
data.energyRatio = NaN(size(t));
active = data.inputEnergy>1e-12;
data.energyRatio(active) = sqrt(data.outputEnergy(active)./data.inputEnergy(active));

    function derivative = dynamics(t,q)
        x = q(1:n);
        [d,~,u,z] = signals(t,x);
        derivative = [sys.A*x+sys.B*u+sys.E*d+sys.f(:); d.'*d; z.'*z];
    end

    function [d,v,u,z] = signals(t,x)
        d = disturbance(t);
        d = d(:);
        assert(numel(d)==nd,'disturbance(t) must return nd entries.');
        v = sys.C*x+sys.D*d+sys.b(:);
        u = min(max(v,lower),upper);         % simulate direct physical clipping
        z = sys.Cz*(x-xeq)+sys.Dz*(u-ueq)+sys.Ez*d;
    end
end
