# This file is:
# src/main/python/saoirse_server.py


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


import sys #, uuid
from dataclasses import dataclass
from time import time as gettime
from os import path as ospath, makedirs, mknod
#from msgpack import pack as mpack, unpack as munpack
from json import dumps as jdumps, loads as jloads
from pickle import dump as pkldump, load as pklload
from saoirse_lib import saoirse_lib_version, saoirse_id, saoirse_images_path, logger, expand_full_path, Identifier, IdentifierEnum, MultiKeyDict, BaseRegistry, Item, ThreeDimensionalPosition, ThreeDimensionalSpace, Tile, Fluid, Entity, BaseServer, ThreeDimensionalShape


saoirse_server_version = "0.0.1"


class SaoirseIdentifierEnum(IdentifierEnum):
    def get_base_ide(self):
        return Identifier(saoirse_id)


class SaoirseThreeDimensionalSpace(ThreeDimensionalSpace):
    @dataclass(frozen=True)
    class DataKeys:
        player_key = "player"

    def __init__(self, ide, server):
        super().__init__(ide, server)

        self.space_game_obj_sets = MultiKeyDict()

    def add_obj_at_pos(self, pos, obj):
        return super().add_obj_at_pos(pos, obj, additional_keys=[self.DataKeys.player_key] if isinstance(obj, Entities.PlayerEntity) else [])

    def get_players(self):
        return self.space_game_obj_sets.get(self.DataKeys.player_key, [])


class Items:
    class CanvasSheetItem(Item):
        def get_mass(self):
            return 999999999999

        def get_model(self):
            return ThreeDimensionalShape(boxes=[ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 1), ThreeDimensionalPosition(1, 0, 1), ThreeDimensionalPosition(1, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 1, 1), ThreeDimensionalPosition(1, 1, 1), ThreeDimensionalPosition(1, 1, 0), ThreeDimensionalPosition(0, 1, 0), tex_default=saoirse_images_path.append("pic1.png"))])

    class Equipment:
        class Tools:
            class BaseToolItem(Item):
                integrity_key = "integrity"

                def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), space=None, integrity=100):
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
                def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), space=None, integrity=300):
                    super().__init__(ide, server, pos=pos, space=space, integrity=integrity)

                def get_model(self):
                    return Items.Equipment.Tools.HatchetItem.HatchetItemShape()

                def get_mass(self):
                    return 0.3

                class HatchetItemShape(Item.BaseItemShape):
                    def __init__(self, boxes=[]):
                        boxes.extend([
                            ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(0, 0, 1), ThreeDimensionalPosition(1, 0, 1), ThreeDimensionalPosition(1, 0, 0), ThreeDimensionalPosition(0, 0, 0), ThreeDimensionalPosition(0, 1, 1), ThreeDimensionalPosition(1, 1, 1), ThreeDimensionalPosition(1, 1, 0), ThreeDimensionalPosition(0, 1, 0), tex_default=saoirse_images_path.append("pic2.png")),
                            ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(1, 1, 11), ThreeDimensionalPosition(3, 1, 9), ThreeDimensionalPosition(1, 1, 3.25), ThreeDimensionalPosition(3, 1, 3.25), ThreeDimensionalPosition(1, 1.5, 9), ThreeDimensionalPosition(3, 1.5, 9), ThreeDimensionalPosition(1, 1.5, 3.25), ThreeDimensionalPosition(3, 1.5, 3.25), tex_default=saoirse_images_path.append("pic1.png")),
                            ThreeDimensionalShape.ThreeDimensionalBox.rectangular_prism(ThreeDimensionalPosition(10, 10, 9), ThreeDimensionalPosition(30, 10, 9), ThreeDimensionalPosition(10, 10, 3.25), ThreeDimensionalPosition(30, 10, 3.25), ThreeDimensionalPosition(10, 10.5, 9), ThreeDimensionalPosition(30, 10.5, 9), ThreeDimensionalPosition(10, 10.5, 3.25), ThreeDimensionalPosition(30, 10.5, 3.25), tex_default=saoirse_images_path.append("missing.png")),
                        ])
                        super().__init__(boxes=boxes)


