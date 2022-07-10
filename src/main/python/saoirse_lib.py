# This file is:
# src/main/python/saoirse_lib.py


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


from logging import getLogger
from typing import Union, Any
from dataclasses import dataclass
from os import path as ospath
from time import sleep
from enum import Enum


saoirse_lib_version = "0.0.1"
saoirse_id = "saoirse"
logger = getLogger(saoirse_id)


def expand_full_path(path_str: str) -> str:
    return ospath.expandvars(ospath.expanduser(path_str))


#class Logger():
#    class LogLevels(Enum):
#        LOG_LEVEL_INFO="info"
#        LOG_LEVEL_WARN="warn"
#        LOG_LEVEL_ERROR="error"
#
#    def log_msg(sender="Nobody", msg="This is a test message, please ignore it!", level=LogLevels.LOG_LEVEL_INFO, should_print=True):
#        formatted_msg = f"Log: Sender = {sender}: Level = {level}: Message =\n{msg}\n"
#        if should_print:
#            print(formatted_msg)
#        return formatted_msg


#class VarHolder():
#    pass


class MultiKeyDict(dict):
    def __setitem__(self, __k, __v):
        super().__setitem__(__k, __v)
        if isinstance(__k, (tuple)):
            if not hasattr(self, "extmap"):
                self.extmap = {}
            for subkey in __k:
                subkeymap = self.extmap.get(subkey, [])
                if __k not in subkeymap:
                    subkeymap.append(__k)
                    self.extmap[subkey] = subkeymap

    def __getitem__(self, __k):
        if __k in self.keys():
            return super().__getitem__(__k)
        elif hasattr(self, "extmap"):
            if __k in self.extmap.keys():
                return [self[subkey] for subkey in self.extmap.get(__k, [])]
        return super().__getitem__(__k)

    def get(self, __k, __default=None):
        if (__k in self.keys() or (hasattr(self, "extmap") and __k in self.extmap.keys())):
            return self[__k]
        return __default


class Identifier():
    def __init__(self, path: Union[str, list]="", delimiter: str=":", constant: bool=False):
        self.constant=constant
        self.set_delimiter(delimiter)
        self.set_path(path)

    def set_path(self, new_path_in: Union[str, list], update_self: bool=True):
        new_path = new_path_in
        if isinstance(new_path_in, list):
            for i, part in enumerate(new_path):
                if isinstance(part, str):
                    if self.get_delimiter() in part:
                        fixed = part.split(self.get_delimiter())
                        new_path.pop(i)
                        fixed.reverse()
                        for fixed_part in fixed:
                            new_path.insert(i, fixed_part)
        elif isinstance(new_path_in, str):
            new_path = new_path_in.split(self.get_delimiter())

        if update_self:
            self.path = new_path
            return self
        return Identifier(new_path)

    def set_delimiter(self, new_delimiter_in: str, update_self: bool=True):
        if isinstance(new_delimiter_in, str):
            new_delimiter = new_delimiter_in
        else:
            new_delimiter = "/"

        if update_self:
            self.delimiter = new_delimiter
            return self
        return Identifier(delimiter=new_delimiter)

    def get_path(self) -> list:
        return self.path

    def get_delimiter(self) -> str:
        return self.delimiter

    def get_path_str(self) -> str:
        return self.get_delimiter().join(self.get_path())

    def __str__(self):
        return self.get_path_str()

    def is_equal(self, other_in) -> bool:
        return isinstance(other_in, Identifier) and other_in.get_path() == self.get_path()

    def __eq__(self, other_in):
        return self.is_equal(other_in)

    def append(self, other_path_in: Union[str, list], update_self: Union[bool, None]=None):
        if update_self is None:
            update_self = not self.constant
        new_path = self.path.copy()
        if isinstance(other_path_in, list):
            new_path.extend(other_path_in)
        elif isinstance(other_path_in, str):
            new_path.append(other_path_in)
        else:
            logger.warning(f"Failed to append invalid path {other_path_in} to identifier {self} as it is not of type list or str!")
        if update_self:
            self.set_path(new_path)
            return self
        return Identifier(new_path, constant=self.constant)

    def extend(self, other_in, update_self: Union[bool, None]=None):
        if isinstance(other_in, Identifier):
            if update_self is None:
                update_self = not self.constant
            new_path = self.path.copy()
            new_path.extend(other_in.get_path())
            if update_self:
                self.set_path(new_path)
                return self
            return Identifier(new_path, constant=self.constant)

    def copy(self):
        return Identifier(self.get_path(), self.get_delimiter(), self.constant)

    def get_file_path(self) -> str:
        return ospath.join(*self.get_path())

    def get_id_from_str_list_or_id(ide: Union[str, list, Any]) -> Union[Any, None]:
        if isinstance(ide, str) or isinstance(ide, list):
            return Identifier(ide)
        elif isinstance(ide, Identifier):
            return ide
        return None


saoirse_resources_path = Identifier(["resources", saoirse_id], constant=True)
saoirse_media_path = saoirse_resources_path.append("media")
saoirse_images_path = saoirse_media_path.append("images")
saoirse_missing_image_path = saoirse_images_path.append("missing.png")
saoirse_audio_path = saoirse_media_path.append("audio")


class IdentifierEnum(Enum):
    def get_base_ide(self) -> Identifier:
        return Identifier()

    def get_identifier(self) -> Identifier:
        return self.get_base_ide().extend(Identifier.get_id_from_str_list_or_id(self.value), False)


