function u = saturation_relu(v,lower,upper)
%SATURATION_RELU Elementwise clipping through two shifted ReLUs.
% saturation_relu(v)       uses [-1,1].
% saturation_relu(v,h)     uses [-h,h] (backwards compatible).
% saturation_relu(v,l,u)   uses [l,u]; scalar or per-channel limits.
if nargin < 2, lower = 1; end
if nargin < 3, upper = lower; lower = -upper; end
assert(all(isfinite(lower(:))) && all(isfinite(upper(:))) ...
    && all(lower(:)<upper(:)),'Require finite lower < upper.');
u = lower+max(v-lower,0)-max(v-upper,0);
end
