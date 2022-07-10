# This file is:
# src/main/python/saoirse_client.py


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


import pyglet, pyray, gc
from typing import Union
from dataclasses import dataclass
from sys import argv
from os import path, makedirs
from random import choice as randchoice
from threading import Thread
from PIL import ImageTk, Image, ImageDraw, ImageFont
from tkinter import Tk, Label as TkLabel, BOTH as TkBOTH
from time import time as gettime, sleep as timesleep
from json import dumps as jdumps, loads as jloads
from saoirse_lib import saoirse_lib_version, saoirse_images_path, ThreeDimensionalPosition, logger, expand_full_path, Identifier, MainGameObject, InteractableObject, SpaceGameObject, ThreeDimensionalShape
from saoirse_server import saoirse_server_version, SaoirseServer, SaoirseIdentifierEnum


saoirse_client_version = "0.0.1"


default_font = "Exo 2 Regular"
#default_font = None


saoirse_missing_img_path = saoirse_images_path.append("missing")


class BaseWidgets:
    class BaseWidget(MainGameObject, InteractableObject):
        def __init__(self, ide: Identifier, parent=None, left: Union[int, float]=0, top: Union[int, float]=20, right: Union[int, float]=20, bottom: Union[int, float]=20):
            self.set_parent(parent)

            super().__init__(ide, None)

            self.children = {}
            self.set_left(left)
            self.set_top(top)
            self.set_right(right)
            self.set_bottom(bottom)

        def set_parent(self, parent):
            self.parent = parent

        def get_parent(self):
            return self.parent

        def get_children(self):
            return self.children

        def add_child(self, child):
            child.set_parent(self)
            self.children[child.get_id().get_path_str()] = child

        def set_right(self, width: Union[int, float]):
            self.right = width

        def set_bottom(self, bottom: Union[int, float]):
            self.bottom = bottom

        def get_right(self) -> Union[int, float]:
            return self.right

        def get_bottom(self) -> Union[int, float]:
            return self.bottom

        def set_left(self, left: Union[int, float]):
            self.left = left

        def set_top(self, top: Union[int, float]):
            self.top = top

        def get_left(self) -> Union[int, float]:
            return self.left

        def get_top(self) -> Union[int, float]:
            return self.top

        def get_width(self) -> Union[int, float]:
            return self.get_right() - self.get_left()

        def get_height(self) -> Union[int, float]:
            return self.get_top() - self.get_bottom()

        def draw_image(self, img, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, shade_red: Union[int, float, None]=None, shade_green: Union[int, float, None]=None, shade_blue: Union[int, float, None]=None, shade_alpha: Union[int, float, None]=None, layer: Union[int, float]=0):
            self.get_parent().draw_image(img, self.get_left() + left, self.get_bottom() + top, self.get_right() + right, self.get_bottom() + bottom, shade_red=shade_red, shade_green=shade_green, shade_blue=shade_blue, shade_alpha=shade_alpha, layer=layer)

        def draw_model(self, model: ThreeDimensionalShape, x: Union[int, float]=0, y: Union[int, float]=0, z: Union[int, float]=0, dots_per_meter: int=1, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin(), layer: Union[int, float]=0, reuse: Union[Identifier, None]=None):
            self.get_parent().draw_model(model, self.get_left() + x, y, self.get_bottom() + z, dots_per_meter, cam_pos, layer, reuse)

        def draw_text(self, text: Union[str, Identifier], font_size: int=11, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[float, int, None]=None, bottom: Union[float, int, None]=None, font_name: str=default_font, color_red: int=150, color_green: int=150, color_blue: int=100, color_alpha: int=255):
            self.get_parent().draw_text(text=text, font_size=font_size, left=self.get_left() + left, top=self.get_bottom() + top, right=right, bottom=self.get_bottom() + bottom, font_name=font_name, color_red=color_red, color_green=color_green, color_blue=color_blue, color_alpha=color_alpha)

        def play_sound(self, ide: Identifier):
            self.get_parent().play_sound(ide)

        def set_server(self, server: SaoirseServer):
            if self.get_parent() is not None:
                self.get_parent().set_server(server)

        def get_server(self) -> Union[SaoirseServer, None]:
            if self.get_parent() is not None:
                return self.get_parent().get_server()
            return None

        def on_removed(self):
            for child in self.get_children().values():
                if isinstance(child, BaseWidgets.BaseWidget):
                    child.on_removed()
            super().on_removed()

        def draw_content(self):
            pass

        def draw(self):
            self.draw_content()
            for child in self.get_children().values():
                if isinstance(child, BaseWidgets.BaseWidget):
                    child.draw()

        def tick(self, *args, **kwargs):
            super().tick()
            for child in self.get_children().values():
                if isinstance(child, BaseWidgets.BaseWidget):
                    child.tick()
            self.tick_content()

        def tick_content(self):
            pass

    class ImageWidget(BaseWidget):
        def __init__(self, ide: Identifier, parent=None, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0,  img: Union[str, Identifier]="", shade_red: Union[int, None]=None, shade_green: Union[int, None]=None, shade_blue: Union[int, None]=None, shade_alpha: Union[int, None]=None, layer: Union[int, float]=0):
            super().__init__(ide, parent=parent, left=left, top=top, right=right, bottom=bottom)

            self.img = img
            self.shade_red=shade_red
            self.shade_green=shade_green
            self.shade_blue=shade_blue
            self.shade_alpha=shade_alpha
            self.layer = layer

        def tick_content(self):
            self.draw_image(self.img, self.get_left(), self.get_top(), self.get_right(), self.get_bottom(), self.shade_red, self.shade_green, self.shade_blue, self.shade_alpha, self.layer)

    class TextWidget(BaseWidget):
        def __init__(self, ide: Identifier, parent=None, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, text: Union[str, Identifier]="", font_name: str=default_font, color_red: int=150, color_green: int=150, color_blue: int=100, color_alpha: int=255):
            super().__init__(ide, parent=parent, left=left, top=top, right=right, bottom=bottom)

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

        def set_color_red(self, color: int=255):
            self.color_red = color

        def get_color_red(self) -> int:
            return self.color_red

        def set_color_green(self, color: int=255):
            self.color_green = color

        def get_color_green(self) -> int:
            return self.color_green

        def set_color_blue(self, color: int=255):
            self.color_blue = color

        def get_color_blue(self) -> int:
            return self.color_blue

        def set_color_alpha(self, color: int=255):
            self.color_alpha = color

        def get_color_alpha(self) -> int:
            return self.color_alpha

        def tick_content(self):
            self.draw_text(self.get_text(), left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), font_size=int(self.get_font_size()), font_name=self.get_font_name(), color_red=self.get_color_red(), color_green=self.get_color_green(), color_blue=self.get_color_blue(), color_alpha=self.get_color_alpha())


    class ButtonWidget(BaseWidget):
        def __init__(self, ide: Identifier, parent=None, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, label: Union[str, Identifier]="", img: Union[str, Identifier]=saoirse_missing_img_path):
            super().__init__(ide, parent=parent, left=left, top=top, right=right, bottom=bottom)

            self.label = label
            self.img = img

        def draw_content(self):
            if self.get_label() is not None:
                self.add_child(BaseWidgets.TextWidget(Identifier("label"), left=self.get_left() * 0.75, top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), text=self.get_label()))
            if self.get_img() is not None:
                self.add_child(BaseWidgets.ImageWidget(Identifier("img"), left=self.get_left() * 0.75, top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), img=self.get_img()))

        def get_label(self) -> Union[str, Identifier]:
            return self.label

        def get_img(self) -> Union[str, Identifier]:
            return self.img