class IdentifierObjGetterPair():
    def __init__(self, obj_in: Union[Any, None]=None, id_in: Identifier=Identifier()):
        self.obj = obj_in
        self.set_id(id_in)

    def is_equal(self, other_in):
        return isinstance(other_in, IdentifierObjGetterPair) and self.get_id().is_equal(other_in.get_id()) and self.get_obj() == other_in.get_obj()

    def copy(self):
        return IdentifierObjGetterPair(self.get_obj(), self.get_id().copy())

    def set_id(self, id_in: Union[str, list, Identifier]):
        self.ide = Identifier.get_id_from_str_list_or_id(id_in)

    def get_id(self) -> Union[Identifier, None]:
        return self.ide

    def get_obj_nocall(self):
        return self.obj

    def get_obj(self, *args, **kwargs):
        obj = self.get_obj_nocall()
        if callable(obj):
            ret_obj = obj(*args, **kwargs)
        else:
            ret_obj = obj
        if ret_obj is not None and hasattr(ret_obj, "set_id"):
            if callable(ret_obj.set_id):
                ret_obj.set_id(self.get_id())
        return ret_obj

    def __str__(self):
        return f"{self.get_id()} : {self.obj}"


class BaseRegistry():
    def __init__(self):
        self.entries = {}

    def get_entries_dict(self):
        return self.entries

    def get_entries(self):
        return self.entries.values()

    def get_entry(self, id_in):
        ide = Identifier.get_id_from_str_list_or_id(id_in)

        if self.contains_id(ide):
            return self.entries[ide.get_path_str()]
        return None

    def get_entries_under_category(self, category_id):
        category_entries = {}
        category_key = category_id.get_path_str()
        for key, obj in self.get_entries_dict().items():
            if key.startswith(category_key):
                category_entries[key] = obj
        return category_entries

    def contains_id(self, id_in):
        ide = Identifier.get_id_from_str_list_or_id(id_in)
        return ide.get_path_str() in self.get_entries_dict().keys()

    def register_id_obj(self, obj_in, id_in):
        if isinstance(id_in, Identifier):
            self.register_id_obj_pair(IdentifierObjGetterPair(obj_in, id_in), id_in)

    def register_id_obj_pair(self, id_obj_pair, ide = None):
        if isinstance(id_obj_pair, IdentifierObjGetterPair):
            if ide is None:
                ide = id_obj_pair.get_id()
            if isinstance(ide, Identifier):
                id_str = ide.get_path_str()
                if id_str in self.get_entries_dict().keys():
                    logger.warning(msg=f"Failed to register {id_obj_pair} as its id of {id_str} is alread registered!")
                else:
                    id_obj_pair.set_id(ide)
                    self.entries[id_str] = id_obj_pair
            else:
                logger.warning(msg=f"Failed to register {id_obj_pair} as its id of {ide} is not an Identifier!")
        else:
            logger.warning(msg=f"Failed to register {id_obj_pair} as it is not an IdentifierObjectPair!")


