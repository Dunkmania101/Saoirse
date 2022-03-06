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


import sys, os, pyglet
from json import dumps as jdumps, loads as jloads
from pyglet.gl import glEnable, glClearColor, GL_DEPTH_TEST, GL_CULL_FACE
from saoirse_base import logger, expand_full_path, Identifier, MainGameObject, InteractableObject, SpaceGameObject, ThreeDimensionalShape
from saoirse_server import saoirse_id, SaoirseServer, SaoirseIdentifierEnum


default_font = "Exo 2 Regular"


class BaseWidgets:
    class BaseWidget(MainGameObject, InteractableObject):
        def __init__(self, ide, server, current_space=None, parent=None, width=20, height=20, left=0, top=0):
            self.set_parent(parent)

            super().__init__(ide, server)

            self.children = {}
            self.set_current_space(current_space)
            self.set_width(width)
            self.set_height(height)
            self.set_left(left)
            self.set_top(top)

        def set_current_space(self, space):
            self.current_space = space

        def get_current_space(self):
            return self.current_space

        def set_parent(self, parent):
            self.parent = parent

        def get_parent(self):
            return self.parent

        def get_children(self):
            return self.children

        def add_child(self, child, move_child=True, set_child_server=True, set_child_current_space=True):
            child.set_parent(self)
            if set_child_server and hasattr(child, "set_server"):
                child.set_server(self.get_server())
            if set_child_current_space and hasattr(child, "set_current_space"):
                child.set_current_space(self.get_current_space())
            if move_child:
                child.set_left(child.get_left() + self.get_left())
                child.set_top(child.get_top() + self.get_top())
            i = 0
            child_key = child.get_id().get_path_str()
            for key in self.children.keys():
                if key.startswith(child_key):
                    i += 1
            self.children[child.get_id().append(str(i)).get_path_str()] = child

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

        def draw_image(self, ide, left=0, top=0):
            self.get_parent().draw_image(ide, self.get_top() + top, self.get_left() + left)

        def draw_model(self, ide, left=0, top=0, depth=0, rotX=0, rotY=0, rotZ=0):
            self.get_parent().draw_model(ide, self.get_top() + top, self.get_left() + left, depth, rotX, rotY, rotZ)

        def draw_text(self, text, font_size=11, left=0, top=0, font_name=default_font, color_red=255, color_green=255, color_blue=255, color_alpha=255):
            self.get_parent().draw_text(text=text, font_size=font_size, left=self.get_left() + left, top=self.get_top() + top, font_name=font_name, color_red=color_red, color_green=color_green, color_blue=color_blue, color_alpha=color_alpha)

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


    class TextWidget(BaseWidget):
        def __init__(self, ide, server, current_space=None, parent=None, width=20, height=20, left=0, top=0, text="", font_name=default_font, color_red=255, color_green=255, color_blue=255, color_alpha=255):
            super().__init__(ide, server, current_space=current_space, parent=parent, width=width, height=height, left=left, top=top)

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
            self.draw_text(self.get_text(), self.get_font_size(), font_name=self.get_font_name(), color_red=self.get_color_red(), color_green=self.get_color_green(), color_blue=self.get_color_blue(), color_alpha=self.get_color_alpha())


    class ButtonWidget(BaseWidget):
        def __init__(self, ide, server, current_space=None, parent=None, width=20, height=20, left=0, top=0, label=""):
            super().__init__(ide, server, current_space=current_space, parent=parent, width=width, height=height, left=left, top=top)

            self.label = label

        def draw_content(self):
            self.add_child(BaseWidgets.TextWidget(self.get_id(), self.get_server(), width=self.get_width() * 0.75, height=self.get_height(), left=0, top=0, text=self.get_label()))

        def get_label(self):
            return self.label


