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


import sys, os, tkinter
from PIL import ImageTk, Image, ImageDraw, ImageFont
from time import time as gettime
from json import dumps as jdumps, loads as jloads
from saoirse_base import logger, expand_full_path, Identifier, MainGameObject, InteractableObject, SpaceGameObject, ThreeDimensionalShape
from saoirse_server import saoirse_id, SaoirseServer, SaoirseIdentifierEnum, Items


# default_font = "Exo 2 Regular"
default_font = None


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

        def draw_image(self, img, left=0, top=0, right=0, bottom=0):
            self.get_parent().draw_image(img, self.get_top() + top, self.get_left() + left, self.get_right() + right, self.get_bottom() + bottom)

        def draw_model(self, model, left=0, top=0, depth=0):
            self.get_parent().draw_model(model, self.get_left() + left, self.get_top() + top, depth)

        def draw_text(self, text, font_size=11, left=0, top=0, right=0, bottom=0, font_name=default_font, color_red=255, color_green=255, color_blue=190, color_alpha=255):
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


    class TextWidget(BaseWidget):
        def __init__(self, ide, parent=None, width=20, height=20, left=0, top=0, text="", font_name=default_font, color_red=255, color_green=255, color_blue=190, color_alpha=255):
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
            def __init__(self, parent=None, player_id=""):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.world.get_identifier(), parent=parent, title="")

                self.set_server(SaoirseServer())
                self.set_player_id(player_id)
                self.connect_with_server()

            def set_player_id(self, ide):
                self.player_id = ide

            def get_player_id(self):
                return self.player_id

            def get_player_entity(self):
                if self.get_server() is not None:
                    return self.get_server().get_player_by_id(self.get_player_id())
                return None

            def get_current_space(self):
                player = self.get_player_entity()
                if player is not None:
                    return player.get_current_space()
                return None

            def connect_with_server(self):
                if self.get_server() is not None:
                    self.get_server().add_player(self.get_player_id())

            def tick_content(self):
                # TODO: This blindly draws all objects
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
            def __init__(self, parent):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.home.get_identifier(), parent=parent, width=parent.get_width(), height=parent.get_height(), left=0, top=0, title="Saoirse")

        class SaoirseClientMainScreen(ScreenWidget):
            def __init__(self, parent=None, left=0, top=0, width=1200, height=800, title=""):
                super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main.get_identifier(), parent=parent, left=left, top=top, width=width, height=height, title=title)

            def draw_content(self):
                self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientWorldScreen(self))
                self.add_child(SaoirseClientWidgets.ClientWidgets.Buttons.SaoirseClientSingleplayerButton(self))

            def tick_content(self):
                self.set_width(self.get_parent().get_width())
                self.set_height(self.get_parent().get_height())
                # pyglet.resource.image("resources/saoirse/media/pic1.png")
                # self.draw_model(Identifier(["resources", saoirse_id, "media", "box1.obj"]), 5, 15)
                self.draw_model(Items.Equipment.Tools.HatchetItem.HatchetItemShape(), 10, 15)


class SaoirseClientMainWindowScreen(ScreenWidget):
    class ConfigKeys:
        key_config = "config"
        key_username = "username"
        key_max_framerate = "max_framerate"

    def __init__(self, data_dir="", username=None, width=1920, height=1080):
        super().__init__(SaoirseClientWidgets.ClientScreens.ScreenIdentifiers.main_window.get_identifier(), parent=None, title="Saoirse", left=0, top=0, width=width, height=height)

        self.set_data_dir(data_dir)
        self.config_file = os.path.join(self.get_data_dir(), "client_config.json")
        self.read_config_from_file()

        if username is not None:
            self.set_username(username)
        if not hasattr(self, "username"):
            self.set_username("Player1")
        if not hasattr(self, "max_framerate"):
            self.set_max_framerate()
        if not hasattr(self, "current_framerate"):
            self.set_current_framerate(0)

        self.draw()

    def set_max_framerate(self, framerate=60):
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

    def save_config_to_file(self):
        try:
            data = jdumps(self.get_data(), indent=2) # Get data first to avoid writing a broken config to the config file
        except Exception as e:
            logger.warning(f"Failed to write config to file, it will not be saved (the old config will still remain intact): {str(e)}")
            data = None
        if data is not None:
            with open(self.get_config_file(), "w") as f:
                f.write(data)

    def read_config_from_file(self):
        if os.path.isfile(self.get_config_file()):
            try:
                with open(self.get_config_file(), "r") as f:
                    data = jloads(f.read()) # Get data first to avoid reading a broken config from the config file
            except Exception as e:
                logger.warning(f"Failed to load config from file, the default will be used: {str(e)}")
                data = None
            if data is not None:
                self.set_data(data)

    def set_data(self, data):
        super().set_data(data)
        if self.ConfigKeys.key_config in data.keys():
            config = data.get(self.ConfigKeys.key_config)
            if self.ConfigKeys.key_username in config.keys():
                self.set_username(config.get(self.ConfigKeys.key_username))
            if self.ConfigKeys.key_max_framerate in config.keys():
                self.set_max_framerate(config.get(self.ConfigKeys.key_max_framerate))

    def get_data(self):
        data = super().get_data()
        config = {
            self.ConfigKeys.key_username: self.get_username(),
            self.ConfigKeys.key_max_framerate: self.get_max_framerate(),
        }
        data[self.ConfigKeys.key_config] = config
        return data

    def set_username(self, username="Player1"):
        self.username = username

    def get_username(self):
        return self.username

    def set_server(self, server):
        self.server = server

    def get_server(self):
        return self.server

    def draw_content(self):
        self.add_child(SaoirseClientWidgets.ClientScreens.SaoirseClientMainScreen(self))

    def tick_content(self):
        self.draw_text(text=f"FPS: {int(self.get_current_framerate())}", left=5, top=5, right=65, bottom=25)

    def on_removed(self):
        self.save_config_to_file()
        super().on_removed()