class ThreeDimensionalPosition():
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def get_origin():
        return ThreeDimensionalPosition(x = 0, y = 0, z = 0)

    def set_x(self, x=0):
       self.x = x

    def set_y(self, y=0):
       self.y = y

    def set_z(self, z=0):
       self.z = z

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def get_distance_from_other(self, other):
        return ((self.get_x() + other.get_x())**2 + (self.get_y() + other.get_y())**2 + (self.get_z() + other.get_z())**2)**0.5

    def get_distance_two_1d_points(primary, secondary):
        return secondary - primary

    def get_distance_from_other_x(self, other):
        return ThreeDimensionalPosition.get_distance_two_1d_points(self.get_x(), other.get_x())

    def get_distance_from_other_y(self, other):
        return ThreeDimensionalPosition.get_distance_two_1d_points(self.get_y(), other.get_y())

    def get_distance_from_other_z(self, other):
        return ThreeDimensionalPosition.get_distance_two_1d_points(self.get_z(), other.get_z())

    class Direction(Enum):
        def of_index(i=1):
            if i < -6 or i > 6:
                i %= 6
            if i == 0:
                i = 6
            return getattr(ThreeDimensionalPosition.Direction, abs(i))

        def get_opposite(self):
            if self == ThreeDimensionalPosition.Direction.UP:
                return ThreeDimensionalPosition.Direction.DOWN
            elif self == ThreeDimensionalPosition.Direction.DOWN:
                return ThreeDimensionalPosition.Direction.UP
            elif self == ThreeDimensionalPosition.Direction.FRONT:
                return ThreeDimensionalPosition.Direction.BACK
            elif self == ThreeDimensionalPosition.Direction.BACK:
                return ThreeDimensionalPosition.Direction.FRONT
            elif self == ThreeDimensionalPosition.Direction.LEFT:
                return ThreeDimensionalPosition.Direction.RIGHT
            return ThreeDimensionalPosition.Direction.LEFT

        def get_relative(self, front, up):
            if front == up or front.get_opposite() == up:
                return None
            dist_front = ThreeDimensionalPosition.Direction.FRONT.value - self.value
            dist_up = ThreeDimensionalPosition.Direction.UP.value - self.value
            for d in ThreeDimensionalPosition.Direction:
                if front.value - d.value == dist_front and up.value - d.value == dist_up:
                    return d
            return None

        FRONT = 1
        LEFT = 2
        BACK = 3
        UP = 4
        RIGHT = 5
        DOWN = 6

    def offset(self, x=0, y=0, z=0, update_self=False):
        new_x = self.get_x() + x
        new_y = self.get_y() + y
        new_z = self.get_z() + z
        if update_self:
            self.set_x(new_x)
            self.set_y(new_y)
            self.set_z(new_z)
            return self
        else:
            return ThreeDimensionalPosition(new_x, new_y, new_z)

    def offset_direction(self, direction, distance):
        if direction == ThreeDimensionalPosition.Direction.UP:
            return ThreeDimensionalPosition(self.get_x(), self.get_y(), self.get_z() + distance)

        elif direction == ThreeDimensionalPosition.Direction.DOWN:
            return ThreeDimensionalPosition(self.get_x(), self.get_y(), self.get_z() - distance)

        elif direction == ThreeDimensionalPosition.Direction.FRONT:
            return ThreeDimensionalPosition(self.get_x(), self.get_y() + distance, self.get_z())

        elif direction == ThreeDimensionalPosition.Direction.BACK:
            return ThreeDimensionalPosition(self.get_x(), self.get_y() - distance, self.get_z())

        elif direction == ThreeDimensionalPosition.Direction.RIGHT:
            return ThreeDimensionalPosition(self.get_x() + distance, self.get_y(), self.get_z())

        elif direction == ThreeDimensionalPosition.Direction.LEFT:
            return ThreeDimensionalPosition(self.get_x() - distance, self.get_y(), self.get_z())

        else:
            logger.warning(f"Could not get offset of ThreeDimensionalPosition by direction {direction} because it is not a Direction!")
            return self

    def get_intersection(edge, edge1, allow_edges=True):
        intersection = ThreeDimensionalPosition(
            (edge[0].get_x() + edge[1].get_x() + edge1[0].get_x() + edge1[1].get_x()) / 4,
            (edge[0].get_y() + edge[1].get_y() + edge1[0].get_y() + edge1[1].get_y()) / 4,
            (edge[0].get_z() + edge[1].get_z() + edge1[0].get_z() + edge1[1].get_z()) / 4,
        )
        if intersection.is_in_shaded(edge[0], edge[1], allow_edges) and intersection.is_in_shaded(edge1[0], edge1[1], allow_edges):
            return intersection
        else:
            return None


    def get_relative(self, other):
        return ThreeDimensionalPosition(self.get_x() + other.get_x(), self.get_y() + other.get_y(), self.get_z() + other.get_z())

    def approach(self, other, distance):
        steps = self.get_distance_from_other(other) / distance
        return self.get_relative(ThreeDimensionalPosition(self.get_distance_from_other_x(other) / steps, self.get_distance_from_other_y(other) / steps, self.get_distance_from_other_z(other) / steps))

    def trace(self, other, resolution=1):
        positions = [self]
        pos = self.approach(other, distance=resolution)
        while pos.get_distance_from_other(other) < resolution * 2:
            positions.append(pos)
            pos = pos.approach(other, distance=resolution)
        positions.append(other)
        return positions

    def get_nearest_direction_to_other_pos(self, other):
        dist_x = self.get_distance_from_other_x(other)
        dist_y = self.get_distance_from_other_y(other)
        dist_z = self.get_distance_from_other_z(other)

        dist_farthest = max(abs(dist_x), abs(dist_y), abs(dist_z))
        if dist_farthest == abs(dist_x):
            if dist_x < 0:
                return ThreeDimensionalPosition.Direction.LEFT
            return ThreeDimensionalPosition.Direction.RIGHT
        elif dist_farthest == abs(dist_y):
            if dist_y < 0:
                return ThreeDimensionalPosition.Direction.BACK
            return ThreeDimensionalPosition.Direction.FRONT
        else:
            if dist_z < 0:
                return ThreeDimensionalPosition.Direction.DOWN
            return ThreeDimensionalPosition.Direction.UP

    def is_point_in_shaded_1d(point, corner, corner1, allow_edges=True):
        lo, hi = min(corner, corner1), max(corner, corner1)
        return (allow_edges and (lo <= point <= hi)) or (lo < point < hi)

    def is_in_shaded(self, corner, corner1, allow_edges=True):
        return ThreeDimensionalPosition.is_point_in_shaded_1d(self.get_x(), corner.get_x(), corner1.get_x(), allow_edges) and ThreeDimensionalPosition.is_point_in_shaded_1d(self.get_y(), corner.get_y(), corner1.get_y(), allow_edges) and ThreeDimensionalPosition.is_point_in_shaded_1d(self.get_z(), corner.get_z(), corner1.get_z(), allow_edges)

    def is_inside_shape(self, shape, allow_edges=True):
        # I'm quite proud of this approach as I came up with it myself.
        # It works by checking whether self is between each pair of corners in shape while only considering the axis of the line connecting them.
        # (In theory) It works in any number of spatial dimensions. I'm pretty sure it can handle concave shapes, although I'm not 100% sure on that one so more testing is needed there.
        if isinstance(shape, ThreeDimensionalCornerHolder):
            edges = shape.get_edges()
            if len(edges) > 0:
                return all(self.is_in_shaded(edge[0], edge[1], allow_edges) for edge in edges)
        return False

    def find_closest(self, others=[]):
        if len(others) == 0:
            return None
        elif len(others) == 1:
            return others[0]
        else:
            least_dist = None
            closest = None
            for other in others:
                dist = self.get_distance_from_other(other)
                if least_dist is None:
                    least_dist = dist
                    closest = other
                elif dist < least_dist:
                    least_dist = dist
                    closest = other
            return closest

    class Axies(Enum):
        X = "x"
        Y = "y"
        Z = "z"

    def copy(self):
        return ThreeDimensionalPosition(self.get_x(), self.get_y(), self.get_z())

    def to_dict(self):
        return {ThreeDimensionalPosition.Axies.X.value: self.get_x(), ThreeDimensionalPosition.Axies.Y.value: self.get_y(), ThreeDimensionalPosition.Axies.Z.value: self.get_z()}

    def to_str(self):
        return f"x{self.get_x()}y{self.get_y()}z{self.get_z()}"

    def of_dict(pos_dict):
        return ThreeDimensionalPosition(pos_dict.get(ThreeDimensionalPosition.Axies.X.value, 0), pos_dict.get(ThreeDimensionalPosition.Axies.Y.value, 0), pos_dict.get(ThreeDimensionalPosition.Axies.Z.value, 0))

    def of_str(pos_str):
        x = float(pos_str[pos_str.find("x")+1:pos_str.find("y")])
        y = float(pos_str[pos_str.find("y")+1:pos_str.find("z")])
        z = float(pos_str[pos_str.find("z")+1:])
        return ThreeDimensionalPosition(x, y, z)

    def __str__(self):
        return self.to_str()

    def __eq__(self, other):
        return self.get_x() == other.get_x() and self.get_y() == other.get_y() and self.get_z() == other.get_z()


