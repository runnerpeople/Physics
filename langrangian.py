#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

# Using SymPy
from sympy.physics.mechanics import *
from sympy.utilities.lambdify import lambdify, implemented_function
from sympy import *
import numpy as np

from objects import *
import abc

class RungeKutta(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,t0,y0,diff_eq=None,name_coord=None):
        self.t = t0
        self.y = y0
        self.yy = [0,0]
        self.y1 = [0,0]
        self.y2 = [0,0]
        self.y3 = [0,0]
        self.y4 = [0,0]
        self.diff_eq = diff_eq
        self.name_coord = name_coord

    @abc.abstractclassmethod
    def f(self,t,y):
        pass

    def nextStep(self,dt):
        if dt < 0:
            return None

        self.y1 = self.f(self.t, self.y)
        for i in range(2):
            self.yy[i] = self.y[i] + self.y1[i] * (dt / 2.0)

        self.y2 = self.f(self.t + dt / 2.0, self.yy)
        for i in range(2):
            self.yy[i] = self.y[i] + self.y2[i] * (dt / 2.0)

        self.y3 = self.f(self.t + dt / 2.0, self.yy)
        for i in range(2):
            self.yy[i] = self.y[i] + self.y3[i] * dt

        self.y4 = self.f(self.t + dt, self.yy)
        for i in range(2):
            self.y[i] = self.y[i] + dt / 6.0 * (self.y1[i] + 2.0 * self.y2[i] + 2.0 * self.y3[i] + self.y4[i])

        self.t += dt

class RungeKuttaImpl(RungeKutta):
    def f(self,t,y):
        fy = [0,0]
        fy[0] = y[1]
        fy[1] = self.diff_eq.subs(self.name_coord,self.y[0])
        return fy


def indexof(list,value):
    for i in range(len(list)):
        if list[i] == value:
            return i
        elif isinstance(list[i],MeshPendulum):
            if list[i].a == value or list[i].b == value:
                return i
    return -1


