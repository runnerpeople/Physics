#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from objects import *

def indexof(list,value):
    for i in range(len(list)):
        if list[i] == value:
            return i
        elif isinstance(list[i],MeshPendulum):
            if list[i].a == value or list[i].b == value:
                return i
    return -1

def animate(langrange):

    fig = plt.figure()
    ax = fig.add_subplot(111,autoscale_on=False)
    points,     = ax.plot([], [],'ro',animated=True)
    lines,      = ax.plot([],[],'b-',linewidth = 4)
    springs,    = ax.plot([],[],'m--',linewidth = 2)
    ax.grid()

    def init():
        ax.set_ylim(0, 900)
        ax.set_xlim(0, 1600)
        return points,lines,springs


    def run(i):
        coord_xy = 0
        coord_phi = 0
        xdata, ydata = [],[]
        line_points_x,line_points_y = [],[]
        spring_points_x,spring_points_y = [],[]
        for j in range(len(langrange.world)):
            if isinstance(langrange.world[j], (MeshCircle, MeshSquare,MeshNonStaticCircle)):
                xdata.extend([langrange.result_x[coord_xy][i]])
                ydata.extend([langrange.result_y[coord_xy][i]])
                coord_xy += 1
            elif isinstance(langrange.world[j],(MeshPendulum)):
                phi = langrange.result_phi[coord_phi][i]
                x = langrange.world[j].a.center[0] + langrange.world[j].l * math.sin(phi)
                y = langrange.world[j].a.center[1] - langrange.world[j].l * math.cos(phi)
                line_points_x.extend([langrange.world[j].a.center[0],x])
                line_points_y.extend([langrange.world[j].a.center[0],y])
                xdata.extend(line_points_x)
                ydata.extend(line_points_y)
                coord_phi += 1
            elif isinstance(langrange.world[j],(MeshSpring)):
                a = langrange.world[j].a
                b = langrange.world[j].b
                spring_points_x.extend([langrange.result_x[indexof(langrange.world,a)][i],langrange.result_x[indexof(langrange.world,b)][i]])
                spring_points_y.extend([langrange.result_y[indexof(langrange.world,a)][i],langrange.result_y[indexof(langrange.world,b)][i]])

        points.set_data(xdata,ydata)
        lines.set_data(line_points_x,line_points_y)
        springs.set_data(spring_points_x,spring_points_y)
        return points,lines,springs,

    anim = animation.FuncAnimation(fig, run, blit=True, interval=15,
                                  init_func=init,repeat=True)
    plt.show()
