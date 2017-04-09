#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from enum import Enum


class PaintMode(Enum):

    circle = 1
    square = 2
    circle_static = 3


class DragMode(Enum):

    move = 1
    change_properties = 2
    delete = 3
    accept_changes = 4


class VectorMode(Enum):

    spring = 1
    velocity = 2
    pendulum = 3