class ActionIds(Enum):
    MAIN = "main"
    SECONDARY = "secondary"


class TickableObject():
    def tick(self):
        pass

    def get_max_tickrate(self):
        return 64


class SaveableObject():
    persist_data_key = "persist_data"
    def __init__(self):
        self.persist_data = {}

    def set_persist_data(self, data: Union[dict, MultiKeyDict]):
        self.persist_data = data
        return self

    def get_persist_data(self) -> Union[dict, MultiKeyDict]:
        return self.persist_data

    def set_data(self, data: Union[dict, MultiKeyDict]):
        if self.persist_data_key in data.keys():
            persist_data = data.get(self.persist_data_key)
            if isinstance(persist_data, (dict, MultiKeyDict)):
                self.set_persist_data(persist_data)
        return self

    def get_data(self) -> Union[dict, MultiKeyDict]:
        return {self.persist_data_key: self.get_persist_data()}

    def __str__(self):
        return str(self.get_data())

    def __eq__(self, other):
        if type(self) == type(other) and hasattr(other, "get_data"):
            if callable(other.get_data):
                return self.get_data() == other.get_data()
        return False


class InteractableObject():
    def get_action_by_id(self, ide, actor):
        return None

    def get_main_action(self, actor):
        return self.get_action_by_id(ActionIds.MAIN, actor)

    def get_secondary_action(self, actor):
        return self.get_action_by_id(ActionIds.SECONDARY, actor)


class MainGameObject(SaveableObject, TickableObject, InteractableObject):
    def __init__(self, ide: Identifier, server):
        super().__init__()
        self.ide = ide
        self.set_server(server)
        self.on_created()

    def set_server(self, server):
        self.server = server

    def set_removed(self, removed: bool=True):
        self.removed = removed
        return self

    def on_created(self):
        self.set_removed(False)
        return self

    def on_removed(self):
        return self.set_removed(True)

    def get_server(self):
        return self.server

    def get_id(self) -> Identifier:
        return self.ide


class ThreeDimensionalCornerHolder():
    def get_faces(self) -> list:
        return []

    def get_corners(self) -> list:
        corners = []
        for face in self.get_faces():
            for corner in face.get_corners():
                if corner not in corners:
                    corners.append(corner)
        return corners

    def get_edges(self) -> list:
        edges = []
        for face in self.get_faces():
            edge = []
            for corner in face.get_corners():
                edge.append(corner)
                if len(edge) > 1:
                    edges.append(edge)
                    edge = [corner]
            if len(edge) == 1 and len(self.get_corners()) > 1:
                edge.append(self.get_corners()[0])
                edges.append(edge)
        return edges

    def is_inside_shape(self, shape, allow_edges: bool=True) -> bool:
        if isinstance(shape, (ThreeDimensionalShape, ThreeDimensionalShape.ThreeDimensionalBox, ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace)):
            return all(corner.is_inside_shape(shape, allow_edges) for corner in self.get_corners())
        else:
            logger.warning(f"Could not determine if {self} is inside shape {shape} because it is not of type ThreeDimensionalShape, ThreeDimensionalBox, or ThreeDimensionalFace!")
            return False