class Entities:
    class PlayerEntity(Entity):
        @dataclass(frozen=True)
        class DataKeys:
            player_id_key = "player_id"

        def __init__(self, server, ide=None):
            super().__init__(ide=SaoirseRegistry.Identifiers.ENTITIES.player.get_identifier(), server=server)

            self.set_player_id(ide=ide)

        def set_player_id(self, ide=None):
            self.player_id = ide

        def get_player_id(self):
            return self.player_id

        def set_data(self, data):
            super().set_data(data)
            if self.DataKeys.player_id_key in data.keys():
                self.set_player_id(data.get(self.DataKeys.player_id_key))

        def get_data(self):
            data = super().get_data()
            data[self.DataKeys.player_id_key] = self.get_player_id()
            return data


class Spaces:
    class NormalSpace(SaoirseThreeDimensionalSpace):
        def __init__(self, server):
            super().__init__(SaoirseRegistry.Identifiers.SPACES.normal.get_identifier(), server)

        def generate_terrain_at_pos(self, pos=ThreeDimensionalPosition.get_origin()):
            # TEST - adding objects
            if pos == ThreeDimensionalPosition.get_origin():
                self.add_obj_at_pos(pos.get_relative(ThreeDimensionalPosition(3, 3, 2)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.hatchet.get_identifier()).get_obj())
                self.add_obj_at_pos(pos.get_relative(ThreeDimensionalPosition(2, 3, 70)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.canvas_sheet.get_identifier()).get_obj())

    class GhostlySpace(SaoirseThreeDimensionalSpace):
        def __init__(self, server):
            super().__init__(SaoirseRegistry.Identifiers.SPACES.ghostly.get_identifier(), server)

        def generate_terrain_at_pos(self, pos=ThreeDimensionalPosition.get_origin()):
            # TEST - adding objects
            if pos == ThreeDimensionalPosition.get_origin():
                self.add_obj_at_pos(pos.get_relative(ThreeDimensionalPosition(1, 5, 1)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.hatchet.get_identifier()).get_obj())


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
            elif ide == SaoirseRegistry.Identifiers.ITEMS.canvas_sheet.get_identifier():
                item_obj = lambda : Items.CanvasSheetItem(server=self.get_server(), ide=ide)
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
    @dataclass(frozen=True)
    class DataKeys:
        world_key = "world"
        config_key = "config"
        max_tickrate_key = "max_tickrate"
        min_tickrate_key = "min_tickrate"
        last_version_key = "last_version"
        save_dir_key = "%savedir%"

    def __init__(self, save_file="world.pkl", config_file=f"{DataKeys.save_dir_key}/server_config.json"):
        self.set_current_tickrate(0)

        self.set_save_file(save_file)
        config_file = config_file.replace(self.DataKeys.save_dir_key, self.get_save_dir())
        self.set_config_file(config_file)

        super().__init__(saoirse_id, SaoirseRegistry(self))

        if ospath.isfile(self.get_config_file()):
            self.read_config_from_file()
        if not hasattr(self, "max_tickrate"):
            self.set_max_tickrate(64)
        if not hasattr(self, "min_tickrate"):
            self.set_min_tickrate(10)

        self.set_spawn_space(SaoirseRegistry.Identifiers.SPACES.normal.get_identifier())
        self.set_spawn_pos(ThreeDimensionalPosition(0, 0, 4000))

        if ospath.isfile(self.get_save_file()):
            self.read_world_from_file()
        else:
            self.generate_spaces()

    def get_players(self):
        players = []
        for space_players in [space.get_players() for space in self.get_spaces() if hasattr(space, "get_players")]:
            players.extend(space_players)
        return players

    def get_players_dict(self):
        return {str(player.get_player_id()): player for player in self.get_players()}

    def get_player_ids(self):
        return self.get_players_dict().keys()

    def get_spawn_space(self):
        return SaoirseRegistry.Identifiers.SPACES.normal.get_identifier()

    def add_player(self, player_id="Player1"):
        if player_id is None or player_id == "":
            logger.warning("Failed to add player with blank id!")
        elif player_id not in self.get_player_ids():
            player = self.get_registry().get_entry(SaoirseRegistry.Identifiers.ENTITIES.player.get_identifier()).get_obj()
            player.set_server(self)
            player.set_player_id(player_id)
            if self.get_spawn_space_id().get_path_str() not in self.get_spaces_dict().keys():
                self.generate_space(self.get_spawn_space_id())
            self.get_space(self.get_spawn_space_id()).add_obj_at_pos(player.get_pos(), player)

    def get_player_by_id(self, player_id):
        player_id_str = str(player_id)
        players = self.get_players_dict()
        if player_id_str in players.keys():
            return players.get(player_id_str)
        return None

    def generate_space(self, space_ide):
        space = self.get_registry().get_entry(space_ide).get_obj()
        space.generate_terrain_at_pos()
        self.add_space(space)

    def generate_spaces(self):
        for space_ide in [SaoirseRegistry.Identifiers.SPACES.normal, SaoirseRegistry.Identifiers.SPACES.ghostly]:
            self.generate_space(space_ide.get_identifier())

    def set_max_tickrate(self, tickrate):
        self.max_tickrate = tickrate

    def set_min_tickrate(self, tickrate):
        self.min_tickrate = tickrate

    def get_max_tickrate(self):
        return self.max_tickrate

    def get_min_tickrate(self):
        return self.min_tickrate

    def set_data(self, data):
        if self.DataKeys.world_key in data.keys():
            super().set_data(data.get(self.DataKeys.world_key))
        if self.DataKeys.config_key in data.keys():
            config = data.get(self.DataKeys.config_key)
            if self.DataKeys.max_tickrate_key in config.keys():
                self.set_max_tickrate(config.get(self.DataKeys.max_tickrate_key))
            if self.DataKeys.min_tickrate_key in config.keys():
                self.set_min_tickrate(config.get(self.DataKeys.min_tickrate_key))

    def get_world_data(self):
        world_data = super().get_data()
        world_data[self.DataKeys.last_version_key] = saoirse_server_version
        return world_data

    def get_config_data(self):
        return {
            self.DataKeys.max_tickrate_key: self.get_max_tickrate(),
            self.DataKeys.min_tickrate_key: self.get_min_tickrate(),
            self.DataKeys.last_version_key: saoirse_server_version,
        }

    def get_data(self):
        return {
            self.DataKeys.world_key: self.get_world_data(),
            self.DataKeys.config_key: self.get_config_data(),
        }

    def set_save_file(self, save_file="world.pkl"):
        self.save_file = save_file

    def set_config_file(self, config_file="server_config.json"):
        self.config_file = config_file

    def get_save_file(self):
        return self.save_file

    def get_config_file(self):
        return self.config_file

    def get_save_dir(self):
        p = ospath.dirname(self.get_save_file())
        if p.isspace():
            p = str(ospath.curdir)
        return p

    def get_config_dir(self):
        p = ospath.dirname(self.get_config_file())
        if p.isspace():
            p = str(ospath.curdir)
        return p

    #def save_to_file(self):
    #    with open(self.get_save_file(), "w") as f:
    #        mpack(self.get_data(), f)

    #def read_from_file(self):
    #    with open(self.get_save_file(), "r") as f:
    #        self.set_data(munpack(f))

    def save_to_file(self, file_path, data, use_pkl=False):
        if data is not None:
            try:
                file_dir = ospath.dirname(file_path)
                if not ospath.isdir(file_dir):
                    makedirs(file_dir)
                if not ospath.isfile(file_path):
                    mknod(file_path)
                if use_pkl:
                    with open(file_path, "wb") as f:
                        pkldump(data, f)
                else:
                    with open(file_path, "w") as f:
                        f.write(jdumps(data, indent=2))
            except Exception as e:
                logger.warning(f"Failed to write save to file, the old file may have been written with broken data (see the following exception for more info, \"no such file or directory\" means no damage was done): {e}")

    def save_world_to_file(self):
        try:
            data = self.get_world_data() # Get data first to avoid writing a broken state to the save file
        except Exception as e:
            data = None
            logger.warning(f"Failed to write save to file, it will not be saved (the old save will still remain intact): {e}")
        if data is not None:
            self.save_to_file(self.get_save_file(), data, True)

    def save_config_to_file(self):
        try:
            data = self.get_config_data() # Get data first to avoid writing a broken state to the config file
        except Exception as e:
            data = None
            logger.warning(f"Failed to write config to file, it will not be saved (the old config will still remain intact): {e}")
        if data is not None:
            self.save_to_file(self.get_config_file(), data, False)

    def read_data_from_file(self, file_path, use_pkl=False):
        data = None
        try:
            if ospath.isfile(file_path):
                # Get data first to avoid reading a broken state from the save file
                if use_pkl:
                    with open(file_path, "rb") as f:
                        data = pklload(f)
                else:
                    with open(file_path, "r") as f:
                        data = jloads(f.read())
        except Exception as e:
            logger.warning(f"Failed to load either the world or the config from file. The path that was failed to be read was: {file_path}  The server will NOT continue to load to avoid overwriting the existing file, please change the save path if a new level is desired and/or the config path if a new configuration is desired. The broken file might be fixable by hand as it is stored in plain JSON syntax")
            raise e # The server should still crash to avoid overwriting the intended save
        if data is not None:
            if self.DataKeys.last_version_key in data.keys():
                save_last_version = data.get(self.DataKeys.last_version_key)
                if save_last_version != saoirse_server_version:
                    logger.warning(f"The server data saved in the file at {file_path} was last run using server version {save_last_version} but the current version is {saoirse_server_version}. This is probably fine, but be careful of incompatibilities.")
            self.set_data(data)

    def read_world_from_file(self):
        self.read_data_from_file(self.get_save_file(), True)

    def read_config_from_file(self):
        self.read_data_from_file(self.get_config_file(), False)

    def read_from_file(self):
        self.read_config_from_file()
        self.read_world_from_file()

    def set_current_tickrate(self, tickrate):
        self.current_tickrate = tickrate

    def get_current_tickrate(self):
        return self.current_tickrate

    def tick(self):
        do_tick = True
        current_time = gettime()
        if hasattr(self, "last_time"):
            if current_time - self.last_time < 1/self.get_max_tickrate():
                do_tick = False
        if do_tick:
            super().tick()
            if hasattr(self, "last_time"):
                self.set_current_tickrate(1/(current_time - self.last_time))
                if self.get_current_tickrate() < self.get_min_tickrate():
                    logger.warning(f"Server is ticking somewhat slowly, the last recorded rate was {self.get_current_tickrate()} ticks / second")
            self.last_time = current_time

    def on_removed(self):
        self.save_world_to_file()
        self.save_config_to_file()
        super().on_removed()


