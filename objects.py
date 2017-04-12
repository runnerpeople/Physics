#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from kivy.graphics import *
import math
import sys

G = 9.807

class MeshCircle(Mesh):
    def __init__(self,**kwargs):
        super(MeshCircle, self).__init__(**kwargs)

        self.group = kwargs['name']
        self.color = kwargs['color']
        self.mass = kwargs['mass']
        self.velocity = (0.0,0.0)

        self.connected = []

        self.radius_circle = 0
        self.center = []

        self.g = G

        self.move_flag = False

        self.velocity_vector = None

        self.partPendulum = None
        self.Pendulum = None
        try:
            self.partPendulum = kwargs['pendulum']
        except:
            self.partPendulum = False


    def add_conn(self,value):
        self.connected.append(value)

    def collision(self,coord_x,coord_y):
        if math.sqrt(((coord_x - self.center[0]) ** 2) + (
            (coord_y - self.center[1]) ** 2)) > self.radius_circle:
            return False
        else:
            return True

    def extreme_points(self):
        x1,x2 = self.center[0] - self.radius_circle,self.center[0] + self.radius_circle
        y1,y2 = self.center[1] - self.radius_circle,self.center[1] + self.radius_circle
        return (x1,y1,x2,y2)

    def moveBy(self, x, y):
        for i in range(0,len(self.vertices) // 4):
            self.vertices[4*i] += x
            self.vertices[4*i+1] += y

        self.indices = range(len(self.vertices) // 4)

        self.center[0] += x
        self.center[1] += y
        if self.velocity_vector is not None:
            self.velocity_vector.moveBy(x, y)

        for conn in self.connected:
            self.move_flag = True
            conn.moveByObject(x, y,self)

        self.move_flag = False

    def moveByObject(self,x,y,object):
        if not self.move_flag:
            for i in range(0,len(self.vertices) // 4):
                self.vertices[4*i] += x
                self.vertices[4*i+1] += y

            self.indices = range(len(self.vertices) // 4)

            self.center[0] += x
            self.center[1] += y

            if self.velocity_vector is not None:
                self.velocity_vector.moveBy(x,y)

            self.move_flag = True
            for conn in self.connected:
                if conn == object:
                    continue
                conn.moveBy(x, y)

        self.move_flag = False

    def delete_conn(self,object):
        self.connected.remove(object)


class MeshStaticLine(Mesh):
    def __init__(self,**kwargs):
        super(MeshStaticLine,self).__init__(**kwargs)

        self.group = kwargs['name']
        self.color = kwargs['color']

        self.mode = 'line_strip'

    def moveBy(self, x, y):
        for i in range(0,len(self.vertices) // 4):
            self.vertices[4*i] += x
            self.vertices[4*i+1] += y

        self.indices = range(len(self.vertices) // 4)


class MeshNonStaticCircle(Mesh):
    def __init__(self,**kwargs):
        super(MeshNonStaticCircle,self).__init__(**kwargs)

        self.group = kwargs['name']
        self.color = kwargs['color']
        self.mass = float("+inf")

        self.connected = []

        self.radius_circle = (0.,0.)
        self.center = []

        self.static_lines = []

        self.move_flag = False

        self.g = 0

        self.partPendulum = None
        self.Pendulum = None
        try:
            self.partPendulum = kwargs['pendulum']
        except:
            self.partPendulum = False



    def add_static_lines(self,*args):
        for elem in args:
            self.static_lines.append(elem)

    def add_conn(self,value):
        if len(self.connected) == 1 and self.partPendulum:
            raise Exception("Can't append")
        else:
            self.connected.append(value)

    def collision(self, coord_x, coord_y):
        if math.sqrt(((coord_x - self.center[0]) ** 2) + (
                    (coord_y - self.center[1]) ** 2)) > self.radius_circle:
            return False
        else:
            return True

    def extreme_points(self):
        x1, x2 = self.center[0] - self.radius_circle, self.center[0] + self.radius_circle
        y1, y2 = self.center[1] - self.radius_circle, self.center[1] + self.radius_circle
        return (x1, y1, x2, y2)

    def moveBy(self,x,y):
        for i in range(0, len(self.vertices) // 4):
            self.vertices[4 * i] += x
            self.vertices[4 * i + 1] += y

        self.indices = range(len(self.vertices) // 4)

        self.center[0] += x
        self.center[1] += y

        for line in self.static_lines:
            line.moveBy(x,y)

        for conn in self.connected:
            self.move_flag = True
            conn.moveByObject(x,y,self)

        self.move_flag = False

    def moveByObject(self,x,y,object):
        if not self.move_flag:
            for i in range(0,len(self.vertices) // 4):
                self.vertices[4*i] += x
                self.vertices[4*i+1] += y

            self.indices = range(len(self.vertices) // 4)

            self.center[0] += x
            self.center[1] += y

            for line in self.static_lines:
                line.moveBy(x,y)

            self.move_flag = True
            for conn in self.connected:
                if conn == object:
                    continue
                conn.moveBy(x, y)

        self.move_flag = False

    def delete_conn(self,object):
        self.connected.remove(object)

# square = cargo #
class MeshSquare(Mesh):
    def __init__(self,**kwargs):
        super(MeshSquare, self).__init__(**kwargs)

        self.group = kwargs['name']
        self.color = kwargs['color']
        self.mass = kwargs['mass']
        self.velocity = (0.,0.)

        self.connected = []

        self.center = []

        self.g = G

        self.move_flag = False

        self.velocity_vector = None

        self.partPendulum = None
        self.Pendulum = None
        try:
            self.partPendulum = kwargs['pendulum']
        except:
            self.partPendulum = False

    def add_conn(self,value):
        self.connected.append(value)

    def collision(self,coord_x,coord_y):
        if self.vertices[0]<coord_x and self.vertices[1]<coord_y and self.vertices[8]>coord_x and self.vertices[9]>coord_y:
            return True
        else:
            return False

    def extreme_points(self):
        x1, x2 = self.vertices[0], self.vertices[8]
        y1, y2 = self.vertices[1], self.vertices[9]
        return (x1, y1, x2, y2)

    def moveBy(self,x,y):
        for i in range(0, len(self.vertices) // 4):
            self.vertices[4 * i] += x
            self.vertices[4 * i + 1] += y

        self.indices = range(len(self.vertices) // 4)

        self.center[0] += x
        self.center[1] += y

        if self.velocity_vector is not None:
            self.velocity_vector.moveBy(x, y)

        for conn in self.connected:
            self.move_flag = True
            conn.moveBy(x,y,self)

        self.move_flag = False

    def moveByObject(self,x,y,object):
        if not self.move_flag:
            for i in range(0,len(self.vertices) // 4):
                self.vertices[4*i] += x
                self.vertices[4*i+1] += y

            self.indices = range(len(self.vertices) // 4)

            self.center[0] += x
            self.center[1] += y

            if self.velocity_vector is not None:
                self.velocity_vector.moveBy(x, y)

            self.move_flag = True
            for conn in self.connected:
                if conn == object:
                    continue
                conn.moveBy(x, y)

        self.move_flag = False

    def delete_conn(self,object):
        self.connected.remove(object)


class MeshSpring(Mesh):
    def __init__(self,**kwargs):
        super(MeshSpring, self).__init__(**kwargs)

        self.group = kwargs['name']
        self.color = kwargs['color']

        self.center = []

        self.a = kwargs['a']
        self.b = kwargs['b']

        self.a.add_conn(self)
        self.b.add_conn(self)

        self.k = 100
        self.l = 0
        self.l0 = 0

        self.move_flag = False

    def setMinMax(self,x_min,x_max,y_min,y_max):
        self._x_min = x_min
        self._y_min = y_min
        self._x_max = x_max
        self._y_max = y_max

    def collision(self,coord_x,coord_y):
        if self._x_min<coord_x and self._y_min<coord_y and self._x_max>coord_x and self._y_max>coord_y:
            return True
        else:
            return False

    def extreme_points(self):
        x1, x2 = self._x_min, self._x_max
        y1, y2 = self._y_min, self._y_max
        return (x1, y1, x2, y2)

    def moveBy(self,x,y):
        if not self.move_flag:
            for i in range(0, len(self.vertices) // 4):
                self.vertices[4 * i] += x
                self.vertices[4 * i + 1] += y

            self.center[0] += x
            self.center[1] += y

            self._x_min += x
            self._y_min += y
            self._x_max += x
            self._y_max += y

            self.indices = range(len(self.vertices) // 4)


            if not self.a.move_flag:
                self.move_flag = True
                self.a.moveByObject(x, y,self)
            if not self.b.move_flag:
                self.move_flag = True
                self.b.moveByObject(x, y,self)

        self.move_flag = False

    def moveByObject(self,x,y,object):
        if not self.move_flag:
            for i in range(0, len(self.vertices) // 4):
                self.vertices[4 * i] += x
                self.vertices[4 * i + 1] += y

            self.center[0] += x
            self.center[1] += y

            self._x_min += x
            self._y_min += y
            self._x_max += x
            self._y_max += y

            self.indices = range(len(self.vertices) // 4)


        if object == self.a and not self.b.move_flag:
            self.move_flag = True
            self.b.moveBy(x,y)
        elif object == self.b and not self.a.move_flag:
            self.move_flag = True
            self.a.moveBy(x,y)

        self.move_flag = False

    def delete_conn(self):
        self.a.delete_conn(self)
        self.b.delete_conn(self)

    def find_rotate_point(self,obj):
        if self.a == obj:
            return self.b
        elif self.b == obj:
            return self.a
        else:
            return None

class MeshPendulum(Mesh):
    def __init__(self,**kwargs):
        super(MeshPendulum, self).__init__(**kwargs)

        self.group = kwargs['name']
        self.color = kwargs['color']

        self.center = []

        self.a = kwargs['a']
        self.b = kwargs['b']

        self.a.add_conn(self)
        self.b.add_conn(self)

        self.l = 0
        self.phi = 0
        self.phi0 = 0

        self.move_flag = False

    def setMinMax(self, x_min, x_max, y_min, y_max):
        self._x_min = x_min
        self._y_min = y_min
        self._x_max = x_max
        self._y_max = y_max

    def collision(self, coord_x, coord_y):
        if self._x_min < coord_x and self._y_min < coord_y and self._x_max > coord_x and self._y_max > coord_y:
            return True
        else:
            return False

    def extreme_points(self):
        x1, x2 = self._x_min, self._x_max
        y1, y2 = self._y_min, self._y_max
        return (x1, y1, x2, y2)

    def moveBy(self, x, y):
        if not self.move_flag:
            for i in range(0, len(self.vertices) // 4):
                self.vertices[4 * i] += x
                self.vertices[4 * i + 1] += y

            self.center[0] += x
            self.center[1] += y

            self._x_min += x
            self._y_min += y
            self._x_max += x
            self._y_max += y

            self.indices = range(len(self.vertices) // 4)

            if not self.a.move_flag:
                self.move_flag = True
                self.a.moveByObject(x, y, self)
            if not self.b.move_flag:
                self.move_flag = True
                self.b.moveByObject(x, y, self)

        self.move_flag = False

    def moveByObject(self, x, y, object):
        if not self.move_flag:
            for i in range(0, len(self.vertices) // 4):
                self.vertices[4 * i] += x
                self.vertices[4 * i + 1] += y

            self.center[0] += x
            self.center[1] += y

            self._x_min += x
            self._y_min += y
            self._x_max += x
            self._y_max += y

            self.indices = range(len(self.vertices) // 4)

        if object == self.a and not self.b.move_flag:
            self.move_flag = True
            self.b.moveBy(x, y)
        elif object == self.b and not self.a.move_flag:
            self.move_flag = True
            self.a.moveBy(x, y)

        self.move_flag = False

    def delete_conn(self):
        self.a.delete_conn(self)
        self.b.delete_conn(self)

    def find_rotate_point(self, obj):
        if self.a == obj:
            return self.b
        elif self.b == obj:
            return self.a
        else:
            return None