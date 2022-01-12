# This file is:
# src/python/saoirse_client.py

import time, sys, pyglet
from saoirse_base import Identifier, MainGameObject, InteractableGameObject
from saoirse_server import saoirse_id


class SaoirseClientScreenWidget(MainGameObject, InteractableGameObject):
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

    def draw_text(self, text, size, left=0, top=0):
        self.get_parent().draw_text(size, text, self.get_left() + left, self.get_top() + top)

    def play_sound(self, ide):
        self.get_parent().play_sound(ide)

    def draw(self):
        pass

    def tick_content(self):
        pass

    def tick(self):
        self.tick_content()


class SaoirseClientButton(SaoirseClientScreenWidget):
    def __init__(self, ide, server, parent=None, width=20, height=20, left=0, top=0, label=""):
        super().__init__(ide, server, parent=parent, width=width, height=height, left=left, top=top)

        self.label = label

    def get_label(self):
        return self.label

    def tick_content(self):
        self.draw_text(self.get_label(), self.get_width()/2, self.get_left() + self.get_width()/4, self.get_top() + self.get_height()/4)


class SaoirseScreen(SaoirseClientScreenWidget):
    def __init__(self, ide, server, parent=None, width=1200, height=800, left=0, top=0, title=""):
        super().__init__(ide, server, parent, width, height, left, top)

        self.title = title
        self.children = {}

    def get_title(self):
        return self.title

    def get_children(self):
        return self.children

    def add_child(self, child):
        child.set_parent(self)
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


class SaoirseClientWorldScreen(SaoirseScreen):
    def __init__(self, server, parent):
        super().__init__(Identifier([saoirse_id, "screens", "world"]), server, parent, title="")


class SaoirseClientSingleplayerButton(SaoirseClientButton):
    def __init__(self, server, parent=None, width=50, height=20, left=50, top=50):
        super().__init__(Identifier([saoirse_id, "screens", "singleplayer"]), server, parent=parent, width=width, height=height, left=left, top=top, label="Singleplayer")

    def tick_content(self):
        self.draw_image(Identifier(["resources", saoirse_id, "media", "pic1.png"]), -self.left, -self.top)
        super().tick_content()


class SaoirseClientMainScreen(SaoirseScreen):
    def __init__(self, server, parent=None, width=1200, height=800, left=0, top=0, title=""):
        super().__init__(Identifier([saoirse_id, "screens", "main"]), server, parent=parent, width=width, height=height, left=left, top=top, title=title)

    def draw(self):
        self.add_child(SaoirseClientSingleplayerButton(self.get_server()))
        super().draw()


class SaoirseClientMainWindowScreen(SaoirseScreen):
    def __init__(self):
        super().__init__(Identifier([saoirse_id, "screens", "main_window"]), None, self, title="Saoirse")

        self.draw()

        self.window = pyglet.window.Window(width=self.get_width(), height=self.get_height())

        @self.window.event
        def on_draw():
            self.window.clear()
            self.tick()

        pyglet.app.run()

        self.on_removed()

    def draw(self):
        self.add_child(SaoirseClientMainScreen(self.get_server()))
        super().draw()

    def tick(self):
        super().tick()
        time.sleep(1 / self.get_ticks_per_second())

    def tick_content(self):
        pass
        #self.draw_image(Identifier(["resources", saoirse_id, "media", "pic1.png"]), 0, 0)

    def draw_image(self, ide, left, top):
        pyglet.resource.image(ide.get_file_path()).blit(left, top)

    def draw_text(self, text, size, left, top):
        pyglet.text.Label(text,
                          font_name='Exo 2 Regular',
                          font_size=size,
                          x=left, y=top,
                          anchor_x='left', anchor_y='top').draw()

    def play_sound(self, ide):
        pyglet.resource.media(ide.get_file_path()).play()


def main(args):
    SaoirseClientMainWindowScreen()


if __name__ == "__main__":
    main(sys.argv)
