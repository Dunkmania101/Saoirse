# This file is:
# src/python/saoirse_server.py


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


import sys, time #, uuid
from os import path, mkdir, mknod
#from msgpack import pack as mpack, unpack as munpack
# from json import dumps as jdumps, loads as jloads
from pickle import dump as pkldump, load as pklload
from saoirse_base import logger, expand_full_path, Identifier, IdentifierEnum, BaseRegistry, Item, ThreeDimensionalPosition, ThreeDimensionalSpace, Tile, Fluid, Entity, BaseServer, ThreeDimensionalShape


saoirse_id = "saoirse"


class SaoirseIdentifierEnum(IdentifierEnum):
    def get_base_ide(self):
        return Identifier(saoirse_id)


class Items:
    class Equipment:
        class Tools:
            class BaseToolItem(Item):
                integrity_key = "integrity"

                def __init__(self, ide, server, pos=..., space=None, integrity=100):
                    super().__init__(ide, server, pos=pos, space=space)

                    self.set_integrity(integrity)

                def set_integrity(self, integrity=100):
                    self.integrity = integrity

                def get_integrity(self):
                    return self.integrity

                def set_data(self, data):
                    if self.integrity_key in data.keys():
                        self.set_integrity(data.get(self.integrity_key))
                    return super().set_data(data)

                def get_data(self):
                    data = super().get_data()
                    data[self.integrity_key] = self.get_integrity()
                    return data

            class HatchetItem(BaseToolItem):
                def __init__(self, ide, server, pos=..., space=None, integrity=100):
                    super().__init__(ide, server, pos=pos, space=space, integrity=integrity)

                def get_model(self):
                    return Items.Equipment.Tools.HatchetItem.HatchetItemShape()

                class HatchetItemShape(ThreeDimensionalShape):
                    def __init__(self, boxes=[]):
                        boxes1 = boxes.copy()
                        boxes1.extend([
                            ThreeDimensionalShape.ThreeDimensionalBox(faces=[ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0.05, 0, 0), ThreeDimensionalPosition(0, 0.05, 0), ThreeDimensionalPosition(0.05, 0.05, 0)], texture=Identifier("resources/saoirse/media/pic1.png")), ThreeDimensionalShape.ThreeDimensionalBox.ThreeDimensionalFace(corners=[ThreeDimensionalPosition(0, 0, 0.25), ThreeDimensionalPosition(0.05, 0, 0.25), ThreeDimensionalPosition(0, 0.05, 0.25), ThreeDimensionalPosition(0.5, 0.5, 0.5), ThreeDimensionalPosition(3, 5, 1)], texture=Identifier("resources/saoirse/media/pic1.png"))]),
                        ])
                        super().__init__(boxes=boxes1)


class Entities:
    class PlayerEntity(Entity):
        def __init__(self, server, ide=None):
            super().__init__(ide=SaoirseRegistry.Identifiers.ENTITIES.player.get_identifier(), server=server)

            self.set_player_id(ide=ide)

        def set_player_id(self, ide=None):
            self.player_id = ide

        def get_player_id(self):
            return self.player_id


class Spaces:
    class NormalSpace(ThreeDimensionalSpace):
        def __init__(self, server):
            super().__init__(SaoirseRegistry.Identifiers.SPACES.normal.get_identifier(), server)

        def generate_terrain_at_pos(self, pos=ThreeDimensionalPosition.get_origin()):
            # TEST - adding objects
            if pos == ThreeDimensionalPosition.get_origin():
                self.add_object_at_pos(pos.get_relative(ThreeDimensionalPosition(3, 5, 4)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.canvas_sheet.get_identifier()).get_obj())
                self.add_object_at_pos(pos.get_relative(ThreeDimensionalPosition(4, 9, 4)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.canvas_thread.get_identifier()).get_obj())
                self.add_object_at_pos(pos.get_relative(ThreeDimensionalPosition(5, 3, 4)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.hatchet.get_identifier()).get_obj())

    class GhostlySpace(ThreeDimensionalSpace):
        def __init__(self, server):
            super().__init__(SaoirseRegistry.Identifiers.SPACES.ghostly.get_identifier(), server)

        def generate_terrain_at_pos(self, pos=ThreeDimensionalPosition.get_origin()):
            # TEST - adding objects
            if pos == ThreeDimensionalPosition.get_origin():
                self.add_object_at_pos(pos.get_relative(ThreeDimensionalPosition(9, 25, 4500)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.ironwood_stick.get_identifier()).get_obj())


