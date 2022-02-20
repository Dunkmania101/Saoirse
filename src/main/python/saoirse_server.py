# This file is:
# src/python/saoirse_server.py

import sys, os, time
#from msgpack import pack as mpack, unpack as munpack
from json import dumps as jdumps, loads as jloads
from saoirse_base import expand_full_path, Identifier, IdentifierEnum, BaseRegistry, Item, ThreeDimensionalPosition, ThreeDimensionalSpace, Tile, Fluid, Entity, BaseServer


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


class Spaces:
    class NormalSpace(ThreeDimensionalSpace):
        def __init__(self, server):
            super().__init__(SaoirseRegistry.Identifiers.SPACES.normal.get_identifier(), server)

        def generate_terrain_at_pos(self, pos=ThreeDimensionalPosition.get_origin()):
            # TEST - adding objects
            if pos == ThreeDimensionalPosition.get_origin():
                self.add_space_game_object_at_pos(pos.get_relative(ThreeDimensionalPosition(99, 53, 215)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.canvas_sheet.get_identifier()).get_obj())

    class GhostlySpace(ThreeDimensionalSpace):
        def __init__(self, server):
            super().__init__(SaoirseRegistry.Identifiers.SPACES.ghostly.get_identifier(), server)

        def generate_terrain_at_pos(self, pos=ThreeDimensionalPosition.get_origin()):
            # TEST - adding objects
            self.add_space_game_object_at_pos(pos.get_relative(ThreeDimensionalPosition(99, 53, 215)), self.get_server().get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.canvas_sheet.get_identifier()).get_obj())



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
        for ide in SaoirseRegistry.Identifiers.ITEMS:
            self.register_item(ide.get_identifier(), None)

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

    def register_fluids(self):
        for ide in SaoirseRegistry.Identifiers.FLUIDS:
            self.register_fluid(ide.get_identifier())

    def register_fluid(self, ide, fluid_obj=None):
        if fluid_obj is None:
            fluid_obj = lambda : Fluid(server=self.get_server(), ide=ide)
        self.register_id_obj(fluid_obj, ide)

    def register_entities(self):
        pass

    def register_entity(self, ide, entity_obj=None):
        if entity_obj is None:
            entity_obj = lambda : Entity(server=self.get_server(), ide=ide)
        self.register_id_obj(entity_obj, ide)

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
    def __init__(self, save_file="world.json"):
        super().__init__(saoirse_id, SaoirseRegistry(self))

        self.set_save_file(save_file)

        if os.path.isfile(self.get_save_file()):
            self.read_from_file()
        else:
            self.generate_spaces()

    def generate_spaces(self):
        for space_ide in SaoirseRegistry.Identifiers.SPACES:
            self.add_space(self.get_registry().get_entry(space_ide.get_identifier()).get_obj())

        for space in self.get_spaces():
            space.generate_terrain_at_pos()

    def set_save_file(self, save_file="world.json"):
        self.save_file = save_file

    def get_save_file(self):
        return self.save_file

    #def save_to_file(self):
    #    with open(self.get_save_file(), "w") as f:
    #        mpack(self.get_data(), f)

    #def read_from_file(self):
    #    with open(self.get_save_file(), "r") as f:
    #        self.set_data(munpack(f))

    def save_to_file(self):
        with open(self.get_save_file(), "w") as f:
            f.write(jdumps(self.get_data(), indent=2))

    def read_from_file(self):
        with open(self.get_save_file(), "r") as f:
            self.set_data(jloads(f.read()))

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

    --save_file=SAVEFILE                                Sets the file for saving all game data to SAVEFILE
    """

    arg_key_help = ("--help", "-h")
    arg_key_save_file = "--save_file="

    if len(args) > 1:
        for arg in args[1:]:
            if arg.startswith(arg_key_help):
                print(help_msg)
                return
            if arg.startswith(arg_key_save_file):
                print(arg)
                save_file = expand_full_path(arg.replace(arg_key_save_file, ""))

    server = SaoirseServer(save_file = save_file)
    while not server.removed:
        server.tick()
        time.sleep(1 / server.get_ticks_per_second())

        # Kill the server after 1 tick for testing
        server.on_removed()


if __name__ == "__main__":
    main(sys.argv)