class ScreenWidget(BaseWidgets.BaseWidget):
    def __init__(self, ide: Identifier, parent=None, left: Union[int, float]=0, top: Union[int, float]=1080, right: Union[int, float]=1920, bottom: Union[int, float]=0, title: Union[str, Identifier, None]=""):
        super().__init__(ide, parent=parent, left=left, top=top, right=right, bottom=bottom)

        self.title = title

    def get_title(self) -> Union[str, Identifier, None]:
        return self.title


class SaoirseClientBaseRenderer(ScreenWidget):
    def __init__(self, headless: bool=False, parent=None, left: Union[int, float]=0, top: Union[int, float]=1080, right: Union[int, float]=1920, bottom: Union[int, float]=0, fov_x: Union[int, float]=5, fov_y: Union[int, float]=5000, fov_z: Union[int, float]=3, title: Union[str, Identifier, None]="Saoirse", render_method: str="dummy", save_frame_list: bool=False):
        super().__init__(ide=Identifier(["renderer", render_method]), parent=parent, left=left, top=top, right=right, bottom=bottom, title=title)
        self.set_fov_x(fov_x)
        self.set_fov_y(fov_y)
        self.set_fov_z(fov_z)

        self.set_headless(headless)
        self.save_frame_list = save_frame_list
        if self.save_frame_list:
            self.frame_list = []

    def get_frame_list(self) -> Union[list, None]:
        if hasattr(self, "frame_list"):
            return self.frame_list
        return None

    def set_headless(self, headless: bool=False):
        self.headless = headless

    def get_headless(self) -> bool:
        return self.headless

    def set_fov_x(self, fov: Union[int, float]):
        self.fov_x = fov

    def set_fov_y(self, fov: Union[int, float]):
        self.fov_y = fov

    def set_fov_z(self, fov: Union[int, float]):
        self.fov_z = fov

    def get_fov_x(self) -> Union[int, float]:
        return self.fov_x

    def get_fov_y(self) -> Union[int, float]:
        return self.fov_y

    def get_fov_z(self) -> Union[int, float]:
        return self.fov_z

    def get_dots_per_meter(self) -> int:
        return max(int(self.get_width()/self.get_fov_x()), 1)

    def pre_tick(self):
        pass

    def tick(self):
        super().tick()

    def post_tick(self):
        pass

    def on_removed(self):
        parent = self.get_parent()
        if parent is not None:
            self.get_parent().on_removed()
        super().on_removed()


