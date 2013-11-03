from bs4 import BeautifulSoup as Soup

class AbilityLevel(object):
    tooltip_values = {}

    cooldown = -1
    cost = -1

    def __init__(self):
        self.tooltip_values = {}

    def set_scales(self, scale1, scale2):
        # TODO: Refactor?
        self.tooltip_values['@CharAbilityPower1@'] = scale1
        self.tooltip_values['@CharBonusPhysical1@'] = scale1
        self.tooltip_values['@CharAbilityPower2@'] = scale2
        self.tooltip_values['@CharBonusPhysical2@'] = scale2


class Ability(object):
    name = ''
    description = ''
    key = ''
    tooltip = ''

    levels = []

    def __init__(self):
        self.levels = []

    @staticmethod
    def format_tooltip(tooltip):
        """Convert tooltip html to text."""
        tooltip = tooltip.replace('<br>', '\n')
        tooltip = Soup(tooltip)
        tooltip = tooltip.maintext.text
        return tooltip

    KEYS = 'QWER'
    # TODO: Level 6 support
    LEVELS = ['level%d' % i for i in range(1, 6)]

    @classmethod
    def convert_to_level_array(cls, obj):
        """Extract values for 'level%d' keys from obj."""
        # TODO: Improve method description
        # TODO: Level 6 support
        # TODO: Refactor static level array
        arr = []
        for level in cls.LEVELS:
            arr.append(obj.get(level, None))
        return arr

    @classmethod
    def from_inibin(cls, inibin, key):
        """ ...
        key should be range [0, 4) and refer to ability index
        is_ult should be set to True when dealing with the fourth skill a champion has.

        """
        is_ult = key == 3
        levels = cls.LEVELS[:4 if is_ult else 6]

        ability = cls()

        # Extract tooltip text
        ability.name = inibin['name']
        ability.description = inibin['desc']
        ability.key = cls.KEYS[key]
        ability.tooltip = Ability.format_tooltip(inibin['tooltip'])

        # Extract effect amounts for all levels
        effect_amounts = []
        for i in range(1, 6):
            # TODO: Fix for effect 6
            key = 'effect%d' % i
            amounts = cls.convert_to_level_array(inibin[key])
            effect_amounts.append(amounts)
        # Extract all level values for other data
        # TODO: Improve comment
        cooldowns = cls.convert_to_level_array(inibin['cooldown'])
        costs = cls.convert_to_level_array(inibin['cost'])


        for i, level in enumerate(levels):
            level = AbilityLevel()

            # Set ability scale amounts
            # These are constant across all levels
            # TODO: Refactor
            level.set_scales(inibin['scale1'], inibin['scale2'])

            # Get level-specific values
            level.cooldown = cooldowns[i]
            level.cost = costs[i]

            # TODO: Refactor this loop
            for j in range(1, 6):
                # TODO: Reduce duplication with earlier effect extraction
                effect_amount = effect_amounts[j][i]
                level.tooltip_values['@Effect%dAmount@' % j] = effect_amount
