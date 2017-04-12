#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from objects import *

def indexof(list,value,type_value):
    coord = 0
    for i in range(len(list)):
        if value == list[i]:
            return coord
        if isinstance(list[i],(MeshPendulum)) and type_value == MeshPendulum:
            coord+=1
        elif isinstance(list[i],(MeshSquare,MeshCircle,MeshNonStaticCircle)) and (type_value == MeshSquare or type_value == MeshCircle or type_value == MeshNonStaticCircle):
            coord+=1
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
        xdata, ydata = [],[]
        line_points_x,line_points_y = [],[]
        spring_points_x,spring_points_y = [],[]
        for j in range(len(langrange.world)):
            if isinstance(langrange.world[j], (MeshCircle, MeshSquare,MeshNonStaticCircle)):
                xdata.extend([langrange.result_x[indexof(langrange.world,langrange.world[j],type(langrange.world[j]))][i]])
                ydata.extend([langrange.result_y[indexof(langrange.world,langrange.world[j],type(langrange.world[j]))][i]])
            elif isinstance(langrange.world[j],(MeshPendulum)):
                phi = langrange.result_phi[indexof(langrange.world,langrange.world[j],type(langrange.world[j]))][i]
                x = langrange.world[j].a.center[0] + langrange.world[j].l * math.sin(phi)
                y = langrange.world[j].a.center[1] - langrange.world[j].l * math.cos(phi)
                line_points_x.extend([langrange.world[j].a.center[0],x])
                line_points_y.extend([langrange.world[j].a.center[1],y])
                xdata.extend(line_points_x)
                ydata.extend(line_points_y)
            elif isinstance(langrange.world[j],(MeshSpring)):
                first = langrange.world[j].a
                second = langrange.world[j].b
                if isinstance(first, (MeshCircle, MeshSquare, MeshNonStaticCircle)) and \
                   isinstance(second, (MeshCircle, MeshSquare, MeshNonStaticCircle)) and \
                   not first.partPendulum and not second.partPendulum:
                    spring_points_x.extend([langrange.result_x[indexof(langrange.world,first,type(first))][i],langrange.result_x[indexof(langrange.world,second,type(second))][i]])
                    spring_points_y.extend([langrange.result_y[indexof(langrange.world,first,type(first))][i],langrange.result_y[indexof(langrange.world,second,type(second))][i]])
                elif isinstance(first, (MeshSquare)) and \
                    isinstance(second, (MeshCircle, MeshSquare, MeshNonStaticCircle)) and \
                    first.partPendulum and not second.partPendulum:
                    phi = langrange.result_phi[indexof(langrange.world,first.Pendulum,type(first.Pendulum))][i]
                    x = first.Pendulum.a.center[0] + first.Pendulum.l * math.sin(phi)
                    y = first.Pendulum.a.center[1] - first.Pendulum.l * math.cos(phi)
                    spring_points_x.extend([x,langrange.result_x[indexof(langrange.world, second,type(second))][i]])
                    spring_points_y.extend([y,langrange.result_y[indexof(langrange.world, second,type(second))][i]])
                elif isinstance(second, (MeshSquare)) and \
                     isinstance(first, (MeshCircle, MeshSquare, MeshNonStaticCircle)) and \
                     second.partPendulum and not first.partPendulum:
                    phi = langrange.result_phi[indexof(langrange.world,second.Pendulum,type(second.Pendulum))][i]
                    x = second.Pendulum.a.center[0] + second.Pendulum.l * math.sin(phi)
                    y = second.Pendulum.a.center[1] - second.Pendulum.l * math.cos(phi)
                    spring_points_x.extend([langrange.result_x[indexof(langrange.world, second,type(second)),x][i]])
                    spring_points_y.extend([langrange.result_y[indexof(langrange.world, second,type(second)),y][i]])
                elif isinstance(first, (MeshSquare)) and \
                     isinstance(second, (MeshSquare)) and \
                     second.partPendulum and first.partPendulum:
                    phi = langrange.result_phi[indexof(langrange.world,first.Pendulum,type(first.Pendulum))][i]
                    x = first.Pendulum.a.center[0] + first.Pendulum.l * math.sin(phi)
                    y = first.Pendulum.a.center[1] - first.Pendulum.l * math.cos(phi)
                    phi2 = langrange.result_phi[indexof(langrange.world,second.Pendulum,type(second.Pendulum))][i]
                    x2 = second.Pendulum.a.center[0] + second.Pendulum.l * math.sin(phi2)
                    y2 = second.Pendulum.a.center[1] - second.Pendulum.l * math.cos(phi2)
                    spring_points_x.extend([x,x2])
                    spring_points_y.extend([y,y2])



        points.set_data(xdata,ydata)
        lines.set_data(line_points_x,line_points_y)
        springs.set_data(spring_points_x,spring_points_y)
        return points,lines,springs,

    anim = animation.FuncAnimation(fig, run, range(500), blit=True, interval=1,
                                  init_func=init,repeat=True)
    plt.show()
