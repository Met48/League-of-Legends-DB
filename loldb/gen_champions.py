"""League champion data generator."""

import re
from util import get_sql_rows


def get_champions_map(connection):
    """Get formatted champion details from sql database."""

    champions_map = {}

    # Process database rows
    for row in get_sql_rows(connection, 'champions'):
        # Helper functions
        def get_tips(string):
            return [tip for tip in string.split('*') if tip]

        def get_description(string):
            # The description often contains '' instead of "
            return string.replace("''", '"')

        # Main data
        # Stats, skins, and abilities come from other sources
        champion = {
            'id': row.id,
            'internal_name': row.name,
            'name': row.displayName,
            'title': row.title,
            'icon': row.iconPath,
            'lore': {
                'desc': get_description(row.description),
                'quote': row.quote,
                'quote_author': row.quoteAuthor,
            },
            'tips': {
                'as': get_tips(row.tips),
                'against': get_tips(row.opponentTips),
            },
            'rating': {
                'attack': row.ratingAttack,
                'defense': row.ratingDefense,
                'magic': row.ratingMagic,
                'difficulty': row.ratingDifficulty,
            },
            # TODO: videos?
            # TODO: selection sound name?
            'select_sound': row.selectSoundPath,
        }

        # Tags
        # A set would be ideal but is not supported by JSON
        tags = row.tags.split(',')
        tags_map = dict((tag, True) for tag in tags)
        champion['tags'] = tags_map

        # For convenience, champions should be accessible via ascii variable
        # names; any groups of invalid characters will be replaced by _
        name = row.displayName.lower()
        name = re.sub('[^a-z0-9]+', '_', name)
        # name = re.sub('^[0-9]', '', name)
        champion['aliases'] = [name]

        # Store by id
        champions_map[row.id] = champion

    return champions_map


def correct_champions_map(champions_map, corrections_map):
    """Correct champions in-place."""

    # Currently no corrections are needed for champions
    return