class ThreeDimensionalShape(ThreeDimensionalCornerHolder):
    def __init__(self, boxes=[]):
        self.set_boxes(boxes)

    def get_contained_positions(self, resolution=1) -> list:
        positions = []
        for box in self.get_boxes():
            for pos in box.get_contained_positions(resolution=resolution):
                if pos not in positions:
                    positions.append(pos)
        return positions

    def set_boxes(self, boxes: list=[]):
        self.boxes = boxes

    def get_boxes(self) -> list:
        return self.boxes

    def remove_empty(self):
        for box in self.get_boxes():
            if len(box.get_faces()) == 0:
                self.boxes.remove(box)
            else:
                box.remove_empty()

    def get_faces(self) -> list:
        faces = []
        for box in self.get_boxes():
            faces.extend(box.get_faces())
        return faces

    def add_box(self, box):
        self.boxes.append(box)

    def merge(self, other, offset_x=0, offset_y=0, offset_z=0, update_self=True):
        if isinstance(other, ThreeDimensionalShape):
            if len(other.get_boxes()) > 0:
                if offset_x != 0 or offset_y != 0 or offset_z != 0:
                    other = other.move(offset_x, offset_y, offset_z, False)
                other_boxes = other.get_boxes().copy()
            else:
                other_boxes = []
            other_boxes.extend(self.get_boxes())
            if not update_self:
                return ThreeDimensionalShape(other_boxes)
            else:
                self.set_boxes(other_boxes)
                return self
        else:
            logger.warning(f"Could not merge shape {self} with other object {other} because other is not a ThreeDimensionalShape! ")
            return self

    def move(self, offset_x=0, offset_y=0, offset_z=0, update_self=True):
        other_boxes = self.get_boxes().copy()
        for box in other_boxes:
            box.move(offset_x, offset_y, offset_z)
        if update_self:
            self.boxes = other_boxes
            return self
        else:
            return ThreeDimensionalShape(other_boxes)

    def copy(self):
        return ThreeDimensionalShape([box.copy() for box in self.get_boxes()])

    class ThreeDimensionalBox(ThreeDimensionalCornerHolder):
        def __init__(self, faces=[]):
            self.set_faces(faces)

        def copy(self):
            return ThreeDimensionalShape.ThreeDimensionalBox([face.copy() for face in self.get_faces()])

        def rectangular_prism(lft, rft, rfb, lfb, lbt, rbt, rbb, lbb, texfront=None, texback=None, texleft=None, texright=None, textop=None, texbottom=None, tex_default=saoirse_missing_image_path):
            if texfront is None:
                texfront=tex_default
            if texback is None:
                texback=tex_default
            if texleft is None:
                texleft=tex_default
            if texright is None:
                texright=tex_default
            if textop is None:
                textop=tex_default
            if texbottom is None:
                texbottom=tex_default

            return ThreeDimensionalShape.ThreeDimensionalBox(faces=[
                ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[lbt, rbt, rbb, lbb], texture=texback), # Back
                ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[lbt, rbt, rft, lft], texture=textop), # Top
                ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[rft, rbt, rbb, rfb], texture=texright), # Right
                ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[lbt, lft, lfb, lbb], texture=texleft), # Left
                ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[lbb, rbb, rfb, lfb], texture=texbottom), # Bottom
                ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[lft, rft, rfb, lfb], texture=texfront), # Front
            ])

        def set_faces(self, faces):
            self.faces = faces

        def get_faces(self):
            return self.faces

        def remove_empty(self):
            for face in self.get_faces():
                if len(face.get_corners()) == 0:
                    self.faces.remove(face)

        def move(self, offset_x=0, offset_y=0, offset_z=0, update_self=True):
            other_faces = self.get_faces().copy()
            for face in other_faces:
                face.move(offset_x, offset_y, offset_z)
            if update_self:
                self.set_faces(other_faces)
                return self
            else:
                return ThreeDimensionalShape.ThreeDimensionalBox(other_faces)

        def get_wireframe_positions(self, resolution=1):
            positions = self.get_corners().copy()
            for i, corner in enumerate(positions):
                for corner1 in positions[i:]:
                    for pos in corner.trace(corner1, resolution=resolution):
                        if pos not in positions:
                            positions.append(pos)
            return positions

        def get_contained_positions(self, resolution=1):
            # This works because it traces all points in self's wireframe, filling it
            return ThreeDimensionalShape.ThreeDimensionalBox(faces=[ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[corner]) for corner in self.get_wireframe_positions(resolution=resolution)]).get_wireframe_positions()

        class ThreeDimensionalFace(ThreeDimensionalCornerHolder):
            def __init__(self, corners=[], texture=None, shade_red=0, shade_green=0, shade_blue=0, shade_alpha=0):
                self.set_corners(corners)
                self.set_texture(texture)
                self.set_shade_red(shade_red)
                self.set_shade_green(shade_green)
                self.set_shade_blue(shade_blue)
                self.set_shade_alpha(shade_alpha)

            def set_corners(self, corners=[]):
                self.corners = corners
                # self.sort_corners()

            #def sort_corners(self): #FIXME: Currently doesn't give the correct order
            #    current_corners = self.corners.copy()
            #    corners = []
            #    if len(current_corners) > 0:
            #        corner = current_corners[0]
            #        current_corners.remove(corner)
            #        corners.append(corner)
            #        while True:
            #            if len(current_corners) > 1:
            #                corner = corner.find_closest(current_corners)
            #                corners.append(corner)
            #                current_corners.remove(corner)
            #            else:
            #                if len(current_corners) > 0:
            #                    corners.append(current_corners[0])
            #                break
            #    self.corners = corners

            def get_overlaps(self, others=[], cam_pos=ThreeDimensionalPosition.get_origin()):
                overlaps_self = []
                overlaps_others = []
                new_others = others.copy()
                for other in new_others:
                    if other.is_inside_shape(self):
                        overlaps_others.append(self)
                        new_others.remove(other)
                    elif self.is_inside_shape(other):
                        overlaps_self.append(other)
                    else:
                        cut_corners_self = []
                        cut_corners_other = []
                        other_edges = other.get_edges().copy()
                        for edge in self.get_edges():
                            for edge1 in other_edges:
                                cut_corner = ThreeDimensionalPosition.get_intersection(edge, edge1)
                                if cut_corner is not None:
                                    # if cut_corner.is_inside_shape(self) or cut_corner.is_inside_shape(other):
                                        cam_dist_self = edge[0].get_distance_from_other(cam_pos)
                                        cam_dist_other = edge1[0].get_distance_from_other(cam_pos)
                                        cam_dist_self_y = edge[0].get_y() - cam_pos.get_y()
                                        cam_dist_other_y = edge1[0].get_y() - cam_pos.get_y()
                                        if cam_dist_self < cam_dist_other and cam_dist_self_y < cam_dist_other_y:
                                            if edge[0] not in cut_corners_other:
                                                cut_corners_other.append(edge[0].copy())
                                            if cut_corner not in cut_corners_other:
                                                cut_corners_other.append(cut_corner)
                                        elif cam_dist_self > cam_dist_other and cam_dist_self_y > cam_dist_other_y:
                                            if edge1[0] not in cut_corners_self:
                                                cut_corners_self.append(edge1[0].copy())
                                            if cut_corner not in cut_corners_self:
                                                cut_corners_self.append(cut_corner)
                        if len(cut_corners_other) > 1:
                            # if overlaps.is_inside_shape(self) or overlaps.is_inside_shape(other):
                            new_others.remove(other)
                            overlaps_others.append(ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(cut_corners_other, self.get_texture()))
                        if len(cut_corners_self) > 1:
                            #overlaps = ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(cut_corners_self, other.get_texture())
                            #if overlaps.is_inside_shape(self) or overlaps.is_inside_shape(other):
                            #    overlaps_self.append(overlaps)
                            overlaps = ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(cut_corners_self, other.get_texture())
                            overlaps_self.append(overlaps)
                            new_others.append(overlaps)
                return [overlaps_self, overlaps_others, new_others]

            def get_corners(self):
                return self.corners

            def get_faces(self):
                return [self]

            def set_texture(self, texture):
                self.texture = texture

            def get_texture(self):
                return self.texture

            def set_shade_red(self, shade):
                self.shade_red = shade

            def get_shade_red(self):
                return self.shade_red

            def set_shade_green(self, shade):
                self.shade_green = shade

            def get_shade_green(self):
                return self.shade_green

            def set_shade_blue(self, shade):
                self.shade_blue = shade

            def get_shade_blue(self):
                return self.shade_blue

            def set_shade_alpha(self, shade):
                self.shade_alpha = shade

            def get_shade_alpha(self):
                return self.shade_alpha

            def move(self, offset_x=0, offset_y=0, offset_z=0, update_self=True):
                other_corners = self.get_corners().copy()
                for corner in other_corners:
                    corner.offset(offset_x, offset_y, offset_z, True)
                if update_self:
                    self.set_corners(other_corners)
                    return self
                else:
                    return ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(other_corners)

            def copy(self):
                texture = self.get_texture()
                if hasattr(texture, "copy"):
                    texture = texture.copy()
                return ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace([corner.copy() for corner in self.get_corners()], texture)


