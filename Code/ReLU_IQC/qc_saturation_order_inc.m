function [prog,M] = qc_saturation_order_inc(prog,p,side)
%QC_SATURATION_ORDER_INC Cross products from ordered saturation secants.
% The lifted input is [v;v] (primal) or [v;-v] (dual), and the two output
% blocks use slopes 0 <= lambda_upper <= lambda_lower <= 1.
% The QC acts on [input_lower;input_upper;output_lower;output_upper].
I = eye(4*p);
upperSign = 1;
if strcmp(side,'dual'), upperSign = -1; end
M = dpvar(zeros(4*p));
for k = 1:p
    lowerOutput = I(:,2*p+k);
    upperOutput = upperSign*I(:,3*p+k);
    G = [upperOutput, lowerOutput-upperOutput, I(:,k)-lowerOutput];
    % For each channel the three quantities G'*[v;w] have the same sign.
    for i = 1:2
        for j = i+1:3
            [prog,weight] = sospolyvar(prog,polynomial(1));
            prog = sosineq(prog,weight);
            M = M+weight*(G(:,i)*G(:,j).'+G(:,j)*G(:,i).');
        end
    end
end
end
