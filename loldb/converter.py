def format_item(item):
    """

    :type item: item.Item
    """
    return {
        'id': item.id,
        'name': item.name,
        'alias': item.alias,
        'icon_path': item.icon_path,
        'cost': item.cost,
        'tooltip': item.tooltip,
        'tier': item.tier,
        'stats': format_item_stats(item.stats),
        'categories': item.categories,
        'recipe': item.recipe,
    }


def format_item_stats(item_stats):
    """

    :type item_stats: item.ItemStats
    """
    output = {}

    for stat_name, _ in item_stats.STATS_TABLE:
        stat = getattr(item_stats, stat_name)
        output[stat_name] = {
            'flat': stat.flat,
            'percentage': stat.percentage,
        }

    return output


def format_champion(champion):
    """

    :type champion: champion.Champion
    """
    return {
        'id': champion.id,
        'internal_name': champion.internal_name,
        'name': champion.name,
        'alias': champion.alias,
        'title': champion.title,
        'icon_path': champion.icon_path,
        'select_sound_path': champion.select_sound_path,
        'tips_as': champion.tips_as,
        'tips_against': champion.tips_against,
        'tags': champion.tags,
        'stats': format_champion_stats(champion.stats),
        'lore': format_champion_lore(champion.lore),
        'ratings': format_champion_ratings(champion.ratings),
        'abilities': map(format_ability, champion.abilities),
        'skins': map(format_skin, champion.skins)
    }


def format_champion_stats(stats):
    """

    :type stats: champion.ChampionStats
    """
    output = {}

    for stat_name in stats._STATS:
        stat = getattr(stats, stat_name)
        if hasattr(stat, 'base'):
            output[stat_name] = {
                'base': stat.base,
                'per_level': stat.per_level,
            }
        else:
            output[stat_name] = stat

    return output


def format_champion_lore(lore):
    """

    :type lore: champion.Lore
    """
    return {
        'body': lore.body,
        'quote': lore.quote,
        'quote_author': lore.quote_author,
    }


def format_champion_ratings(ratings):
    """

    :type ratings: champion.Ratings
    """
    return {
        'attack': ratings.attack,
        'defense': ratings.defense,
        'magic': ratings.magic,
        'difficulty': ratings.difficulty,
    }


def format_ability(ability):
    """

    :type ability: ability.Ability
    """
    return {
        'name': ability.name,
        'description': ability.description,
        'key': ability.key,
        'tooltip': ability.tooltip,
        'levels': map(format_ability_level, ability.levels)
    }


def format_ability_level(ability_level):
    """

    :type ability_level: ability.AbilityLevel
    """
    return {
        'tooltip_values': ability_level.tooltip_values,
        'cooldown': ability_level.cooldown,
        'cost': ability_level.cost
    }


def format_skin(skin):
    """

    :type skin: skin.Skin
    """
    return {
        'id': skin.id,
        'name': skin.name,
        'internal_name': skin.internal_name,
        'portrait_path': skin.portrait_path,
        'splash_path': skin.splash_path,
        'is_base': skin.is_base,
        'champion_id': skin.champion_id,
        'rank': skin.rank,
    }
