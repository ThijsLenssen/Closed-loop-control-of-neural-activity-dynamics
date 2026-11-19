function [prog,M] = qc_M2(prog,m,method,y)
%QC_M2 Positivity QC: [w-v;w]'*Q2*[w-v;w] >= 0 (paper, Eq. 4).
% Q2 is copositive; select an inner approximation of COP.
switch method
    case 'matrix'
        [prog,Q2] = cop_matrix(prog,2*m);
    case 'sos0'
        [prog,Q2] = cop_sos(prog,y,0);
    case 'sos1'
        [prog,Q2] = cop_sos(prog,y,1);
    otherwise
        error('Unknown COP method: %s',method);
end
T = [-eye(m) eye(m); zeros(m) eye(m)];
M = T.'*Q2*T;
end