class SaoirseClientMainWindowScreenPIL(SaoirseClientMainWindowScreen):
    def create_frame_img(self, img_args={}):
        if hasattr(self, "frame_img"):
            self.frame_img.close()
        self.frame_img = Image.new(mode="RGBA", size=(self.get_width(), self.get_height()), color=(100, 100, 100, 255), **img_args)

    def get_frame_img(self):
        return self.frame_img

    def get_next_frame(self):
        if hasattr(self, "frame_img"):
            self.frame_img.close()
        self.create_frame_img()
        self.tick()
        return self.get_frame_img().copy()

    def draw_image(self, img, left=0, top=0, right=20, bottom=20):
        if isinstance(img, Identifier):
            img = Image.open(img.get_file_path())
        self.frame_img.paste(im=img.resize((right-left, bottom-top), reducing_gap=3), box=(left, top, right, bottom))

    def draw_model(self, model, left=0, top=0, depth=20):
        return # TODO: This function is incomplete and way too slow
        if isinstance(model, ThreeDimensionalShape):
            if depth == 0:
                depth = 1
            for box in model.get_boxes():
                for face in box.get_faces():
                    img = Image.new(mode="RGBA", size=(self.get_width(), self.get_height()), color=(0, 0, 0, 255))
                    xy=[]
                    for corner in face.get_corners():
                        z = corner.get_z()
                        if z == 0:
                            z = 1
                        xy.append((corner.get_x()/(z*depth), corner.get_y()/(z*depth)))
                    ImageDraw.Draw(im=img).polygon(xy=xy, fill=(255, 255, 255, 255))
                    texture = face.get_texture()
                    if isinstance(texture, Identifier):
                        texture = Image.open(texture.get_file_path())
                    bbox = img.getbbox()
                    img = img.resize((bbox[2] - bbox[0], bbox[3] - bbox[1]), reducing_gap=3)
                    img.paste(im=texture.resize(img.size, reducing_gap=3), mask=img)
                    self.draw_image(img, left, top, left + bbox[2], top + bbox[3])
        else:
            logger.warning(f"Unable to draw {str(model)} as a model as it is not an Identifier or a ThreeDimensionalShape!")

    def draw_text(self, text, font_size=11, left=0, top=0, right=20, bottom=20, font_name=default_font, color_red=255, color_green=255, color_blue=190, color_alpha=255):
        if font_name is None:
            font = None
        else:
            try:
                font=ImageFont.load_path(font_name)
            except Exception as e:
                logger.warning(f"Using plain font: Failed to draw text using font {str(font_name)} with exception: {str(e)}")
                font=None
        img = Image.new(mode="RGBA", size=((int(right-left), int(bottom-top))), color=(0, 0, 0, 0))
        ImageDraw.Draw(im=img).multiline_text(xy=(0, 0), text=text, font=font, stroke_width=font_size, fill=(color_red, color_green, color_blue, color_alpha))
        self.draw_image(img, int(left), int(top), int(right), int(bottom))

    def play_sound(self, ide):
        pass
        #ide.get_file_path() # TODO


class SaoirseClientMainWidowScreenTk(tkinter.Tk):
    def __init__(self, client, save_frame_list=False):
        super().__init__(className="Saoirse")
        self.save_frame_list = save_frame_list
        if self.save_frame_list:
            self.frame_list = []
        self.client = client
        self.wm_resizable(True, True)
        self.frame_label = tkinter.Label(self)
        self.frame_label.pack(expand=True, fill=tkinter.BOTH)
        self.update_frame()

    def get_frame_list(self):
        if hasattr(self, "frame_list"):
            return self.frame_list
        return None

    def destroy(self):
        self.client.on_removed()
        super().destroy()

    def update_frame(self):
        self.sync_size()
        do_frame = True
        if hasattr(self, "last_time"):
            if gettime() - self.last_time < 1/self.client.get_max_framerate():
                do_frame = False
        if do_frame:
            self.next_frame()
            self.frame_label.config(image=self.frame)
            current_time = gettime()
            if hasattr(self, "last_time"):
                self.client.set_current_framerate(1/(current_time - self.last_time))
            self.last_time = current_time

    def next_frame(self):
        img = self.client.get_next_frame()
        self.frame = ImageTk.PhotoImage(img)
        if self.save_frame_list:
            self.frame_list.append(img)
        else:
            img.close()

    def sync_size(self):
        width = self.winfo_width()
        height = self.winfo_height()
        self.client.set_width(width)
        self.client.set_height(height)


def main(args=[],
         headless = False,
         return_frame_list = False,
         data_dir = "",
         username = None,
):

    arg_key_headless = "--headless"
    arg_key_return_frame_list = "--return_frame_list"
    arg_key_data_dir = "--data_dir="
    arg_key_username = "--username="

    if len(args) > 1:
        for arg in args[1:]:
            if arg.startswith(arg_key_data_dir):
                data_dir = expand_full_path(arg.replace(arg_key_data_dir, ""))
            elif arg.startswith(arg_key_username):
                username = arg.replace(arg_key_username, "")
            elif arg.startswith(arg_key_headless):
                headless = True
            elif arg.startswith(arg_key_return_frame_list):
                return_frame_list = True

    client = SaoirseClientMainWindowScreenPIL(data_dir=data_dir, username=username)
    if not headless:
        root = SaoirseClientMainWidowScreenTk(client, return_frame_list)
        while not client.removed:
            root.update_frame()
            root.update_idletasks()
            root.update()
        if return_frame_list:
            return root.get_frame_list()
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
    main(args=sys.argv)