class SaoirseRegistry(BaseRegistry):
    def __init__(self, server):
        super().__init__()

        self.server = server

        self.register_items()
        self.register_tiles()
        self.register_fluids()
        self.register_entities()
        self.register_spaces()

    def get_server(self):
        return self.server

    def register_items(self):
        for idee in SaoirseRegistry.Identifiers.ITEMS:
            ide = idee.get_identifier()
            item_obj = None
            if ide == SaoirseRegistry.Identifiers.ITEMS.hatchet.get_identifier():
                item_obj = lambda : Items.Equipment.Tools.HatchetItem(server=self.get_server(), ide=ide)
            self.register_item(ide, item_obj)

    def register_item(self, ide, item_obj=None):
        if item_obj is None:
            item_obj = lambda : Item(server=self.get_server(), ide=ide)
        self.register_id_obj(item_obj, ide)

    def register_tiles(self):
        for ide in SaoirseRegistry.Identifiers.TILES:
            self.register_tile(ide.get_identifier(), add_item=True)

    def register_tile(self, ide, tile_obj=None, add_item=False, item_obj=None):
        if tile_obj is None:
            tile_obj = lambda : Tile(server=self.get_server(), ide=ide)
        if add_item:
            if item_obj is None:
                item_obj = lambda : Item(server=self.get_server(), ide=ide)
            self.register_item(Identifier("items").extend(ide), item_obj)
        self.register_id_obj(tile_obj, ide)

    def register_entities(self):
        self.register_entity(SaoirseRegistry.Identifiers.ENTITIES.player.get_identifier(),
                            lambda : Entities.PlayerEntity(server=self.get_server()))

    def register_entity(self, ide, entity_obj=None):
        if entity_obj is None:
            entity_obj = lambda : Entity(server=self.get_server(), ide=ide)
        self.register_id_obj(entity_obj, ide)

    def register_fluids(self):
        for ide in SaoirseRegistry.Identifiers.FLUIDS:
            self.register_fluid(ide.get_identifier())

    def register_fluid(self, ide, fluid_obj=None):
        if fluid_obj is None:
            fluid_obj = lambda : Fluid(server=self.get_server(), ide=ide)
        self.register_id_obj(fluid_obj, ide)

    def register_spaces(self):
        self.register_space(SaoirseRegistry.Identifiers.SPACES.normal.get_identifier(),
                            lambda : Spaces.NormalSpace(server=self.get_server()))

        self.register_space(SaoirseRegistry.Identifiers.SPACES.ghostly.get_identifier(),
                            lambda : Spaces.GhostlySpace(server=self.get_server()))

    def register_space(self, ide, space_obj=None):
        if space_obj is None:
            space_obj = lambda : ThreeDimensionalSpace(server=self.get_server(), ide=ide)
        self.register_id_obj(space_obj, ide)


    class Identifiers:
        class ITEMS(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("items").extend(super().get_base_ide())

            pebble = "pebble"
            ##########
            paper = "paper"
            ##########
            silkworm = "silkworm"
            ##########
            cotton_seed = "cotton_seed"
            ##########
            silk_thread = "silk_thread"
            cotton_thread = "cotton_thread"
            woolen_thread = "woolen_thread"
            canvas_thread = "canvas_thread"
            #####
            silk_sheet = "silk_sheet"
            cotton_sheet = "cotton_sheet"
            woolen_sheet = "woolen_sheet"
            canvas_sheet = "canvas_sheet"
            ##########
            glass_shard = "glass_shard"
            ##########
            oak_stick = "oak_stick"
            spruce_stick = "spruce_stick"
            ironwood_stick = "ironwood_stick"
            hickory_stick = "hickory_stick"
            ##########
            hatchet = "hatchet"

        class TILES(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("tiles").extend(super().get_base_ide())

            dirt = "dirt"
            gravel = "gravel"
            sand = "sand"
            peat = "peat"
            ##########
            granite = "granite"
            gabboro = "gabbro"
            bassalt = "bassalt"
            obsidian = "obsidian"
            limestone = "limestone"
            bedrock = "bedrock"
            ##########
            oak_log = "oak_log"
            spruce_log = "spruce_log"
            ironwood_log = "ironwood_log"
            hickory_log = "hickory_log"

        class ENTITIES(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("entities").extend(super().get_base_ide())

            player = "player"

        class FLUIDS(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("fluids").extend(super().get_base_ide())

            water = "water"
            lava = "lava"
            milk = "milk"
            honey = "honey"
            slime = "slime"
            oil = "oil"
            tar = "tar"

        class GASSES(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("gasses").extend(super().get_base_ide())

            oxygen = "oxygen"

        class SPACES(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("spaces").extend(super().get_base_ide())

            normal = "normal"
            ghostly = "ghostly"


class SaoirseServer(BaseServer):
    saved_players_key = "saved_players"

    def __init__(self, save_file="world.pkl"):
        super().__init__(saoirse_id, SaoirseRegistry(self))

        self.saved_players = {}
        self.players = {}

        self.set_spawn_space(SaoirseRegistry.Identifiers.SPACES.normal.get_identifier())
        self.set_spawn_pos(ThreeDimensionalPosition(0, 0, 4000))

        self.set_save_file(save_file)

        if path.isfile(self.get_save_file()):
            self.read_from_file()
        else:
            self.generate_spaces()

    def get_saved_players(self):
        return self.saved_players

    def refresh_players(self):
        players = {}
        for space in self.get_spaces():
            for obj_set in space.get_obj_sets():
                for obj in obj_set:
                    if isinstance(obj, Entities.PlayerEntity):
                        players[str(obj.get_player_id())] = obj
        if self.players != players:
            self.players.clear()
            self.players = players

    def get_players_dict(self):
        return self.players

    def get_players(self):
        return list(self.get_players_dict())

    def get_player_ids(self):
        return self.get_players_dict().keys()

    def add_player(self, player_id):
        player_id_str = str(player_id)
        if player_id_str == "":
            logger.warning("Failed to add player with blank id!")
        else:
            self.refresh_players()
            if player_id_str not in self.get_player_ids():
                player = self.get_registry().get_entry(SaoirseRegistry.Identifiers.ENTITIES.player.get_identifier()).get_obj()
                player.set_server(self)
                player.set_player_id(player_id_str)
                if player_id_str in self.get_saved_players().keys():
                    player.set_data(self.get_saved_players().get(player_id_str))
                self.get_space(SaoirseRegistry.Identifiers.SPACES.normal.get_identifier()).add_object_at_pos(player.get_pos(), player)
                self.players[player_id_str] = player

    def get_player_by_id(self, player_id):
        player_id_str = str(player_id)
        players = self.get_players_dict()
        if player_id_str in players.keys():
            return players.get(player_id_str)
        return None

    def generate_spaces(self):
        for space_ide in SaoirseRegistry.Identifiers.SPACES:
            self.add_space(self.get_registry().get_entry(space_ide.get_identifier()).get_obj())

        for space in self.get_spaces():
            space.generate_terrain_at_pos()

    def set_data(self, data):
        super().set_data(data)
        if self.saved_players_key in data.keys():
            self.saved_players.update(data.get(self.saved_players_key))

    def get_data(self):
        data = super().get_data()
        saved_players_data = self.get_saved_players()
        players_dict = self.get_players_dict()
        for player_id in players_dict.keys():
            saved_players_data[player_id] = players_dict.get(player_id).get_data()
        data[self.saved_players_key] = saved_players_data
        return data

    def set_save_file(self, save_file="world.pkl"):
        self.save_file = save_file

    def get_save_file(self):
        return self.save_file

    def get_save_dir(self):
        return path.dirname(self.get_save_file())

    #def save_to_file(self):
    #    with open(self.get_save_file(), "w") as f:
    #        mpack(self.get_data(), f)

    #def read_from_file(self):
    #    with open(self.get_save_file(), "r") as f:
    #        self.set_data(munpack(f))

    def save_to_file(self):
        data = None
        try:
            data = self.get_data() # Get data first to avoid writing a broken state to the save file
        except Exception as e:
            logger.warning(f"Failed to write save to file, it will not be saved (the old save will still remain intact): {str(e)}")
        if data is not None:
            try:
                if not path.isdir(self.get_save_dir()):
                    mkdir(self.get_save_dir())
                if not path.isfile(self.get_save_file()):
                    mknod(self.get_save_file())
                with open(self.get_save_file(), "wb") as f:
                    pkldump(data, f)
            except Exception as e:
                logger.warning(f"Failed to write save to file, the old file may have been written with broken data (see the following exception for more info, \"no such file or directory\" means no damage was done): {str(e)}")

    def read_from_file(self):
        data = None
        try:
            with open(self.get_save_file(), "rb") as f:
                data = pklload(f) # Get data first to avoid reading a broken state from the save file
        except Exception as e:
            logger.warning(f"Failed to load save from file. A new level will NOT be created to avoid overwriting the existing file, please change the save path if a new level is desired. The broken save might be fixable by hand as it is stored in plain JSON syntax: {str(e)}")
            raise e # The server should still crash to avoid overwriting the intended save
        if data is not None:
            self.set_data(data)

    def on_removed(self):
        self.save_to_file()
        super().on_removed()


def main(args):
    save_file = "saoirse_world.json"

    help_msg = """
    Server program for the game Saoirse

    Usage (depends on which executable form is being run):

    For binary releases:

    saoirse_server OPTIONS
    saoirse_server.exe OPTIONS

    For Python source files:

    pypy3 saoirse_server.py OPTIONS
    python3 saoirse_server.py OPTIONS

    Valid OPTIONS:

    --save_file=SAVEFILE                                Sets the file for saving all game data in the JSON format to SAVEFILE.
    --help                                              Prints this message and exits
    -h                                                  Same as --help
    """

    arg_key_help = ("--help", "-h")
    arg_key_save_file = "--save-file="

    if len(args) > 1:
        for arg in args[1:]:
            if arg.startswith(arg_key_help):
                logger.info(help_msg)
                return
            if arg.startswith(arg_key_save_file):
                save_file = expand_full_path(arg.replace(arg_key_save_file, ""))

    server = SaoirseServer(save_file = save_file)
    while not server.removed:
        server.tick()
        time.sleep(1 / server.get_ticks_per_second())

        # Kill the server after 1 tick for testing
        server.on_removed()


if __name__ == "__main__":
    main(sys.argv)
