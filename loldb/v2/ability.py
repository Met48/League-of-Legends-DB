from bs4 import BeautifulSoup as Soup

class AbilityLevel(object):
    tooltip_values = {}

    cooldown = -1
    cost = -1

    def __init__(self):
        self.tooltip_values = {}

    def set_tooltip_value(self, key, value, tooltip=None):
        """
        Sets a tooltip value.

        If tooltip is provided, the key will only be
        set if it is present within the tooltip.

        """
        if tooltip is None or key in tooltip:
            self.tooltip_values[key] = value

    def set_scales(self, scale1, scale2, tooltip=None):
        # TODO: Refactor?
        self.set_tooltip_value('@CharAbilityPower@', scale1, tooltip)
        self.set_tooltip_value('@CharBonusPhysical@', scale1, tooltip)
        self.set_tooltip_value('@CharAbilityPower2@', scale2, tooltip)
        self.set_tooltip_value('@CharBonusPhysical2@', scale2, tooltip)

    def __repr__(self):
        return '<AbilityLevel cost={} cooldown={} tooltip_values={}>'.format(
            self.cost,
            self.cooldown,
            self.tooltip_values
        )


class Ability(object):
    name = ''
    description = ''
    key = ''
    tooltip = ''

    levels = []

    def __init__(self):
        self.levels = []

    def __repr__(self):
        return '<Ability \'{}\'>'.format(self.name)

    @staticmethod
    def format_tooltip(tooltip):
        """Convert tooltip html to text."""
        tooltip = tooltip.replace('<br>', '\n')
        tooltip = Soup(tooltip)
        maintext = tooltip.maintext
        if maintext is None:
            return None
        else:
            return maintext.text

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
        levels = cls.LEVELS[:4 if is_ult else 5]  # 6]

        ability = cls()

        # Extract tooltip text
        ability.name = inibin['name']
        ability.description = inibin['desc']
        ability.key = cls.KEYS[key]
        ability.tooltip = tooltip = Ability.format_tooltip(inibin['tooltip'])

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
            level.set_scales(inibin['scale1'], inibin['scale2'], tooltip)

            # Get level-specific values
            level.cooldown = cooldowns[i]
            level.cost = costs[i]

            # TODO: Refactor this loop
            for j in range(5):
                # TODO: Reduce duplication with earlier effect extraction
                effect_amount = effect_amounts[j][i]
                level.set_tooltip_value(
                    '@Effect%dAmount@' % (j + 1),
                    effect_amount,
                    tooltip
                )

            ability.levels.append(level)

        return ability
