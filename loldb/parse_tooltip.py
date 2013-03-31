from bs4 import NavigableString, BeautifulSoup as soup
import re


EXPRESSIONS = {}


def make_re(name, expression, mapping=None):
    """
    Create an re pattern that contains references to other expressions.

    References are denoted as [[name]].
    """

    global EXPRESSIONS

    def rep_ref(match):
        if match.group(1) in EXPRESSIONS:
            return EXPRESSIONS[match.group(1)][0]
        else:
            raise RuntimeError("No expression of name %s" % name)
            # return match.group(0)

    expression = re.sub(r"\[\[([^\]]+)\]\]", rep_ref, expression)
    EXPRESSIONS[name] = expression, re.compile(expression, re.I | re.X), mapping


def search_re(name, string):
    """
    Searches a string using a compiled expression.

    Returns the match object and a mapping, if applicable.
    """

    global EXPRESSIONS

    assert name in EXPRESSIONS

    expression = EXPRESSIONS[name]
    matches = expression[1].finditer(string)
    matches = list(matches)
    mappings = []

    for match in matches:
        mapping = None
        if expression[2] is not None:
            mapping = {}
            for k, v in expression[2].items():
                try:
                    mapping[k] = match.group(v)
                except IndexError:
                    mapping[k] = None
        mappings.append(mapping)

    return matches, mappings


# To skip all characters that do not involve a key or constant
make_re('skip', r"""
    (?:
        [^@\d]*?  # Stop before any @key@ or numeric constant
    )
    """)

# To read the value of a key or constant
make_re('value', r"""
    (?:
        \s*
        (
            @[^@]+@
            |
            \d+(?:\.\d+)?
        )
        \s*
    )
    """)

# Slows
# Slows can either diminish over or last a specific amount of time
# Both conditions must be checked for
# TODO: Investigate any cases where one of the two optional parts are not matched
# TODO: Any skills where the slow amount scales with a stat?
make_re('slow', r"""
    slow(?:s|ing)?  # Keyword to know it's a slow
    [[skip]]
    by
    [[value]]
    %  # Must be percentage for slows
    # TODO: Scaling
    (?:  # Optionally find how the effect persists
        (?:  # Diminishes
            [^.]*?
            (?:diminish|decrease)
            [^.@\d]*  # TODO: Refactor
            over
            [[value]]
            second
        )
        |
        (?:  # Lasts
            \s* for
            [[value]]
            second
        )
    )?""", {
        'amount': 1,
        'diminishes_over': 2,
        'lasts': 3
        })


make_re('scaling', r"""
    (?:
        [[skip]]
        \(\+
        [[value]]
        \)
    )""")

make_re('damage', r"""
    (?:  # Optional "after x seconds ..."
        # TODO: Move into own pattern?
        after
        [[value]]
        second
        [[skip]]
    )?
    deal(?:s|ing)
    [[skip]]
    [[value]]
    [[scaling]]
    [[scaling]]?  # Up to two stats to scale off of
    [[skip]]
    (\w+)  # magic|physical)  # Kind
    \s* damage
    (?:  # Optional "over x seconds"
        \s* over
        (?:\s* the \s* next)?
        [[value]]
        second
    )?
    (  # Optional "per second"
        \s*
        (?: each | per )?
        \s* second
    )?
    (?:  # Optional "at x range"
        # TODO: Only used by cait ult, worth keeping?
        \s* at
        [[value]]
        range
    )?
    (?:  # Optional "plus x% of missing? health"
        \s* plus
        [[value]]
        % \s* of
        [^.(@\d]*
        (missing)?
        \s* health
    )?
    """, {
        'delay': 1,
        'amount': 2,
        'scaling_1': 3,
        'scaling_2': 4,
        'kind': 5,
        'over_duration': 6,
        'is_per_second': 7,
        'range': 8,
        'additional_percentage_of_hp': 9,
        'additional_percentage_is_of_missing_hp': 10
        })

        # Buffs:
        #     for \d+ seconds, lee sin gains @E?A@ lifesteal and spell vamp
        #     increasing movement speed by @E?A@% and attack speed by @E1A@% for @E?A@ seconds
        #     gaining @E?A@ attack damage plus @E?A@ per \d+% health missing
        #     gains @E?A@ movment speed

# TODO: Improve the way these stats are handled - should it even be hard coded?
BUFFABLE_STATS = """
    life steal
    lifesteal
    spell vamp
    spellvamp
    attack damage
    damage
    ability power
    ap
    movement speed
    speed
    health
    mana
    armor
    magic resist
    mr
    attack speed
    energy
    ferocity
"""
BUFFABLE_STATS = [x.strip().replace(' ', r'\s*') for x in BUFFABLE_STATS.split('\n') if x.strip()]
make_re('stat', r"(?:\s* (?:%s) \s*)" % '|'.join(BUFFABLE_STATS))
del BUFFABLE_STATS