class SpaceGameObject(MainGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), space=None):
        super().__init__(ide, server)

        self.set_pos(pos)
        self.set_current_space(space)

    def get_model(self):
        return None

    def get_collision_shape(self):
        return self.get_model()

    def set_pos(self, pos):
        should_set = True
        has_pos = hasattr(self, "pos")
        if has_pos:
            should_set = self.pos != pos
        if should_set:
            if has_pos and self.get_current_space() is not None and self.get_current_space() != self:
                self.get_current_space().remove_obj_at_pos(self.pos, [self])
                self.pos = pos
                self.get_current_space().add_obj_at_pos(pos, self)
            else:
                self.pos = pos
        return self

    def get_pos(self):
        return self.pos

    def set_current_space(self, space):
        self.space = space
        return self

    def get_current_space(self):
        return self.space

    def has_gravity(self):
        return True

    def get_mass(self):
        return 1


class Item(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), space=None):
        super().__init__(ide, server, pos, space)

    def get_model(self):
        return Item.BaseItemShape()

    class BaseItemShape(ThreeDimensionalShape):
        def __init__(self, boxes=[]):
            boxes1 = boxes.copy()
            if len(boxes1) == 0:
                boxes1.append(
                    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 1), ThreeDimensionalPosition(1, 0, 1), ThreeDimensionalPosition(1, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 1, 1), ThreeDimensionalPosition(1, 1, 1), ThreeDimensionalPosition(1, 1, 0), ThreeDimensionalPosition(0, 1, 0)),
                )
            super().__init__(boxes=boxes1)


class Tile(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), space=None):
        super().__init__(ide, server, pos, space)

    def get_model(self):
        return Tile.BaseTilehape()

    class BaseTilehape(ThreeDimensionalShape):
        def __init__(self, boxes=[]):
            boxes1 = boxes.copy()
            if len(boxes1) == 0:
                boxes1.append(
                    ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 1), ThreeDimensionalPosition(1, 0, 1), ThreeDimensionalPosition(1, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 1, 1), ThreeDimensionalPosition(1, 1, 1), ThreeDimensionalPosition(1, 1, 0), ThreeDimensionalPosition(0, 1, 0)),
                )
            super().__init__(boxes=boxes1)


