classdef wc_exogenous < surrogate_model
    %UNTITLED2 Summary of this class goes here
    %   Detailed explanation goes here

    properties
        PIE
    end

    methods
        function obj = wc_exogenous()
            [c12, c21, c22, b1, b2] = deal(1.12, 19, 0.9, 2.42, 15.2);

        end

        function outputArg = method1(obj,inputArg)
            %METHOD1 Summary of this method goes here
            %   Detailed explanation goes here
            outputArg = obj.Property1 + inputArg;
        end
    end
end

classdef wc_exogenous < handle

    properties (SetAccess = private)
        P
    end

    properties (Access = private)
        t
        s
    end

    methods
        function obj = wc_exogenous()
            obj.t = pvar('t');
            obj.s = pvar('s');

            obj.P = obj.buildPlant();
        end
    end

    methods (Access = private)
        function P = buildPlant(obj)
            t = obj.t;
            s = obj.s;


            
        end
    end
end