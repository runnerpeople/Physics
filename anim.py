#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from objects import *

def animate(langrange):

    fig = plt.figure()
    ax = fig.add_subplot(111,autoscale_on=False)
    points, = ax.plot([], [],'ro',animated=True)
    lines,  = ax.plot([],[],'b-',linewidth = 2)
    static_points, = ax.plot([],[],'g^',markersize=10)
    ax.grid()

    def init():
        ax.set_ylim(0, 900)
        ax.set_xlim(0, 1600)
        return points,lines,static_points


    def run(i):
        coord = 0
        xdata, ydata = [],[]
        line_points_x,line_points_y = [],[]
        for j in range(len(langrange.world)):
            if isinstance(langrange.world[j], (MeshCircle, MeshSquare,MeshNonStaticCircle)):
                xdata = langrange.result_x[coord][i]
                ydata = langrange.result_y[coord][i]
            elif isinstance(langrange.world[j],(MeshPendulum)):
                phi = langrange.result_phi[coord][i]
                x = langrange.world[j].a.center[0] + langrange.world[j].l * math.sin(phi)
                y = langrange.world[j].a.center[1] - langrange.world[j].l * math.cos(phi)
                line_points_x = [langrange.world[j].a.center[0],x]
                line_points_y = [langrange.world[j].a.center[0],y]
                xdata = line_points_x
                ydata = line_points_y

        points.set_data(xdata,ydata)
        lines.set_data(line_points_x,line_points_y)
        return points,lines,static_points

    anim = animation.FuncAnimation(fig, run, blit=True, interval=15,
                                  init_func=init,repeat=True)
    plt.show()