class ScreenWidget(BaseWidgets.BaseWidget):
    def __init__(self, ide, server, current_space=None, parent=None, width=1200, height=800, left=0, top=0, title=""):
        super().__init__(ide, server, current_space=current_space, parent=parent, width=width, height=height, left=left, top=top)

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
                def __init__(self, server, current_space=None, parent=None, width=50, height=20, left=50, top=50):
                    super().__init__(SaoirseClientWidgets.ClientWidgets.Buttons.ButtonIdentifiers.singleplayer.get_identifier(), server, current_space=current_space, parent=parent, width=width, height=height, left=left, top=top, label="Singleplayer")

                def tick_content(self):
                    self.draw_image(Identifier(["resources", saoirse_id, "media", "pic1.png"]))

    class ClientScreens:
        class ScreenIdentifiers(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier(["screens"]).extend(super().get_base_ide())

            main_window = "main_window"
            main = "main"
            home = "home"
            world = "world"

        class SaoirseClientWorldScreen(ScreenWidget):
            def __init__(self, server, current_space=None, parent=None, player_id=""):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.world.get_identifier(), server, current_space=current_space, parent=parent, title="")

                self.set_player_id(player_id)
                self.connect_with_server()

            def set_player_id(self, ide):
                self.player_id = ide

            def get_player_id(self):
                return self.player_id

            def get_player_entity(self):
                return self.get_server().get_player_by_id(self.get_player_id())

            def connect_with_server(self):
                pass
                # Currently has a NoneTypeException
                #self.get_server().add_player(self.get_player_id())
                #self.get_player_entity().set_pos(self.get_player_entity().get_pos().offset(ThreeDimensionalPosition.Direction.FRONT, 3))

            def tick_content(self):
                if self.get_current_space() is not None:
                    for obj_set in self.get_current_space().get_objects():
                        for obj in obj_set:
                            if isinstance(obj, SpaceGameObject):
                                model = obj.get_model()
                                if model is not None:
                                    self.draw_model(model)

            def on_removed(self):
                if self.get_server() is not None:
                    self.get_server().on_removed()
                super().on_removed()

        class SaoirseClientHomeScreen(ScreenWidget):
            def __init__(self, server, parent):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.home.get_identifier(), server, parent=parent, width=parent.get_width(), height=parent.get_height(), left=0, top=0, title="Saoirse")

        class SaoirseClientMainScreen(ScreenWidget):
            def __init__(self, server, parent=None, width=1200, height=800, left=0, top=0, title=""):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main.get_identifier(), server, parent=parent, width=width, height=height, left=left, top=top, title=title)

            def draw_content(self):
                self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientWorldScreen(self.get_server(), None, self))
                self.add_child(SaoirseClientWidgets.ClientWidgets.Buttons.SaoirseClientSingleplayerButton(self.get_server(), self))

            def tick_content(self):
                # pyglet.resource.image("resources/saoirse/media/pic1.png")
                self.draw_model(Identifier(["resources", saoirse_id, "media", "box1.obj"]), 5, 5, 5, 2.5, 2.3, 2.1)


