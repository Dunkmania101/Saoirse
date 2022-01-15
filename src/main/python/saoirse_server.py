# This file is:
# src/python/saoirse_server.py

import sys, os
from enum import Enum
#from msgpack import pack as mpack, unpack as munpack
from json import dumps as jdump, loads as jload
from saoirse_base import Identifier, BaseCategorizedRegistry, MainGameObject, Item, SpaceGameObject, ThreeDimensionalPosition, ThreeDimensionalSpace, Tile, Fluid, Entity, BaseServer

saoirse_id = "saoirse"

class SaoirseRegistry(BaseCategorizedRegistry):
    def __init__(self, server):
        super().__init__()

        self.server = server

        self.register_items()
        self.register_tiles()
        self.register_fluids()
        self.register_entities()

    def get_server(self):
        return self.server

    def register_game_obj_under_category(self, ide, category_ide, game_obj_pair):
        if isinstance(game_obj_pair, MainGameObject):
            self.register_id_obj_under_category(ide, category_ide, game_obj_pair)
        return ide

    def register_items(self):
        self.register_category(SaoirseRegistry.SaoirseRegistryCategories.ITEMS.value)

        for ide_str in [
                "pebble",
                "paper",
                ##########
                "silkworm",
                ##########
                "cotton_seed",
                ##########
                "silk_thread",
                "cotton_thread",
                "woolen_thread",
                "canvas_thread",
                #####
                "silk_sheet",
                "cotton_sheet",
                "woolen_sheet",
                "canvas_sheet",
                ##########
                "glass_shard",
                ##########
                "oak_stick",
                "spruce_stick",
                "ironwood_stick",
                "hickory_stick",
                ]:
            ide = Identifier([saoirse_id, ide_str])
            self.register_item(ide, True)                                   

    def register_item(self, ide, item_obj=None):
        if item_obj is None:
            item_obj = lambda: Item(ide, self.get_server())
        self.register_id_obj_under_category(ide, SaoirseRegistry.SaoirseRegistryCategories.ITEMS.value, item_obj)

    def register_tiles(self):
        self.register_category(SaoirseRegistry.SaoirseRegistryCategories.TILES.value)

        for ide_str in [
                "dirt", 
                "gravel",
                "sand",
                "peat",
                ##########
                "granite",
                "gabbro",
                "bassalt",
                "obsidian",
                "limestone",
                "bedrock",
                ##########
                "oak_log",
                "spruce_log",
                "ironwood_log",
                "hickory_log",
                ]:
            ide = Identifier([saoirse_id, ide_str])
            self.register_tile(ide, True)                                   

    def register_tile(self, ide, tile_obj=None, add_item=False, item_obj=None):
        if tile_obj is None:
            tile_obj = lambda: Tile(ide, self.get_server())
        if add_item:
            if item_obj is None:
                item_obj = lambda: Item(ide, self.get_server())
            self.register_item(ide, item_obj)
        self.register_id_obj_under_category(ide, SaoirseRegistry.SaoirseRegistryCategories.TILES.value, tile_obj)

    def register_fluids(self):
        self.register_category(SaoirseRegistry.SaoirseRegistryCategories.FLUIDS.value)

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
            fluid_obj = lambda: Fluid(ide, self.get_server())
        self.register_id_obj_under_category(ide, SaoirseRegistry.SaoirseRegistryCategories.FLUIDS.value, fluid_obj)

    def register_entities(self):
        self.register_category(SaoirseRegistry.SaoirseRegistryCategories.ENTITIES.value)

    def register_entity(self, ide, entity_obj):
        if entity_obj is None:
            entity_obj = lambda: Entity(ide, self.get_server())
        self.register_id_obj_under_category(ide, SaoirseRegistry.SaoirseRegistryCategories.ENTITIES.value, entity_obj)

    class SaoirseRegistryCategories(Enum):
        ITEMS = Identifier([saoirse_id, "items"])
        TILES = Identifier([saoirse_id, "tiles"])
        FLUIDS = Identifier([saoirse_id, "fluids"])
        ENTITIES = Identifier([saoirse_id, "entities"])


class SaoirseServer(BaseServer):
    def __init__(self, save_file="world.sworld"):
        super().__init__(saoirse_id, SaoirseRegistry(self))

        self.save_file = save_file

        if os.path.isfile(self.get_save_file()):
            self.read_from_file()
        else:
            self.prefill_content()

    def prefill_content(self):
        self.add_three_dimensional_space(ThreeDimensionalSpace(Identifier([saoirse_id, "spaces", "natural_land"]), self))

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
            f.write(jdump(self.get_data(), indent=2))

    def read_from_file(self):
        with open(self.get_save_file(), "r") as f:
            self.set_data(jload(f.read()))

    def on_removed(self):
        self.save_to_file()
        super().on_removed()


def main(args):
    server = SaoirseServer()
    #while True:
    #    server.tick()
    server.tick()
    server.on_removed()


if __name__ == "__main__":
    main(sys.argv)
