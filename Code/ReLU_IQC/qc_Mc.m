function [prog,M] = qc_Mc(prog,m,method,y)
%QC_MC Complete ReLU QC cone, with a chosen COP approximation (Theorem 1).
% A free symmetric M satisfies R_D'*M*R_D in COP^m for all 2^m signs D.
% matrix/sos0/sos1 approximate COP; matrix is exact here when m <= 4.
[prog,M] = sospolymatrixvar(prog,polynomial(1),[2*m 2*m],'symmetric');

for k = 0:2^m-1
    D = diag(2*bitget(k,1:m)-1);             % every diagonal +/-1 pattern
    R = [D; (eye(m)+D)/2];                  % [v;ReLU(v)] = R*abs(v)
    Q = R.'*M*R;

    switch method
        case 'matrix'
            prog = cop_matrix(prog,m,Q);
        case 'sos0'
            prog = cop_sos(prog,y(1:m),0,Q);
        case 'sos1'
            prog = cop_sos(prog,y(1:m),1,Q);
        otherwise
            error('Unknown COP method: %s',method);
    end
end
end