class SaoirseClientWidgets:
    class ClientWidgets:
        class Buttons:
            class ButtonIdentifiers(SaoirseIdentifierEnum):
                def get_base_ide(self):
                    return Identifier(["widgets", "buttons"]).extend(super().get_base_ide())

                singleplayer = "singleplayer"

            class SaoirseClientSingleplayerButton(BaseWidgets.ButtonWidget):
                def __init__(self, parent=None, left: Union[int, float]=50, top: Union[int, float]=50, right: Union[int, float]=70, bottom: Union[int, float]=40):
                    super().__init__(SaoirseClientWidgets.ClientWidgets.Buttons.ButtonIdentifiers.singleplayer.get_identifier(), parent=parent, left=left, top=top, right=right, bottom=bottom, label="Singleplayer")

                def tick_content(self):
                    self.draw_image(saoirse_images_path.append("pic1.png"), left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), layer=1)

    class ClientScreens:
        class ScreenIdentifiers(SaoirseIdentifierEnum):
            def get_base_ide(self) -> Identifier:
                return Identifier(["screens"]).extend(super().get_base_ide())

            main_window = "main_window"
            main = "main"
            home = "home"
            world = "world"

        class SaoirseClientWorldScreen(ScreenWidget):
            def __init__(self, parent=None, ide: Identifier=Identifier("main"), player_id: Union[str, Identifier]="Player1", server: Union[SaoirseServer, None]=None):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.world.get_identifier().append(ide.get_path(), update_self=False), parent=parent, title=server.get_id().get_path_str() if server is not None else "")

                self.server_is_local = server is None
                if self.server_is_local:
                    # pass
                    self.create_local_server()
                else:
                    self.set_server(server)
                self.set_player_id(player_id)
                self.connect_with_server()

            def set_server(self, server: Union[SaoirseServer, None]):
                self.server = server

            def server_loop(self):
                def _server_loop():
                    while self.server is not None and not self.server.removed:
                        self.server.tick()
                Thread(target=_server_loop, daemon=True).start()

            def create_local_server(self, save_dir: Union[str, Identifier, None]=None, save_name: Union[str, Identifier, None]=None):
                if save_name is None:
                    save_name = "world1"
                elif isinstance(save_name, Identifier):
                    save_name = save_name.get_file_path()
                if save_dir is None:
                    save_dir = path.join(self.get_parent().get_parent().get_data_dir(), "saves", save_name)
                elif isinstance(save_dir, Identifier):
                    save_dir = save_dir.get_file_path()
                self.server = SaoirseServer(save_file=path.join(str(save_dir), "server.pkl"))
                self.server_loop()

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
                return max(int(((self.get_width()/self.get_fov_x()) + (self.get_height()/self.get_fov_z()))/2), 1)

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
                    for obj in current_space.get_objects_in_shape(shape=ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[
                            ThreeDimensionalPosition(vx - fx, vy, vz + fz), # lft
                            ThreeDimensionalPosition(vx + fx, vy, vz + fz), # rft
                            ThreeDimensionalPosition(vx + fx, vy, vz - fz), # rfb
                            ThreeDimensionalPosition(vx - fx, vy, vz - fz), # lfb
                            ThreeDimensionalPosition((vx - fx)*fy, vy + fy, (vz + fz)*fy), # lbt
                            ThreeDimensionalPosition((vx + fx)*fy, vy + fy, (vz + fz)*fy), # rbt
                            ThreeDimensionalPosition((vx + fx)*fy, vy + fy, (vz - fz)*fy), # rbb
                            ThreeDimensionalPosition((vx - fx)*fy, vy + fy, (vz - fz)*fy), # lbb
                            ]
                    )):
                        if isinstance(obj, SpaceGameObject):
                            obj_model = obj.get_model()
                            if obj_model is not None and isinstance(obj_model, ThreeDimensionalShape):
                                obj_pos = obj.get_pos()
                                frame_model.merge(obj_model.copy(), fx+obj_pos.get_x()-vx, obj_pos.get_y()-vy1, fz+obj_pos.get_z()-vz)
                    frame_model.remove_empty()
                    dots_per_meter=self.get_dots_per_meter()
                    self.draw_model(frame_model, dots_per_meter=dots_per_meter, cam_pos=ThreeDimensionalPosition(fx, 0, fz), layer=999999, reuse=self.get_id())

            def on_removed(self):
                if self.get_server() is not None:
                    self.get_server().on_removed()
                super().on_removed()

        class SaoirseClientHomeScreen(ScreenWidget):
            def __init__(self, parent):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.home.get_identifier(), parent=parent, left=parent.get_left(), top=parent.get_top(), right=parent.get_right(), bottom=parent.get_bottom(), title="Saoirse")

        class SaoirseClientMainScreen(ScreenWidget):
            def __init__(self, parent=None, ide=Identifier("main"), left=0, top=1080, right=1920, bottom=0, title=""):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main.get_identifier().append(ide.get_path(), update_self=False), parent=parent, left=left, top=top, right=right, bottom=bottom, title=title)

            def draw_content(self):
                self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientWorldScreen(self, player_id=self.get_parent().get_username()))
                # self.add_child(SaoirseClientWidgets.ClientWidgets.Buttons.SaoirseClientSingleplayerButton(self))
                # pass

            def tick_content(self):
                self.set_right(self.get_parent().get_width())
                self.set_bottom(self.get_parent().get_height())
                ## TEST
                #frame_model = ThreeDimensionalShape()
                #test_shape_pillar = ThreeDimensionalShape(boxes=[
                #    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 1), ThreeDimensionalPosition(1, 0, 1), ThreeDimensionalPosition(1, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 0.25, 2), ThreeDimensionalPosition(1, 0.25, 2), ThreeDimensionalPosition(1, 0.25, 0), ThreeDimensionalPosition(0, 0.25, 0), texfront=saoirse_images_path.append("pic2.png"), tex_default=saoirse_images_path.append("pic3.png")),
                #    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0.25, 0, 3), ThreeDimensionalPosition(1, 0, 3), ThreeDimensionalPosition(1, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 0.25, 4), ThreeDimensionalPosition(1, 0.25, 4), ThreeDimensionalPosition(1, 0.25, 0), ThreeDimensionalPosition(0, 0.25, 0), texfront=saoirse_images_path.append("pic2.png"), texback=saoirse_images_path.append("pic3.png"), textop=saoirse_images_path.append("pic2.png"), texbottom=saoirse_images_path.append("pic4.png") ,texleft=saoirse_images_path.append("pic1.png"), texright=saoirse_images_path.append("pic4.png")).move(0.35, 0.12, -0.1),
                #    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0.25, 0, 8), ThreeDimensionalPosition(1, 0, 8), ThreeDimensionalPosition(1, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 0.25, 8), ThreeDimensionalPosition(1, 0.25, 8), ThreeDimensionalPosition(1, 0.25, 0), ThreeDimensionalPosition(0, 0.25, 0), texfront=saoirse_images_path.append("pic2.png"), texback=saoirse_images_path.append("pic3.png"), textop=saoirse_images_path.append("pic2.png"), texbottom=saoirse_images_path.append("pic4.png") ,texleft=saoirse_images_path.append("pic1.png"), texright=saoirse_images_path.append("pic4.png")).move(0.75, 0.12, -0.1),
                #    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 2), ThreeDimensionalPosition(1, 0, 2), ThreeDimensionalPosition(1, 0, -1), ThreeDimensionalPosition(0, 0, -1), ThreeDimensionalPosition(0, 0.25, 4), ThreeDimensionalPosition(1, 0.25, 4), ThreeDimensionalPosition(1, 0.25, 1), ThreeDimensionalPosition(0, 0.25, 1), texbottom=saoirse_images_path.append("pic4.png"), tex_default=saoirse_images_path.append("pic3.png")).move(0.5, 0, 4),
                #    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 1), ThreeDimensionalPosition(0.1, 0, 1), ThreeDimensionalPosition(0.1, 0, 0.2), ThreeDimensionalPosition(0, 0, 0.1), ThreeDimensionalPosition(0, 0.1, 1), ThreeDimensionalPosition(0.1, 0.1, 1), ThreeDimensionalPosition(0.1, 0.1, 0.1), ThreeDimensionalPosition(0, 0.1, 0.1), tex_default=saoirse_images_path.append("pic4.png")).move(0.5, -0.01, 3),
                #    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 2), ThreeDimensionalPosition(0.5, 0, 1), ThreeDimensionalPosition(1, 0.25, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 0.25, 2), ThreeDimensionalPosition(1, 0.25, 2), ThreeDimensionalPosition(1, 0.25, 0), ThreeDimensionalPosition(0, 0.25, 0), tex_default=saoirse_images_path.append("pic3.png")).move(1),
                #])
                #for i in range(1, 5):
                #    frame_model.merge(test_shape_pillar.copy(), (i*4)+4, (i/2)+3, 2)
                #    # frame_model.merge(strongest_shape.copy(), 4+(i/10), (i/10)+3, 9)
                #test_shape_sun = ThreeDimensionalShape(boxes=[
                #    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 8), ThreeDimensionalPosition(8, 0, 8), ThreeDimensionalPosition(8, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 0.25, 9), ThreeDimensionalPosition(8, 0.25, 9), ThreeDimensionalPosition(8, 0.25, 0), ThreeDimensionalPosition(0, 0.25, 0), texfront=saoirse_images_path.append("pic5.png"), tex_default=saoirse_images_path.append("pic3.png")),
                #])
                #frame_model.merge(test_shape_sun.copy(), 16, 4, 13)
                ## frame_model.merge(test_shape_pillar.copy(), 2, 4, 0)
                ##frame_model.merge(strongest_shape.copy(), randchoice([4, 7]), 3, 2)
                ##frame_model.merge(strongest_shape.copy(), 12, 3, randchoice([9, 12]))
                #self.draw_model(frame_model, dots_per_meter=210, cam_pos=ThreeDimensionalPosition(-5, 0, 2), layer=999991, reuse=self.get_id())
                ## self.draw_model(frame_model, dots_per_meter=210, cam_pos=ThreeDimensionalPosition(randchoice([0, 2, -10]), randchoice([2, 4, 6]), randchoice([0, 5, -5])), layer=999991, reuse=self.get_id())
                ## ENDTEST