def main(args):
    save_file = "world1.pkl"

    help_msg = """
    Server program for the game Saoirse

    Usage (depends on which executable form is being run):

    For binary releases:

    *NIX: saoirse_server OPTIONS
    WINDOWS: saoirse_server.exe OPTIONS

    For Python source files:

    pypy3 saoirse_server.py OPTIONS
    python3 saoirse_server.py OPTIONS

    Valid OPTIONS:

    --save_file=SAVEFILE                                Set the file for saving all game data in the JSON format to SAVEFILE.
    --version, -v                                       Print the version of the game server file being run, along with that of the base library
    --help, -h                                          Print this message and exit
    """

    version_msg = f"""
    Saoirse Library Version: {saoirse_lib_version}
    Saoirse *Server* Version: {saoirse_server_version}
    """

    arg_key_help = ("--help", "-h")
    arg_key_version = ("--version", "-v")
    arg_key_save_file = "--save-file="

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
            elif arg.startswith(arg_key_save_file):
                save_file = expand_full_path(arg.replace(arg_key_save_file, ""))

    server = SaoirseServer(save_file = save_file)
    try:
        while not server.removed:
            server.tick()
    except KeyboardInterrupt as e:
        logger.warning(f"Recieved KeyboardInterrupt signal, stopping server: {e}")
        server.on_removed()
    if not server.removed:
        server.on_removed()


if __name__ == "__main__":
    main(sys.argv)