class Fluid(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), space=None):
        super().__init__(ide, server, pos, space)


class Entity(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), space=None):
        super().__init__(ide, server, pos, space)

    def get_agenda(self):
        return []


class ThreeDimensionalSpace(SpaceGameObject):
    def __init__(self, ide, server):
        super().__init__(ide, server, ThreeDimensionalPosition.get_origin(), self)

        self.space_game_obj_sets = MultiKeyDict()
        self.obj_lock = False

    def get_server(self):
        return self.server

    def generate_terrain_at_pos(self, pos=ThreeDimensionalPosition.get_origin()):
        pass

    def get_gravity_speed(self, m1, m2, distance):
        return ((self.get_g_constant() * m1 * m2) / (distance**2)) / self.get_server().get_max_tickrate()

    def get_objects_dict(self):
        return self.space_game_obj_sets

    def get_objects(self):
        return self.get_objects_dict().values()

    def get_obj_sets(self):
        return [[self.get_objects_dict().get(key) for key in self.get_obj_keys_at_pos(pos_key)] for pos_key in self.get_obj_pos_keys()]

    def get_g_constant(self):
        # return 6.67 * (10**-11)
        return 1

    def get_obj_pos_keys(self):
        return [key[:key[0].find("_")] for key in self.get_objects_dict().keys()]

    def get_obj_keys_at_pos(self, pos):
        pos_str = str(pos)
        return [key for key in self.space_game_obj_sets.keys() if pos_str in str(key)]

    def add_obj_at_pos(self, pos, obj, additional_keys=[]):
        self.obj_lock = True
        obj.set_pos(pos)
        obj.set_current_space(self)
        key = (pos.to_str(), str(len(self.get_obj_keys_at_pos(pos))), *additional_keys)
        self.space_game_obj_sets[key] = obj
        self.obj_lock = False
        return self

    def remove_obj_at_pos(self, pos, check_objects=[]):
        self.obj_lock = True
        if len(check_objects) > 0:
            for key in self.get_obj_keys_at_pos(pos):
                obj = self.get_objects_dict().get(key)
                if obj == check_objects:
                    self.get_objects_dict.pop(key)
                elif isinstance(check_objects, list):
                    if obj in check_objects:
                        self.get_objects_dict.pop(key)
        self.obj_lock = False
        return self

    def replace_object_at_pos(self, pos, old_space_game_object, new_space_game_object):
        self.remove_obj_at_pos(pos, old_space_game_object)
        self.add_obj_at_pos(pos, new_space_game_object)
        return self

    def get_object_set_at_pos(self, pos, check_objects=[]):
        self.obj_lock = True
        obj_set = self.get_objects_dict().get(pos.to_str(), [])
        if len(check_objects) == 0:
            return obj_set
        objects = []
        for obj in obj_set:
            if obj in check_objects:
                objects.append(obj)
        self.obj_lock = False
        return objects

    def get_object_sets_in_shape(self, shape, check_objects=[], allow_edges=True):
        self.obj_lock = True
        obj_sets = []
        handled_poses = []
        for pos_key in self.get_objects_dict().keys():
            if isinstance(pos_key, tuple):
                pos_key = pos_key[0]
            obj_set_pos = ThreeDimensionalPosition.of_str(pos_key)
            if obj_set_pos not in handled_poses:
                handled_poses.append(obj_set_pos)
                if obj_set_pos.is_inside_shape(shape, allow_edges):
                    obj_set = self.get_object_set_at_pos(obj_set_pos)
                    if len(obj_set) > 0:
                        if len(check_objects) == 0:
                            obj_sets.append(obj_set)
                        else:
                            obj_set1 = []
                            for obj in obj_set:
                                if obj in check_objects:
                                    obj_set1.append(obj)
                            if len(obj_set1) > 0:
                                obj_sets.append(obj_set1)
        self.obj_lock = False
        return obj_sets

    def get_objects_in_shape(self, shape, check_objects=[], allow_edges=True):
        objects = []
        for obj_set in self.get_object_sets_in_shape(shape, check_objects, allow_edges):
            objects.extend(obj_set)
        return objects

    def get_nearest_obj_set_to_pos(self, pos, exclusions=[]):
        self.obj_lock = True
        if len(self.get_objects_dict().keys()) > 0:
            nearest_pos = ThreeDimensionalPosition.of_str(list(self.get_objects_dict().keys())[0])
            if len(self.get_obj_sets()) > 1:
                nearest_dist = pos.get_distance_from_other(nearest_pos)
                if nearest_dist > 0:
                    for key in self.get_objects_dict().keys():
                        if len(self.get_object_set_at_pos(nearest_pos, exclusions)) > 0:
                            check_pos = ThreeDimensionalPosition.of_str(key)
                            check_dist = pos.get_distance_from_other(check_pos)
                            if check_dist < nearest_dist:
                                nearest_pos = check_pos
                                nearest_dist = check_dist
            self.obj_lock = False
            return self.get_object_set_at_pos(nearest_pos, exclusions), nearest_pos
        self.obj_lock = False
        return None, None

    def get_heaviest_objects_in_set(self, obj_set):
        self.obj_lock = True
        if len(obj_set) > 0:
            heaviest = []
            mass = 0
            for obj in obj_set:
                obj_mass = obj.get_mass()
                if obj_mass > mass:
                    mass = obj_mass
                    heaviest = [obj]
                elif obj_mass == mass:
                    heaviest.append(obj)
            self.obj_lock = False
            return heaviest
        self.obj_lock = False
        return None

    def get_mass_of_set(self, obj_set):
        if len(obj_set) > 0:
            return sum([obj.get_mass() for obj in obj_set])
        return 0

    def tick_object_gravity(self, obj):
        if len(self.get_obj_sets()) > 1 and obj.has_gravity():
            nearest_set, nearest_pos = self.get_nearest_obj_set_to_pos(obj.get_pos(), [obj])
            if nearest_set is not None and nearest_pos != obj.get_pos():
                if len(nearest_set) > 0:
                    mass = self.get_mass_of_set(nearest_set)
                    if mass > 0:
                        obj.set_pos(obj.get_pos().approach(nearest_pos, self.get_gravity_speed(obj.get_mass(), mass, nearest_pos.get_distance_from_other(obj.get_pos()))))
        return self

    def tick(self):
        if self.obj_lock:
            while self.obj_lock:
                sleep(0.0001)
        for obj_set in self.get_obj_sets():
            for obj in obj_set:
                obj.tick()
                self.tick_object_gravity(obj)
        return self

    @dataclass(frozen=True)
    class SaveDataKeys:
        IDE = "ide"
        POS = "pos"
        DATA = "data"
        OBJECTS = "objects"

    def set_data(self, data):
        if ThreeDimensionalSpace.SaveDataKeys.OBJECTS in data.keys():
            objects_data = data.get(ThreeDimensionalSpace.SaveDataKeys.OBJECTS)
            for obj_set_data in objects_data.values():
                for obj_data in obj_set_data:
                    if ThreeDimensionalSpace.SaveDataKeys.IDE in obj_data.keys() and ThreeDimensionalSpace.SaveDataKeys.POS in obj_data.keys():
                        ide = Identifier(obj_data[ThreeDimensionalSpace.SaveDataKeys.IDE])
                        obj_pair = self.get_server().get_registry().get_entry(ide)
                        if obj_pair is not None:
                            obj = obj_pair.get_obj()
                            if obj is not None:
                                pos = ThreeDimensionalPosition.of_dict(obj_data[ThreeDimensionalSpace.SaveDataKeys.POS])
                                obj.set_pos(pos)
                                obj.set_data(obj_data.get(ThreeDimensionalSpace.SaveDataKeys.DATA))
                                self.add_obj_at_pos(pos, obj)

    def get_data(self):
        data = super().get_data()
        objects_data = {}
        for i, obj in self.get_objects_dict().items():
            if obj is not None:
                ide_path_str = obj.get_id().get_path_str()
                pos_dict = obj.get_pos().to_dict()
                saved_data = obj.get_data()
                obj_data = {}
                obj_data[ThreeDimensionalSpace.SaveDataKeys.IDE] = ide_path_str
                obj_data[ThreeDimensionalSpace.SaveDataKeys.POS] = pos_dict
                obj_data[ThreeDimensionalSpace.SaveDataKeys.DATA] = saved_data
                objects_data[str(i)] = obj_data
        data[ThreeDimensionalSpace.SaveDataKeys.OBJECTS] = objects_data
        return data


