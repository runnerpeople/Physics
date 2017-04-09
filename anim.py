#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def animate(langrange):

    fig = plt.figure()
    ax = fig.add_subplot(111,autoscale_on=False)
    points, = ax.plot([], [],'ro',animated=True)
    springs, = ax.plot([],[],'b-',linewidth = 2)
    static_points, = ax.plot([],[],'g^',markersize=10)
    ax.grid()


    def init():
        ax.set_ylim(0, 900)
        ax.set_xlim(0, 1600)
        static_points.set_data(langrange.static_x,langrange.static_y)
        return points,springs,static_points


    def run(i):
        xdata=langrange.result_x[0][i]
        ydata=langrange.result_y[0][i]
        points.set_data(xdata,ydata)
        springs.set_data([langrange.world[0].center[0],xdata],[langrange.world[0].center[1],ydata])
        return points,springs,static_points

    anim = animation.FuncAnimation(fig, run, blit=True, interval=15,
                                  init_func=init)
    plt.show()