class SaoirseClientMainWindowScreen(ScreenWidget):
    @dataclass(frozen=True)
    class RendererKeys:
        key_pyray = "pyray"
        key_pyglet = "pyglet"
        key_PIL = "PIL"
        key_tk = "tk"

    @dataclass(frozen=True)
    class ConfigKeys:
        key_config = "config"
        key_username = "username"
        key_max_framerate = "max_framerate"
        key_resolution = "resolution"
        key_fov = "fov"
        key_x = "x"
        key_y = "y"
        key_z = "z"
        key_renderer = "renderer"
        key_method = "method"
        key_border = "border"
        key_thickness = "thickness"

    def __init__(self, headless=False, data_dir="", username=None, left=0, top=1080, right=1920, bottom=0, title: Union[str, Identifier, None]="Saoirse", splash_txt=None, render_method="pylget", save_frame_list=False):
        self.set_headless(headless)
        self.render_method = render_method
        self.save_frame_list = save_frame_list

        super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main_window.get_identifier(), parent=None, title=title, left=left, top=top, right=right, bottom=bottom)

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
            self.set_fov_x(5)
        if not hasattr(self, "fov_y"):
            self.set_fov_y(5000)
        if not hasattr(self, "fov_z"):
            self.set_fov_z(4)

        self.set_renderer()

        self.draw()

    def get_render_method(self):
        return self.render_method

    def set_renderer(self):
        if self.get_render_method() == self.RendererKeys.key_pyglet:
            self.renderer = SaoirseClientRendererPyglet(headless=self.get_headless(), parent=self, left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), title=self.get_title(), save_frame_list=self.save_frame_list)
        elif self.get_render_method() == self.RendererKeys.key_PIL or (self.get_render_method() == self.RendererKeys.key_tk and self.get_headless()):
            self.renderer = SaoirseClientRendererPIL(headless=self.get_headless(), parent=self, left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), title=self.get_title(), save_frame_list=self.save_frame_list)
        elif self.get_render_method() == self.RendererKeys.key_tk:
            self.renderer = SaoirseClientRendererTk(headless=self.get_headless(), parent=self, left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), title=self.get_title(), save_frame_list=self.save_frame_list)
        else:
            self.renderer = SaoirseClientRendererPyray(headless=self.get_headless(), parent=self, left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), title=self.get_title(), save_frame_list=self.save_frame_list)

    def get_renderer(self):
        return self.renderer

    def get_frame_list(self):
        return self.renderer.get_frame_list()

    def set_headless(self, headless=False):
        self.headless = headless

    def get_headless(self):
        return self.headless

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
                    self.set_right(resolution.get(self.ConfigKeys.key_x))
                if self.ConfigKeys.key_y in resolution.keys():
                    self.set_bottom(resolution.get(self.ConfigKeys.key_y))
            if self.ConfigKeys.key_renderer in config.keys():
                config_renderer = config.get(self.ConfigKeys.key_renderer)
                if self.ConfigKeys.key_fov in config.keys():
                    config_fov = config_renderer.get(self.ConfigKeys.key_fov)
                    if self.ConfigKeys.key_x in config_fov.keys():
                        self.set_fov_x(config_fov.get(self.ConfigKeys.key_x))
                    if self.ConfigKeys.key_y in config_fov.keys():
                        self.set_fov_y(config_fov.get(self.ConfigKeys.key_y))
                    if self.ConfigKeys.key_z in config_fov.keys():
                        self.set_fov_z(config_fov.get(self.ConfigKeys.key_z))

    def get_data(self):
        data = super().get_data()
        config = {
            self.ConfigKeys.key_username: self.get_username(),
            self.ConfigKeys.key_max_framerate: self.get_max_framerate(),
            self.ConfigKeys.key_renderer: {
                self.ConfigKeys.key_fov: {
                    self.ConfigKeys.key_x: self.get_fov_x(),
                    self.ConfigKeys.key_y: self.get_fov_y(),
                    self.ConfigKeys.key_z: self.get_fov_z(),
                },
            },
        }
        data[self.ConfigKeys.key_config] = config
        return data

    def set_username(self, username="Player1"):
        self.username = username

    def get_username(self):
        return self.username

    def draw_image(self, img, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, shade_red: Union[int, float, None]=None, shade_green: Union[int, float, None]=None, shade_blue: Union[int, float, None]=None, shade_alpha: Union[int, float, None]=None, layer: Union[int, float]=0):
        imgpath = None
        if isinstance(img, Identifier):
            imgpath = img.get_file_path()
        elif isinstance(img, str):
            imgpath = img

        if imgpath is None or not path.isfile(imgpath):
            imgpath = saoirse_missing_img_path.copy()
        self.get_renderer().draw_image(imgpath, self.get_left() + left, self.get_bottom() + top, self.get_right() + right, self.get_bottom() + bottom, shade_red=shade_red, shade_green=shade_green, shade_blue=shade_blue, shade_alpha=shade_alpha, layer=layer)

    def draw_model(self, model: ThreeDimensionalShape, x: Union[int, float]=0, y: Union[int, float]=0, z: Union[int, float]=0, dots_per_meter: int=1, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin(), layer: Union[int, float]=0, reuse: Union[Identifier, None]=None):
        self.get_renderer().draw_model(model, self.get_left() + x, y, self.get_bottom() + z, dots_per_meter, cam_pos, layer, reuse)

    def draw_text(self, text: Union[str, Identifier], font_size: int=11, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float, None]=None, bottom: Union[int, float, None]=None, font_name: Union[str, Identifier]=default_font, color_red: int=150, color_green: int=150, color_blue: int=100, color_alpha: int=255):
        self.get_renderer().draw_text(text=text, font_size=font_size, left=self.get_left() + left, top=self.get_bottom() + top, right=right, bottom=bottom, font_name=font_name, color_red=color_red, color_green=color_green, color_blue=color_blue, color_alpha=color_alpha)

    def play_sound(self, ide):
        self.get_renderer().play_sound(ide)

    def set_server(self, server):
        pass

    def get_server(self):
        return None

    def draw_content(self):
        self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientMainScreen(self))

    def tick_content(self):
        fps = f"FPS: {self.get_current_framerate()}"
        self.draw_text(text=fps, left=20, top=self.get_height()-20)

    def tick(self, *args, **kwargs):
        do_frame = True
        current_time = gettime()
        if hasattr(self, "last_time"):
            if current_time - self.last_time < 1/self.get_max_framerate():
                do_frame = False
        if do_frame:
            self.renderer.pre_tick()
            self.set_right(self.renderer.get_width())
            self.set_bottom(self.renderer.get_height())
            super().tick()
            self.renderer.tick()
            self.renderer.post_tick()
            if hasattr(self, "last_time"):
                self.set_current_framerate(round(1/(current_time - self.last_time)))
            self.last_time = current_time

    def on_removed(self):
        self.save_config_to_file()
        super().on_removed()


