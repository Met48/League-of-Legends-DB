from bs4 import BeautifulSoup as soup


def fix(league):
    """Extracts data from raw ability values."""

    for champion in league['champions'].values():
        new_abilities = {}

        # Process each ability
        for key, ability in champion['abilities'].items():
            if not isinstance(ability, dict):
                continue

            raw = ability['raw']
            new_ability = new_abilities[key] = {}

            tooltip = raw['tooltip']
            tooltip = tooltip.replace('<br>', '\n')
            tooltip = soup(tooltip)
            tooltip = tooltip.maintext.text
            new_ability['tooltip'] = tooltip

            # Format the per-effect bonuses to match the tooltip versions
            is_ult = key == 'skill4'
            levels = ['level%d' % x for x in range(1, 4 if is_ult else 6)]

            # The per-level values for the effects
            new_ability['tooltip_values'] = {}
            for i in range(1, 5):  # 7):
                # TODO: Fix for effects 5 and 6
                if ('@Effect%dAmount@' % i) not in tooltip:
                    continue
                amounts = raw['effect%d' % i]
                amounts = [amounts[x] for x in levels]
                new_ability['tooltip_values']['@Effect%dAmount@' % i] = amounts

            # Scaling
            new_ability['tooltip_values']['@CharAbilityPower@'] = raw['scale1']
            # TODO: Scale2

            # Misc
            new_ability['name'] = raw['name']
            # new_ability['img'] = raw['img']
            new_ability['cooldown'] = [raw['cooldown'][x] for x in levels]
            new_ability['cost'] = [raw['cost'][x] for x in levels]
            new_ability['desc'] = raw['desc']

            del champion['abilities'][key]

        # Convert to a list
        keys = ['skill%d' % i for i in range(1, 5)]
        champion['abilities'] = [new_abilities.get(k, {}) for k in keys]

    return league