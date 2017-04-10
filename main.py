#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import kivy
kivy.require('1.9.1')

from kivy.config import Config
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '900')

from os.path import join, dirname
import sys
import os

import random
import math

from kivy.app import App, Widget
from kivy.uix.actionbar import ActionBar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ListProperty,ObjectProperty,AliasProperty
from kivy.clock import Clock
from kivy.garden import iconfonts
from kivy.graphics import *
from kivy.animation import Animation

from Widgets import menu
from objects import *
from mode import *
from langrangian import *
from anim import animate

# Random color #
def random_color():
    list_colors = list(map(lambda a: a/100,random.sample(range(100),3)))
    list_colors.append(1.0)
    return list_colors

def tuple_to_str(tuple):
    return ' '.join(list(map(str,tuple)))

def convert_point(x,y,cx,cy,angle):
    x1,y1 = x-cx,y-cy
    x_new = x1*math.cos(angle)-y1*math.sin(angle)
    y_new = x1*math.sin(angle)+y1*math.cos(angle)
    return (x_new+cx,y_new+cy)


class AppActionBar(ActionBar):
    pass

def create_and_register_font():
    # FontAwesome #
    iconfonts.create_fontdict_file(join(dirname(__file__),"Fonts","font-awesome.css",),
                                   join(dirname(__file__),"Fonts","font-awesome.fontd"))

    iconfonts.register("font-awesome",
                       join(dirname(__file__),"Fonts","fontawesome-webfont.ttf"),
                       join(dirname(__file__),"Fonts","font-awesome.fontd"))

    # Flaticon font #
    iconfonts.create_fontdict_file(join(dirname(__file__), "Fonts", "flaticon.css", ),
                                   join(dirname(__file__), "Fonts", "flaticon.fontd"))

    iconfonts.register("flaticon",
                       join(dirname(__file__), "Fonts", "Flaticon.ttf"),
                       join(dirname(__file__), "Fonts", "flaticon.fontd"))



class PropertyLayout(GridLayout):

    def __init__(self,**kwargs):
        super(PropertyLayout,self).__init__(**kwargs)

        self.enabled = False

        self.change = False

    def get_textinput(self,id):
        return self.ids[str(id)]

    def set_text(self,id, value):
        self.ids[str(id)].text = value

    def clear_all(self):
        for i in range(200,209):
            self.ids[str(i)].text = ''

    def disable_all(self):
        self.clear_all()
        self.change = False
        if self.enabled:
            for i in range(200,209):
                self.ids[str(i)].disabled = True
            self.enabled = False

    def enable_all(self):
        if not self.enabled:
            for i in range(200,204):
                self.ids[str(i)].disabled = False
            self.enabled = True

    def enable_for_static_body(self):
        self.enable_all()
        self.ids['203'].disabled = True
        self.ids['204'].disabled = True
        self.ids['207'].disabled = True
        self.ids['208'].disabled = False

    def enable_for_body(self):
        self.enable_all()
        self.ids['204'].disabled = False
        self.ids['208'].disabled = False

    def enable_for_spring(self):
        self.enable_all()
        self.ids['203'].disabled = True
        self.ids['205'].disabled = False
        self.ids['206'].disabled = False

    def enable_for_pendulum(self):
        self.enable_all()
        self.ids['203'].disabled = True
        self.ids['207'].disabled = False

    def changes_value(self):
        self.change = True


class SettingsLayout(GridLayout):

    state = None

    def set_paintmode(self,id):
        if id == 100:
            SettingsLayout.state = PaintMode.circle
        elif id == 101:
            SettingsLayout.state = PaintMode.square
        elif id == 102:
            SettingsLayout.state = PaintMode.circle_static

    def set_dragmode(self,id):
        if id == 110:
            SettingsLayout.state = DragMode.move
        elif id == 111:
            SettingsLayout.state = DragMode.change_properties
        elif id == 112:
            SettingsLayout.state = DragMode.delete
        elif id == 113:
            SettingsLayout.state = DragMode.accept_changes

    def set_vectormode(self,id):
        if id == 120:
            SettingsLayout.state = VectorMode.spring
        elif id == 121:
            SettingsLayout.state = VectorMode.pendulum
        elif id == 122:
            SettingsLayout.state = VectorMode.velocity


