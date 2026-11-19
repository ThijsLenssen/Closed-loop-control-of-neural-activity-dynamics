function [f,s,theta] = sigmoid_saturation(q,lower,upper,center,slope)
%SIGMOID_SATURATION Increasing tanh sigmoid with asymptotes lower and upper.
% f = midpoint + theta.*s, where s is the CENTERED saturation output.
% center defaults to the output midpoint; slope = f'(center) defaults to 1.
% Example: [f,s,theta] = sigmoid_saturation(-5:.01:5,-2,4,0,1.5);
validateattributes(lower,{'double','single'},{'real','finite','scalar'});
validateattributes(upper,{'double','single'},{'real','finite','scalar','>',lower});
midpoint = upper/2 + lower/2;
halfRange = upper/2 - lower/2;
if nargin < 4, center = midpoint; end
if nargin < 5, slope = 1; end
validateattributes(center,{'double','single'},{'real','finite','scalar'});
validateattributes(slope,{'double','single'},{'real','finite','scalar','positive'});
validateattributes(q,{'double','single'},{'real','finite'});

r = slope*((q-center)/halfRange);
clipped = min(max(r,-1),1);
s = halfRange*clipped;
shape = tanh(r);
f = midpoint + halfRange*shape;
theta = ones(size(r),'like',r);
away = r~=0;
theta(away) = shape(away)./clipped(away);
end
