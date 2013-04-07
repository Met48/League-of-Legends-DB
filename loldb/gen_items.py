"""League item data generator."""

import re
from util import get_sql_rows


def get_items_map(connection):
    """Get formatted item details from sql database."""

    items_map = {}

    # Basic item details
    for row in get_sql_rows(connection, 'items'):
        item = {
            'id': row.id,
            'name': row.name,
            'icon': row.iconPath,
            'cost': row.price,
            'tooltip': row.description,
            'stats': None,
            'tier': row.epicness,
            'categories': {},
            'recipe': [],
        }

        # Stats
        # Ignored: Dodge , EXPBonus
        stats = {}
        stats_table = [
            ('ap', 'AbilityPower'),
            ('armor', 'Armor'),
            ('ad', 'AttackDamage'),
            ('aspd', 'AttackSpeed'),
            ('crit', 'CritChance'),
            ('crit_dmg', 'CritDamage'),
            ('hp', 'HPPool'),
            ('hp5', 'HPRegen'),
            ('mr', 'MagicResist'),
            ('mspd', 'MovementSpeed'),
            ('mana', 'MPPool'),
            ('mp5', 'MPRegen'),
        ]
        row_dict = row._asdict()

        for name, key in stats_table:
            stats[name] = {
                'flat': row_dict['flat%sMod' % key],
                'percentage': row_dict['percent%sMod' % key] * 100,
            }
            if name.endswith('p5'):
                # Database stores values as per second
                stats[name]['flat'] *= 5
                stats[name]['percentage'] *= 5
        item['stats'] = stats

        # Convenience alias
        name = item['name'].lower()
        name = re.sub('[^a-z0-9]+', '_', name)
        item['aliases'] = [name]

        # Store by id
        items_map[row.id] = item

    # Recipes
    for row in get_sql_rows(connection, 'itemRecipes'):
        if row.buildsToItemId not in items_map:
            print "ERROR: Missing recipe result, item id", row.buildsToItemId
            continue
        if row.recipeItemId not in items_map:
            print ("ERROR: Missing recipe component for %s, component id %d." %
                   (row.buildsToItemId, row.recipeItemId))
            continue
        item = items_map[row.buildsToItemId]
        item['recipe'].append(row.recipeItemId)

    # Categories
    categories = {}
    for row in get_sql_rows(connection, 'itemCategories'):
        categories[row.id] = row.name
    for row in get_sql_rows(connection, 'itemItemCategories'):
        if row.itemId not in items_map:
            print "ERROR: Missing category item, item id", row.itemId
            continue
        if row.itemCategoryId not in categories:
            print "ERROR: Missing category", row.itemCategoryId
        category_name = categories[row.itemCategoryId]
        items_map[row.itemId]['categories'][category_name] = True

    return items_map


def correct_items_map(items_map, corrections_map):
    """Correct items in-place."""

    # Currently no corrections are needed for items
    return
