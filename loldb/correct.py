import collections
import warnings


def correct_champions(champions):
    for champion in champions:
        for ability in champion.abilities:
            correct_ability(ability)


ABILITY_CORRECTIONS = {
    # @f1@ is usually attack damage scaling
    # It is also often used for calculated values
    # TODO: Aatrox - Blood Thirst / Blood Price
    # Ahri
    'Fox-Fire': {
        # @f1 shows maximum damage to a single target
        # Each fox-fire after the first does 30% damage
        # So if three hit a single target total is 160% damage
        '@f1@': lambda x: float(int(1.6 * x.tooltip_values['@Effect1Amount@'])),
    },
    # Akali
    'Crescent Slash': {
        '@f1@': 60,
    },
    'Shadow Dance': {
        # How frequently new marks of the shadow are added
        '@f1@': [30, 22.5, 15],
    },
    # Annie
    'Summon: Tibbers': {
        # How long Tibbers is up
        '@Effect6Amount@': 45,
    },
    # Ashe
    'Hawkshot': {
        # Gold earned
        '@f1@': 0,
    },
    'Volley': {
        '@f1@': 100,
    },
    # Caitlyn
    'Ace in the Hole': {
        '@f1@': 200,
    },
    'Piltover Peacemaker': {
        # AD scaling
        '@CharTotalPhysical@': 130,
    },
    # Cassiopeia
    'Twin Fang': {
        # This is actually AP scaling
        # TODO: Check if this value can be calculated from another key
        '@f1@': 50,
    },
    # Corki
    'Gatling Gun': {
        '@f1@': 20,
    },
    'Missile Barrage': {
        # AD scaling
        '@CharTotalPhysical2@': 20,
        # Missile reload time
        # Is affected by CDR
        '@f1@': [12, 10, 8],
    },
    # Darius
    'Decimate': {
        # AD scaling
        '@f2@': 70,
    },
    'Noxian Guillotine': {
        '@f1@': 75,
        # Maximum true damage based on stacks
        '@f3@': lambda x: float(int(2.0 * x.tooltip_values['@Effect1Amount@'])),
    },
    # Draven
    'Spinning Axe': {
        # Bonus damage as percentage of AD
        '@f1@': [45, 55, 65, 75, 85],
    },
    'Stand Aside': {
        '@f1@': 50,
    },
    'Whirling Death': {
        '@f1@': 110,
    },
    # Evelynn
    'Hate Spike': {
        '@f1@': 50,
    },
    'Ravage': {
        '@f1@': 50,
    },
    # Ezreal
    'Mystic Shot': {
        # These two may be interchangeable
        '@f1@': 100,
        # AP scaling
        '@f2@': 20,
    },
    'Trueshot Barrage': {
        '@f1@': 100,
    },
    # Fiora
    'Blade Waltz': {
        '@f1@': 120,
    },
    'Lunge': {
        '@f1@': 60,
    },
    # Gangplank
    'Parrrley': {
        '@f1@': 100,
        # Gold earned
        '@f2@': 0,
    },
    # Garen
    'Decisive Strike': {
        # AD scaling
        '@CharTotalPhysical@': 140,
        # Seconds effect applies to next basic attack
        '@Effect6Amount@': 4.5,
    },
    'Judgment': {
        # Calculated physical damage with scaling
        # TODO: Remove from tooltip
        '@f1@': 0,
    },
}


def correct_ability(ability):
    def apply_correction(key, correction, level):
        if isinstance(correction, collections.Callable):
            correction = correction(level)
        level.tooltip_values[key] = correction

    correction = ABILITY_CORRECTIONS.get(ability.name, None)
    if correction is not None:
        for key, value in correction.items():
            if key not in ability.tooltip:
                warnings.warn('Ability %s has unused correction %s.' %
                              (ability, key))
            # Apply to all levels
            for level in ability.levels:
                apply_correction(key, value, level)
