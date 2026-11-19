function fig = plot_flipped_relu
%PLOT_FLIPPED_RELU Show the 180 degree rotation of the ReLU graph.
v = [-3 0 3];
blue = [0 .32 .66];
orange = [.76 .29 .06];

fig = figure('Name','ReLU and flipped ReLU','Color','w', ...
    'Position',[100 100 710 530]);
ax = axes(fig);
hold(ax,'on');
grid(ax,'on');
axis(ax,'equal');
xlim(ax,[-3.35 3.35]);
ylim(ax,[-3.35 3.35]);
ax.FontSize = 12;
ax.GridAlpha = .13;
xline(ax,0,'Color',[.45 .45 .45],'HandleVisibility','off');
yline(ax,0,'Color',[.45 .45 .45],'HandleVisibility','off');

% Both graphs pass through the origin.
plot(ax,v,max(v,0),'-','Color',blue,'LineWidth',2.7, ...
    'DisplayName','ReLU: max(v,0)');
plot(ax,v,min(v,0),'--','Color',orange,'LineWidth',2.7, ...
    'DisplayName','Flipped ReLU: min(v,0)');

% A semicircle shows the path of (2,2) to its centrally reflected point.
t = linspace(pi/4,5*pi/4,120);
r = sqrt(8);
arcColor = [.40 .40 .40];
plot(ax,r*cos(t),r*sin(t),':','Color',arcColor,'LineWidth',1.4, ...
    'HandleVisibility','off');
tip = 109;
quiver(ax,r*cos(t(tip)),r*sin(t(tip)), ...
    -.36*sin(t(tip)),.36*cos(t(tip)),0, ...
    'Color',arcColor,'LineWidth',1.25,'MaxHeadSize',1.8,'HandleVisibility','off');
plot(ax,2,2,'o','MarkerFaceColor',blue,'MarkerEdgeColor','w', ...
    'MarkerSize',8,'HandleVisibility','off');
plot(ax,-2,-2,'o','MarkerFaceColor',orange,'MarkerEdgeColor','w', ...
    'MarkerSize',8,'HandleVisibility','off');
plot(ax,0,0,'k.','MarkerSize',14,'HandleVisibility','off');
text(ax,2.01,1.65,'(2, 2)','Color',blue,'FontSize',11);
text(ax,-1.9,-2.30,'(-2, -2)','Color',orange,'FontSize',11);
text(ax,-2.21,1.55,'180\circ','Color',arcColor,'FontSize',12);

xlabel(ax,'Input v');
ylabel(ax,'Output');
title(ax,'Flipped ReLU is a 180\circ rotation about the origin');
legend(ax,'Location','southeast','FontSize',10);
end
