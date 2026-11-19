function [prog,M] = qc_Mc_inc(prog,m,method,y)
%QC_MC_INC Complete incremental cone before COP approximation (Theorem 3).
% All incremental ReLU pairs have dv=D*(a+b), dw=D*b, a,b>=0.
% Conversely, use the raw input pair (b,-a) in each positive channel and
% (-a,b) in each negative channel. D and -D give identical quadratic tests.
[prog,M] = sospolymatrixvar(prog,polynomial(1),[2*m 2*m],'symmetric');
for pattern = 0:2^(m-1)-1
    D = diag(2*bitget(pattern,1:m)-1);
    R = [D D; zeros(m) D];
    Q = R.'*M*R;
    switch method
        case 'matrix'
            prog = cop_matrix(prog,2*m,Q);
        case 'sos0'
            prog = cop_sos(prog,y,0,Q);
        case 'sos1'
            prog = cop_sos(prog,y,1,Q);
        otherwise
            error('Unknown COP method: %s',method);
    end
end
end