class CanvasLayout(FloatLayout):

    def __init__(self,**kwargs):
        super(CanvasLayout,self).__init__(**kwargs)

        self.points = []
        self.world  = []
        self.mass_generalized = []
        self.world_result = []

        self.num_of_objects = 0

        self.__max_objects = 20
        self.__name_index = 0

        self.selected = None
        self.sel = False
        self.sel_square = None

        self.properties = None

    def get_layout(self,type_layout):
        for widget in self.parent.parent.parent.walk():
            if type(widget) == type_layout:
                self.properties = widget
                break

    @staticmethod
    def get_color():
        return random_color()

    def nextName(self,name='object'):
        self.__name_index += 1
        return name + str(self.__name_index)

    def calculate_mass_and_world(self):
        for object in self.world:
            if isinstance(object,(MeshCircle,MeshSquare)):
                self.mass_generalized.append(object.mass)
                self.world_result.append(object)
            elif isinstance(object,(MeshNonStaticCircle)):
                self.mass_generalized.append(float("+inf"))
                self.world_result.append(object)
            elif isinstance(object,(MeshSpring)):
                self.mass_generalized.append(0)
                self.world_result.append(object)
            elif isinstance(object,(MeshPendulum)):
                self.mass_generalized.pop()
                self.mass_generalized.pop()
                self.world_result.pop()
                self.world_result.pop()
                self.mass_generalized.append(object.b.mass * object.l ** 2)
                self.world_result.append(object)

    def on_touch_down(self, touch):
        if self.num_of_objects == self.__max_objects or not self.collide_point(*touch.pos):
            return None
        if SettingsLayout.state == None:
            return None
        elif SettingsLayout.state in (VectorMode.spring,VectorMode.pendulum,VectorMode.velocity):
            self.points = []
            self.points.append([touch.x,touch.y])
        elif SettingsLayout.state == DragMode.move:
            for child in self.world:
                if child.collision(touch.x,touch.y):
                    self.selected = child
                    self.sel = True
                    with self.canvas.before:
                        points = child.extreme_points()
                        self.sel_square = Line(rectangle=(points[0],points[1],points[2]-points[0],points[3]-points[1]),
                                                dash_length=5, dash_offset=2,group='selected')
                    break
        elif SettingsLayout.state == DragMode.change_properties:
            for child in self.world:
                if child.collision(touch.x,touch.y):
                    self.selected = child
                    if isinstance(self.selected, (MeshCircle,MeshNonStaticCircle,MeshSquare)):
                        self.get_layout(PropertyLayout)
                        if type(self.selected) == MeshCircle or type(self.selected) == MeshSquare:
                            self.properties.disable_all()
                            self.properties.enable_for_body()
                            self.properties.set_text(200, self.selected.group)
                            self.properties.set_text(201,tuple_to_str(self.selected.color.rgba))
                            self.properties.set_text(202,tuple_to_str(self.selected.center))
                            self.properties.set_text(203,tuple_to_str(self.selected.velocity))
                            self.properties.set_text(204, str(self.selected.mass))
                            self.properties.set_text(208, str(self.selected.g))
                        elif type(self.selected) == MeshNonStaticCircle:
                            self.properties.disable_all()
                            self.properties.enable_for_static_body()
                            self.properties.set_text(200, self.selected.group)
                            self.properties.set_text(201, tuple_to_str(self.selected.color.rgba))
                            self.properties.set_text(202, tuple_to_str(self.selected.center))
                            self.properties.set_text(208, str(self.selected.g))
                    elif isinstance(self.selected, MeshSpring):
                        self.get_layout(PropertyLayout)
                        self.properties.disable_all()
                        self.properties.enable_for_spring()
                        self.properties.set_text(200, self.selected.group)
                        self.properties.set_text(201,tuple_to_str(self.selected.color.rgba))
                        self.properties.set_text(202,tuple_to_str(self.selected.center))
                        self.properties.set_text(205, str(self.selected.k))
                        self.properties.set_text(206, str(self.selected.l0))
                    elif isinstance(self.selected, MeshPendulum):
                        self.get_layout(PropertyLayout)
                        self.properties.disable_all()
                        self.properties.enable_for_pendulum()
                        self.properties.set_text(200, self.selected.group)
                        self.properties.set_text(201,tuple_to_str(self.selected.color.rgba))
                        self.properties.set_text(202,tuple_to_str(self.selected.center))
                        self.properties.set_text(207, str(self.selected.phi0))
                    break
                else:
                    if self.properties is not None:
                        self.properties.disable_all()
        elif SettingsLayout.state == DragMode.delete:
            for child in self.world:
                if child.collision(touch.x,touch.y):
                    self.selected = child
                    if not isinstance(self.selected, (MeshSpring, MeshPendulum)):
                        while len(self.selected.connected) != 0:
                            for object in self.selected.connected:
                                self.canvas.remove_group(object.group)
                                object.delete_conn()
                        self.canvas.remove_group(child.group)
                        self.world.remove(child)

                    elif not isinstance(self.selected, MeshPendulum):
                        child.delete_conn()
                        self.canvas.remove_group(child.group)
                        self.world.remove(child)
                    else:
                        child.delete_conn()
                        self.canvas.remove_group(child.group)
                        while len(self.selected.a.connected) != 0:
                            for object in self.selected.a.connected:
                                self.canvas.remove_group(object.group)
                                object.delete_conn()
                        while len(self.selected.b.connected) != 0:
                            for object in self.selected.b.connected:
                                self.canvas.remove_group(object.group)
                                object.delete_conn()
                        self.canvas.remove_group(self.selected.a.group)
                        self.canvas.remove_group(self.selected.b.group)
                        self.world.remove(self.selected.a)
                        self.world.remove(self.selected.b)
                        self.world.remove(child)
                    break
        elif SettingsLayout.state == DragMode.accept_changes:
            if self.properties is not None and self.properties.change == True and self.selected is not None:
                if type(self.selected) == MeshCircle or type(self.selected) == MeshSquare:
                    self.selected.group = self.properties.get_textinput(200).text
                    validate = self.properties.get_textinput(201).text
                    if len(validate.split(" ")) == 4:
                        try:
                            list_color = list(map(float, validate.split(" ")))
                            result = list(filter(lambda a: a >= 0 and a <= 1,list_color))
                            if len(result) < 4:
                                raise Exception
                            self.canvas.remove(self.selected.color)
                            self.canvas.remove_group(self.selected.group)
                            self.selected.color = Color(*list_color)
                            self.canvas.add(self.selected.color)
                            self.canvas.add(self.selected)
                        except:
                            sys.stderr.write('You need write 4 float values to change color object')
                            self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    else:
                        sys.stderr.write('You need write 4 float values to change color object')
                        self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    validate2 = self.properties.get_textinput(202).text
                    if len(validate2.split(" ")) == 2:
                        try:
                            list_moveBy = list(map(float, validate2.split(" ")))
                            self.selected.moveBy(list_moveBy[0]-self.selected.center[0],list_moveBy[1]-self.selected.center[1])
                        except:
                            sys.stderr.write('You need write 2 float values to moveBy object')
                            self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    else:
                        sys.stderr.write('You need write 2 float values to moveBy object')
                        self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    validate3 = self.properties.get_textinput(203).text
                    if len(validate3.split(" ")) == 2:
                        try:
                            list_velocity = list(map(float, validate3.split(" ")))
                            self.selected.velocity = list_velocity
                            line_points = [self.selected.center[0],self.selected.center[1], 0, 0,
                                          self.selected.center[0] + list_velocity[0],self.selected.center[1] + list_velocity[1], 0, 0]
                            if self.selected.velocity_vector is not None:
                                self.canvas.remove(self.selected.velocity_vector.color)
                                self.canvas.remove_group(self.selected.velocity_vector.group)

                            static_line = MeshStaticLine(name='velocity_vector' + self.selected.group, color=Color(1, 0, 0))
                            static_line.vertices = line_points
                            static_line.indices = range(len(line_points) // 4)

                            self.selected.velocity_vector = static_line

                            self.canvas.add(Color(1, 0, 0))
                            self.canvas.add(static_line)
                        except:
                            sys.stderr.write('You need write 2 float values to velocity object')
                            self.properties.get_textinput(203).text = tuple_to_str(self.selected.velocity)
                    else:
                        sys.stderr.write('You need write 2 float values to velocity object')
                        self.properties.get_textinput(203).text = tuple_to_str(self.selected.velocity)
                    validate4 = self.properties.get_textinput(204).text
                    try:
                        new_mass = float(validate4)
                        self.selected.mass = new_mass
                    except:
                        sys.stderr.write('You need write 1 float value to mass object')
                        self.properties.get_textinput(204).text = str(self.selected.mass)
                    validate5 = self.properties.get_textinput(208).text
                    try:
                        new_g = float(validate5)
                        self.selected.g = new_g
                    except:
                        sys.stderr.write('You need write 1 float value to gravity constant object')
                        self.properties.get_textinput(208).text = str(self.selected.g)
                elif type(self.selected) == MeshNonStaticCircle:
                    self.selected.group = self.properties.get_textinput(200).text
                    validate = self.properties.get_textinput(201).text
                    if len(validate.split(" ")) == 4:
                        try:
                            list_color = list(map(float, validate.split(" ")))
                            result = list(filter(lambda a: a >= 0 and a <= 1, list_color))
                            if len(result) < 4:
                                raise Exception
                            self.canvas.remove(self.selected.color)
                            self.canvas.remove_group(self.selected.group)
                            self.selected.color = Color(*list_color)
                            self.canvas.add(self.selected.color)
                            self.canvas.add(self.selected)
                        except:
                            sys.stderr.write('You need write 4 float values to change color object')
                            self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    else:
                        sys.stderr.write('You need write 4 float values to change color object')
                        self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    validate2 = self.properties.get_textinput(202).text
                    if len(validate2.split(" ")) == 2:
                        try:
                            list_moveBy = list(map(float, validate2.split(" ")))
                            self.selected.moveBy(list_moveBy[0] - self.selected.center[0],
                                                 list_moveBy[1] - self.selected.center[1])
                        except:
                            sys.stderr.write('You need write 2 float values to moveBy object')
                            self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    else:
                        sys.stderr.write('You need write 2 float values to moveBy object')
                        self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    validate4 = self.properties.get_textinput(204).text
                    try:
                        new_mass = float(validate4)
                        self.selected.mass = new_mass
                    except:
                        sys.stderr.write('You need write 1 float value to mass object')
                        self.properties.get_textinput(204).text = str(self.selected.mass)
                    validate5 = self.properties.get_textinput(208).text
                    try:
                        new_g = float(validate5)
                        self.selected.g = new_g
                    except:
                        sys.stderr.write('You need write 1 float value to gravity constant object')
                        self.properties.get_textinput(208).text = str(self.selected.g)
                elif type(self.selected) == MeshSpring:
                    self.selected.group = self.properties.get_textinput(200).text
                    validate = self.properties.get_textinput(201).text
                    if len(validate.split(" ")) == 4:
                        try:
                            list_color = list(map(float, validate.split(" ")))
                            result = list(filter(lambda a: a >= 0 and a <= 1, list_color))
                            if len(result) < 4:
                                raise Exception
                            self.canvas.remove(self.selected.color)
                            self.canvas.remove_group(self.selected.group)
                            self.selected.color = Color(*list_color)
                            self.canvas.add(self.selected.color)
                            self.canvas.add(self.selected)
                        except:
                            sys.stderr.write('You need write 4 float values to change color object')
                            self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    else:
                        sys.stderr.write('You need write 4 float values to change color object')
                        self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    validate2 = self.properties.get_textinput(202).text
                    if len(validate2.split(" ")) == 2:
                        try:
                            list_moveBy = list(map(float, validate2.split(" ")))
                            self.selected.moveBy(list_moveBy[0] - self.selected.center[0],
                                                 list_moveBy[1] - self.selected.center[1])
                        except:
                            sys.stderr.write('You need write 2 float values to moveBy object')
                            self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    else:
                        sys.stderr.write('You need write 2 float values to moveBy object')
                        self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    validate4 = self.properties.get_textinput(205).text
                    try:
                        new_mass = float(validate4)
                        self.selected.k = new_mass
                    except:
                        sys.stderr.write('You need write 1 float value to k spring')
                        self.properties.get_textinput(205).text = str(self.selected.k)
                    else:
                        sys.stderr.write('You need write 1 float value to k spring')
                        self.properties.get_textinput(205).text = str(self.selected.k)
                    validate5 = self.properties.get_textinput(206).text
                    try:
                        new_l0 = float(validate5)
                        self.selected.l0 = new_l0
                    except:
                        sys.stderr.write('You need write 1 float value to l spring')
                        self.properties.get_textinput(206).text = str(self.selected.l0)
                    else:
                        sys.stderr.write('You need write 1 float value to l spring')
                        self.properties.get_textinput(206).text = str(self.selected.l0)
                elif type(self.selected) == MeshPendulum:
                    self.selected.group = self.properties.get_textinput(200).text
                    validate = self.properties.get_textinput(201).text
                    if len(validate.split(" ")) == 4:
                        try:
                            list_color = list(map(float, validate.split(" ")))
                            result = list(filter(lambda a: a >= 0 and a <= 1, list_color))
                            if len(result) < 4:
                                raise Exception
                            self.canvas.remove(self.selected.color)
                            self.canvas.remove_group(self.selected.group)
                            self.selected.color = Color(*list_color)
                            self.canvas.add(self.selected.color)
                            self.canvas.add(self.selected)
                        except:
                            sys.stderr.write('You need write 4 float values to change color object')
                            self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    else:
                        sys.stderr.write('You need write 4 float values to change color object')
                        self.properties.get_textinput(201).text = tuple_to_str(self.selected.color.rgba)
                    validate2 = self.properties.get_textinput(202).text
                    if len(validate2.split(" ")) == 2:
                        try:
                            list_moveBy = list(map(float, validate2.split(" ")))
                            self.selected.moveBy(list_moveBy[0] - self.selected.center[0],
                                                 list_moveBy[1] - self.selected.center[1])
                        except:
                            sys.stderr.write('You need write 2 float values to moveBy object')
                            self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    else:
                        sys.stderr.write('You need write 2 float values to moveBy object')
                        self.properties.get_textinput(202).text = tuple_to_str(self.selected.center)
                    validate4 = self.properties.get_textinput(207).text
                    try:
                        new_phi0 = float(validate4)
                        self.selected.phi0 = math.radians(new_phi0)
                    except:
                        sys.stderr.write('You need write 1 float value to phi0 pendulum')
                        self.properties.get_textinput(207).text = str(self.selected.phi0)
                    else:
                        sys.stderr.write('You need write 1 float value to phi0 pendulum')
                        self.properties.get_textinput(207).text = str(self.selected.phi0)


    def on_touch_up(self, touch):
        if self.num_of_objects == self.__max_objects or not self.collide_point(*touch.pos):
            return None
        if SettingsLayout.state == None:
            pass
        elif SettingsLayout.state in (PaintMode.circle,PaintMode.circle_static):
            points = [[touch.x,touch.y]]
            circle_point = []
            radius = 20 if SettingsLayout.state == PaintMode.circle_static else 10
            for i in range(50):
                alpha = 2 * i * math.pi / 50
                point = (points[0][0] + math.sin(alpha) * radius, points[0][1] + math.cos(alpha) * radius,math.sin(alpha),math.cos(alpha))
                if not self.collide_point(point[0],point[1]):
                    self.points = []
                    return None
                circle_point.extend(point)

            mesh_object,color = None, None
            if SettingsLayout.state == PaintMode.circle:
                color = Color(*self.get_color())
                mesh_object = MeshCircle(name=self.nextName(),color = color,mass = 1)
            else:
                color = Color(0,0,0)
                mesh_object = MeshNonStaticCircle(name=self.nextName(),color = color, mass = 1)

            mesh_object.vertices=circle_point
            mesh_object.indices=range(len(circle_point)//4)
            if SettingsLayout.state == PaintMode.circle:
                mesh_object.mode = 'triangle_fan'
            else:
                mesh_object.mode = 'line_loop'
            mesh_object.radius_circle = radius
            mesh_object.center = points[0]

            if SettingsLayout.state == PaintMode.circle_static:
                name_group_line = mesh_object.group
                line_points = [points[0][0],points[0][1]-5,0,0,points[0][0],points[0][1]+5,0,0]
                static_line  = MeshStaticLine(name=name_group_line,color=Color(0,0,0))
                static_line.vertices = line_points
                static_line.indices  = range(len(line_points)//4)

                line_points2 = [points[0][0]-5,points[0][1], 0, 0, points[0][0]+5,points[0][1], 0, 0]
                static_line2 = MeshStaticLine(name=name_group_line, color=Color(0, 0, 0))
                static_line2.vertices = line_points2
                static_line2.indices = range(len(line_points) // 4)

                self.canvas.add(Color(0,0,0))
                self.canvas.add(static_line)
                self.canvas.add(Color(0,0,0))
                self.canvas.add(static_line2)
                mesh_object.add_static_lines(static_line,static_line2)
                self.world.append(mesh_object)
                self.canvas.add(color)
                self.canvas.add(mesh_object)
                self.num_of_objects += 1
            else:
                self.world.append(mesh_object)
                self.canvas.add(color)
                self.canvas.add(mesh_object)
                self.num_of_objects += 1

        elif SettingsLayout.state == PaintMode.square:
            points = [touch.x, touch.y]
            color = Color(*self.get_color())

            if not self.collide_point(*points):
                self.points = []
                return None

            square_point = []
            square_point.extend([points[0]-20,points[1]-20,0,0])
            square_point.extend([points[0]-20,points[1]+20,0,1])
            square_point.extend([points[0]+20,points[1]+20,1,1])
            square_point.extend([points[0]+20,points[1]-20,1,0])


            mesh_object = MeshSquare(name=self.nextName(),color = color, mass = 1)
            mesh_object.vertices=square_point
            mesh_object.indices=range(len(square_point)//4)
            mesh_object.mode = 'triangle_fan'
            mesh_object.center = [points[0],points[1]]
            mesh_object.mass = 100


            self.world.append(mesh_object)
            self.canvas.add(color)
            self.canvas.add(mesh_object)
            self.num_of_objects += 1
        elif SettingsLayout.state == VectorMode.spring:
            points = [self.points.pop(0), [touch.x, touch.y]]
            first_object = None
            for child in self.world:
                if child.collision(points[0][0], points[0][1]):
                    points[0] = child.center
                    first_object = child
                    break
            if not first_object:
                self.points = []
                return None
            second_object = None
            for child in self.world:
                if child.collision(points[1][0], points[1][1]):
                    points[1] = child.center
                    second_object = child
                    break
            if not second_object:
                self.points = []
                return None
            color = Color(*self.get_color())

            c = math.sqrt((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2)

            mesh_object = MeshSpring(name=self.nextName("spring"), color=color, a=first_object, b=second_object)
            mesh_object.setMinMax(min(points[0][0],points[1][0]),max(points[0][0],points[1][0]),
                                  min(points[0][1],points[1][1]),max(points[0][1],points[1][1]))
            points_ext = mesh_object.extreme_points()
            center_point = [(points_ext[2]- points_ext[0]) / 2 + points_ext[0], (points_ext[3] - points_ext[1]) / 2 + points_ext[1]]
            spring_point = [points[0][0],points[0][1],0,0,points[1][0],points[1][1],0,0]

            mesh_object.l = c
            mesh_object.center = center_point
            mesh_object.vertices = spring_point
            mesh_object.indices = range(len(spring_point) // 4)
            mesh_object.mode = 'line_strip'

            self.world.append(mesh_object)
            self.canvas.add(color)
            self.canvas.add(mesh_object)
            self.num_of_objects += 1

        elif SettingsLayout.state == VectorMode.pendulum:
            points = [self.points.pop(0), [touch.x, touch.y]]

            c = math.sqrt((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2)

            b = math.fabs(points[0][1] - points[1][1])
            phi = math.acos(b / c)

            circle_point_static = []
            circle_point = []
            radius_first = 20
            radius_second = 10
            for i in range(50):
                alpha = 2 * i * math.pi / 50
                point = (points[0][0] + math.sin(alpha) * radius_first, points[0][1] + math.cos(alpha) * radius_first, math.sin(alpha),math.cos(alpha))
                point_second = (points[1][0] + math.sin(alpha) * radius_second, points[1][1] + math.cos(alpha) * radius_second, math.sin(alpha),math.cos(alpha))
                if not self.collide_point(point[0], point[1]) or not self.collide_point(point_second[0], point_second[1]):
                    self.points = []
                    return None
                circle_point_static.extend(point)
                circle_point.extend(point_second)

            first_object = MeshNonStaticCircle(name=self.nextName(), color=Color(0, 0, 0), pendulum=True)
            second_object, second_color = None, Color(*self.get_color())
            second_object = MeshCircle(name=self.nextName(), color=second_color, mass=1,pendulum=True)

            first_object.vertices = circle_point_static
            second_object.vertices = circle_point
            first_object.indices = range(len(circle_point) // 4)
            second_object.indices = range(len(circle_point) // 4)
            first_object.mode = 'line_loop'
            second_object.mode = 'triangle_fan'

            first_object.radius_circle = radius_first
            second_object.radius_circle = radius_second
            first_object.center = points[0]
            second_object.center = points[1]

            name_group_line = first_object.group
            line_points = [points[0][0], points[0][1] - 5, 0, 0, points[0][0], points[0][1] + 5, 0, 0]
            static_line = MeshStaticLine(name=name_group_line, color=Color(0, 0, 0))
            static_line.vertices = line_points
            static_line.indices = range(len(line_points) // 4)

            line_points2 = [points[0][0] - 5, points[0][1], 0, 0, points[0][0] + 5, points[0][1], 0, 0]
            static_line2 = MeshStaticLine(name=name_group_line, color=Color(0, 0, 0))
            static_line2.vertices = line_points2
            static_line2.indices = range(len(line_points) // 4)

            self.canvas.add(Color(0, 0, 0))
            self.canvas.add(static_line)
            self.canvas.add(Color(0, 0, 0))
            self.canvas.add(static_line2)
            first_object.add_static_lines(static_line, static_line2)

            self.world.append(first_object)
            self.canvas.add(Color(0,0,0))
            self.canvas.add(first_object)
            self.world.append(second_object)
            self.canvas.add(second_color)
            self.canvas.add(second_object)

            self.num_of_objects += 2

            color = Color(*self.get_color())
            mesh_object = MeshPendulum(name=self.nextName("pendulum"), color=color, a=first_object, b=second_object)
            first_object.Pendulum = mesh_object
            second_object.Pendulum = mesh_object
            mesh_object.setMinMax(min(points[0][0], points[1][0]), max(points[0][0], points[1][0]),
                                  min(points[0][1], points[1][1]), max(points[0][1], points[1][1]))
            points_ext = mesh_object.extreme_points()
            center_point = [(points_ext[2] - points_ext[0]) / 2 + points_ext[0],
                            (points_ext[3] - points_ext[1]) / 2 + points_ext[1]]
            spring_point = [points[0][0]-2, points[0][1], 0, 0, points[0][0]+c*math.sin(phi)-2,points[0][1]-c*math.cos(phi), 0, 0,
                            points[0][0]+2, points[0][1], 0, 0, points[0][0]+c*math.sin(phi)+2,points[0][1]-c*math.cos(phi), 0, 0]

            mesh_object.l = c
            mesh_object.phi = phi
            mesh_object.center = center_point
            mesh_object.vertices = spring_point
            mesh_object.indices = range(len(spring_point) // 4)
            mesh_object.mode = 'lines'

            self.world.append(mesh_object)
            self.canvas.add(color)
            self.canvas.add(mesh_object)
            self.num_of_objects += 1

        elif SettingsLayout.state == VectorMode.velocity:
            points = [self.points.pop(0), [touch.x, touch.y]]
            object = None
            for child in self.world:
                if child.collision(points[0][0], points[0][1]) and isinstance(child,(MeshCircle,MeshSquare)):
                    points[0] = child.center
                    object = child
                    break
            if not object:
                self.points = []
                return None

            velocity_vector = [points[1][0]-points[0][0],points[1][1]-points[0][1]]
            line_points = [points[0][0],points[0][1],0,0,points[1][0],points[1][1],0,0]

            static_line = MeshStaticLine(name='velocity_vector' + object.group, color=Color(1, 0, 0))
            static_line.vertices = line_points
            static_line.indices = range(len(line_points) // 4)
            static_line.moveBy(points[0][0]-object.center[0],points[0][1]-object.center[1])

            object.velocity = velocity_vector
            object.velocity_vector = static_line

            self.canvas.add(Color(1,0,0))
            self.canvas.add(static_line)

        elif SettingsLayout.state == DragMode.move and self.sel == True:
            self.canvas.before.remove_group('selected')
            self.sel = False
            self.sel_square = None


    def on_touch_move(self, touch):
        if self.num_of_objects == self.__max_objects or not self.collide_point(*touch.pos):
            self.points = []
            return None
        elif SettingsLayout.state == DragMode.move and self.sel == True:
            self.canvas.before.remove_group('selected')
            child = self.selected
            with self.canvas.before:
                child.moveBy(touch.x - child.center[0], touch.y - child.center[1])
                points = child.extreme_points()
                self.sel_square = Line(rectangle=(points[0], points[1], points[2] - points[0], points[3] - points[1]),
                                       dash_length=5, dash_offset=2, group='selected')



class PhysicsGUI(BoxLayout):
    def __init__(self,**kwargs):
        super(PhysicsGUI, self).__init__(**kwargs)

class PhysicsApp(App):

    def get_layout(self,type_layout):
        for widget in self.root.walk():
            if type(widget) == type_layout:
                self.properties = widget
                break

    def button(self, id):
        if id == 51:
            self.get_layout(CanvasLayout)
            self.properties.calculate_mass_and_world()
            langrange = System(self.properties.world_result,self.properties.mass_generalized)

            animate(langrange)


    def build(self):
        return PhysicsGUI()


if __name__ == '__main__':
    create_and_register_font()
    PhysicsApp().run()