# TODO: All of this buff code is terrible!
#   There should be a more generic way to account for all the varieties
#   - for \d+ seconds ...
#   - ... for \d+ seconds
#   - ... gain \d stat and \d stat ...
#   - ... gain \d stat and stat ...
#   - ... increase stat by \d ...
#   - ... increase stat and stat by \d ...
#   - ... increase stat by \d and stat by \d ...

make_re('buff_pre', r"""
    (?:
        # Duration 1
        for
        [[value]]
        second
        [[skip]]
    )?
    gain
    [[skip]]
    [[value]]
    %?  # TODO: Capture when it's a percentage
    # TODO: Scaling
    \s*
    ([[stat]])  # Stat being gained
    (?:  # More than one stat?
        \s*
        (?: ,? \s* (?:and)?)
        \s*
        [[value]]?
        ([[stat]])
    ){0,1}
    (?:
        # Duration 2
        # TODO: Confirm one of the two duration patterns match
        \s*
        (?: over | for )
        [[value]]
        second
    )?
    """, {
        # TODO: How to handle repeat?
        'buff_duration': 1,
        'buff_1_amount': 2,
        'buff_1': 3,
        'buff_2_amount': 4,
        'buff_2': 5,
        # Do any skills even have three buffs?
        # 'buff_3_amount': 6,
        # 'buff_3': 7,
        'buff_duration_2': 6
        })

make_re('buff_post', r"""
    (?: increases? )
    ([[stat]])
    (?:  # More than one stat?
        \s*
        (?: ,? \s* (?: and )?)
        ([[stat]])
    ){0,1}
    \s* by
    [[value]]
    for
    [[value]]
    second
    """, {
        'buff_1': 1,
        'buff_2': 2,
        'buff_1_amount': 3,
        'buff_duration': 4,
        # Do any skills have three buffs?
        })

#shielding them both for @Effect1Amount@ (+@CharAbilityPower@) damage over the next 5 seconds
make_re('shield', r"""
    shield(?:s|ing)
    [[skip]]
    [[value]]
    [[scaling]]
    [[scaling]]?  # Up to two stats to scale off of
    [[skip]]
    (\w+)?  # magic|physical)  # Kind
    \s* damage
    (?:  # Optional "over x seconds"
        \s* over
        (?:\s* the \s* next)?
        [[value]]
        second
    )?
    (?:  # Optional "plus x% of missing? health"
        \s* plus
        [[value]]
        % \s* of
        [^.(@\d]*
        (missing)?
        \s* health
    )?
    """, {
        'amount': 1,
        'scaling_1': 2,
        'scaling_2': 3,
        'kind': 4,
        'over_duration': 5,
        'range': 6,
        'additional_percentage_of_hp': 7,
        'additional_percentage_is_of_missing_hp': 8
        })

# Font colours:
#   #FF9900 for splitting up ability parts (ex. 'Passive: ', 'Passive? as Valor: ', 'Active: ')
#   #FF8C00 scales of physical damage (not sure if this includes base)
#   #99FF99 scales of ap


