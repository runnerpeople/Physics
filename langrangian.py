#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

# Using SymPy
from sympy.physics.mechanics import *
from sympy import *
import numpy as np

from objects import *
import abc

G = lambda x: 0 if type(x) == MeshNonStaticCircle else 9.81

class RungeKutta(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,t0,y0):
        self.t = t0
        self.y = y0
        self.yy = [0,0]
        self.y1 = [0,0]
        self.y2 = [0,0]
        self.y3 = [0,0]
        self.y4 = [0,0]

    @abc.abstractclassmethod
    def f(self,t,y,diff_eq):
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

# y' = t
# t' = 0 (t - non-dependent variable)
class RungeKuttaTask1(RungeKutta):
    def f(self,t,y,diff_eq=None):
        fy = [0,0]
        fy[0] = y[1]
        fy[1] = -0
        return fy

# y' = gx
# g = g (g = 9.87)
class RungeKuttaTask2(RungeKutta):
    def f(self,t,y,diff_eq=None):
        fy = [0,0]
        fy[0] = y[1]
        fy[1] = -G(0)
        return fy

# y' = (g/l)*y
# g/l  (g = 9.87)
class RungeKuttaTask3(RungeKutta):

    l = 0

    def f(self,t,y,diff_eq=None):
        fy = [0,0]
        fy[0] = y[1]
        fy[1] = G(0)/self.l
        return fy