class System(object):

    def __init__(self,world,mass_generalized):

        self.world = world
        self.freedom = 0
        self.mass_generalized = mass_generalized
        self.generalized_coord = []

        for obj in self.world:
            if isinstance(obj,(MeshCircle,MeshSquare,MeshNonStaticCircle)):
                self.freedom += 2
            elif isinstance(obj,MeshPendulum):
                self.freedom += 1

        for i in range(self.freedom):
            self.generalized_coord.append([dynamicsymbols('q' + str(i)),dynamicsymbols('q' + str(i),level=1)])

        self.kinetic_energy_var = self.kinetic_energy()
        self.potential_energy_var  = self.potential_energy()

        self.l = self.kinetic_energy_var - self.potential_energy_var
        self.langrangian()

    def kinetic_energy(self):
        result = None
        coord = 0
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshPendulum)):
                if result is None:
                    result = self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2
                else:
                    result += self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2
                coord += 1
            elif isinstance(self.world[i],(MeshCircle,MeshSquare,MeshNonStaticCircle)):
                if result is None:
                    result = self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2 +\
                             self.mass_generalized[i] * self.generalized_coord[coord+1][1] ** 2 / 2
                else:
                    result += self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2 +\
                              self.mass_generalized[i] * self.generalized_coord[coord+1][1] ** 2 / 2
                coord += 2
        return result

    def potential_energy(self):
        result = None
        coord = 0
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshCircle,MeshSquare, MeshNonStaticCircle)):
                if result is None:
                    if self.world[i].g == 0:
                        result = 0
                    else:
                        result = self.world[i].mass * self.world[i].g * self.generalized_coord[coord+1][0]
                else:
                    if self.world[i].g == 0:
                        result += 0
                    else:
                        result += self.world[i].mass * self.world[i].g * self.generalized_coord[coord+1][0]
                coord += 2
            elif isinstance(self.world[i],(MeshPendulum)):
                if result is None:
                    result = self.world[i].b.mass * self.world[i].b.g * self.world[i].l * (1 - cos(self.generalized_coord[coord][0]))
                else:
                    result += self.world[i].b.mass * self.world[i].b.g * self.world[i].l * (1 - cos(self.generalized_coord[coord][0]))
                coord += 1
            elif isinstance(self.world[i],(MeshSpring)):
                first = self.world[i].a
                second = self.world[i].b
                r = None
                p,p2 = None, None
                if isinstance(first,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   isinstance(second,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   not first.partPendulum and not second.partPendulum:
                    r = (sqrt((self.generalized_coord[indexof(self.world,first)][0]-self.generalized_coord[indexof(self.world,second)][0]) ** 2 +
                                   (self.generalized_coord[indexof(self.world,first)+1][0]-self.generalized_coord[indexof(self.world,second)+1][0]) ** 2) - self.world[i].l) ** 2
                    if first.g == 0:
                        p = 0
                    else:
                        p = first.mass * first.g * self.generalized_coord[indexof(self.world,first)+1][0]
                    if second.g == 0:
                        p2 = 0
                    else:
                        p2 = second.mass * second.g * self.generalized_coord[indexof(self.world,second)+1][0]
                elif isinstance(first,(MeshCircle)) and \
                   isinstance(second,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   first.partPendulum and not second.partPendulum:
                    r = (sqrt((first.Pendulum.l * sin(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[0]-self.generalized_coord[indexof(self.world,second)][0]) ** 2 +
                              (first.Pendulum.l * cos(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[1]-self.generalized_coord[indexof(self.world,second)+1][0]) ** 2) - self.world[i].l) ** 2
                    p = 0
                    if second.g == 0:
                        p2 = 0
                    else:
                        p2 = second.mass * second.g * self.generalized_coord[indexof(self.world,second)+1][0]
                elif isinstance(second,(MeshCircle)) and \
                   isinstance(first,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   second.partPendulum and not first.partPendulum:
                    r = (sqrt((self.generalized_coord[indexof(self.world,first)][0] -   second.Pendulum.l * sin(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[0]) ** 2 +
                                   (self.generalized_coord[indexof(self.world,first)+1][0] - second.Pendulum.l * cos(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[1]) ** 2)-self.world[i].l) ** 2
                    if first.g == 0:
                        p = 0
                    else:
                        p = first.mass * first.g * self.generalized_coord[indexof(self.world,first)+1][0]
                    p2 = 0
                elif isinstance(first,(MeshCircle)) and \
                   isinstance(second,(MeshCircle)) and \
                   second.partPendulum and first.partPendulum:
                    r = (sqrt((first.Pendulum.l * sin(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[0] - second.Pendulum.l * sin(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[0]) ** 2 +
                                   (first.Pendulum.l * cos(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[1] - second.Pendulum.l * cos(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[1]) ** 2)-self.world[i].l) ** 2
                    p = 0
                    p2 = 0
                if result is None:
                    result = self.world[i].k * r / 2
                else:
                    result += self.world[i].k * r / 2
                result += p
                result += p2
        return result

    def langrangian(self):
        self.system = []
        t = Symbol('t')
        for i in range(self.freedom):
            self.system.append(diff(diff(self.l,self.generalized_coord[i][1]),t)-diff(self.l,self.generalized_coord[i][0]))
        self.odeint()

    def odeint(self):
        print(self.system)
        x0,y0,phi0 = [],[],[]
        x_,y_,phi_ = [],[],[]
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshCircle, MeshSquare,MeshNonStaticCircle)):
                x0.append(self.world[i].center[0])
                y0.append(self.world[i].center[1])
                if isinstance(self.world[i], (MeshCircle, MeshSquare)):
                    x_.append(self.world[i].velocity[0])
                    y_.append(self.world[i].velocity[1])
                else:
                    x_.append(0)
                    y_.append(0)
            elif isinstance(self.world[i],(MeshPendulum)):
                phi0.append(self.world[i].phi)
                phi_.append(self.world[i].phi0)

        dt = 0.05
        t = Symbol('t')

        x,y,phi = [],[],[]
        equation = 0
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshCircle, MeshSquare, MeshNonStaticCircle)):
                x.append(RungeKuttaImpl(0,[x0.pop(0),x_.pop(0)],-(self.system[equation]/self.mass_generalized[equation]-diff(self.generalized_coord[equation][1],t)),self.generalized_coord[equation][0]))
                y.append(RungeKuttaImpl(0,[y0.pop(0),y_.pop(0)],-(self.system[equation+1]/self.mass_generalized[equation]-diff(self.generalized_coord[equation+1][1],t)),self.generalized_coord[equation+1][0]))
                equation += 2
            elif isinstance(self.world[i], (MeshPendulum)):
                phi.append(RungeKuttaImpl(0,[phi0.pop(0),phi_.pop(0)],-(self.system[equation]/self.mass_generalized[equation]-diff(self.generalized_coord[equation][1],t)),self.generalized_coord[equation][0]))
                equation += 1

        self.result_x   = [[] for _ in range(len(x))]
        self.result_y   = [[] for _ in range(len(y))]
        self.result_phi = [[] for _ in range(len(phi))]


        for i in range(len(x)):
            while x[i].t < 15 and y[i].t < 15:
                print(x[i].y[0],y[i].y[0])
                x[i].nextStep(dt)
                y[i].nextStep(dt)
                self.result_x[i].extend([x[i].y[0]])
                self.result_y[i].extend([y[i].y[0]])

        for i in range(len(phi)):
            while phi[i].t < 15:
                phi[i].nextStep(dt)
                self.result_phi[i].extend([phi[i].y[0]])
