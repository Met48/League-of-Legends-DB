"""League of Legend Champion Representation."""

# TODO: Don't use as many classes?

class Lore(object):
    body = ''
    quote = ''
    quote_author = ''

    def __init__(self, body='', quote='', quote_author=''):
        self.body = body.replace("''", '"')
        self.quote = quote
        self.quote_author = quote_author


class Ratings(object):
    attack = 0
    defense = 0
    magic = 0
    difficulty = 0


class Champion(object):
    id = -1

    internal_name = ''
    name = ''
    title = ''

    icon_path = ''
    select_sound_path = ''

    lore = None
    ratings = None
    tips_as = []
    tips_against = []
    abilities = {}
    # TODO: videos?
    # TODO: selection sound name?

    def __init__(self, internal_name):
        self.internal_name = internal_name
        self.lore = Lore()
        self.ratings = Ratings()
        self.tips_as = []
        self.tips_against = []
        self.abilities = {}

    def add_tip_as(self, tip):
        self.tips_as.append(tip.strip())

    def add_tip_against(self, tip):
        self.tips_against.append(tip.strip())

    @property
    def friendly_name(self):
        name = self.name
        name = name.lower()
        name = re.sub('[^a-z0-9]+', '_', name)
        # name = re.sub('^[0-9]', '', name)
        return name



import re
from .util import get_sql_rows


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