class SaoirseClientRendererPyray(SaoirseClientBaseRenderer):
    def __init__(self, headless=False, parent=None, left=0, top=1080, right=1920, bottom=0, title="Saoirse", save_frame_list=False):
        super().__init__(headless=headless, parent=parent, left=left, top=top, right=right, bottom=bottom, title=title, render_method="pyray", save_frame_list=save_frame_list)

        self.window = pyray.init_window(int(self.get_width()), int(self.get_height()), title)
        pyray.set_target_fps(self.get_parent().get_max_framerate())
        self.camera = pyray.Camera3D([0.0, 0.0, 0.0], [0.0, 7.0, 0.0], [0.0, 1.0, 0.0], self.get_parent().get_fov_y(), 0)

    def draw_image(self, img, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, shade_red: Union[int, float, None]=None, shade_green: Union[int, float, None]=None, shade_blue: Union[int, float, None]=None, shade_alpha: Union[int, float, None]=None, layer: Union[int, float]=0):
        if right is None:
            right = 1
        if bottom is None:
            bottom = 0
        pyray.load_texture(img.get_path_str())
        pyray.draw_texture(pyray.Texture(img.get_path_str(), right-left, top-bottom, 1, 1), int(left), int(top), pyray.Color(shade_red, shade_green, shade_blue, shade_alpha))

    def draw_model(self, model: ThreeDimensionalShape, x: Union[int, float]=0, y: Union[int, float]=0, z: Union[int, float]=0, dots_per_meter: int=1, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin(), layer: Union[int, float]=0, reuse: Union[Identifier, None]=None):
        if isinstance(model, ThreeDimensionalShape):
            meshes = []
            materials = []
            for face in model.get_faces():
                # mesh = pyray.gen_mesh_cube(0, 0, 0)
                # mesh.vertexCount = len(face.get_edges())
                # for i, corner in enumerate(face.get_corners()):
                    # for i1, val in enumerate([corner.get_x(), corner.get_y(), corner.get_z()]):
                        # mesh.vertices[i+i1] = val
                edges = face.get_edges()
                meshes.append(pyray.Mesh(len(edges), int(len(edges)/3), [pyray.Vector3(corner.get_x(), corner.get_y(), corner.get_z()) for corner in face.get_corners()], None, None, None, None, None, None, None, None, None, None, None, None))
                # meshes.append(mesh)
                material = pyray.load_material_default()
                tex = face.get_texture()
                if tex is not None:
                    pyray.set_material_texture(material, 1, pyray.load_texture(tex))
                materials.append(material)
            pyray.draw_model(pyray.Model([0, 0, 0], len(meshes), len(meshes), meshes, materials, pyray.load_material_default(), 0, None, None), pyray.Vector3(x, y, z), 1, pyray.Color(255, 255, 255, 255))
        else:
            logger.warning(f"Unable to draw {model} as a model as it is not a a ThreeDimensionalShape!")

    def draw_text(self, text: str, font_size: int=11, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float, None]=None, bottom: Union[int, float, None]=None, font_name: Union[str, Identifier]=default_font, color_red: int=150, color_green: int=150, color_blue: int=100, color_alpha: int=255):
        pyray.draw_text(text, int(left), int(self.get_height() - top), font_size, pyray.Color(color_red, color_green, color_blue, color_alpha))

    def play_sound(self, ide: Identifier):
        pyray.play_sound_multi(pyray.load_sound(ide.get_file_path()))

    def on_removed(self):
        pyray.close_window()
        super().on_removed()

    def pre_tick(self):
        self.set_left(0)
        self.set_top(pyray.get_screen_height())
        self.set_right(pyray.get_screen_width())
        self.set_bottom(0)
        pyray.begin_drawing()
        pyray.clear_background(pyray.Color(110, 110, 110, 255))

    def tick(self, *args, **kwargs):
        super().tick()

    def post_tick(self):
        pyray.end_drawing()
        if pyray.window_should_close():
            self.on_removed()


