#!/usr/bin/env python
# -*- coding: utf-8 -*-#

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.properties import ListProperty, ObjectProperty,\
        StringProperty, BooleanProperty, NumericProperty


class MenuItem(Widget):
    '''Background color, in the format (r, g, b, a).'''
    background_color_normal = ListProperty([0.2, 0.2, 0.2, 1])
    background_color_down = ListProperty([0.3, 0.3, 0.3, 1])
    background_color = ListProperty([])
    separator_color = ListProperty([0.8, 0.8, 0.8, 1])
    text_color = ListProperty([1,1,1,1])
    inside_group = BooleanProperty(False)
    pass

class MenuSubmenu(MenuItem, Spinner):
    triangle = ListProperty()

    def __init__(self, **kwargs):
        self.list_menu_item = []
        super().__init__(**kwargs)
        self.dropdown_cls = MenuDropDown

    def add_widget(self, item):
        self.list_menu_item.append(item)
        self.show_submenu()

    def show_submenu(self):
        self.clear_widgets()
        for item in self.list_menu_item:
            item.inside_group = True
            self._dropdown.add_widget(item)

    def _build_dropdown(self, *largs):
        if self._dropdown:
            self._dropdown.unbind(on_dismiss=self._toggle_dropdown)
            self._dropdown.dismiss()
            self._dropdown = None
        self._dropdown = self.dropdown_cls()
        self._dropdown.bind(on_dismiss=self._toggle_dropdown)

    def _update_dropdown(self, *largs):
        pass

    def _toggle_dropdown(self, *largs):
        self.is_open = not self.is_open
        ddn = self._dropdown
        ddn.size_hint_x = None
        if not ddn.container:
            return
        children = ddn.container.children
        if children:
            ddn.width = max(self.width, max(c.width for c in children))
        else:
            ddn.width = self.width
        for item in children:
            item.size_hint_y = None
            item.height = max([self.height, 48])

    def clear_widgets(self):
        self._dropdown.clear_widgets()

class MenuDropDown(DropDown):
        pass

class MenuButton(MenuItem,Button):
    icon = StringProperty(None, allownone=True)
    pass

class MenuEmptySpace(MenuItem):
    pass

class MenuBar(BoxLayout):

    '''Background color, in the format (r, g, b, a).'''
    background_color = ListProperty([0.2, 0.2, 0.2, 1])
    separator_color = ListProperty([0.8, 0.8, 0.8, 1])

    def __init__(self, **kwargs):
        self.itemsList = []
        super().__init__(**kwargs)

    def add_widget(self, item, index=0):
        if not isinstance(item, MenuItem):
            raise TypeError("MenuBar accepts only MenuItem widgets")
        super().add_widget(item, index)
        if index == 0:
            index = len(self.itemsList)
        self.itemsList.insert(index, item)