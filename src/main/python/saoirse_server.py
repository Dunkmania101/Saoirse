# This file is:
# src/python/saoirse_server.py

import sys, os, time
#from msgpack import pack as mpack, unpack as munpack
from json import dumps as jdumps, loads as jloads
from saoirse_base import Identifier, IdentifierEnum, BaseRegistry, Item, ThreeDimensionalPosition, ThreeDimensionalSpace, Tile, Fluid, Entity, BaseServer


saoirse_id = "saoirse"


class SaoirseIdentifierEnum(IdentifierEnum):
    def get_base_ide(self):
        return Identifier(saoirse_id)


class Spaces:
    class NormalSpace(ThreeDimensionalSpace):
        def __init__(self, server):
            super().__init__(SaoirseRegistry.Identifiers.SPACES.normal.get_value(), server)

            # TEST - adding objects
            self.add_space_game_object_at_pos(ThreeDimensionalPosition(99, 53, 215), server.get_registry().get_entry(SaoirseRegistry.Identifiers.ITEMS.canvas_sheet.get_value()).get_obj())


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
            self.register_item(ide.get_value(), None)

    def register_item(self, ide, item_obj=None):
        if item_obj is None:
            item_obj = lambda : Item(server=self.get_server(), ide=ide)
        self.register_id_obj(item_obj, ide)

    def register_tiles(self):
        for ide in SaoirseRegistry.Identifiers.TILES:
            self.register_tile(ide.get_value(), add_item=True)

    def register_tile(self, ide, tile_obj=None, add_item=False, item_obj=None):
        if tile_obj is None:
            tile_obj = lambda : Tile(server=self.get_server(), ide=ide)
        if add_item:
            if item_obj is None:
                item_obj = lambda : Item(server=self.get_server(), ide=ide)
            self.register_item(Identifier("items").extend(ide), item_obj)
        self.register_id_obj(tile_obj, ide)

    def register_fluids(self):
        for ide_str in [
                "water",
                "lava",
                "milk",
                "honey",
                "slime",
                "oil",
                "tar",
        ]:
            ide = Identifier([saoirse_id, ide_str])
            self.register_fluid(ide)

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
        self.register_space(SaoirseRegistry.Identifiers.SPACES.normal.get_value(),
                            lambda : Spaces.NormalSpace(server=self.get_server()))

    def register_space(self, ide, space_obj=None):
        if space_obj is None:
            space_obj = lambda : ThreeDimensionalSpace(server=self.get_server(), ide=ide)
        self.register_id_obj(space_obj, ide)


    class Identifiers:
        class ITEMS(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("items").extend(super().get_base_ide())
            pebble = "pebble"
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

        class SPACES(SaoirseIdentifierEnum):
            def get_base_ide(self):
                return Identifier("spaces").extend(super().get_base_ide())
            normal = "normal"


class SaoirseServer(BaseServer):
    def __init__(self, save_file="world.sworld"):
        super().__init__(saoirse_id, SaoirseRegistry(self))

        self.save_file = save_file

        if os.path.isfile(self.get_save_file()):
            self.read_from_file()
        else:
            self.generate_spaces()

    def generate_spaces(self):
        # for space in self.get_registry().get_entries_under_category(Identifier("spaces")).values():
            # self.add_three_dimensional_space(space.get_obj(server=self))
        self.add_three_dimensional_space(self.get_registry().get_entry(SaoirseRegistry.Identifiers.SPACES.normal.get_value()).get_obj())

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
    server = SaoirseServer()
    while not server.removed:
        server.tick()
        time.sleep(1 / server.get_ticks_per_second())

        # Kill the server after 1 tick for testing
        server.on_removed()


if __name__ == "__main__":
    main(sys.argv)