def parse_ability(ability):  # raw, tooltip):
    if not isinstance(ability, dict):
        return {
            'name': ability
        }
    tooltip = soup(ability['raw']['tooltip'])
    out = {
        'name': tooltip.titleleft.text,
        'scalings': [],
        # 'raw': ability['raw']  # TODO: Get rid of this entirely
        'tooltip': tooltip.maintext.text
    }

    cost = tooltip.subtitleleft.text.lower()
    if 'mana' in cost:
        out['res'] = 'mana'
    elif 'energy' in cost:
        out['res'] = 'energy'
    elif 'health' in cost:
        out['res'] = 'health'
    elif 'heat' in cost:
        out['res'] = 'heat'
    elif 'no cost' in cost:
        out['res'] = 'none'
    else:
        out['res'] = None
        print "WARNING: NO RESOURCE DETECTED FOR", out['name']

    text = tooltip.maintext.text

    # TODO: Use font colours

    abc = """
        For damage dealt, there are a few forms:
            dealing @E?A@ <font>(+@CAB@)</font> magic damage
            dealing @E?A@ <font>(+@CAB@)</font> magic damage over \d+ seconds
            deals @E?A@ <font>(+@CAB@)</font> magic damage to nearby enemies
            dealing @E?A@ <font>(+@f1@)</font> physical damage
            dealing @E?A@ <font>(+@f1@)</font> physical damage plus \d+% of their missing heath (Max: \d+ damage vs. Monsters)
            dealing @E?A@ <font>(+@f1@)</font> physical damage at @E?A@ range
            2. dealing @E1A@ physical damage
            3. dealing @E1A@ (+@f1@) (+@f2@) physical damage ???

        Shielding:
            shield(ing)? them both for @E?A@ <font>(+@CAB@)</font> damage over the next \d+ seconds

        Buffs:
            for \d+ seconds, lee sin gains @E?A@ lifesteal and spell vamp
            increasing movement speed by @E?A@% and attack speed by @E1A@% for @E?A@ seconds
            gaining @E?A@ attack damage plus @E?A@ per \d+% health missing
            gains @E?A@ movment speed

        Knockback:
            knocks surrounding units back @E?A@ distance

        Stun:
            stun the target for \d+ seconds

        Range:
            within @E?A@ distance of him  (warwick ability)

        Random notes:
            - With Lee Sin, his first part tooltips include the second part's
    """

    for font_tag in tooltip.maintext('font'):
        if font_tag['color'] == '#FF8C00':
            # Physical damage
            previous = font_tag.previous_sibling
            if previous is None:
                continue  # Just to prevent assertion for now
            assert isinstance(previous, NavigableString)
            #

    # Find specific effects
    # Slows
    # match, mapping = search_re('slow', text)
    # if match:
    #     out['slow'] = mapping['amount']
    #     diminishes_over = mapping['diminishes_over']
    #     duration = mapping['lasts']
    #     if not diminishes_over and not duration:
    #         print "WARNING: Slow percentage", out["slow"], "found, no duration."
    #     else:
    #         out['slow_duration'] = diminishes_over or duration
    #         out['slow_diminishes'] = diminishes_over is not None

    # Quick, find all matches!
    matchers = ['slow', 'damage', 'buff_pre', 'buff_post', 'shield']
    for matcher in matchers:
        matches, mappings = search_re(matcher, text)
        if len(matches) == 0:
            out[matcher] = None
        elif len(matches) == 1:
            out[matcher] = mappings[0]
        else:
            for i, (match, mapping) in enumerate(zip(matches, mappings)):
                out['%s_%d' % (matcher, i)] = mapping

    return out


def main():
    import json
    import yaml

    with open('league.part.json') as f:
        dat = json.load(f)

    dat = dat['champions']

    counts = {
        'ok': 0,
        'bad': 0
    }

    out = {
        'bad': {},
        'ok': {},

        'counts': counts,
    }

    EA_PAT = re.compile(r"@Effect(\d+)Amount@", re.I)

    def walk(node, collector):
        for k, v in node.items():
            if isinstance(v, dict):
                walk(v, collector)
            elif isinstance(v, basestring):
                match = EA_PAT.match(v)
                if match:
                    collector[match.group(0)] = k

    def init_struct(base, champ_name, ability_name, val):
        base = out[base]
        if champ_name not in base:
            base[champ_name] = {}
        if ability_name not in base[champ_name]:
            base[champ_name][ability_name] = val
        return base[champ_name][ability_name]

    for champ_name, champion in dat.items():
        for key, ability in champion['abilities'].items():
            if not isinstance(ability, dict):
                init_struct('bad', champ_name, key, {'missing': 4})
                counts['bad'] += 1
                continue
            res = parse_ability(ability)
            collector = {}
            walk(res, collector)
            expected = len(EA_PAT.findall(ability['raw']['tooltip']))
            collector['missing'] = expected - len(collector)
            collector['raw'] = res
            if collector['missing'] != 0:
                init_struct('bad', champ_name, key, collector)
                counts['bad'] += 1
            else:
                init_struct('ok', champ_name, key, collector)
                counts['ok'] += 1

    with open('tooltip_status.yaml', 'w') as f:
        f.write(yaml.safe_dump(out))


def test():
    tooltip = "Increases Armor and Magic Resist by @Effect1Amount@ for @Effect3Amount@ seconds. Deals @Effect2Amount@ (+@CharAbilityPower@) magic damage to enemies who attack Annie with basic attacks."
    tooltip = "<titleleft></titleleft><subtitleleft></subtitleleft><maintext>%s</maintext>" % tooltip
    res = parse_ability({'raw': {'tooltip': tooltip}})
    from pprint import pprint
    pprint(res)

if __name__ == '__main__':
    main()
    # test()

    HISTORY = """
        initial
            counts: {bad: 359, ok: 85}
        buff_post
            counts: {bad: 358, ok: 86}
            ... Just the one skill?
        fix multiple matches
            counts: {bad: 350, ok: 94}
        delayed damage
            counts: {bad: 347, ok: 97}
        more buff_pre, add ferocity + energy
            counts: {bad: 340, ok: 104}
    """
