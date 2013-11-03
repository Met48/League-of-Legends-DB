import collections
import re

from inibin import Inibin

from .ability import Ability


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
    attack_speed = Stat(0, 0)
    armor = Stat(0, 0)
    magic_resist = Stat(0, 0)
    range = 0
    speed = 0

    # TODO: These methods are specific to champion inibins, should they be here?
    @staticmethod
    def _create_stat(inibin_map, key):
        """Read base and per_level values from inibin map."""
        stat = inibin_map['stats'][key]
        return Stat(stat['base'], stat['per_level'])

    def update_from_inibin(self, inibin_map):
        # TODO: Better error checking
        self.hp = self._create_stat(inibin_map, 'hp')
        self.hp5 = self._create_stat(inibin_map, 'hp5')
        self.mana = self._create_stat(inibin_map, 'mana')
        self.mp5 = self._create_stat(inibin_map, 'mp5')
        self.range = inibin_map['stats']['range']
        self.damage = self._create_stat(inibin_map, 'dmg')
        self.attack_speed = self._create_stat(inibin_map, 'aspd')
        self.armor = self._create_stat(inibin_map, 'armor')
        self.magic_resist = self._create_stat(inibin_map, 'mr')
        self.speed = inibin_map['stats']['speed']


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
    abilities = []

    def __init__(self, internal_name):
        self.internal_name = internal_name
        self.stats = Stats()
        self.lore = Lore()
        self.ratings = Ratings()
        self.tips_as = []
        self.tips_against = []
        self.tags = set()
        self.abilities = []

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

    def __lt__(self, other):
        return self.id < other.id

    def __repr__(self):
        return '<Champion {} \'{}\'>'.format(self.id, self.name)


def _get_tips(tips_str):
    """Get list of tips from tips string."""
    return [tip for tip in tips_str.split('*') if tip]


def _get_description(desc):
    """Format description text."""
    # Description often contains '' instead of "
    return desc.replace("''", '"')


def _find_inibin(provider, pattern):
    raf_master = provider.get_raf_master()
    raf_results = list(raf_master.find_re(pattern))
    if not raf_results:
        print('No inibin for %s' % pattern)
    if len(raf_results) > 1:
        # TODO: Is this ever triggered?
        print('Ambiguous inibin for %s' % pattern)
    try:
        inibin = Inibin(data=raf_results[0].read())
    except Exception:  # TODO: Less generic Exception
        print('Malformed inibin for %s' % pattern)
        return None
    else:
        return inibin


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
        champ_name = champion.internal_name.lower()
        champ_pattern = '^data/characters/{0}/{0}.inibin$'.format(champ_name)
        champ_inibin = _find_inibin(provider, champ_pattern)
        if champ_inibin is not None:
            font_config = provider.get_font_config()
            champ_inibin = champ_inibin.as_champion(font_config)
            # Read stats
            champion.stats.update_from_inibin(champ_inibin)

            # Find abilities
            abilities = champ_inibin['abilities']
            ability_keys = ['skill%d' % i for i in range(1, 5)]
            abilities = [abilities[key] for key in ability_keys]
            for i, ability_name in enumerate(abilities):
                ability_pattern = r"^data/(?:characters/{0}/)?spells/{1}.inibin$".format(champ_name, ability_name)
                ability_inibin = _find_inibin(provider, ability_pattern)
                if ability_inibin is None:
                    continue
                ability_inibin = ability_inibin.as_ability(font_config)
                ability = Ability.from_inibin(ability_inibin, i)
                champion.abilities.append(ability)

        yield champion
