import collections
import warnings

from .util import alias

ItemStat = collections.namedtuple('ItemStat', 'flat percentage')


class ItemStats(object):
    ap = ItemStat(0, 0)
    armor = ItemStat(0, 0)
    damage = ItemStat(0, 0)
    attack_speed = ItemStat(0, 0)
    crit_chance = ItemStat(0, 0)
    crit_damage = ItemStat(0, 0)
    hp = ItemStat(0, 0)
    hp5 = ItemStat(0, 0)
    magic_resist = ItemStat(0, 0)
    movement_speed = ItemStat(0, 0)
    mana = ItemStat(0, 0)
    mp5 = ItemStat(0, 0)

    STATS_TABLE = [
        ('ap', 'AbilityPower'),
        ('armor', 'Armor'),
        ('damage', 'AttackDamage'),
        ('attack_speed', 'AttackSpeed'),
        ('crit_chance', 'CritChance'),
        ('crit_damage', 'CritDamage'),
        ('hp', 'HPPool'),
        ('hp5', 'HPRegen'),
        ('magic_resist', 'MagicResist'),
        ('movement_speed', 'MovementSpeed'),
        ('mana', 'MPPool'),
        ('mp5', 'MPRegen'),
    ]

    def update_from_sql_row(self, row):
        row = row._asdict()

        for name, key in self.STATS_TABLE:
            flat = row['flat%sMod' % key]
            percentage = row['percent%sMod' % key]
            if name.endswith('p5'):
                flat *= 5
                percentage *= 5
            stat = ItemStat(flat, percentage)
            assert hasattr(self, name)
            setattr(self, name, stat)

    def __repr__(self):
        return '<ItemStats %s>' % ' '.join(
            '%s=%s' % (key, getattr(self, key))
            for key, _ in self.STATS_TABLE
        )


class Item(object):
    id = -1
    name = ''
    alias = ''
    icon_path = ''
    cost = 0
    tooltip = ''
    tier = 0  # TODO
    stats = None
    categories = set()
    recipe = set()

    def __init__(self):
        self.stats = ItemStats()
        self.categories = set()
        self.recipe = set()

    def __repr__(self):
        return '<Item %s \'%s\'>' % (self.id, self.name)


def _get_item_map(provider):
    """
    Return map of item ids to incomplete Items.

    Item instances at this stage do not have their recipe or categories.

    """
    items = {}
    for row in provider.get_db_rows('items'):
        item = Item()
        item.id = row.id
        item.name = row.name
        item.icon_path = row.iconPath
        item.cost = row.price
        item.tooltip = row.description
        item.stats = ItemStats()
        item.tier = row.epicness

        item.stats.update_from_sql_row(row)

        item.alias = alias(item.name)

        items[item.id] = item
    return items


def _get_categories(provider):
    """Generate category (id, name) tuples."""
    for row in provider.get_db_rows('itemCategories'):
        yield row.id, row.name


def _set_item_categories(provider, items):
    categories = dict(_get_categories(provider))
    for row in provider.get_db_rows('itemItemCategories'):
        if row.itemId not in items:
            warnings.warn('Category applies to invalid item id %s' % row.itemId)
            continue
        if row.itemCategoryId not in categories:
            warnings.warn('Missing category id %s' % row.itemCategoryId)
        category_name = categories[row.itemCategoryId]
        items[row.itemId].categories.add(category_name)


def _set_item_recipes(provider, items):
    for row in provider.get_db_rows('itemRecipes'):
        if row.buildsToItemId not in items:
            warnings.warn('Missing recipe result item id %s' %
                          row.buildsToItemId)
            continue
        if row.recipeItemId not in items:
            warnings.warn('Missing recipe component id %s for item id %s' %
                          (row.recipeItemId, row.buildsToItemId))
            continue
        item = items[row.buildsToItemId]
        item.recipe.add(row.recipeItemId)


def get_items(provider):
    """Return dictionary of all Items."""
    items = _get_item_map(provider)
    _set_item_categories(provider, items)
    _set_item_recipes(provider, items)
    return items