class BaseServer(MainGameObject):
    spaces_key = "spaces"
    spawn_space_key = "spawn_space"
    spawn_pos_key = "spawn_pos"

    def __init__(self, ide, registry):
        super().__init__(ide, self)

        self.registry = registry
        self.registry.server = self
        self.spaces = {}

    def get_registry(self):
        return self.registry

    def get_spaces_dict(self):
        return self.spaces

    def get_spaces(self):
        return list(self.get_spaces_dict().values())

    def add_space(self, space):
        self.spaces[space.get_id().get_path_str()] = space
        return self

    def get_space(self, ide):
        return self.spaces.get(ide.get_path_str(), None)

    def set_spawn_space(self, space_id):
        self.spawn_space_id = space_id

    def set_spawn_pos(self, pos):
        self.spawn_pos = pos

    def get_spawn_space_id(self):
        return self.spawn_space_id

    def get_spawn_space(self):
        return self.get_spaces_dict().get(self.get_spawn_space_id)

    def get_spawn_pos(self):
        return self.spawn_pos

    def tick(self):
        for space in self.get_spaces():
            space.tick()
        return self

    def set_data(self, data):
        super().set_data(data)
        if self.spaces_key in data.keys():
            spaces_data = data.get(self.spaces_key)
            for space_key in spaces_data.keys():
                space_ide = Identifier(space_key)
                if space_key not in self.get_spaces_dict().keys():
                    self.add_space(self.get_registry().get_entry(space_ide).get_obj())
                self.get_space(space_ide).set_data(spaces_data.get(space_key))
        if self.spawn_space_key in data.keys():
            self.set_spawn_space(Identifier(data.get(self.spawn_space_key)))
        if self.spawn_pos_key in data.keys():
            self.set_spawn_pos(ThreeDimensionalPosition.of_dict(data.get(self.spawn_pos_key)))
        return self

    def get_data(self):
        data = super().get_data()
        spaces_data = {}
        for space in self.get_spaces_dict().values():
            spaces_data[space.get_id().get_path_str()] = space.get_data()
        data[self.spaces_key] = spaces_data
        data[self.spawn_space_key] = self.get_spawn_space_id().get_path()
        data[self.spawn_pos_key] = self.get_spawn_pos().to_dict()
        return data