class SaoirseClientRendererPyglet(SaoirseClientBaseRenderer):
    class RenderGroup(pyglet.graphics.Group):
        """A Group that enables and binds a Texture and ShaderProgram.
        RenderGroups are equal if their Texture and ShaderProgram
        are equal.
        """
        def __init__(self, texture, program, order=0, parent=None):
            """Create a RenderGroup.
            :Parameters:
                `texture` : `~pyglet.image.Texture`
                    Texture to bind.
                `program` : `~pyglet.graphics.shader.ShaderProgram`
                    ShaderProgram to use.
                `order` : int
                    Change the order to render above or below other Groups.
                `parent` : `~pyglet.graphics.Group`
                    Parent group.
            """
            super().__init__(order, parent)
            self.texture = texture
            self.program = program

        def set_state(self):
            pyglet.gl.glActiveTexture(pyglet.gl.GL_TEXTURE0)
            pyglet.gl.glBindTexture(self.texture.target, self.texture.id)
            pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
            pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
            self.program.use()

        def unset_state(self):
            pyglet.gl.glDisable(pyglet.gl.GL_BLEND)

        def __hash__(self):
            return hash((self.texture.target, self.texture.id, self.order, self.parent, self.program))

        def __eq__(self, other):
            return (self.__class__ is other.__class__ and
                    self.texture.target == other.texture.target and
                    self.texture.id == other.texture.id and
                    self.order == other.order and
                    self.program == other.program and
                    self.parent == other.parent)

    def __init__(self, headless: bool=False, parent=None, left: int=0, top: int=1080, right: int=1920, bottom: int=0, title: str="Saoirse", save_frame_list: bool=False):
        super().__init__(headless=headless, parent=parent, left=left, top=top, right=right, bottom=bottom, title=title, render_method="pyglet", save_frame_list=save_frame_list)

        self.render_que = []

        self.window = pyglet.window.Window(resizable=True, caption=self.get_title())
        # self.window.projection = pyglet.window.Mat4.perspective_projection(0, self.get_height(), self.get_width(), 0, z_near=0.1, z_far=self.get_fov_y())
        self.window.projection = pyglet.window.Mat4.perspective_projection(self.window.aspect_ratio, z_near=0.1, z_far=self.get_fov_y())
        pyglet.graphics.glClearColor(100/255, 100/255, 100/255, 1.0)

        pyglet.gl.glEnable(pyglet.gl.GL_DEPTH_TEST)
        pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)

        self.batch_2d = pyglet.graphics.Batch()
        self.batch_3d = pyglet.graphics.Batch()

        @self.window.event
        def on_resize(width, height):
            if width > 0:
                self.set_right(width)
            if height > 0:
                self.set_top(height)
            self.window.projection = pyglet.window.Mat4.perspective_projection(self.window.aspect_ratio, z_near=0.1, z_far=self.get_fov_y())
            # self.window.projection = pyglet.window.Mat4.perspective_projection(0, self.get_width(), 0, self.get_height(), z_near=0.1, z_far=self.get_fov_y())
            return pyglet.event.EVENT_UNHANDLED

    def set_headless(self, headless: bool = False):
        super().set_headless(headless)
        pyglet.options["headless"] = self.get_headless()

    def draw_image(self, img, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, shade_red: Union[int, float, None]=None, shade_green: Union[int, float, None]=None, shade_blue: Union[int, float, None]=None, shade_alpha: Union[int, float, None]=None, layer: Union[int, float]=0):
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

    def draw_model(self, model: ThreeDimensionalShape, x: Union[int, float]=0, y: Union[int, float]=0, z: Union[int, float]=0, dots_per_meter: int=1, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin(), layer: Union[int, float]=0, reuse: Union[Identifier, None]=None):
        if isinstance(model, ThreeDimensionalShape):
            shader = pyglet.model.get_default_textured_shader()
            dots_per_meter //= 10
            if y == 0:
                y = 1
            elif y == 1:
                y = 2
            for face in model.get_faces():
                # corners = face.get_corners()
                corners = []
                for edge in face.get_edges():
                    corners.extend(edge)
                count = len(corners)
                if count > 0:
                    texture = face.get_texture()
                    if isinstance(texture, Identifier):
                        texture_name = texture.get_file_path()
                    else:
                        texture_name = str(texture)
                    if not isinstance(texture, pyglet.image.Texture):
                        if str(texture_name) == str(None):
                            texture = None
                        else:
                            texture = pyglet.resource.image(texture_name)
                    if texture is not None:
                        vertices = []
                        for corner in corners:
                            vertices.extend([dots_per_meter*(corner.get_x()), dots_per_meter*(corner.get_z()), dots_per_meter*(corner.get_y())])
                            # vertices.extend([dots_per_meter*(corner.get_x() + x), dots_per_meter*(corner.get_z() + z), dots_per_meter*(corner.get_y() + y)])
                        #diffuse = [0.5, 0.0, 0.3, 1.0]
                        #ambient = [0.5, 0.0, 0.3, 1.0]
                        #specular = [1.0, 1.0, 1.0, 1.0]
                        #emission = [0.0, 0.0, 0.0, 1.0]
                        #shininess = 50
                        #material = pyglet.model.Material(texture_name, diffuse, ambient, specular, emission, shininess, texture_name)
                        #group = pyglet.model.TexturedMaterialGroup(material, shader, texture, layer)
                        # group = pyglet.graphics.TextureGroup(texture, layer)
                        group = SaoirseClientRendererPyglet.RenderGroup(texture, shader, layer)
                        # groups.append(group)
                        # self.render_que.append(group)
                        # self.batch_3d._add_group(group)
                        indices = []
                        for i in range(1, len(vertices)-2):
                            indices.extend([0, i, i+1])
                        self.render_que.append(shader.vertex_list_indexed(count=count, indices=indices, mode=pyglet.gl.GL_TRIANGLES, batch=self.batch_3d, group=group, vertices=("f", vertices), tex_coords=("f", texture.tex_coords)))
                        # print(shader.vertex_list(count=count, mode=pyglet.gl.GL_LINE_STRIP, batch=self.batch_3d, group=group, vertices=("f", vertices)))
            # if len(vertex_lists) > 0:
                # modelgl = pyglet.model.Model(vertex_lists=vertex_lists, groups=groups, batch=self.batch_3d)
                # model.translation = dots_per_meter*x, dots_per_meter*z, dots_per_meter*y
                # self.render_que.append(modelgl)
        else:
            logger.warning(f"Unable to draw {model} as a model as it is not a a ThreeDimensionalShape!")

    def draw_text(self, text: Union[str, Identifier], font_size: int=11, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float, None]=None, bottom: Union[int, float, None]=None, font_name: Union[str, Identifier]=default_font, color_red: int=150, color_green: int=150, color_blue: int=100, color_alpha: int=255):
        self.render_que.append(pyglet.text.Label(
                          text=text,
                          font_name=font_name,
                          font_size=font_size,
                          x=left, y=self.get_height()-top,
                          color=(color_red, color_green, color_blue, color_alpha),
                          anchor_x='left', anchor_y='top', batch=self.batch_2d))

    def play_sound(self, ide):
        pyglet.resource.media(ide.get_file_path()).play()

    def pre_tick(self):
        self.window.clear()

    def tick(self, *args, **kwargs):
        super().tick()
        self.batch_3d.draw()
        self.batch_2d.draw()

    def post_tick(self):
        for obj in self.render_que:
            if hasattr(obj, "delete"):
                obj.delete()
        self.render_que.clear()