# #Spring pendulum
# class RungeKuttaTask4(RungeKutta):
#
#     point = [0,0]
#
#     k = 0
#     m = 0
#     l = 0
#
#     second_var = [0,0]
#
#     def f(self,t,y,diff_eq=None):
#         fy = [0,0]
#         fy[0] = y[1]
#         fy[1] = (self.l+y[0])*(self.second_var[1]**2)+G*math.cos(math.radians(self.second_var[0])) - (self.k/self.m)*y[0]
#         return fy
#
#
# class RungeKuttaTask5(RungeKutta):
#
#     point = [0,0]
#
#     l = 0
#
#     second_var = [0, 0]
#
#     def f(self, t, y, diff_eq=None):
#         fy = [0, 0]
#         fy[0] = y[1]
#         fy[1] = (-2/(self.l+self.second_var[0])*self.second_var[1]*y[1])-((G)/(self.l+self.second_var[0])*math.sin(math.radians(y[0])))
#         return fy

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
                    if G(self.world[i]) == 0:
                        result += 0
                    else:
                        result = self.world[i].mass * G(self.world[i]) * self.generalized_coord[coord+1][0]
                else:
                    if G(self.world[i]) == 0:
                        result += 0
                    else:
                        result += self.world[i].mass * G(self.world[i]) * self.generalized_coord[coord+1][0]
                coord += 2
            elif isinstance(self.world[i],(MeshPendulum)):
                if result is None:
                    result = self.world[i].b.mass * G(self.world[i]) * self.world[i].l * (1 - cos(self.generalized_coord[coord][0]))
                else:
                    result += self.world[i].b.mass * G(self.world[i]) * self.world[i].l * (1 - cos(self.generalized_coord[coord][0]))
                coord += 1
            elif isinstance(self.world[i],(MeshSpring)):
                first = self.world[i].a
                second = self.world[i].b
                r = None
                inc = 0
                p,p2 = None, None
                if isinstance(first,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   isinstance(second,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   not first.partPendulum and not second.partPendulum:
                    r = (sqrt((self.generalized_coord[indexof(self.world,first)][0]-self.generalized_coord[indexof(self.world,second)][0]) ** 2 +
                                   (self.generalized_coord[indexof(self.world,first)+1][0]-self.generalized_coord[indexof(self.world,second)+1][0]) ** 2) - self.world[i].l) ** 2
                    if G(first) == 0:
                        p = 0
                    else:
                        p = first.mass * G(first) * self.generalized_coord[indexof(self.world,first)+1][0]
                    if G(second) == 0:
                        p2 = 0
                    else:
                        p2 = second.mass * G(second) * self.generalized_coord[indexof(self.world,second)+1][0]
                    inc = 4
                elif isinstance(first,(MeshCircle)) and \
                   isinstance(second,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   first.partPendulum and not second.partPendulum:
                    r = (sqrt((first.Pendulum.l * sin(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[0]-self.generalized_coord[indexof(self.world,second)][0]) ** 2 +
                                   (first.Pendulum.l * cos(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[1]-self.generalized_coord[indexof(self.world,second)+1][0]) ** 2) - self.world[i].l) ** 2
                    p = 0
                    if G(second) == 0:
                        p2 = 0
                    else:
                        p2 = second.mass * G(self.world[i]) * self.generalized_coord[indexof(self.world,second)+1][0]
                    inc = 3
                elif isinstance(second,(MeshCircle)) and \
                   isinstance(first,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   second.partPendulum and not first.partPendulum:
                    r = (sqrt((self.generalized_coord[indexof(self.world,first)][0] -   second.Pendulum.l * sin(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[0]) ** 2 +
                                   (self.generalized_coord[indexof(self.world,first)+1][0] - second.Pendulum.l * cos(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[1]) ** 2)-self.world[i].l) ** 2
                    if G(first) == 0:
                        p = 0
                    else:
                        p = first.mass * G(self.world[i]) * self.generalized_coord[indexof(self.world,first)+1][0]
                    p2 = 0
                    inc = 3
                elif isinstance(first,(MeshCircle)) and \
                   isinstance(second,(MeshCircle)) and \
                   second.partPendulum and first.partPendulum:
                    r = (sqrt((first.Pendulum.l * sin(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[0] - second.Pendulum.l * sin(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[0]) ** 2 +
                                   (first.Pendulum.l * cos(self.generalized_coord[indexof(self.world,first)][0])+first.Pendulum.a.center[1] - second.Pendulum.l * cos(self.generalized_coord[indexof(self.world,second)][0]) + second.Pendulum.a.center[1]) ** 2)-self.world[i].l) ** 2
                    p = 0
                    p2 = 0
                    inc = 2
                if result is None:
                    result = self.world[i].k * r / 2
                else:
                    result += self.world[i].k * r / 2
                result += p
                result += p2
                coord += inc
        return result

    def langrangian(self):
        self.system = []
        t = Symbol('t')
        for i in range(self.freedom):
            self.system.append(diff(diff(self.l,self.generalized_coord[i][1]),t)-diff(self.l,self.generalized_coord[i][0]))
        self.odeint()

    def odeint(self):
        print(self.kinetic_energy_var)
        print(self.potential_energy_var)
        print(self.system)
        x0, y0 = [],[]
        x_, y_ = [],[]
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshCircle, MeshSquare)):
                for conn in self.world[i].connected:
                    if isinstance(conn, MeshSpring):
                        x0.append(math.sqrt(conn.velocity[0]**2+conn.velocity[1]**2))
                        y0.append(conn.phi)
                        x_.append(math.sqrt(self.world[i].velocity[0]**2+self.world[i].velocity[1]**2))
                        y_.append(math.sqrt(conn.k/self.world[i].mass))
                if self.world[i].connected == []:
                    x0.append(self.world[i].center[0])
                    y0.append(self.world[i].center[1])
                    x_.append(self.world[i].velocity[0])
                    y_.append(self.world[i].velocity[1])


        dt = 1.0 / 30.0

        x, y = [],[]

        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshCircle, MeshSquare)):
                for conn in self.world[i].connected:
                    if isinstance(conn, MeshSpring):
                        x_new,y_new = RungeKuttaTask4(dt,[x0.pop(),x_.pop()]),RungeKuttaTask5(dt,[y0.pop(),y_.pop()])
                        x_new.k,x_new.l,x_new.m = conn.k,conn.l,self.world[i].mass
                        y_new.l = conn.l
                        x.append(x_new)
                        y.append(y_new)
                        x_new.point = conn.find_rotate_point(self.world[i])
                        y_new.point = conn.find_rotate_point(self.world[i])
                if self.world[i].connected == []:
                    x.append(RungeKuttaTask1(dt,[x0.pop(),x_.pop()]))
                    y.append(RungeKuttaTask2(dt,[y0.pop(),y_.pop()]))

        self.result_x = [[] for _ in range(len(x))]
        self.result_y = [[] for _ in range(len(y))]

        self.static_x = []
        self.static_y = []

        coord = 0
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshCircle, MeshSquare)):
                self.result_x[coord].append(self.world[i].center[0])
                self.result_y[coord].append(self.world[i].center[1])
                coord += 1
            elif type(self.world[i])==MeshNonStaticCircle:
                self.static_x.append(self.world[i].center[0])
                self.static_y.append(self.world[i].center[1])

        for i in range(len(x)):
            while x[i].t < 20 and y[i].t < 20:
                if type(x[i]) == RungeKuttaTask4:
                    x[i].second_var = [y[i].y[0],y[i].y[1]]
                    y[i].second_var = [x[i].y[0],x[i].y[1]]
                x[i].nextStep(dt)
                y[i].nextStep(dt)
                if type(x[i]) == RungeKuttaTask4:
                    # transform to x and y
                    x_result = x[i].point.center[0] + ((x[i].l + x[i].y[0]) * sin(math.radians(y[i].y[0])))
                    y_result = y[i].point.center[1] - ((x[i].l + x[i].y[0]) * cos(math.radians(y[i].y[0])))
                    self.result_x[i].extend([x_result])
                    self.result_y[i].extend([y_result])
                    print(x[i].y)
                    print(y[i].y)
                else:
                    self.result_x[i].extend([x[i].y[0]])
                    self.result_y[i].extend([y[i].y[0]])
            print(self.result_x[i])
            print(self.result_y[i])

