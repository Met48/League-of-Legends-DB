import collections
import re
import inibin


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


Stat = collections.namedtuple('Stat', 'base per_level')


class Stats(object):
    hp = Stat(0, 0)
    hp5 = Stat(0, 0)
    mana = Stat(0, 0)
    mp5 = Stat(0, 0)
    damage = Stat(0, 0)
    sttack_speed = Stat(0, 0)
    armor = Stat(0, 0)
    magic_resist = Stat(0, 0)
    range = 0
    speed = 0


class Champion(object):
    id = -1

    internal_name = ''
    name = ''
    alias = ''
    title = ''

    icon_path = ''
    select_sound_path = ''

    stats = None
    lore = None
    ratings = None
    tips_as = []
    tips_against = []
    tags = set()
    abilities = {}

    def __init__(self, internal_name):
        self.internal_name = internal_name
        self.stats = Stats()
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


def _create_stat(inibin_map, key):
    """Return a Stat instance with base and per_level values within inibin key."""
    stat = inibin_map['stats'][key]
    return Stat(stat['base'], stat['per_level'])


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

        # Find champion inibin
        raf_master = provider.get_raf_master()
        raf_pattern = '^data/characters/{0}/{0}.inibin$'.format(champion.internal_name.lower())
        raf_results = list(raf_master.find_re(raf_pattern))
        if not raf_results:
            print('No champion inibin for %s' % champion.internal_name)
        if len(raf_results) > 1:
            # TODO: Is this ever triggered?
            print('Ambiguous champion inibin for %s' % champion.internal_name)
        try:
            inibin_map = inibin.Inibin(data=raf_results[0].read())
        except Exception:  # TODO: Less generic Exception
            print('Malformed champion inibin for %s' % champion.internal_name)
        else:
            inibin_map = inibin_map.as_champion(provider.get_font_config())
            # Read stats
            # TODO: Better error checking
            # TODO: Refactor
            stats = champion.stats
            stats.hp = _create_stat(inibin_map, 'hp')
            stats.hp5 = _create_stat(inibin_map, 'hp5')
            stats.mana = _create_stat(inibin_map, 'mana')
            stats.mp5 = _create_stat(inibin_map, 'mp5')
            stats.range = inibin_map['stats']['range']
            stats.damage = _create_stat(inibin_map, 'dmg')
            stats.attack_speed = _create_stat(inibin_map, 'aspd')
            stats.armor = _create_stat(inibin_map, 'armor')
            stats.magic_resist = _create_stat(inibin_map, 'mr')
            stats.speed = inibin_map['stats']['speed']

            # Find abilities
            # TODO
            abilities = inibin_map['abilities']
            ability_keys = ['skill%d' % i for i in range(1, 5)]
            abilities = [abilities[key] for key in ability_keys]
            print(abilities)

        yield champion
