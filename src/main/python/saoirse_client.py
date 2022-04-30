# This file is:
# src/python/saoirse_client.py


"""
MIT License

Copyright (c) 2022 Duncan Brasher (Dunkmania101)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import pyglet
from sys import argv
from os import path, makedirs
from random import choice as randchoice
from threading import Thread
from PIL import ImageTk, Image, ImageDraw, ImageFont
from tkinter import Tk, Label as TkLabel, BOTH as TkBOTH
from time import time as gettime
from json import dumps as jdumps, loads as jloads
from saoirse_base import saoirse_base_version, ThreeDimensionalPosition, logger, expand_full_path, Identifier, MainGameObject, InteractableObject, SpaceGameObject, ThreeDimensionalShape
from saoirse_server import saoirse_server_version, SaoirseServer, SaoirseIdentifierEnum


saoirse_client_version = "0.0.1"


default_font = "Exo 2 Regular"
#default_font = None


class BaseWidgets:
    class BaseWidget(MainGameObject, InteractableObject):
        def __init__(self, ide, parent=None, left=0, top=0, width=20, height=20):
            self.set_parent(parent)

            super().__init__(ide, None)

            self.children = {}
            self.set_left(left)
            self.set_top(top)
            self.set_width(width)
            self.set_height(height)

        def set_parent(self, parent):
            self.parent = parent

        def get_parent(self):
            return self.parent

        def get_children(self):
            return self.children

        def add_child(self, child):
            child.set_parent(self)
            self.children[child.get_id().get_path_str()] = child

        def set_width(self, width):
            self.width = width

        def set_height(self, height):
            self.height = height

        def get_width(self):
            return self.width

        def get_height(self):
            return self.height

        def set_left(self, left):
            self.left = left

        def set_top(self, top):
            self.top = top

        def get_left(self):
            return self.left

        def get_top(self):
            return self.top

        def get_right(self):
            return self.get_left() + self.get_width()

        def get_bottom(self):
            return self.get_top() + self.get_height()

        def draw_image(self, img, left=0, top=0, right=0, bottom=0, shade_red=None, shade_green=None, shade_blue=None, shade_alpha=None):
            self.get_parent().draw_image(img, self.get_top() + top, self.get_left() + left, self.get_right() + right, self.get_bottom() + bottom, shade_red=shade_red, shade_green=shade_green, shade_blue=shade_blue, shade_alpha=shade_alpha)

        def draw_model(self, model, x=0, y=0, z=0, dots_per_meter=1):
            self.get_parent().draw_model(model, self.get_left() + x, y, self.get_top() + z, dots_per_meter)

        def draw_text(self, text, font_size=11, left=0, top=0, right=0, bottom=0, font_name=default_font, color_red=150, color_green=150, color_blue=100, color_alpha=255):
            self.get_parent().draw_text(text=text, font_size=font_size, left=self.get_left() + left, top=self.get_top() + top, right=self.get_right() + right, bottom=self.get_bottom() + bottom, font_name=font_name, color_red=color_red, color_green=color_green, color_blue=color_blue, color_alpha=color_alpha)

        def play_sound(self, ide):
            self.get_parent().play_sound(ide)

        def set_server(self, server):
            if self.get_parent() is not None:
                self.get_parent().set_server(server)

        def get_server(self):
            if self.get_parent() is not None:
                return self.get_parent().get_server()
            return None

        def on_removed(self):
            for child in self.get_children().values():
                child.on_removed()
            super().on_removed()

        def draw_content(self):
            pass

        def draw(self):
            self.draw_content()
            for child in self.get_children().values():
                child.draw()

        def tick(self, *args, **kwargs):
            super().tick()
            for child in self.get_children().values():
                child.tick()
            self.tick_content()

        def tick_content(self):
            pass

    class ImageWidget(BaseWidget):
        def __init__(self, ide, parent=None, width=20, height=20, left=0, top=0,  img="", shade_red=None, shade_green=None, shade_blue=None, shade_alpha=None):
            super().__init__(ide, parent=parent, left=left, top=top, width=width, height=height)

            self.img = img
            self.shade_red=shade_red
            self.shade_green=shade_green
            self.shade_blue=shade_blue
            self.shade_alpha=shade_alpha

        def tick_content(self):
            self.draw_image(self.get_left(), self.get_top(), self.get_right(), self.get_bottom())

    class TextWidget(BaseWidget):
        def __init__(self, ide, parent=None, width=20, height=20, left=0, top=0, text="", font_name=default_font, color_red=150, color_green=150, color_blue=100, color_alpha=255):
            super().__init__(ide, parent=parent, left=left, top=top, width=width, height=height)

            self.set_text(text)
            self.set_font_name(font_name)
            self.set_color_red(color_red)
            self.set_color_green(color_green)
            self.set_color_blue(color_blue)
            self.set_color_alpha(color_alpha)

        def set_text(self, text):
            self.text = text

        def get_text(self):
            return self.text

        def set_font_name(self, font_name):
            self.font_name = font_name

        def get_font_name(self):
            return self.font_name

        def get_font_size(self):
            return self.get_width() / (len(self.get_text()) + 1)

        def set_color(self, color_red=-1, color_green=-1, color_blue=-1, color_alpha=-1):
            if color_red != -1:
                self.set_color_red(color_red)
            if color_green != -1:
                self.set_color_green(color_green)
            if color_blue != -1:
                self.set_color_blue(color_blue)
            if color_alpha != -1:
                self.set_color_alpha(color_alpha)

        def set_color_red(self, color=255):
            self.color_red = color

        def get_color_red(self):
            return self.color_red

        def set_color_green(self, color=255):
            self.color_green = color

        def get_color_green(self):
            return self.color_green

        def set_color_blue(self, color=255):
            self.color_blue = color

        def get_color_blue(self):
            return self.color_blue

        def set_color_alpha(self, color=255):
            self.color_alpha = color

        def get_color_alpha(self):
            return self.color_alpha

        def tick_content(self):
            self.draw_text(self.get_text(), left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), font_size=self.get_font_size(), font_name=self.get_font_name(), color_red=self.get_color_red(), color_green=self.get_color_green(), color_blue=self.get_color_blue(), color_alpha=self.get_color_alpha())


    class ButtonWidget(BaseWidget):
        def __init__(self, ide, parent=None, width=20, height=20, left=0, top=0, label=""):
            super().__init__(ide, parent=parent, left=left, top=top, width=width, height=height)

            self.label = label

        def draw_content(self):
            self.add_child(BaseWidgets.TextWidget(self.get_id(), width=self.get_width() * 0.75, height=self.get_height(), left=0, top=0, text=self.get_label()))

        def get_label(self):
            return self.label


class ScreenWidget(BaseWidgets.BaseWidget):
    def __init__(self, ide, parent=None, left=0, top=0, width=1200, height=800, title=""):
        super().__init__(ide, parent=parent, left=left, top=top, width=width, height=height)

        self.title = title

    def get_title(self):
        return self.title


class SaoirseClientWidgets:
    class ClientWidgets:
        class Buttons:
            class ButtonIdentifiers(SaoirseIdentifierEnum):
                def get_base_ide(self):
                    return Identifier(["widgets", "buttons"]).extend(super().get_base_ide())

                singleplayer = "singleplayer"

            class SaoirseClientSingleplayerButton(BaseWidgets.ButtonWidget):
                def __init__(self, parent=None, left=50, top=50, width=20, height=5):
                    super().__init__(SaoirseClientWidgets.ClientWidgets.Buttons.ButtonIdentifiers.singleplayer.get_identifier(), parent=parent, left=left, top=top, width=width, height=height, label="Singleplayer")

                def tick_content(self):
                    pass
                    # self.draw_image(Identifier(["resources", saoirse_id, "media", "pic1.png"]), left=self.get_left(), top=self.get_top(), right=self.get_left() + self.get_width(), bottom=self.get_top() + self.get_height())

    class ClientScreens:
        class ScreenIdentifiers(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier(["screens"]).extend(super().get_base_ide())

            main_window = "main_window"
            main = "main"
            home = "home"
            world = "world"

        class SaoirseClientWorldScreen(ScreenWidget):
            def __init__(self, parent=None, player_id="Player1", server=None):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.world.get_identifier(), parent=parent, title="")

                self.server_is_local = server is None
                if self.server_is_local:
                    self.create_local_server()
                else:
                    self.set_server(server)
                self.set_player_id(player_id)
                self.connect_with_server()

            def set_server(self, server):
                self.server = server

            def create_local_server(self, save_dir=None, save_name=None):
                if save_name is None:
                    save_name = "world1"
                if save_dir is None:
                    save_dir = path.join(self.get_parent().get_parent().get_data_dir(), "saves", save_name)
                self.server = SaoirseServer(save_file=path.join(save_dir, f"{save_name}.pkl"))
                def tick_server():
                    while not self.server.removed:
                         self.server.tick()
                Thread(target=tick_server).start()

            def get_server(self):
                return self.server

            def set_player_id(self, ide):
                self.player_id = ide

            def get_player_id(self):
                return self.player_id

            def get_player_entity(self):
                if self.get_server() is not None:
                    return self.get_server().get_player_by_id(self.get_player_id())
                return None

            def get_view_pos(self):
                player = self.get_player_entity()
                if player is not None:
                    return player.get_pos()
                return ThreeDimensionalPosition.get_origin()

            def get_fov_x(self):
                return self.get_parent().get_parent().get_fov_x()

            def get_fov_y(self):
                return self.get_parent().get_parent().get_fov_y()

            def get_fov_z(self):
                return self.get_parent().get_parent().get_fov_z()

            def get_dots_per_meter(self):
                return max(int(((self.get_width()/self.get_fov_x())+(self.get_height()/self.get_fov_z()))/2), 1)

            def get_current_space(self):
                player = self.get_player_entity()
                if player is not None:
                    return player.get_current_space()
                return None

            def connect_with_server(self):
                if self.get_server() is not None:
                    self.get_server().add_player(self.get_player_id())

            def tick_content(self):
                current_space = self.get_current_space()
                if current_space is not None:
                    fx, fy, fz = self.get_fov_x()/2, self.get_fov_y(), self.get_fov_z()/2
                    view_pos = self.get_view_pos()
                    vx, vy, vz = view_pos.get_x(), view_pos.get_y(), view_pos.get_z()
                    if vy == 0:
                        vy1 = 1
                    elif vy == 0:
                        vy1 = 2
                    else:
                        vy1 = vy
                    frame_model = ThreeDimensionalShape()
                    for obj in current_space.get_objects_in_shape(shape=ThreeDimensionalShape.ThreeDimensionalBox(faces=[ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[
                            ThreeDimensionalPosition(vx + fx, vy, vz + fz),
                            ThreeDimensionalPosition(vx + fx, vy, vz - fz),
                            ThreeDimensionalPosition((vx + fx)*fy, vy + fy, (vz + fz)*fy),
                            ThreeDimensionalPosition((vx + fx)*fy, vy + fy, (vz - fz)*fy),
                            ThreeDimensionalPosition(vx - fx, vy, vz + fz),
                            ThreeDimensionalPosition(vx - fx, vy, vz - fz),
                            ThreeDimensionalPosition((vx - fx)*fy, vy + fy, (vz + fz)*fy),
                            ThreeDimensionalPosition((vx - fx)*fy, vy + fy, (vz - fz)*fy),
                                        ])])):
                        if isinstance(obj, SpaceGameObject):
                            obj_model = obj.get_model()
                            if obj_model is not None and isinstance(obj_model, ThreeDimensionalShape):
                                obj_pos = obj.get_pos()
                                frame_model.merge(obj_model, fx+obj_pos.get_x()-vx, obj_pos.get_y()-vy1, fz+obj_pos.get_z()-vz)
                    frame_model.remove_empty()
                    self.draw_model(frame_model, dots_per_meter=self.get_dots_per_meter())

            def on_removed(self):
                if self.get_server() is not None:
                    self.get_server().on_removed()
                super().on_removed()

        class SaoirseClientHomeScreen(ScreenWidget):
            def __init__(self, parent):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.home.get_identifier(), parent=parent, width=parent.get_width(), height=parent.get_height(), left=0, top=0, title="Saoirse")

        class SaoirseClientMainScreen(ScreenWidget):
            def __init__(self, parent=None, left=0, top=0, width=1200, height=800, title=""):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main.get_identifier(), parent=parent, left=left, top=top, width=width, height=height, title=title)

            def draw_content(self):
                self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientWorldScreen(self, self.get_parent().get_username()))
                # self.add_child(SaoirseClientWidgets.ClientWidgets.Buttons.SaoirseClientSingleplayerButton(self))

            def tick_content(self):
                self.set_width(self.get_parent().get_width())
                self.set_height(self.get_parent().get_height())


class SaoirseClientMainWindowScreen(ScreenWidget):
    class ConfigKeys:
        key_config = "config"
        key_username = "username"
        key_max_framerate = "max_framerate"
        key_resolution = "resolution"
        key_fov = "fov"
        key_x = "x"
        key_y = "y"
        key_z = "z"

    def __init__(self, data_dir="", username=None, width=1920, height=1080, title="Saoirse", render_method="headless"):
        self.render_method = render_method

        super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main_window.get_identifier(), parent=None, title=title, left=0, top=0, width=width, height=height)

        self.set_data_dir(data_dir)
        self.config_file = path.join(self.get_data_dir(), "client_config.json")
        self.read_config_from_file()

        if username is not None:
            self.set_username(username)
        if not hasattr(self, "username"):
            self.set_username("Player1")
        if not hasattr(self, "max_framerate"):
            self.set_max_framerate()
        if not hasattr(self, "current_framerate"):
            self.set_current_framerate(0)
        if not hasattr(self, "fov_x"):
            self.set_fov_x(3)
        if not hasattr(self, "fov_y"):
            self.set_fov_y(500)
        if not hasattr(self, "fov_z"):
            self.set_fov_z(1)

        self.draw()

    def get_render_method(self):
        return self.render_method

    def set_fov_x(self, fov):
        self.fov_x = fov

    def set_fov_y(self, fov):
        self.fov_y = fov

    def set_fov_z(self, fov):
        self.fov_z = fov

    def get_fov_x(self):
        return self.fov_x

    def get_fov_y(self):
        return self.fov_y

    def get_fov_z(self):
        return self.fov_z

    def set_max_framerate(self, framerate=1000):
        self.max_framerate = framerate

    def get_max_framerate(self):
        return self.max_framerate

    def set_current_framerate(self, framerate):
        self.current_framerate = framerate

    def get_current_framerate(self):
        return self.current_framerate

    def set_data_dir(self, data_dir):
        self.data_dir = data_dir

    def get_data_dir(self):
        return self.data_dir

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def get_config_dir(self):
        return path.dirname(self.get_config_file())

    def save_config_to_file(self):
        try:
            data = jdumps(self.get_data(), indent=2) # Get data first to avoid writing a broken config to the config file
        except Exception as e:
            logger.warning(f"Failed to write config to file, it will not be saved (the old config will still remain intact): {e}")
            data = None
        if data is not None:
            try:
                if not path.isdir(self.get_config_dir()):
                    makedirs(self.get_config_dir())
                with open(self.get_config_file(), "w") as f:
                    f.write(data)
            except Exception as e:
                logger.warning(f"Failed to write config to file, the old file may have been modified with broken data (see the followin error for more info): {e}")

    def read_config_from_file(self):
        self.initial_config = None
        if path.isfile(self.get_config_file()):
            try:
                with open(self.get_config_file(), "r") as f:
                    data = jloads(f.read()) # Get data first to avoid reading a broken config from the config file
            except Exception as e:
                logger.warning(f"Failed to load config from file, the default will be used: {e}")
                data = None
            if data is not None:
                self.set_data(data)
                self.initial_config = data

    def set_data(self, data):
        super().set_data(data)
        if self.ConfigKeys.key_config in data.keys():
            config = data.get(self.ConfigKeys.key_config)
            if self.ConfigKeys.key_username in config.keys():
                self.set_username(config.get(self.ConfigKeys.key_username))
            if self.ConfigKeys.key_max_framerate in config.keys():
                self.set_max_framerate(config.get(self.ConfigKeys.key_max_framerate))
            if self.ConfigKeys.key_resolution in config.keys():
                resolution = config.get(self.ConfigKeys.key_resolution)
                if self.ConfigKeys.key_x in resolution.keys():
                    self.set_width(resolution.get(self.ConfigKeys.key_x))
                if self.ConfigKeys.key_y in resolution.keys():
                    self.set_height(resolution.get(self.ConfigKeys.key_y))
            if self.ConfigKeys.key_fov in config.keys():
                fov = config.get(self.ConfigKeys.key_fov)
                if self.ConfigKeys.key_x in fov.keys():
                    self.set_fov_x(fov.get(self.ConfigKeys.key_x))
                if self.ConfigKeys.key_y in fov.keys():
                    self.set_fov_y(fov.get(self.ConfigKeys.key_y))
                if self.ConfigKeys.key_z in fov.keys():
                    self.set_fov_z(fov.get(self.ConfigKeys.key_z))

    def get_data(self):
        data = super().get_data()
        config = {
            self.ConfigKeys.key_username: self.get_username(),
            self.ConfigKeys.key_max_framerate: self.get_max_framerate(),
            self.ConfigKeys.key_resolution: {
                self.ConfigKeys.key_x: self.get_width(),
                self.ConfigKeys.key_y: self.get_height(),
            },
            self.ConfigKeys.key_fov: {
                self.ConfigKeys.key_x: self.get_fov_x(),
                self.ConfigKeys.key_y: self.get_fov_y(),
                self.ConfigKeys.key_z: self.get_fov_z(),
            },
        }
        data[self.ConfigKeys.key_config] = config
        return data

    def set_username(self, username="Player1"):
        self.username = username

    def get_username(self):
        return self.username

    def set_server(self, server):
        pass

    def get_server(self):
        return None

    def draw_content(self):
        self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientMainScreen(self))

    def tick_content(self):
        fps = f"FPS: {self.get_current_framerate()}"
        self.draw_text(text=fps, left=5, top=5, right=len(fps)*9, bottom=25)

    def on_removed(self):
        self.save_config_to_file()
        super().on_removed()

class SaoirseClientMainWindowScreenPyglet(SaoirseClientMainWindowScreen):
    def __init__(self, headless=False, data_dir="", username=None, width=960, height=540, title="Saoirse"):
        super().__init__(data_dir=data_dir, username=username, width=width, height=height, title=title, render_method="pyglet")

        pyglet.options["headless"] = headless

        self.render_que = []

        self.window = pyglet.window.Window(resizable=True, caption=self.get_title())
        self.window.projection = pyglet.window.Mat4.perspective_projection(0, self.get_width(), 0, self.get_height(), z_near=0.1, z_far=self.get_fov_y())
        pyglet.graphics.glClearColor(100/255, 100/255, 100/255, 1)

        pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)
        pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)

        self.batch_2d = pyglet.graphics.Batch()
        self.batch_3d = pyglet.graphics.Batch()
        self.shader = pyglet.model.get_default_shader()

        @self.window.event
        def on_resize(width, height):
            if width > 0:
                self.set_width(width)
            if height > 0:
                self.set_height(height)
            self.window.projection = pyglet.window.Mat4.perspective_projection(0, self.get_width(), 0, self.get_height(), z_near=0.1, z_far=self.get_fov_y())

        @self.window.event
        def on_draw():
            self.tick()

    def draw_image(self, img, left=0, top=0, right=None, bottom=None, shade_red=None, shade_green=None, shade_blue=None, shade_alpha=None):
        if isinstance(img, Identifier):
            img = pyglet.resource.image(img.get_file_path())
        img = pyglet.sprite.Sprite(img, x=left, y=self.get_height()-top, batch=self.batch_2d)
        scale_x = None
        if right is not None:
            width = right - left
            if img.width != width:
                scale_x = width/img.width
        scale_z = None
        if bottom is not None:
            height = bottom - top
            if img.height != height:
                scale_z = height/img.height
        if scale_x is not None or scale_z is not None:
            img.update(scale_x=scale_x, scale_y=scale_z)
        r, g, b = img.color
        if shade_red is not None:
            r = shade_red
        if shade_green is not None:
            g = shade_green
        if shade_blue is not None:
            b = shade_blue
        img.color = (r, g, b)
        if shade_alpha is not None:
            img.opacity
        self.render_que.append(img)

    def draw_model(self, model, x=0, y=0, z=0, dots_per_meter=1):
        if isinstance(model, ThreeDimensionalShape):
            if y == 0:
                y = 1
            elif y == 1:
                y = 2
            vertex_lists = []
            groups = []
            for face in model.get_faces():
                vertices = []
                for corner in face.get_corners():
                    vertices.extend([dots_per_meter*corner.get_x(), dots_per_meter*corner.get_z(), dots_per_meter*corner.get_y()])
                count = int(len(vertices)/3)
                if count > 0:
                    texture = face.get_texture()
                    if isinstance(texture, Identifier):
                        texture_name = texture.get_file_path()
                        texture = pyglet.resource.image(texture_name)
                    else:
                        texture_name = str(texture)
                    diffuse = [0.5, 0.0, 0.3, 1.0]
                    ambient = [0.5, 0.0, 0.3, 1.0]
                    specular = [1.0, 1.0, 1.0, 1.0]
                    emission = [0.0, 0.0, 0.0, 1.0]
                    shininess = 50
                    material = pyglet.model.Material(texture_name, diffuse, ambient, specular, emission, shininess, texture_name)
                    group = pyglet.model.TexturedMaterialGroup(material, self.shader, texture)
                    groups.append(group)
                    vertex_lists.append(self.shader.vertex_list(count=count, mode=pyglet.gl.GL_TRIANGLES, batch=self.batch_3d, group=group, vertices=("f", vertices)))
            if len(vertex_lists) > 0:
                model = pyglet.model.Model(vertex_lists=vertex_lists, groups=list(groups), batch=self.batch_3d)
                model.translation = dots_per_meter*x, self.get_height()-(dots_per_meter*z), dots_per_meter*y
                self.render_que.append(model)
        else:
            logger.warning(f"Unable to draw {model} as a model as it is not a a ThreeDimensionalShape!")

    def draw_text(self, text, font_size=11, left=0, top=0, right=None, bottom=None, font_name=default_font, color_red=150, color_green=150, color_blue=100, color_alpha=255):
        self.render_que.append(pyglet.text.Label(
                          text=text,
                          font_name=font_name,
                          font_size=font_size,
                          x=left, y=self.get_height()-top,
                          color=(color_red, color_green, color_blue, color_alpha),
                          anchor_x='left', anchor_y='top', batch=self.batch_2d))

    def play_sound(self, ide):
        pyglet.resource.media(ide.get_file_path()).play()

    def tick(self, *args, **kwargs):
        do_frame = True
        current_time = gettime()
        if hasattr(self, "last_time"):
            if current_time - self.last_time < 1/self.get_max_framerate():
                do_frame = False
        if do_frame:
            self.window.clear()
            super().tick()
            self.batch_3d.draw()
            self.batch_2d.draw()
            for obj in self.render_que:
                if hasattr(obj, "delete"):
                    obj.delete()
            self.render_que.clear()
            if hasattr(self, "last_time"):
                self.set_current_framerate(int(1/(current_time - self.last_time)))
            self.last_time = current_time


class SaoirseClientMainWindowScreenPIL(SaoirseClientMainWindowScreen):
    def create_frame_img(self, img_args={}):
        if hasattr(self, "frame_img"):
            self.frame_img.close()
        self.frame_img = Image.new(mode="RGBA", size=(self.get_width(), self.get_height()), color=(100, 100, 100, 255), **img_args)

    def get_frame_img(self):
        return self.frame_img

    def get_next_frame(self):
        self.create_frame_img()
        self.tick()
        return self.frame_img

    def draw_image(self, img, left=0, top=0, right=None, bottom=None, shade_red=None, shade_green=None, shade_blue=None, shade_alpha=None):
        if isinstance(img, Identifier):
            img = Image.open(img.get_file_path())
        needs_resize = False
        if right is not None:
            width = right-left
            if img.width != width:
                needs_resize = True
        else:
            width = img.width
        if bottom is not None:
            height = bottom-top
            if img.height != height:
                needs_resize = True
        else:
            height = img.height
        if needs_resize:
            img = img.resize((width, height))
        if shade_red is not None:
            r = shade_red
        else:
            r = 0
        if shade_green is not None:
            g = shade_green
        else:
            g = 0
        if shade_blue is not None:
            b = shade_blue
        else:
            b = 0
        rgb_sum = r + g + b
        if rgb_sum > 0:
            shade_img = Image.new(mode="RGBA", size=img.size, color=(r, g, b))
            img = Image.blend(img, shade_img, alpha=int(255/(rgb_sum/3)))
        if shade_alpha is not None:
            img.putalpha(shade_alpha)
        self.frame_img.paste(im=img, box=(left, top), mask=img)

    def draw_model(self, model, x=0, y=0, z=0, dots_per_meter=1):
        if isinstance(model, ThreeDimensionalShape):
            masks = {}
            if y == 0:
                 y = 1
            elif y == 1:
                y = 2
            if y > 0:
                for face in model.get_faces():
                    xz = []
                    greatest_x = 1
                    greatest_z = 1
                    least_y = 0
                    for corner in face.get_corners():
                        vy = corner.get_y()*y
                        if vy == 0:
                            vy = 1
                        elif vy == 1:
                            vy = 2
                        if vy > 0:
                            vx = int(dots_per_meter*(corner.get_x()/vy))
                            vz = int(dots_per_meter*(corner.get_z()/vy))
                            xz.append((vx, vz))
                            if vx > greatest_x:
                                greatest_x = vx
                            if vz > greatest_z:
                                greatest_z = vz
                            if vy < least_y or least_y == 0:
                                least_y = vy
                    if len(xz) >= 2:
                        mask = Image.new(mode="RGBA", size=(greatest_x, greatest_z), color=(0, 0, 0, 0))
                        ImageDraw.Draw(im=mask, mode="RGBA").polygon(xy=xz, fill=(255, 255, 255, 100), outline=(0, 0, 0, 255))
                        texture = face.get_texture()
                        if isinstance(texture, Identifier):
                            texture = Image.open(texture.get_file_path())
                        mask.paste(im=texture.resize(mask.size), mask=mask)
                        texture.close()
                        masks_y = masks.get(least_y, [])
                        masks_y.append(mask)
                        masks[least_y] = masks_y
                yvals = list(masks.keys())
                yvals.sort()
                for yval in yvals:
                    for mask in masks.get(yval, []):
                        self.draw_image(mask, dots_per_meter*x, dots_per_meter*z)
                        mask.close()
        else:
            logger.warning(f"Unable to draw {model} as a model as it is not a ThreeDimensionalShape!")

    def draw_text(self, text, font_size=11, left=0, top=0, right=20, bottom=20, font_name=default_font, color_red=150, color_green=150, color_blue=100, color_alpha=255):
        if font_name is None:
            font = None
        else:
            try:
                font=ImageFont.load_path(font_name)
            except Exception as e:
                if not hasattr(self, "has_warned_missing_font"):
                    logger.warning(f"Using plain font: Failed to draw text using font {font_name} with exception: {e}")
                    self.has_warned_missing_font = True
                font=None
        img = Image.new(mode="RGBA", size=((int(right-left), int(bottom-top))), color=(0, 0, 0, 0))
        ImageDraw.Draw(im=img).multiline_text(xy=(0, 0), text=text, font=font, stroke_width=font_size, fill=(color_red, color_green, color_blue, color_alpha))
        self.draw_image(img, int(left), int(top))

    def play_sound(self, sound):
        # TODO: Make this actually play the sound
        if isinstance(sound, Identifier):
            sound = sound.get_file_path()


class SaoirseClientMainWidowScreenTk(Tk):
    def __init__(self, client, save_frame_list=False):
        super().__init__(className=client.get_title())
        self.save_frame_list = save_frame_list
        if self.save_frame_list:
            self.frame_list = []
        self.client = client
        self.wm_resizable(True, True)
        self.frame_label = TkLabel(self)
        self.frame_label.pack(expand=True, fill=TkBOTH)

    def get_frame_list(self):
        if hasattr(self, "frame_list"):
            return self.frame_list
        return None

    def destroy(self):
        self.client.on_removed()
        super().destroy()

    def update_frame(self):
        do_frame = True
        current_time = gettime()
        if hasattr(self, "last_time"):
            if current_time - self.last_time < 1/self.client.get_max_framerate():
                do_frame = False
        if do_frame:
            self.next_frame()
            self.frame_label.config(image=self.frame)
            if hasattr(self, "last_time"):
                self.client.set_current_framerate(int(1/(current_time - self.last_time)))
            self.last_time = current_time

    def next_frame(self):
        self.client.set_width(self.winfo_width())
        self.client.set_height(self.winfo_height())
        img = self.client.get_next_frame()
        self.frame = ImageTk.PhotoImage(img)
        if self.save_frame_list:
            self.frame_list.append(img.copy())
        img.close()


def main(args=[],
         headless = False,
         return_frame_list = False,
         use_tk = False,
         data_dir = "SaoirseClient.d",
         username = None,
):
    help_msg = """
    Client program for the game Saoirse

    Usage (depends on which executable form is being run):

    For binary releases:

    saoirse_client OPTIONS
    saoirse_client.exe OPTIONS

    For Python source files:

    pypy3 saoirse_client.py OPTIONS
    python3 saoirse_client.py OPTIONS

    Valid OPTIONS:

    --headless                                          Create a client object that ticks and generates frames images without opening a window
    --return-frame-list                                 Makes the main() function save a list of all frames generated as the program runs and return it upon exiting
    -t, --tk                                            Makes the client window use Pillow and Tk instead of pyglet. Not recommended for performance
    --data-dir=DATADIR                                  Sets the directory for saving client-side settings and resources to DATADIR. Uses the current directory if not specified
    --username=USERNAME                                 Sets the client object\'s username to USERNAME. Overrides the name specified in the config.json file under DATADIR. Defaults to \'Player1\' if not specified in either place
    --version, -v                                       Print the version of the game client file being run, along with that of the server and the base library
    --help, -h                                          Print this help message and exit
    """

    version_msg = f"""
    Saoirse Library Version: {saoirse_base_version}
    Saoirse Server Version: {saoirse_server_version}
    Saoirse *Client* Version: {saoirse_client_version}
    """

    arg_key_help = ("--help", "-h")
    arg_key_version = ("--version", "-v")
    arg_key_headless = "--headless"
    arg_key_return_frame_list = "--return-frame-list"
    arg_key_use_tk = "--tk"
    arg_key_data_dir = "--data-dir="
    arg_key_username = "--username="

    if len(args) > 1:
        for arg in args[1:]:
            if arg.startswith(arg_key_help):
                logger.info(help_msg)
                print(help_msg)
                return
            elif arg.startswith(arg_key_version):
                logger.info(version_msg)
                print(version_msg)
                return
            elif arg.startswith(arg_key_headless):
                headless = True
            elif arg.startswith(arg_key_return_frame_list):
                return_frame_list = True
            elif arg.startswith(arg_key_use_tk):
                use_tk = True
            elif arg.startswith(arg_key_data_dir):
                data_dir = expand_full_path(arg.replace(arg_key_data_dir, ""))
            elif arg.startswith(arg_key_username):
                username = arg.replace(arg_key_username, "")

    splash_txts = [
        "No, this is\'t *that* kind of \"do whatever you want\" game!",
        "Want some pi? M, Greek pi!",
        "So then I said \"something about an onion router\"...",
        "So then I said \"something about a programming language not suitable for game development\"...",
        "Did you buy this game? You know you can compile it from source for free, right? Oh, you wanted to support the devloper? Well thanks!",
    ]
    if username is not None:
        splash_txts.append(f"If you aren\'t {username}, stop impersonating people!")
    window_title = f"Saoirse v{saoirse_client_version}:   {randchoice(splash_txts)}"

    if use_tk or headless:
        if headless:
            render_method="headless"
        else:
            render_method="tk"
        client = SaoirseClientMainWindowScreenPIL(data_dir=data_dir, username=username, title=window_title, render_method=render_method)
    else:
        client = SaoirseClientMainWindowScreenPyglet(data_dir=data_dir, headless=headless, username=username, title=window_title)
    if not headless:
        if use_tk:
            root = SaoirseClientMainWidowScreenTk(client, return_frame_list)
            while not client.removed:
                root.update_frame()
                root.update_idletasks()
                root.update()
                if return_frame_list:
                    return root.get_frame_list()
        else:
            pyglet.app.run()
            client.on_removed()
    else:
        if return_frame_list:
            frame_list = []
        while not client.removed:
            if return_frame_list:
                frame_list.append(client.get_next_frame())
            else:
                client.get_next_frame()
        if return_frame_list:
            return frame_list


if __name__ == "__main__":
    main(args=argv)
