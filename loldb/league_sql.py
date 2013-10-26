import sqlite3

from . import gen_champions
from . import gen_items
from . import gen_skins


def merge_skins(skins_map, champions_map):
    """Add the skins to the champion mapping."""

    for champion_id, champion_skins in skins_map.items():
        assert champion_id in champions_map
        champion = champions_map[champion_id]
        assert 'skins' not in champion
        champion['skins'] = champion_skins


def generate(db_path, corrections_map):
    connection = sqlite3.connect(db_path)

    champions_map = gen_champions.get_champions_map(connection)
    skins_map = gen_skins.get_skins_map(connection)

    gen_champions.correct_champions_map(champions_map, corrections_map)
    gen_skins.correct_skins_map(skins_map, champions_map, corrections_map)

    merge_skins(skins_map, champions_map)

    items_map = gen_items.get_items_map(connection)
    gen_items.correct_items_map(items_map, corrections_map)

    return {
        'champions': champions_map,
        'items': items_map
    }