class SaoirseClientMainWindowScreenPyglet(ScreenWidget):
    key_username = "username"

    def __init__(self, headless=False, data_dir="", username=None):
        super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main_window.get_identifier(), server=None, parent=None, title="Saoirse")

        self.set_data_dir(data_dir)
        self.config_file = os.path.join(self.get_data_dir(), "client_config.json")
        self.read_config_from_file()

        if username is not None:
            self.set_username(username)
        if not hasattr(self, "username"):
            self.set_username("Player1")

        pyglet.options["headless"] = headless

        self.render_que = []

        self.draw()

        self.window = pyglet.window.Window(width=self.get_width(), height=self.get_height(), resizable=True, caption=self.get_title())
        self.window.projection = pyglet.window.Mat4.perspective_projection(0, self.get_width(), 0, self.get_height(), z_near=0.1, z_far=255)
        glClearColor(0, 0, 0, 1)

        self.batch = pyglet.graphics.Batch()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        @self.window.event
        def on_resize(width, height):
            if width > 0 and height > 0:
                self.set_width(width)
                self.set_height(height)

        @self.window.event
        def on_draw():
            # For some reason the window is blank when it tries to render models
            self.window.clear()
            self.batch.draw()
            for obj in self.render_que:
                if hasattr(obj, "delete"):
                    obj.delete()
            self.render_que.clear()

        pyglet.clock.schedule_interval(self.tick, 1 / self.get_ticks_per_second())

        pyglet.app.run()

        self.on_removed()

    def set_data_dir(self, data_dir):
        self.data_dir = data_dir

    def get_data_dir(self):
        return self.data_dir

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def save_config_to_file(self):
        data = None
        try:
            data = jdumps(self.get_data(), indent=2) # Get data first to avoid writing a broken config to the config file
        except Exception as e:
            logger.warning(f"Failed to write config to file, it will not be saved (the old config will still remain intact): {str(e)}")
        if data is not None:
            with open(self.get_config_file(), "w") as f:
                f.write(data)

    def read_config_from_file(self):
        if os.path.isfile(self.get_config_file()):
            data = None
            try:
                with open(self.get_config_file(), "r") as f:
                    data = jloads(f.read()) # Get data first to avoid reading a broken config from the config file
            except Exception as e:
                logger.warning(f"Failed to load config from file, the default will be used: {str(e)}")
            if data is not None:
                self.set_data(data)

    def set_data(self, data):
        super().set_data(data)
        if self.key_username in data.keys():
            self.set_username(data.get(self.key_username))

    def get_data(self):
        data = super().get_data()
        data[self.key_username] = self.get_username()
        return data

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_server(self, server):
        self.server = server

    def get_server(self):
        return self.server

    def draw_content(self):
        # TEST: Create a server
        self.set_server(SaoirseServer())

        self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientMainScreen(self.get_server(), self))

    def draw_image(self, ide, left, top):
        self.render_que.append(pyglet.sprite.Sprite(pyglet.resource.image(ide.get_file_path()), x=left, y=top, batch=self.batch))

    def draw_model_gl(self, model, left=0, top=0, depth=0, rotX=0, rotY=0, rotZ=0):
        if isinstance(model, pyglet.model.Model):
            model.translation = left, top, depth
            model.rotation = rotX, rotY, rotZ
            self.render_que.append(model)

    def draw_model(self, ide_or_model, left=0, top=0, depth=0, rotX=0, rotY=0, rotZ=0):
        if isinstance(ide_or_model, Identifier):
            model = pyglet.resource.model(ide_or_model.get_file_path(), batch=self.batch)
            self.draw_model_gl(model, left=left, top=top, depth=depth, rotX=rotX, rotY=rotY, rotZ=rotZ)
        elif isinstance(ide_or_model, ThreeDimensionalShape):
            for box in ide_or_model.get_boxes():
                model = pyglet.model.Model(pyglet.graphics.vertex_list("v3f", ((float(c.get_pos().get_x()), float(c.get_pos().get_y()), float(c.get_pos().get_z())) for c in box.get_corners())), groups=[pyglet.model.TexturedMaterialGroup(material=pyglet.model.Material("base", 1, 1, 1, 1, 1), texture=pyglet.resource.texture(texture)) for texture in box.get_textures()], batch=self.batch_3d)
                self.draw_model_gl(model, left, top, depth, rotX, rotY, rotZ)
            else:
                logger.warning(f"Unable to draw {str(ide_or_model)} as a model as it is not an Identifier or a ThreeDimensionalShape!")

    def draw_text(self, text, font_size=11, left=0, top=0, font_name=default_font, color_red=255, color_green=255, color_blue=255, color_alpha=255):
        self.render_que.append(pyglet.text.Label(
                          text=text,
                          font_size=font_size,
                          font_name=font_name,
                          x=left, y=top,
                          color=(color_red, color_green, color_blue, color_alpha),
                          anchor_x='center', anchor_y='center', batch=self.batch))

    def play_sound(self, ide):
        pyglet.resource.media(ide.get_file_path()).play()

    def tick(self, *args, **kwargs):
        if self.get_server() is not None:
            self.get_server().tick()
        super().tick()

    def on_removed(self):
        super().on_removed()
        self.save_config_to_file()


def main(args):
    headless = False
    data_dir = ""
    username = None

    arg_key_headless = "--headless"
    arg_key_data_dir = "--data_dir="
    arg_key_username = "--username="

    if len(args) > 1:
        for arg in args[1:]:
            if arg.startswith(arg_key_data_dir):
                data_dir = expand_full_path(arg.replace(arg_key_data_dir, ""))
            if arg.startswith(arg_key_username):
                username = arg.replace(arg_key_username, "")
            if arg.startswith(arg_key_headless):
                headless = True

    SaoirseClientMainWindowScreenPyglet(headless=headless, data_dir=data_dir, username=username)


if __name__ == "__main__":
    main(sys.argv)