class SaoirseClientRendererPIL(SaoirseClientBaseRenderer):
    def create_frame_img(self, img_args={}):
        if hasattr(self, "frame_img"):
            self.frame_img.close()
        self.frame_img = Image.new(mode="RGBA", size=(int(self.get_width()), int(self.get_height())), color=(100, 100, 100, 255), **img_args)
        if not hasattr(self, "img_que"):
            self.img_que = {}

    def get_frame_img(self):
        return self.frame_img

    def pre_tick(self):
        self.create_frame_img()

    def tick(self, *args, **kwargs):
        super().tick()
        self.tick_wait_model_imgs()
        if hasattr(self, "img_que"):
            layer_keys = list(self.img_que.keys())
            layer_keys.sort(reverse=True)
            for layer_key in layer_keys:
                layer = self.img_que.get(layer_key)
                for i, imgpargs in enumerate(layer):
                    img, imgargs = imgpargs
                    if img is not None:
                        self.draw_image_raw(img, **imgargs)
                    layer.pop(i)

    def post_tick(self):
        for layer in self.img_que.values():
            for img, _ in layer:
                if img is not None:
                    if isinstance(img, Image.Image):
                        img.close()
        self.img_que.clear()
        gc.collect()

    def draw_image_raw(self, img, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, shade_red: Union[int, float, None]=None, shade_green: Union[int, float, None]=None, shade_blue: Union[int, float, None]=None, shade_alpha: Union[int, float, None]=None, layer: Union[int, float]=0, thenclose=False):
        if left >= 0 and top >= 0:
            if isinstance(img, Identifier):
                img = Image.open(img.get_file_path())
            elif isinstance(img, str):
                img = Image.open(img)
            needs_resize = False
            if right is not None:
                width = right-left
                if img.width != width:
                    needs_resize = True
            else:
                width = img.width
            if bottom is not None:
                height = top-bottom
                if img.height != height:
                    needs_resize = True
            else:
                height = img.height
            if needs_resize and width > 0 and height > 0:
                img = img.resize((width, height), reducing_gap=3)
            needs_shade = False
            if shade_red is not None:
                r = shade_red
                needs_shade = True
            else:
                r = 0
            if shade_green is not None:
                g = shade_green
                needs_shade = True
            else:
                g = 0
            if shade_blue is not None:
                b = shade_blue
                needs_shade = True
            else:
                b = 0
            if needs_shade:
                img.im += (r, g, b, shade_alpha)
            self.frame_img.paste(im=img, box=(left, top), mask=img)
            if thenclose:
                img.close()

    def draw_image(self, img, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, shade_red: Union[int, float, None]=None, shade_green: Union[int, float, None]=None, shade_blue: Union[int, float, None]=None, shade_alpha: Union[int, float, None]=None, layer: Union[int, float]=0):
        if not hasattr(self, "img_que"):
            self.img_que = {}
        layer_set = self.img_que.get(layer, [])
        layer_set.append([img, {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "shade_red": shade_red,
            "shade_green": shade_green,
            "shade_blue": shade_blue,
            "shade_alpha": shade_alpha,
        }])
        self.img_que[layer] = layer_set

    def get_model_img(self, model: ThreeDimensionalShape, y: Union[int, float]=0, dots_per_meter: int=1, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin()):
        if isinstance(model, ThreeDimensionalShape):
            masks = {}
            model_greatest_x = 1
            model_greatest_z = 1
            draw_faces = []
            for face in model.get_faces():
                overlaps, remains, draw_faces = face.get_overlaps(draw_faces, cam_pos)
                if len(remains) > 0:
                    draw_faces.extend(remains)
                elif len(overlaps) == 0:
                    draw_faces.append(face)
            for draw_face in draw_faces:
                xz = []
                greatest_x = 1
                greatest_z = 1
                for corner in draw_face.get_corners():
                    cy = corner.get_y() + y + 1
                    if cy >= 0:
                        cx = round(dots_per_meter*((corner.get_x()-cam_pos.get_x())/cy))
                        cz = self.get_height() - round(dots_per_meter*((corner.get_z()-cam_pos.get_z())/cy))
                        if cx >= 0 and cz >= 0:
                            if cx > greatest_x:
                                greatest_x = cx
                            if cz > greatest_z:
                                greatest_z = cz
                            xz.append((cx, cz))
                if len(xz) >= 2:
                    if greatest_x > model_greatest_x:
                        model_greatest_x = greatest_x
                    if greatest_z > model_greatest_z:
                        model_greatest_z = greatest_z
                    tex = draw_face.get_texture()
                    key = str(tex)
                    _, mask_group = masks.get(key, (tex, []))
                    mask_group.append((xz, (greatest_x, greatest_z)))
                    masks[key] = (tex, mask_group)
            if len(masks.values()) > 0 and model_greatest_x > 0 and model_greatest_z > 0:
                model_img = Image.new(mode="RGBA", size=(int(model_greatest_x), int(model_greatest_z)), color=(0, 0, 0, 0))
                for i, mask in enumerate(masks.values()):
                    tex, mask_group = mask
                    _shade = min(5*i, 255)
                    shade = (_shade, _shade, _shade, 25)
                    if isinstance(tex, Identifier):
                        tex = Image.open(tex.get_file_path())
                    elif isinstance(tex, str):
                        tex = Image.open(tex)
                    for xzs, size in mask_group:
                        _mask = Image.new(mode="RGBA", size=size, color=(0, 0, 0, 0))
                        ImageDraw.Draw(im=_mask, mode="RGBA").polygon(xy=xzs, fill=(255, 255, 255, 255))
                        if tex is not None:
                            _tex = tex.resize(_mask.size, reducing_gap=3)
                            model_img.paste(im=_tex, mask=_mask)
                            _tex.close()
                        ImageDraw.Draw(im=_mask, mode="RGBA").polygon(xy=xzs, fill=shade, outline=(150, 150, 150, 255), width=2)
                        model_img.paste(im=_mask, mask=_mask)
                        _mask.close()
                    if tex is not None:
                        tex.close()
                return model_img
        else:
            logger.warning(f"Unable to draw {model} as a model as it is not a ThreeDimensionalShape!")
        return None

    def sub_draw_model(self, model: ThreeDimensionalShape, x: Union[int, float], y: Union[int, float], z: Union[int, float], dots_per_meter: int, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin(), layer: Union[int, float]=0, reuse: Identifier=Identifier()):
        self.drawing_model = True
        model_img = self.get_model_img(model, y, dots_per_meter, cam_pos)
        if model_img is not None:
            if hasattr(self, "wait_model_imgs"):
                wait_model_img = self.wait_model_imgs.get(str(reuse), None)
                if wait_model_img is not None:
                    wait_model_img[0].close()
                    self.wait_model_imgs.pop(str(reuse))
            else:
                self.wait_model_imgs = {}
            self.wait_model_imgs[str(reuse)] = [model_img, 0, 0, layer]
            #self.wait_model_imgs[layer] = [model_img, int(x*dots_per_meter), int(z*dots_per_meter)]
        self.drawing_model = False
    
    def tick_wait_model_imgs(self):
        if hasattr(self, "wait_model_imgs"):
            if self.wait_model_imgs is not None:
                for wait_model_img in self.wait_model_imgs.values():
                    if wait_model_img is not None:
                        img, x, z, layer = wait_model_img
                        self.draw_image(img.copy(), x, z, layer=layer)

    def draw_model(self, model: ThreeDimensionalShape, x: Union[int, float]=0, y: Union[int, float]=0, z: Union[int, float]=0, dots_per_meter: int=1, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin(), layer: Union[int, float]=0, reuse: Union[Identifier, None]=None):
        if reuse:
            if hasattr(self, "drawing_model"):
                skip_draw = self.drawing_model
            else:
                skip_draw = False
            if not skip_draw:
                Thread(target=self.sub_draw_model, args=[model, x, y, z, dots_per_meter, cam_pos, layer, reuse], daemon=True).start()
        else:
            self.draw_image(self.get_model_img(model, y, dots_per_meter, cam_pos), int(x*dots_per_meter), self.get_height() - int(z*dots_per_meter), layer=layer)

    def draw_text(self, text: Union[str, Identifier], font_size: int=11, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float, None]=None, bottom: Union[int, float, None]=None, font_name: Union[str, Identifier]=default_font, color_red: int=150, color_green: int=150, color_blue: int=100, color_alpha: int=255):
        txt = str(text)
        if right is None:
            right = left+int(font_size*len(txt))
        if bottom is None:
            bottom = top-font_size
        width = int(right-left)
        height = int(top-bottom)
        if width > 0 and height > 0:
            if font_name is None:
                font = None
            else:
                try:
                    font=ImageFont.load_path(str(font_name))
                except Exception as e:
                    if not hasattr(self, "has_warned_missing_font"):
                        logger.warning(f"Using plain font: Failed to draw text using font (actual name between quotes) \"{font_name}\" with exception: {e}")
                        self.has_warned_missing_font = True
                    font=None
            img = Image.new(mode="RGBA", size=(width, height), color=(0, 0, 0, 0))
            ImageDraw.Draw(im=img).multiline_text(xy=(0, 0), text=txt, font=font, stroke_width=font_size, fill=(color_red, color_green, color_blue, color_alpha))
            self.draw_image(img, int(left), int(top))

    def play_sound(self, sound):
        # TODO: Make this actually play the sound
        if isinstance(sound, Identifier):
            sound = sound.get_file_path()

    def on_removed(self):
        if hasattr(self, "wait_model_imgs"):
            for img in self.wait_model_imgs:
                if img is not None:
                    if hasattr(img, "close"):
                        img[0].close()
            self.wait_model_imgs.clear()
        if hasattr(self, "img_que"):
            for img in self.img_que:
                if img is not None:
                    if hasattr(img, "close"):
                        img.close()
            self.img_que.clear()
        super().on_removed()


