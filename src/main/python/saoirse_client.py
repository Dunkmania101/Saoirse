# This file is:
# src/python/saoirse_client.py

import time, sys, pyglet
from pyglet.gl import glEnable, GL_DEPTH_TEST, GL_CULL_FACE
from saoirse_base import Identifier, MainGameObject, InteractableGameObject
from saoirse_server import saoirse_id


class Widgets:
    class BaseWidget(MainGameObject, InteractableGameObject):
        def __init__(self, ide, server, parent=None, width=20, height=20, left=0, top=0):
            super().__init__(ide, server)

            self.set_parent(parent)
            self.set_width(width)
            self.set_height(height)
            self.set_left(left)
            self.set_top(top)

        def set_parent(self, parent):
            self.parent = parent

        def get_parent(self):
            return self.parent

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

        def draw_model(self, ide, left=0, top=0, depth=0, rotX=0, rotY=0, rotZ=0, group=None):
            self.get_parent().draw_model(ide, self.get_top() + top, self.get_left() + left, depth, rotX, rotY, rotZ, group)

        def draw_text(self, text, font_size, left=0, top=0, font_name="Exo 2 Regular"):
            self.get_parent().draw_text(text=text, font_size=font_size, left=self.get_left() + left, top=self.get_top() + top, font_name=font_name)

        def play_sound(self, ide):
            self.get_parent().play_sound(ide)

        def draw(self):
            pass

        def tick_content(self):
            pass

        def tick(self):
            self.tick_content()


    class TextWidget(BaseWidget):
        def __init__(self, ide, server, parent=None, width=20, height=20, left=0, top=0, text=""):
            super().__init__(ide, server, parent=parent, width=width, height=height, left=left, top=top)

            self.set_text(text)

        def set_text(self, text):
            self.text = text

        def get_text(self):
            return self.text

        def tick_content(self):
            self.draw_text(self.get_text(), 11, self.get_left(), self.get_top())


    class ButtonWidget(BaseWidget):
        def __init__(self, ide, server, parent=None, width=20, height=20, left=0, top=0, label=""):
            super().__init__(ide, server, parent=parent, width=width, height=height, left=left, top=top)

            self.label = label

        def get_label(self):
            return self.label

        def tick_content(self):
            self.draw_text(self.get_label(), 11, left=self.get_left(), top=self.get_top())


class ScreenWidget(Widgets.BaseWidget):
    def __init__(self, ide, server, parent=None, width=1200, height=800, left=0, top=0, title=""):
        super().__init__(ide, server, parent, width, height, left, top)

        self.title = title
        self.children = {}

    def get_title(self):
        return self.title

    def get_children(self):
        return self.children

    def add_child(self, child, move_child=True):
        child.set_parent(self)
        if move_child:
            child.set_left(child.get_left() + self.get_left())
            child.set_top(child.get_top() + self.get_top())
        self.children[child.get_id().get_path_str()] = child

    def on_removed(self):
        for child in self.get_children().values():
            child.on_removed()
        super().on_removed()

    def draw(self):
        for child in self.get_children().values():
            child.draw()

    def tick(self):
        super().tick()
        for child in self.get_children().values():
            child.tick()


class SaoirseClientWidgets:
    class Widgets:
        class Buttons:
            class SaoirseClientSingleplayerButton(Widgets.ButtonWidget):
                def __init__(self, server, parent=None, width=50, height=20, left=50, top=50):
                    super().__init__(Identifier([saoirse_id, "screens", "singleplayer"]), server, parent=parent, width=width, height=height, left=left, top=top, label="Singleplayer")

                def tick_content(self):
                    self.draw_image(Identifier(["resources", saoirse_id, "media", "pic1.png"]))
                    super().tick_content()

    class Screens:
        class SaoirseClientWorldScreen(ScreenWidget):
            def __init__(self, server, parent):
                super().__init__(Identifier([saoirse_id, "screens", "world"]), server, parent, title="")

        class SaoirseClientMainScreen(ScreenWidget):
            def __init__(self, server, parent=None, width=1200, height=800, left=0, top=0, title=""):
                super().__init__(Identifier([saoirse_id, "screens", "main"]), server, parent=parent, width=width, height=height, left=left, top=top, title=title)

            def draw(self):
                self.add_child(SaoirseClientWidgets.Widgets.Buttons.SaoirseClientSingleplayerButton(self.get_server()))
                super().draw()

            def tick_content(self):
                # pyglet.resource.image("resources/saoirse/media/pic1.png")
                self.draw_model(Identifier(["resources", saoirse_id, "media", "box1.obj"]), 10, 10, 2.2, 2, 2, 2)


class SaoirseClientMainWindowScreen(ScreenWidget):
    def __init__(self, headless=False):
        super().__init__(Identifier([saoirse_id, "screens", "main_window"]), None, self, title="Saoirse")

        self.render_que = []
        self.batch_2d = pyglet.graphics.Batch()
        self.batch_3d = pyglet.graphics.Batch()

        self.background_group = pyglet.graphics.OrderedGroup(0)
        self.midground_group = pyglet.graphics.OrderedGroup(1000)
        self.foreground_group = pyglet.graphics.OrderedGroup(10000)
        self.text_group = pyglet.graphics.OrderedGroup(1000000)

        self.draw()

        if headless:
            while True:
                self.tick()
                time.sleep(1 / self.get_ticks_per_second())
        else:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_CULL_FACE)

            self.window = pyglet.window.Window(width=self.get_width(), height=self.get_height(), resizable=True)

            @self.window.event
            def on_show():
                self.tick()

            @self.window.event
            def on_draw():
                self.tick()

            pyglet.app.run()

        self.on_removed()

    def draw(self):
        self.add_child(SaoirseClientWidgets.Screens.SaoirseClientMainScreen(self.get_server()))
        super().draw()

    def tick_content(self):
        self.window.clear()
        self.window.projection = pyglet.window.Projection3D()
        self.batch_3d.draw()
        self.window.projection = pyglet.window.Projection2D()
        self.batch_2d.draw()
        for obj in self.render_que:
            if hasattr(obj, "delete"):
                obj.delete()
        self.render_que.clear()

    def draw_image(self, ide, left, top, group=None):
        if group is None:
            group = self.foreground_group
        self.render_que.append(pyglet.sprite.Sprite(pyglet.resource.image(ide.get_file_path()), x=left, y=top, batch=self.batch_2d, group=group))

    def draw_model(self, ide, left=0, top=0, depth=0, rotX=0, rotY=0, rotZ=0, group=None):
        if group is None:
            group = self.foreground_group
        model = pyglet.resource.model(ide.get_file_path(), batch=self.batch_3d)
        model.rotation = rotX, rotY, rotZ
        model.translation = left, depth, top
        self.render_que.append(model)

    def draw_text(self, text, font_size, left=0, top=0, group=None, font_name="Exo 2 Regular"):
        if group is None:
            group = self.text_group
        self.render_que.append(pyglet.text.Label(
                          text=text,
                          font_size=font_size,
                          font_name=font_name,
                          x=left, y=top,
                          anchor_x='center', anchor_y='center', batch=self.batch_2d, group=group))

    def play_sound(self, ide):
        pyglet.resource.media(ide.get_file_path()).play()


def main(args):
    SaoirseClientMainWindowScreen()


if __name__ == "__main__":
    main(sys.argv)
