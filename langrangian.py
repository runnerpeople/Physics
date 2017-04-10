#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

# Using SymPy
from sympy.physics.mechanics import *
from sympy import *
import csv

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
        self.substitution = None

    def init_values(self,list_variable,list_value):
        self.substitution = [(list_variable[i],list_value[i]) for i in range(len(list_variable))]

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
        fy[1] = self.diff_eq.subs(self.substitution).doit()
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
        self.start_position = []

        for obj in self.world:
            self.start_position.append(self.freedom)
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
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshPendulum)):
                coord = self.start_position[i]
                if result is None:
                    result = self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2
                else:
                    result += self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2
            elif isinstance(self.world[i],(MeshCircle,MeshSquare,MeshNonStaticCircle)):
                coord = self.start_position[i]
                if result is None:
                    result = self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2 +\
                             self.mass_generalized[i] * self.generalized_coord[coord+1][1] ** 2 / 2
                else:
                    result += self.mass_generalized[i] * self.generalized_coord[coord][1] ** 2 / 2 +\
                              self.mass_generalized[i] * self.generalized_coord[coord+1][1] ** 2 / 2
        return result

    def potential_energy(self):
        result = None
        for i in range(len(self.world)):
            if isinstance(self.world[i], (MeshCircle,MeshSquare, MeshNonStaticCircle)):
                coord = self.start_position[i]
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
            elif isinstance(self.world[i],(MeshPendulum)):
                coord = self.start_position[i]
                if result is None:
                    result = self.world[i].b.mass * self.world[i].b.g * self.world[i].l * (1 - cos(self.generalized_coord[coord][0]))
                else:
                    result += self.world[i].b.mass * self.world[i].b.g * self.world[i].l * (1 - cos(self.generalized_coord[coord][0]))
            elif isinstance(self.world[i],(MeshSpring)):
                first = self.world[i].a
                second = self.world[i].b
                r = None
                p,p2 = None, None
                if isinstance(first,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   isinstance(second,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   not first.partPendulum and not second.partPendulum:
                    r = (sqrt((self.generalized_coord[self.start_position[indexof(self.world,first)]][0]-self.generalized_coord[self.start_position[indexof(self.world,second)]][0]) ** 2 +
                              (self.generalized_coord[self.start_position[indexof(self.world,first)]+1][0]-self.generalized_coord[self.start_position[indexof(self.world,second)]+1][0]) ** 2) - self.world[i].l) ** 2
                    p = 0
                    p2 = 0
                elif isinstance(first,(MeshCircle)) and \
                   isinstance(second,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   first.partPendulum and not second.partPendulum:
                    r = (sqrt((first.Pendulum.l * sin(self.generalized_coord[self.start_position[indexof(self.world,first)]][0])+first.Pendulum.a.center[0]-self.generalized_coord[self.start_position[indexof(self.world,second)]][0]) ** 2 +
                              (first.Pendulum.l * cos(self.generalized_coord[self.start_position[indexof(self.world,first)]][0])+first.Pendulum.a.center[1]-self.generalized_coord[self.start_position[indexof(self.world,second)]+1][0]) ** 2) - self.world[i].l) ** 2
                    p = 0
                    if second.g == 0:
                        p2 = 0
                    else:
                        p2 = second.mass * second.g * self.generalized_coord[self.start_position[indexof(self.world,second)]+1][0]
                elif isinstance(second,(MeshCircle)) and \
                   isinstance(first,(MeshCircle,MeshSquare,MeshNonStaticCircle)) and \
                   second.partPendulum and not first.partPendulum:
                    r = (sqrt((self.generalized_coord[self.start_position[indexof(self.world,first)]][0] -   second.Pendulum.l * sin(self.generalized_coord[self.start_position[indexof(self.world,second)]][0]) + second.Pendulum.a.center[0]) ** 2 +
                              (self.generalized_coord[self.start_position[indexof(self.world,first)]+1][0] - second.Pendulum.l * cos(self.generalized_coord[self.start_position[indexof(self.world,second)]][0]) + second.Pendulum.a.center[1]) ** 2)-self.world[i].l) ** 2
                    if first.g == 0:
                        p = 0
                    else:
                        p = first.mass * first.g * self.generalized_coord[self.start_position[indexof(self.world,first)]+1][0]
                    p2 = 0
                elif isinstance(first,(MeshCircle)) and \
                   isinstance(second,(MeshCircle)) and \
                   second.partPendulum and first.partPendulum:
                    r = (sqrt((first.Pendulum.l * sin(self.generalized_coord[self.start_position[indexof(self.world,first)]][0])+first.Pendulum.a.center[0] - second.Pendulum.l * sin(self.generalized_coord[self.start_position[indexof(self.world,second)]][0]) + second.Pendulum.a.center[0]) ** 2 +
                              (first.Pendulum.l * cos(self.generalized_coord[self.start_position[indexof(self.world,first)]][0])+first.Pendulum.a.center[1] - second.Pendulum.l * cos(self.generalized_coord[self.start_position[indexof(self.world,second)]][0]) + second.Pendulum.a.center[1]) ** 2)-self.world[i].l) ** 2
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
                if self.mass_generalized[i] == float("+inf"):
                    x.append(RungeKuttaImpl(0, [x0.pop(0), x_.pop(0)], self.system[equation]/self.mass_generalized[i],self.generalized_coord[equation]))
                    y.append(RungeKuttaImpl(0, [y0.pop(0), y_.pop(0)], self.system[equation+1]/self.mass_generalized[i],self.generalized_coord[equation+1]))
                else:
                    x.append(RungeKuttaImpl(0,[x0.pop(0),x_.pop(0)],-(self.system[equation]/self.mass_generalized[i]-diff(self.generalized_coord[equation][1],t)),self.generalized_coord[equation]))
                    y.append(RungeKuttaImpl(0,[y0.pop(0),y_.pop(0)],-(self.system[equation+1]/self.mass_generalized[i]-diff(self.generalized_coord[equation+1][1],t)),self.generalized_coord[equation+1]))
                equation += 2
            elif isinstance(self.world[i], (MeshPendulum)):
                phi.append(RungeKuttaImpl(0,[phi0.pop(0),phi_.pop(0)],-(self.system[equation]/self.mass_generalized[i]-diff(self.generalized_coord[equation][1],t)),self.generalized_coord[equation]))
                equation += 1

        time_animation = 40

        self.result_x   = [[] for _ in range(len(x))]
        self.result_y   = [[] for _ in range(len(y))]
        self.result_phi = [[] for _ in range(len(phi))]

        if (len(x)) > 0:
            while x[0].t < time_animation:
                list_variable = []
                list_value = []
                for j in range(len(x)):
                    list_variable.append(x[j].name_coord[0])
                    list_value.append(x[j].y[0])
                    list_variable.append(x[j].name_coord[1])
                    list_value.append(x[j].y[1])
                    list_variable.append(y[j].name_coord[0])
                    list_value.append(y[j].y[0])
                    list_variable.append(y[j].name_coord[1])
                    list_value.append(y[j].y[1])
                for k in range(len(phi)):
                    list_variable.append(phi[k].name_coord[0])
                    list_value.append(phi[k].y[0])
                    list_variable.append(phi[k].name_coord[1])
                    list_value.append(phi[k].y[1])
                for z in range(len(x)):
                    x[z].init_values(list_variable, list_value)
                    y[z].init_values(list_variable, list_value)
                for m in range(len(phi)):
                    phi[m].init_values(list_variable, list_value)


                for i in range(len(x)):
                    # with open('test%d.csv' % (i), 'a', newline='') as csvfile:
                    #     writer = csv.writer(csvfile, delimiter=';',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    #     writer.writerow([str(x[i].t).replace(".",","),str(x[i].y[0]).replace(".",","),str(y[i].y[0]).replace(".",",")])
                    x[i].nextStep(dt)
                    y[i].nextStep(dt)
                    self.result_x[i].extend([x[i].y[0]])
                    self.result_y[i].extend([y[i].y[0]])
                    for r in range(len(phi)):
                        phi[r].nextStep(dt)
                        self.result_phi[i].extend([phi[r].y[0]])
        elif len(phi) > 0:
            while phi[0].t < time_animation:
                list_variable = []
                list_value = []
                for k in range(len(phi)):
                    list_variable.append(phi[k].name_coord[0])
                    list_value.append(phi[k].y[0])
                    list_variable.append(phi[k].name_coord[1])
                    list_value.append(phi[k].y[1])
                for m in range(len(phi)):
                    phi[m].init_values(list_variable, list_value)
                for i in range(len(phi)):
                    phi[i].nextStep(dt)
                    self.result_phi[i].extend([phi[i].y[0]])

