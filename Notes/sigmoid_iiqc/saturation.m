function out = saturation(in,a,b)
out = a +relu(in-a) - relu(in-b);
end