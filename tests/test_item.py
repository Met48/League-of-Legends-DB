from collections import namedtuple

import mock
import pytest

import loldb.item
import loldb.provider
import loldb.util


PER5_FIELDS = set([
    'flatHPRegenMod',
    'flatMPRegenMod',
])
MOCK_ITEMS = [
    {
        'id': 0,
        'name': 'test',
        'iconPath': 'icon.png',
        'price': 100,
        'description': 'sample',
        'epicness': 1,
        # Stats are a (base, percent) tuple
        # ie. the actual keys are 'flatArmorMod' and 'percentArmorMod'
        'AbilityPower': (1, 0),
        'Armor': (2, 0),
        'AttackDamage': (3, 3),
        'AttackSpeed': (4, 5),
        'CritChance': (5, 6),
        'CritDamage': (6, 7),
        'HPPool': (7, 9),
        'HPRegen': (8, 10),
        'MagicResist': (9, 0),
        'MovementSpeed': (10, 0),
        'MPPool': (11, 0),
        'MPRegen': (12, 0),
    },
    {
        'id': 1000,
        'name': 'test 2',
        'iconPath': 'icon2.png',
        'price': 110,
        'description': 'sample 2',
        'epicness': 2,
        'AbilityPower': (0, 0),
        'Armor': (0, 0),
        'AttackDamage': (0, 0),
        'AttackSpeed': (0, 0),
        'CritChance': (0, 0),
        'CritDamage': (0, 0),
        'HPPool': (400, 0),
        'HPRegen': (0, 0),
        'MagicResist': (0, 0),
        'MovementSpeed': (0, 0),
        'MPPool': (0, 0),
        'MPRegen': (0, 0),
    }
]
ITEM_STATS_MAP = {
    'AbilityPower': 'ap',
    'Armor': 'armor',
    'AttackDamage': 'damage',
    'AttackSpeed': 'attack_speed',
    'CritChance': 'crit_chance',
    'CritDamage': 'crit_damage',
    'HPPool': 'hp',
    'HPRegen': 'hp5',
    'MagicResist': 'magic_resist',
    'MovementSpeed': 'movement_speed',
    'MPPool': 'mana',
    'MPRegen': 'mp5',
}
MOCK_CATEGORIES = {
    2: 'magic',
    3: 'movement',
    4: 'damage',
}
MOCK_ITEM_CATEGORIES = {
    0: set([2, 4]),
    1000: set([3, 4]),
}
MOCK_RECIPES = {
    0: set([1000]),
}


def _make_row(map):
    row = namedtuple('Row', map.keys())
    return row(*map.values())


def _make_stat_row(item):
    item = dict(item)
    for row_field in ITEM_STATS_MAP:
        flat, percentage = item[row_field]
        del item[row_field]
        item['flat%sMod' % row_field] = flat
        item['percent%sMod' % row_field] = percentage
    return _make_row(item)


def test_item_stats():
    for item in MOCK_ITEMS:
        item_row = _make_stat_row(item)
        yield verify_item_stats, item, item_row


def verify_item_stats(item, row):
    stats = loldb.item.ItemStats()
    stats.update_from_sql_row(row)

    for row_field, item_field in ITEM_STATS_MAP.items():
        flat, percentage = item[row_field]
        if item_field.endswith('p5'):
            flat *= 5
        item_stat = getattr(stats, item_field)
        assert item_stat.flat == flat
        assert item_stat.percentage == percentage


def _get_db_rows_items(table):
    assert table == 'items'
    for item in MOCK_ITEMS:
        yield _make_stat_row(item)


@mock.patch('loldb.item.ItemStats')
def test_get_item_map(ItemStats):
    provider = mock.MagicMock()
    provider.get_db_rows = _get_db_rows_items

    items = loldb.item._get_item_map(provider)

    for item in MOCK_ITEMS:
        result_item = items[item['id']]
        assert result_item.name == item['name']
        assert result_item.icon_path == item['iconPath']
        assert result_item.cost == item['price']
        assert result_item.tooltip == item['description']
        assert result_item.tier == item['epicness']
        result_item.stats.update_from_sql_row.assert_called_once()
        assert result_item.alias == loldb.util.alias(item['name'])

