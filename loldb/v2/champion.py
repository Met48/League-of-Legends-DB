import re


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
    alias = ''
    title = ''

    icon_path = ''
    select_sound_path = ''

    lore = None
    ratings = None
    tips_as = []
    tips_against = []
    tags = set()
    abilities = {}

    def __init__(self, internal_name):
        self.internal_name = internal_name
        self.lore = Lore()
        self.ratings = Ratings()
        self.tips_as = []
        self.tips_against = []
        self.tags = set()
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


def _get_tips(tips_str):
    """Get list of tips from tips string."""
    return [tip for tip in tips_str.split('*') if tip]


def _get_description(desc):
    """Format description text."""
    # Description often contains '' instead of "
    return desc.replace("''", '"')


def get_champions(provider):
    for row in provider.get_db_rows('champions'):
        # TODO: videos?
        # TODO: selection sound name?
        # row.name is the internal name
        champion = Champion(row.name)
        # row.displayName is the public name
        champion.name = row.displayName
        # Misc
        champion.title = row.title
        champion.id = row.id
        champion.icon_path = row.iconPath
        champion.tags = set(row.tags.split(','))
        # Lore
        champion.lore.body = _get_description(row.description)
        champion.lore.quote = row.quote
        champion.lore.quote_author = row.quoteAuthor
        # Ratings
        champion.ratings.attack = row.ratingAttack
        champion.ratings.defense = row.ratingDefense
        champion.ratings.magic = row.ratingMagic
        champion.ratings.difficulty = row.ratingDifficulty
        # Tips
        tips_as = _get_tips(row.tips)
        tips_against = _get_tips(row.opponentTips)
        map(champion.add_tip_as, tips_as)
        map(champion.add_tip_against, tips_against)
        # For convenience, champions should be accessible via ascii variable
        # names; any groups of invalid characters will be replaced by _
        alias = row.displayName.lower()
        alias = re.sub('[^a-z0-9]+', '_', alias)
        champion.alias = alias

        yield champion