class SaoirseClientRendererTk(SaoirseClientBaseRenderer, Tk):
    def __init__(self, headless=False, parent=None, left=0, top=1080, right=1920, bottom=0, title="Saoirse", save_frame_list=False):
        SaoirseClientBaseRenderer.__init__(self=self, headless=headless, parent=parent, left=left, top=top, right=right, bottom=bottom, title=title, render_method="tk", save_frame_list=save_frame_list)
        Tk.__init__(self=self, className=self.get_title())
        self.sub_renderer = SaoirseClientRendererPIL(headless=self.get_headless(), left=self.get_left(), top=self.get_top(), right=self.get_right(), bottom=self.get_bottom(), title=self.get_title(), render_method="tk")
        self.wm_resizable(True, True)
        self.frame = None
        self.frame_label = TkLabel(self)
        self.frame_label.pack(expand=True, fill=TkBOTH)

    def get_frame_list(self):
        return self.sub_renderer.get_frame_list()

    def destroy(self):
        self.on_removed()
        super().destroy()

    def draw_image(self, img, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float]=1, bottom: Union[int, float]=0, shade_red: Union[int, float, None]=None, shade_green: Union[int, float, None]=None, shade_blue: Union[int, float, None]=None, shade_alpha: Union[int, float, None]=None, layer: Union[int, float]=0):
        self.sub_renderer.draw_image(img, top, left, right, bottom, shade_red=shade_red, shade_green=shade_green, shade_blue=shade_blue, shade_alpha=shade_alpha, layer=layer)

    def draw_model(self, model: ThreeDimensionalShape, x: Union[int, float]=0, y: Union[int, float]=0, z: Union[int, float]=0, dots_per_meter: int=1, cam_pos: ThreeDimensionalPosition=ThreeDimensionalPosition.get_origin(), layer: Union[int, float]=0, reuse: Union[Identifier, None]=None):
        self.sub_renderer.draw_model(model, x, y, z, dots_per_meter, cam_pos, layer, reuse)

    def draw_text(self, text: Union[str, Identifier], font_size: int=11, left: Union[int, float]=0, top: Union[int, float]=1, right: Union[int, float, None]=None, bottom: Union[int, float, None]=None, font_name: Union[str, Identifier]=default_font, color_red: int=150, color_green: int=150, color_blue: int=100, color_alpha: int=255):
        self.sub_renderer.draw_text(text=text, font_size=font_size, left=left, top=top, right=right, bottom=bottom, font_name=font_name, color_red=color_red, color_green=color_green, color_blue=color_blue, color_alpha=color_alpha)

    def play_sound(self, ide):
        self.sub_renderer.play_sound(ide)

    def pre_tick(self):
        self.set_left(0)
        self.set_top(self.winfo_height())
        self.set_right(self.winfo_width())
        self.set_bottom(0)
        self.sub_renderer.set_left(0)
        self.sub_renderer.set_top(self.get_height())
        self.sub_renderer.set_right(self.get_width())
        self.sub_renderer.set_bottom(0)

        self.sub_renderer.pre_tick()

    def tick(self, *args, **kwargs):
        self.sub_renderer.tick()

    def post_tick(self):
        img = self.sub_renderer.get_frame_img()
        del self.frame
        self.frame = ImageTk.PhotoImage(img)
        self.frame_label.config(image=self.frame)
        if self.save_frame_list:
            self.frame_list.append(img.copy())
        img.close()
        self.sub_renderer.post_tick()
        self.update_idletasks()
        self.update()

    def on_removed(self):
        if hasattr(self, "sub_renderer"):
            self.sub_renderer.on_removed()
        if self.get_parent() is not None:
            self.get_parent().on_removed()
        super().on_removed()


def main(args=[],
         headless = False,
         return_frame_list = False,
         use_pyglet = False,
         use_tk = False,
         data_dir = "SaoirseClient.d",
         username = None,
):

    arg_key_help = ("--help", "-h")
    arg_key_version = ("--version", "-v")
    arg_key_headless = "--headless"
    arg_key_return_frame_list = "--return-frame-list"
    arg_key_use_tk = "--tk"
    arg_key_use_pyglet = "--pyglet"
    arg_key_data_dir = "--data-dir="
    arg_key_username = "--username="

    help_msg = """
    Client program for the game Saoirse

    Usage (depends on which executable form is being run):

    For binary releases:

    *NIX: saoirse_client OPTIONS
    WINDOWS: saoirse_client.exe OPTIONS

    For Python source files:

    pypy3 saoirse_client.py OPTIONS
    python3 saoirse_client.py OPTIONS

    Valid OPTIONS:

    --headless                                          Create a client object that ticks and generates frames images without opening a window
    --return-frame-list                                 Makes the main() function save a list of all frames generated as the program runs and return it upon exiting
    --pyglet                                            Makes the client window use Pyglet instead of Pyray. Not fully implimented
    --tk                                                Makes the client window use Pillow and Tk instead of Pyray. Not recommended for performance
    --data-dir=DATADIR                                  Sets the directory for saving client-side settings and resources to DATADIR. Uses the current directory if not specified
    --username=USERNAME                                 Sets the client object\'s username to USERNAME. Overrides the name specified in the config.json file under DATADIR. Defaults to \'Player1\' if not specified in either place
    --version, -v                                       Print the version of the game client file being run, along with that of the server and the base library
    --help, -h                                          Print this help message and exit
    """

    version_msg = f"""
    Saoirse Library Version: {saoirse_lib_version}
    Saoirse Server Version: {saoirse_server_version}
    Saoirse *Client* Version: {saoirse_client_version}
    """

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
            elif arg.startswith(arg_key_use_pyglet):
                use_pyglet = True
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
        "So then I said \"something about a programming language named after an acting troop that isn\'t performant enough for game development\"...",
        "Did you buy this game? You know you can compile it from source for free, right? Oh, you wanted to support the devloper? Well thanks!",
        "If you aren\'t $USERNAME, stop impersonating people!",
    ]
    window_title = f"Saoirse v{saoirse_client_version}:   {randchoice(splash_txts).replace('$USERNAME', str(username))}"

    if use_pyglet:
        render_method = "pyglet"
    elif use_tk:
        render_method = "tk"
    else:
        render_method = "pyray"

    client = SaoirseClientMainWindowScreen(data_dir=data_dir, headless=headless, username=username, title=window_title, render_method=render_method)
    if client.get_render_method() == "pyglet":
        pyglet.clock.schedule(client.tick)
        pyglet.app.run()
    else:
        while not client.removed:
            client.tick()
    if return_frame_list:
        return client.get_frame_list()


if __name__ == "__main__":
    main(args=argv)

